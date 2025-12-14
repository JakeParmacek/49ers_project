import requests
from bs4 import BeautifulSoup
import time
import os
from tqdm import tqdm
import subprocess

def fetch_url_content(url):
    """
    Fetches URL content using curl to bypass TLS fingerprinting issues with requests.
    """
    try:
        # -L follows redirects, -s is silent
        result = subprocess.run(['curl', '-L', '-s', url], capture_output=True, text=False)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error fetching {url}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception fetching {url}: {e}")
        return None

def get_season_game_urls(year):
    """
    Fetches the 49ers schedule page for a given year and extracts links to individual game logs.
    Returns a list of (game_id, url) tuples.
    """
    url = f"https://www.pro-football-reference.com/teams/sfo/{year}.htm"
    print(f"Fetching schedule for {year}...")
    
    content = fetch_url_content(url)
    if not content:
        return []

    time.sleep(3) # Rate limiting

    soup = BeautifulSoup(content, 'html.parser')
    
    game_links = []
    # Find the schedule table
    table = soup.find('table', id='games')
    if not table:
        print(f"Could not find schedule table for {year}")
        return []

    for row in table.find_all('tr'):
        # Look for the boxscore link
        boxscore_cell = row.find('td', {'data-stat': 'boxscore_word'})
        if boxscore_cell:
            link = boxscore_cell.find('a')
            if link:
                href = link['href']
                # href looks like /boxscores/202309100pit.htm
                # We want the game_id: 202309100pit
                game_id = href.split('/')[-1].replace('.htm', '')
                full_url = f"https://www.pro-football-reference.com{href}"
                game_links.append((game_id, full_url))
    
    return game_links

def fetch_game_html(url):
    """
    Downloads the page content with rate limiting.
    """
    print(f"Fetching {url}...")
    content = fetch_url_content(url)
    time.sleep(3) # Rate limiting
    return content

def save_raw_html(content, filepath):
    """
    Saves the raw HTML to disk.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(content)

if __name__ == "__main__":
    # Test run for 2024
    year = 2024
    links = get_season_game_urls(year)
    print(f"Found {len(links)} games for {year}")
    for game_id, url in links[:1]: # Just test one
        print(f"Testing fetch for {game_id}")
        content = fetch_game_html(url)
        if content:
            save_path = f"data/raw/{year}/{game_id}.html"
            save_raw_html(content, save_path)
            print(f"Saved to {save_path}")
