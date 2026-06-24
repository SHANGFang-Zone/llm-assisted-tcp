#!/usr/bin/env python3
"""
Run the full pipeline: parse, generate rankings, evaluate.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'

def run_script(script_name):
    script_path = SCRIPTS_DIR / script_name
    print(f"\nRunning {script_path}...")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
    if result.returncode != 0:
        print(f"Error running {script_name}")
        sys.exit(result.returncode)

def main():
    run_script('parse_matrix.py')
    run_script('parse_tests.py')
    run_script('parse_spectra.py')
    run_script('baseline_random.py')
    run_script('baseline_total.py')
    run_script('baseline_addtl.py')
    run_script('build_llm_prompt.py')
    run_script('apply_llm_ranking.py')
    run_script('evaluate_metrics.py')
    print("\nExperiment complete. Check results/ directory.")

if __name__ == '__main__':
    main()