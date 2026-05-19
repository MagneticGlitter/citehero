# Iliad Book 1 Investigator v4 — strict contract / retry / validation / fallback

## Experiment summary
- Edited `src/app/investigator.py` to add:
  - stricter answer contract
  - malformed-answer retry
  - entity/role validation before accepting Qwen output
  - evidence-based fallback synthesis
  - stronger sufficiency checks
- Reran all 18 Iliad prompts from the v3 set.

## Result
- `fallback_count: 18/18`
- `direct_count: 0/18`
- In this run, vector retrieval fell back to lexical mode and Qwen was not available, so every answer used the synthesized fallback path.

## Note
- The fallback answers are more question-aware than v3 (e.g. Q1 now pulls the Chryses/ransom passage instead of a generic opening line), but the environment did not exercise the LLM acceptance path.
