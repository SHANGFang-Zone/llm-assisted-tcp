#!/usr/bin/env python3
"""
Generate LLM prompts for tie groups.
Input: addtl_tie_groups.csv, coverage_matrix.csv, spectra_metadata.csv, test_metadata.csv
Output: prompts/generated/tie_step_XXX.txt
"""
import sys
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RANKINGS_DIR = PROJECT_ROOT / 'results' / 'rankings'
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'
PROMPTS_GEN_DIR = PROJECT_ROOT / 'prompts' / 'generated'

def main():
    tie_groups_path = RANKINGS_DIR / 'addtl_tie_groups.csv'
    if not tie_groups_path.exists():
        print("No tie groups found. Run baseline_addtl.py first.")
        sys.exit(1)

    tie_df = pd.read_csv(tie_groups_path)
    coverage_df = pd.read_csv(PROCESSED_DATA_DIR / 'coverage_matrix.csv')
    spectra_df = pd.read_csv(PROCESSED_DATA_DIR / 'spectra_metadata.csv')
    test_metadata_df = pd.read_csv(PROCESSED_DATA_DIR / 'test_metadata.csv') if (PROCESSED_DATA_DIR / 'test_metadata.csv').exists() else None

    PROMPTS_GEN_DIR.mkdir(parents=True, exist_ok=True)

    for _, row in tie_df.iterrows():
        step = row['step']
        candidate_tests = row['candidate_tests'].split(';')
        add_coverage = row['additional_coverage']

        prompt_lines = [
            "You are assisting with test case prioritization for early failure detection.",
            "Goal: Rank the candidate tests so that tests more likely to reveal failures are executed earlier.",
            f"Failure context: [Insert failure stacktrace or error message if available]",
            "Candidate tests:"
        ]
        for idx, test_id in enumerate(candidate_tests, 1):
            coverage_row = coverage_df[coverage_df['test_id'] == test_id].iloc[0]
            fragment_cols = [c for c in coverage_df.columns if c.startswith('fragment_')]
            covered_fragments = [frag for frag in fragment_cols if coverage_row[frag] == 1]
            total_covered = len(covered_fragments)
            test_name = "Unknown"
            if test_metadata_df is not None and 'test_name' in test_metadata_df.columns:
                meta_row = test_metadata_df[test_metadata_df['test_id'] == test_id]
                if not meta_row.empty:
                    test_name = meta_row.iloc[0]['test_name']
            prompt_lines.append(f"{idx}. {test_id}")
            prompt_lines.append(f"Test name: {test_name}")
            prompt_lines.append(f"Total covered fragments: {total_covered}")
            if test_metadata_df is not None and 'runtime' in test_metadata_df.columns:
                runtime = test_metadata_df[test_metadata_df['test_id'] == test_id]['runtime'].values[0] if not test_metadata_df[test_metadata_df['test_id'] == test_id].empty else "N/A"
                prompt_lines.append(f"Runtime: {runtime}")
            prompt_lines.append("")  # blank line

        prompt_lines.append("Please rank these candidate tests from most likely to least likely to reveal the failure.")
        prompt_lines.append("Return only a JSON list of test IDs, for example: [\"T0041\", \"T0033\", \"T0052\"]")

        prompt_text = "\n".join(prompt_lines)
        prompt_file = PROMPTS_GEN_DIR / f'tie_step_{step:03d}.txt'
        with open(prompt_file, 'w') as f:
            f.write(prompt_text)
        print(f"Generated prompt for step {step} at {prompt_file}")

if __name__ == '__main__':
    main()