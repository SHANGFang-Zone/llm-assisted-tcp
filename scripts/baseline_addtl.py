#!/usr/bin/env python3
"""
Additional coverage ranking with tie group logging.
Input: data/processed/coverage_matrix.csv
Output: results/rankings/addtl_ranking.csv, results/rankings/addtl_tie_groups.csv
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'
RANKINGS_DIR = PROJECT_ROOT / 'results' / 'rankings'

def additional_coverage_ranking(coverage_df: pd.DataFrame):
    fragment_cols = [c for c in coverage_df.columns if c.startswith('fragment_')]
    coverage_matrix = coverage_df[fragment_cols].values.astype(bool)
    test_ids = coverage_df['test_id'].values
    total_coverage = coverage_matrix.sum(axis=1)

    n_tests = len(test_ids)
    selected = [False] * n_tests
    covered = np.zeros(coverage_matrix.shape[1], dtype=bool)
    ranking = []
    tie_groups = []

    for step in range(n_tests):
        best_add = -1
        candidates = []
        for i in range(n_tests):
            if not selected[i]:
                add = np.sum(coverage_matrix[i] & ~covered)
                if add > best_add:
                    best_add = add
                    candidates = [i]
                elif add == best_add:
                    candidates.append(i)

        if len(candidates) > 1:
            tie_groups.append({
                'step': step + 1,
                'additional_coverage': int(best_add),
                'candidate_tests': ';'.join([test_ids[i] for i in candidates])
            })

        # Tie-break by test_id (deterministic baseline)
        chosen_index = sorted(candidates, key=lambda i: test_ids[i])[0] if candidates else None
        if chosen_index is None:
            break

        selected[chosen_index] = True
        covered = covered | coverage_matrix[chosen_index]
        ranking.append({
            'rank': step + 1,
            'test_id': test_ids[chosen_index],
            'additional_coverage': int(best_add),
            'total_coverage': int(total_coverage[chosen_index]),
            'tie_group_size': len(candidates)
        })

    rank_df = pd.DataFrame(ranking)
    return rank_df, tie_groups

def main():
    coverage_path = PROCESSED_DATA_DIR / 'coverage_matrix.csv'
    if not coverage_path.exists():
        print(f"Error: {coverage_path} not found. Run parse_matrix.py first.")
        sys.exit(1)

    RANKINGS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(coverage_path)
    rank_df, tie_groups = additional_coverage_ranking(df)

    rank_file = RANKINGS_DIR / 'addtl_ranking.csv'
    rank_df.to_csv(rank_file, index=False)
    print(f"Saved addtl ranking to {rank_file}")

    if tie_groups:
        tie_df = pd.DataFrame(tie_groups)
        tie_file = RANKINGS_DIR / 'addtl_tie_groups.csv'
        tie_df.to_csv(tie_file, index=False)
        print(f"Saved tie groups to {tie_file}")
    else:
        print("No tie groups found.")

if __name__ == '__main__':
    main()