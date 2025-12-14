# The "Shanahan Algorithm": Predicting 49ers Play-Calling

## Project Overview
This project aims to build a **Binary Classification Model** to predict whether the San Francisco 49ers will execute a **Run** or a **Pass** play. By analyzing the "Kyle Shanahan Era" (2017–Present), we aim to determine if an AI model can identify play-calling tendencies more accurately than a naive baseline.

## Problem Statement
In the NFL, anticipating the opponent's next move is key. While coaches rely on intuition and film, play-calling often follows statistical patterns. This project leverages Machine Learning to decode those patterns.

## Data
- **Source**: Raw play-by-play logs scraped from [Pro-Football-Reference](https://www.pro-football-reference.com/).
- **Scope**: 2017 – Present (Shanahan Era).
- **Target**: `Play Type` (0 = Run, 1 = Pass).

## Methodology
### Data Splitting
- **Training**: 2017–2023 (Learning patterns).
- **Validation**: 2024 (Hyperparameter tuning on a "down" year).
- **Testing**: 2025 (Blind evaluation on current season).

### Models
1. **Logistic Regression**: Baseline and feature importance.
2. **Random Forest**: Capturing non-linear interactions.
3. **XGBoost**: High-performance gradient boosting.

## Setup & Usage
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Pipeline**:
   ```bash
   python src/main.py
   ```
   This will scrape data (if needed), parse it, and generate `data/processed/49ers_plays.csv`.
3. **Explore Data**:
   Open `notebooks/eda.ipynb` to visualize play-calling tendencies.

## Project Structure
- `src/`: Source code for scraping, parsing, and feature engineering.
- `data/`: Raw and processed data storage.
- `notebooks/`: Jupyter notebooks for EDA and modeling.
