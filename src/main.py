import os
import pandas as pd
from tqdm import tqdm
from scraper import get_season_game_urls, fetch_game_html, save_raw_html
from parser import parse_game_html, clean_play_data
import time

def main():
    years = range(2017, 2026) # 2017 to 2025
    all_plays = []

    for year in years:
        print(f"\n--- Processing Season {year} ---")
        
        # 1. Get Game URLs
        game_links = get_season_game_urls(year)
        
        for game_id, url in tqdm(game_links, desc=f"Games in {year}"):
            # Define paths
            raw_dir = f"data/raw/{year}"
            raw_path = f"{raw_dir}/{game_id}.html"
            
            # 2. Check Cache / Scrape
            if not os.path.exists(raw_path):
                content = fetch_game_html(url)
                if content:
                    save_raw_html(content, raw_path)
                else:
                    continue # Skip if fetch failed
            
            # 3. Parse
            df = parse_game_html(raw_path)
            if df is not None:
                clean_df = clean_play_data(df, game_id)
                if not clean_df.empty:
                    all_plays.append(clean_df)

    # 4. Save Final CSV
    if all_plays:
        final_df = pd.concat(all_plays, ignore_index=True)
        final_df.to_csv("data/processed/49ers_plays.csv", index=False)
        print(f"Saved {len(final_df)} plays to data/processed/49ers_plays.csv")
    else:
        print("No plays found.")

if __name__ == "__main__":
    main()
