#!/usr/bin/env python3
"""
Parse spectra.csv metadata file.
Input: data/raw/spectra.csv
Output: data/processed/spectra_metadata.csv
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
    try:
        return pd.read_csv(filepath)
    except pd.errors.ParserError as e:
        print(f"Default pandas read failed: {e}")
        print("Attempting manual CSV parsing with field merging...")

    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        num_header_fields = len(header)
        rows = []
        for line_num, row in enumerate(reader, start=2):
            if len(row) == num_header_fields:
                rows.append(row)
            elif len(row) > num_header_fields:
                merged_row = row[:num_header_fields-1] + [','.join(row[num_header_fields-1:])]
                rows.append(merged_row)
                print(f"Line {line_num}: merged {len(row) - num_header_fields} extra fields into the last column.")
            else:
                padded = row + [''] * (num_header_fields - len(row))
                rows.append(padded)
                print(f"Line {line_num}: padded missing fields.")

    df = pd.DataFrame(rows, columns=header)
    return df

def parse_spectra(spectra_path: Path) -> pd.DataFrame:
    if not spectra_path.exists():
        raise FileNotFoundError(f"spectra.csv not found at {spectra_path}")

    df = read_csv_robust(spectra_path)
    print("Available columns in spectra.csv:", df.columns.tolist())

    if 'fragment_id' not in df.columns:
        df.insert(0, 'fragment_id', [f'fragment_{i}' for i in range(len(df))])

    if 'code_element' not in df.columns:
        possible = [c for c in df.columns if any(k in c.lower() for k in ['class', 'method', 'name', 'element'])]
        if possible:
            df = df.rename(columns={possible[0]: 'code_element'})
        else:
            df['code_element'] = df.iloc[:, 1:].astype(str).agg(' '.join, axis=1)

    return df[['fragment_id', 'code_element']]

def main():
    spectra_path = RAW_DATA_DIR / 'spectra.csv'
    output_path = PROCESSED_DATA_DIR / 'spectra_metadata.csv'
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Parsing {spectra_path}...")
    df = parse_spectra(spectra_path)
    df.to_csv(output_path, index=False)
    print(f"Saved spectra metadata to {output_path}")

if __name__ == '__main__':
    main()