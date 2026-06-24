#!/usr/bin/env python3
"""
Parse tests.csv metadata file.
Input: data/raw/tests.csv
Output: data/processed/test_metadata.csv
"""
import pandas as pd
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'

def read_csv_robust(filepath: Path) -> pd.DataFrame:
    """
    Attempt to read CSV using pandas; if fails due to inconsistent field counts,
    fall back to a manual csv.reader that merges extra fields into the last column.
    """
    # First attempt: default pandas
    try:
        return pd.read_csv(filepath)
    except pd.errors.ParserError as e:
        print(f"Default pandas read failed: {e}")
        print("Attempting manual CSV parsing with field merging...")

    # Manual parsing with csv module
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        num_header_fields = len(header)
        rows = []
        for line_num, row in enumerate(reader, start=2):  # start at line 2 (after header)
            if len(row) == num_header_fields:
                rows.append(row)
            elif len(row) > num_header_fields:
                # Merge extra fields into the last field
                merged_row = row[:num_header_fields-1] + [','.join(row[num_header_fields-1:])]
                rows.append(merged_row)
                print(f"Line {line_num}: merged {len(row) - num_header_fields} extra fields into the last column.")
            else:
                # Too few fields: pad with empty strings
                padded = row + [''] * (num_header_fields - len(row))
                rows.append(padded)
                print(f"Line {line_num}: padded missing fields.")

    df = pd.DataFrame(rows, columns=header)
    return df

def parse_tests(tests_path: Path) -> pd.DataFrame:
    if not tests_path.exists():
        raise FileNotFoundError(f"tests.csv not found at {tests_path}")

    df = read_csv_robust(tests_path)
    print("Available columns in tests.csv:", df.columns.tolist())

    # Map common column names
    col_mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'test' in col_lower and ('id' in col_lower or 'index' in col_lower):
            col_mapping[col] = 'test_id'
        elif 'name' in col_lower or 'method' in col_lower:
            col_mapping[col] = 'test_name'
        elif 'result' in col_lower:
            col_mapping[col] = 'result'
        elif 'time' in col_lower or 'runtime' in col_lower or 'duration' in col_lower:
            col_mapping[col] = 'runtime'
        elif 'stack' in col_lower or 'trace' in col_lower:
            col_mapping[col] = 'stacktrace'

    if col_mapping:
        df = df.rename(columns=col_mapping)
    else:
        print("Warning: No known columns detected. Please check your tests.csv format.")

    if 'test_id' not in df.columns:
        df.insert(0, 'test_id', [f'T{i+1:04d}' for i in range(len(df))])
    else:
        df['test_id'] = df['test_id'].astype(str)

    if 'result' in df.columns:
        df['result'] = df['result'].apply(lambda x: 'PASS' if str(x).strip().upper() in ['+', 'PASS', 'P'] else 'FAIL')
    else:
        print("Warning: 'result' column not found. Cannot align with coverage matrix.")

    return df

def main():
    tests_path = RAW_DATA_DIR / 'tests.csv'
    output_path = PROCESSED_DATA_DIR / 'test_metadata.csv'
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Parsing {tests_path}...")
    df = parse_tests(tests_path)
    df.to_csv(output_path, index=False)
    print(f"Saved test metadata to {output_path}")

if __name__ == '__main__':
    main()