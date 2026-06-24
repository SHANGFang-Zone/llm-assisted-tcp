#!/usr/bin/env python3
"""
Parse matrix.txt coverage file.
Input: data/raw/matrix.txt
Output: data/processed/coverage_matrix.csv
"""
import os
import sys
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'

def parse_matrix(matrix_path: Path) -> pd.DataFrame:
    """
    Reads matrix.txt where each line: coverage values (0/1) followed by result (+ or -).
    Returns DataFrame with columns: test_id, result, fragment_0, fragment_1, ...
    """
    if not matrix_path.exists():
        raise FileNotFoundError(f"matrix.txt not found at {matrix_path}")

    tests = []
    with open(matrix_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            coverage = parts[:-1]
            result = parts[-1]
            if result == '+':
                result_label = 'PASS'
            elif result == '-':
                result_label = 'FAIL'
            else:
                raise ValueError(f"Unknown result symbol: {result}")
            tests.append(coverage + [result_label])

    test_ids = [f'T{i+1:04d}' for i in range(len(tests))]
    num_fragments = len(tests[0]) - 1
    fragment_cols = [f'fragment_{i}' for i in range(num_fragments)]
    df = pd.DataFrame(tests, columns=fragment_cols + ['result'])
    df.insert(0, 'test_id', test_ids)
    return df

def main():
    matrix_path = RAW_DATA_DIR / 'matrix.txt'
    output_path = PROCESSED_DATA_DIR / 'coverage_matrix.csv'
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Parsing {matrix_path}...")
    df = parse_matrix(matrix_path)

    total_tests = len(df)
    passing = (df['result'] == 'PASS').sum()
    failing = (df['result'] == 'FAIL').sum()
    num_fragments = len(df.columns) - 2
    print(f"Total tests: {total_tests}")
    print(f"Passing tests: {passing}")
    print(f"Failing tests: {failing}")
    print(f"Number of code fragments: {num_fragments}")

    df.to_csv(output_path, index=False)
    print(f"Saved processed coverage matrix to {output_path}")

if __name__ == '__main__':
    main()