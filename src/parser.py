import pandas as pd
from bs4 import BeautifulSoup
import re
import os

def parse_game_html(filepath):
    """
    Opens a local HTML file and extracts the play-by-play table.
    Returns a DataFrame.
    """
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None

    with open(filepath, 'rb') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    
    # The play-by-play table usually has id="pbp"
    table = soup.find('table', id='pbp')
    
    if not table:
        # PFR often comments out tables. We need to find the comment containing the table.
        from bs4 import Comment
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if 'id="pbp"' in comment:
                # Parse the comment content as HTML
                comment_soup = BeautifulSoup(comment, 'html.parser')
                table = comment_soup.find('table', id='pbp')
                if table:
                    break
    
    if not table:
        print(f"No PBP table found in {filepath}")
        return None

    # Parse table manually to extract 'csk' attribute from location
    # pd.read_html drops attributes
    data = []
    headers = []
    
    # Get headers
    thead = table.find('thead')
    if thead:
        # Use the last row of thead for column names (handling multi-level headers)
        header_rows = thead.find_all('tr')
        if header_rows:
            cols = header_rows[-1].find_all(['th', 'td'])
            headers = [col.get_text(strip=True) for col in cols]
    
    # Get rows
    tbody = table.find('tbody')
    if not tbody:
        return None
        
    rows = tbody.find_all('tr')
    for row in rows:
        # Skip divider rows or header rows in tbody
        if 'thead' in row.get('class', []) or 'divider' in row.get('class', []):
            continue
            
        cells = row.find_all(['th', 'td'])
        if not cells:
            continue
            
        row_data = {}
        # Map cells to headers if possible, or just list
        # PFR tables are consistent, let's rely on data-stat if available
        
        # Better approach: extract data-stat as keys
        for cell in cells:
            stat = cell.get('data-stat')
            text = cell.get_text(strip=True)
            if stat:
                row_data[stat] = text
                # Special handling for location to get csk
                if stat == 'location':
                    row_data['location_csk'] = cell.get('csk')
        
        if row_data:
            data.append(row_data)

    if not data:
        return None
        
    df = pd.DataFrame(data)
    return df

def clean_play_data(df, game_id):
    """
    Cleans the raw PBP DataFrame.
    """
    # Create a copy to avoid SettingWithCopy warnings
    df = df.copy()
    
    # 1. Standardize Column Names
    # We are now using data-stat keys from the HTML
    rename_map = {
        'quarter': 'quarter',
        'qtr_time_remain': 'time_remaining',
        'down': 'down',
        'yds_to_go': 'ydstogo',
        'location': 'yrdline',
        'detail': 'desc',
        'pbp_score_aw': 'away_score',
        'pbp_score_hm': 'home_score',
        'exp_pts_before': 'epb',
        'exp_pts_after': 'epa'
    }
    df = df.rename(columns=rename_map)
    
    # 2. Remove Header Rows and Invalid Rows
    df = df.dropna(subset=['down'])
    df = df[df['down'] != ''] # Handle empty strings if any
    
    # 3. Filter for Offensive Plays
    df = df.dropna(subset=['desc'])
    
    # Filter out ambiguous 50-yard line plays (empty location)
    df = df.dropna(subset=['yrdline'])
    df = df[df['yrdline'] != '']
    
    # 4. Filter for 49ers Offense
    # Logic:
    # location_csk is "Yards To Go" for the offense.
    # location text is e.g. "SFO 45".
    # If location side is SFO (Home/Team):
    #   If csk == line: Opponent is offense (at SFO 45, 45 to go).
    #   If csk == 100 - line: SFO is offense (at SFO 45, 55 to go).
    # BUT wait, if SFO is at SFO 45.
    # SFO offense: 55 yards to go.
    # Opponent offense: 45 yards to go.
    # So checking csk vs line distinguishes it.
    
    def is_49ers_offense(row):
        loc = str(row.get('yrdline', ''))
        csk = row.get('location_csk')
        
        if not loc or not csk:
            return False
            
        try:
            parts = loc.split()
            if len(parts) != 2:
                return False
            side, line = parts[0], int(parts[1])
            csk = int(csk)
            
            # 49ers are usually SFO or SF
            is_sfo_side = side in ['SFO', 'SF']
            
            if is_sfo_side:
                # On SFO side.
                # If SFO offense: yards to go = 100 - line.
                # If Opp offense: yards to go = line.
                if abs(csk - (100 - line)) <= 1:
                    return True
                elif abs(csk - line) <= 1:
                    return False
            else:
                # On Opponent side.
                # If SFO offense: yards to go = line.
                # If Opp offense: yards to go = 100 - line.
                if abs(csk - line) <= 1:
                    return True
                elif abs(csk - (100 - line)) <= 1:
                    return False
                    
            return False
        except ValueError:
            return False

    df['is_49ers'] = df.apply(is_49ers_offense, axis=1)
    # df = df[df['is_49ers'] == True]
    
    # 5. Parse Play Type (Run vs Pass)
    def get_play_type(desc):
        desc = str(desc).lower()
        if 'pass' in desc or 'sacked' in desc or 'scramble' in desc:
            return 'pass'
        if 'left' in desc or 'right' in desc or 'middle' in desc or 'up the middle' in desc:
            return 'run'
        return 'other'

    df['play_type'] = df['desc'].apply(get_play_type)
    
    # Filter only run/pass
    df = df[df['play_type'].isin(['run', 'pass'])]
    
    # 6. Add Game ID
    df['game_id'] = game_id
    
    # 7. Drop Description
    df = df.drop(columns=['desc'])

    return df

if __name__ == "__main__":
    # Test run
    # Assumes we have a file at data/raw/2024/202309100pit.html (from scraper test)
    # You might need to adjust the filename based on what the scraper actually saved
    pass
