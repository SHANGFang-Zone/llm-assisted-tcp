#!/usr/bin/env python3
"""
Apply LLM tie-breaking to addtl ranking.
Input: addtl_ranking.csv, addtl_tie_groups.csv, manually saved LLM responses
Output: addtl_llm_tiebreak_ranking.csv
"""
import sys
import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RANKINGS_DIR = PROJECT_ROOT / 'results' / 'rankings'
PROMPTS_GEN_DIR = PROJECT_ROOT / 'prompts' / 'generated'

def main():
    addtl_rank_path = RANKINGS_DIR / 'addtl_ranking.csv'
    tie_groups_path = RANKINGS_DIR / 'addtl_tie_groups.csv'
    if not addtl_rank_path.exists() or not tie_groups_path.exists():
        print("addtl_ranking.csv or addtl_tie_groups.csv not found. Run baseline_addtl.py first.")
        sys.exit(1)

    rank_df = pd.read_csv(addtl_rank_path)
    tie_df = pd.read_csv(tie_groups_path)

    for _, row in tie_df.iterrows():
        step = row['step']
        response_file = PROMPTS_GEN_DIR / f'tie_step_{step:03d}_response.json'
        if not response_file.exists():
            print(f"Warning: response file for step {step} not found. Skipping LLM tie-breaking for this group.")
            continue

        with open(response_file, 'r') as f:
            response_data = json.load(f)
        if isinstance(response_data, list):
            llm_order = response_data
        elif isinstance(response_data, dict) and 'ranking' in response_data:
            llm_order = response_data['ranking']
        else:
            print(f"Warning: unrecognized response format for step {step}. Skipping.")
            continue

        candidates = row['candidate_tests'].split(';')
        if set(llm_order) != set(candidates):
            print(f"Warning: LLM order for step {step} does not match candidate set. Skipping.")
            continue

        indices = rank_df[rank_df['test_id'].isin(candidates)].index.tolist()
        indices.sort()
        if len(indices) != len(llm_order):
            print(f"Warning: length mismatch for step {step}. Skipping.")
            continue
        for idx, test_id in zip(indices, llm_order):
            rank_df.at[idx, 'test_id'] = test_id

        print(f"Applied LLM tie-breaking for step {step}")

    output_path = RANKINGS_DIR / 'addtl_llm_tiebreak_ranking.csv'
    rank_df.to_csv(output_path, index=False)
    print(f"Saved LLM tie-break ranking to {output_path}")

if __name__ == '__main__':
    main()