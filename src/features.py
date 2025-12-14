import pandas as pd
import numpy as np

def load_data(filepath):
    """
    Loads the processed CSV file.
    """
    return pd.read_csv(filepath)

def preprocess_features(df):
    """
    Transforms raw columns into features for modeling.
    """
    df = df.copy()
    
    # 1. Convert Numeric Columns
    cols_to_numeric = ['quarter', 'down', 'ydstogo', 'location_csk', 'away_score', 'home_score']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Drop rows with missing critical features
    df = df.dropna(subset=['quarter', 'down', 'ydstogo', 'location_csk'])
    
    # 2. Yards to Endzone
    # Since we filtered for 49ers offense, location_csk IS yards to go.
    df['yards_to_endzone'] = df['location_csk']
    
    # 3. Score Differential
    # Determine if 49ers are Home or Away based on game_id
    # game_id format: YYYYMMDD0team. 'team' is home team.
    # 49ers are 'sfo'.
    
    def get_score_diff(row):
        game_id = str(row['game_id'])
        home_team = game_id[-3:]
        
        is_home = (home_team == 'sfo')
        
        if is_home:
            return row['home_score'] - row['away_score']
        else:
            return row['away_score'] - row['home_score']

    df['score_differential'] = df.apply(get_score_diff, axis=1)
    
    # 4. Time Remaining (in seconds)
    def parse_time(t_str):
        try:
            m, s = map(int, t_str.split(':'))
            return m * 60 + s
        except:
            return None
            
    df['seconds_in_qtr'] = df['time_remaining'].apply(parse_time)
    
    # Total seconds remaining in game
    # Q1: 2700 + seconds_in_qtr (Wait, 15:00 is start)
    # Time remaining in game = (4 - quarter) * 900 + seconds_in_qtr?
    # No, seconds_in_qtr is time remaining in quarter.
    # Q4, 15:00 -> 900 seconds left.
    # Q1, 15:00 -> 3600 seconds left.
    # Formula: (4 - quarter) * 900 + seconds_in_qtr
    # Note: Overtime (Q5) might need handling, but for now assume standard.
    
    df['game_seconds_remaining'] = (4 - df['quarter']) * 900 + df['seconds_in_qtr']
    
    # Handle Overtime (Quarter > 4)
    # If Q5, game_seconds_remaining would be negative with above formula.
    # Let's just set it to seconds_in_qtr for OT.
    df.loc[df['quarter'] > 4, 'game_seconds_remaining'] = df['seconds_in_qtr']
    
    # 5. Encode Target
    df['target'] = df['play_type'].map({'run': 0, 'pass': 1})
    
    # Select final features
    feature_cols = [
        'game_id', 'quarter', 'down', 'ydstogo', 'yards_to_endzone', 
        'score_differential', 'game_seconds_remaining', 'target'
    ]
    
    return df[feature_cols]
