#!/usr/bin/env python3
"""
Evaluate ranking metrics: first failing rank, normalized, APFD, top-k, runtime to first failure.
Input: ranking file (csv with rank, test_id) and coverage matrix (test_id, result, fragments)
Output: metrics summary (appended or new)
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'
RANKINGS_DIR = PROJECT_ROOT / 'results' / 'rankings'
METRICS_DIR = PROJECT_ROOT / 'results' / 'metrics'
TEST_METADATA_PATH = PROCESSED_DATA_DIR / 'test_metadata.csv'

def compute_metrics(ranking_df: pd.DataFrame, coverage_df: pd.DataFrame, test_metadata: pd.DataFrame = None):
    merged = ranking_df.merge(coverage_df[['test_id', 'result']], on='test_id', how='left')
    if 'result' not in merged.columns:
        raise ValueError("Coverage matrix missing 'result' for test_ids.")

    failing = merged[merged['result'] == 'FAIL']
    n_total = len(merged)
    n_failing = len(failing)

    metrics = {}

    if n_failing > 0:
        first_fail_rank = failing['rank'].min()
        metrics['first_failing_rank'] = int(first_fail_rank)
        metrics['normalized_first_failing_rank'] = first_fail_rank / n_total
        sum_ranks = failing['rank'].sum()
        apfd = 1 - (sum_ranks / (n_total * n_failing)) + (1 / (2 * n_total))
        metrics['APFD'] = apfd
    else:
        metrics['first_failing_rank'] = np.nan
        metrics['normalized_first_failing_rank'] = np.nan
        metrics['APFD'] = np.nan

    top_k = [0.05, 0.10, 0.20, 0.30]
    for k in top_k:
        top_n = int(np.ceil(k * n_total))
        top_tests = merged.head(top_n)
        detected = (top_tests['result'] == 'FAIL').any()
        metrics[f'top_{int(k*100)}_detected'] = detected

    if test_metadata is not None and 'runtime' in test_metadata.columns and n_failing > 0:
        merged_with_runtime = merged.merge(test_metadata[['test_id', 'runtime']], on='test_id', how='left')
        merged_with_runtime = merged_with_runtime.sort_values('rank')
        cumsum = merged_with_runtime['runtime'].cumsum()
        first_fail_rank = merged_with_runtime[merged_with_runtime['result'] == 'FAIL']['rank'].min()
        runtime_to_first = cumsum[merged_with_runtime['rank'] == first_fail_rank].values[0]
        metrics['runtime_to_first_failure'] = runtime_to_first
    else:
        metrics['runtime_to_first_failure'] = np.nan

    return metrics

def main():
    parser = argparse.ArgumentParser(description='Evaluate ranking metrics')
    parser.add_argument('--ranking', type=str, help='Path to ranking CSV file (optional, will process all in rankings dir if not given)')
    args = parser.parse_args()

    coverage_path = PROCESSED_DATA_DIR / 'coverage_matrix.csv'
    if not coverage_path.exists():
        print(f"Error: {coverage_path} not found.")
        sys.exit(1)
    coverage_df = pd.read_csv(coverage_path)

    test_metadata = None
    if TEST_METADATA_PATH.exists():
        test_metadata = pd.read_csv(TEST_METADATA_PATH)
        print("Loaded test metadata for runtime.")
    else:
        print("test_metadata.csv not found; runtime metrics will be NA.")

    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    if args.ranking:
        ranking_files = [Path(args.ranking)]
    else:
        ranking_files = list(RANKINGS_DIR.glob('*_ranking.csv'))
        ranking_files = [f for f in ranking_files if 'tie_groups' not in f.name]

    all_metrics = []
    for rank_file in ranking_files:
        print(f"Evaluating {rank_file.name}...")
        ranking_df = pd.read_csv(rank_file)
        ranking_df['rank'] = ranking_df['rank'].astype(int)
        metrics = compute_metrics(ranking_df, coverage_df, test_metadata)
        metrics['method'] = rank_file.stem
        all_metrics.append(metrics)

    metrics_df = pd.DataFrame(all_metrics)
    metrics_df = metrics_df.sort_values('method').reset_index(drop=True)

    summary_path = METRICS_DIR / 'metrics_summary.csv'
    metrics_df.to_csv(summary_path, index=False)
    print(f"Metrics summary saved to {summary_path}")
    print("\nMetrics Summary:")
    print(metrics_df.to_string())

if __name__ == '__main__':
    main()