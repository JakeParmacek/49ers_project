from src.features import load_data, preprocess_features

try:
    df = load_data('data/processed/49ers_plays.csv')
    print(f"Loaded {len(df)} plays.")
    
    features = preprocess_features(df)
    print(f"Processed {len(features)} plays.")
    print(features.head())
    print(features.describe())
except Exception as e:
    print(f"Error: {e}")
