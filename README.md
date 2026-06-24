# LLM-Assisted Test Case Prioritization for Early Failure Detection

## Motivation
This project explores whether Large Language Models can assist traditional test case prioritization techniques in detecting failing tests earlier.

## Background
The project extends prior work on test case prioritization and spectrum-based fault localization using Defects4J/GZoltar coverage data.

## Data
The prototype uses existing coverage matrix and test execution outputs:
- matrix.txt
- tests.csv
- spectra.csv
- ochiai.ranking.csv (optional)
- statistics.csv (optional)

## Methods
- Random ranking
- Total coverage ranking
- Additional coverage ranking
- LLM-guided tie-breaking for addtl

## Metrics
- First failing test rank
- Normalized first failing test rank
- APFD
- Top-k failure detection
- Runtime to first failure

## Current Status
This is an ongoing research prototype.

## Future Work
- Add LLM static ranking
- Add suspicious-code-aware ranking using Ochiai output
- Add dynamic re-ranking
- Extend to more Defects4J bugs
- Connect early failure detection with spectrum-based fault localization
