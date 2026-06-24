#!/usr/bin/env python3
"""
Total coverage ranking.
Input: data/processed/coverage_matrix.csv
Output: results/rankings/total_ranking.csv
"""
import sys
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'
RANKINGS_DIR = PROJECT_ROOT / 'results' / 'rankings'

def total_coverage_ranking(coverage_df: pd.DataFrame):
    fragment_cols = [c for c in coverage_df.columns if c.startswith('fragment_')]
    coverage_df['total_coverage'] = coverage_df[fragment_cols].sum(axis=1)
    sorted_df = coverage_df.sort_values(
        by=['total_coverage', 'test_id'],
        ascending=[False, True]
    ).reset_index(drop=True)
    rank_df = pd.DataFrame({
        'rank': range(1, len(sorted_df)+1),
        'test_id': sorted_df['test_id'],
        'total_coverage': sorted_df['total_coverage']
    })
    return rank_df

def main():
    coverage_path = PROCESSED_DATA_DIR / 'coverage_matrix.csv'
    if not coverage_path.exists():
        print(f"Error: {coverage_path} not found. Run parse_matrix.py first.")
        sys.exit(1)

    RANKINGS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(coverage_path)
    rank_df = total_coverage_ranking(df)
    out_file = RANKINGS_DIR / 'total_ranking.csv'
    rank_df.to_csv(out_file, index=False)
    print(f"Saved total ranking to {out_file}")

if __name__ == '__main__':
    main()