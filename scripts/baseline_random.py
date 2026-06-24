#!/usr/bin/env python3
"""
Generate random rankings.
Input: data/processed/coverage_matrix.csv
Output: results/rankings/random_ranking_seed_*.csv
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'
RANKINGS_DIR = PROJECT_ROOT / 'results' / 'rankings'

def generate_random_rankings(coverage_df: pd.DataFrame, n_runs: int = 30, seed_base: int = 42):
    test_ids = coverage_df['test_id'].tolist()
    for run in range(n_runs):
        seed = seed_base + run
        np.random.seed(seed)
        shuffled = np.random.permutation(test_ids).tolist()
        rank_df = pd.DataFrame({'rank': range(1, len(shuffled)+1), 'test_id': shuffled})
        out_file = RANKINGS_DIR / f'random_ranking_seed_{seed}.csv'
        rank_df.to_csv(out_file, index=False)
        print(f"Saved random ranking with seed {seed} to {out_file}")

def main():
    coverage_path = PROCESSED_DATA_DIR / 'coverage_matrix.csv'
    if not coverage_path.exists():
        print(f"Error: {coverage_path} not found. Run parse_matrix.py first.")
        sys.exit(1)

    RANKINGS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(coverage_path)
    generate_random_rankings(df)

if __name__ == '__main__':
    main()