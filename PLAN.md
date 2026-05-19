# Plan

## Goal
Build a 3-part reading assistant pipeline:
1. OCR + page indexing
2. Investigator / retrieval answering
3. Hierarchical summarization for whole-document understanding

## Current direction
- Keep OCR + indexing local
- Use embeddings for retrieval
- Use an LLM only for summarization and synthesis
- Ground every answer in OCR/page content

## Summarization strategy
### Windowing
- Default window: 10 pages
- Make window size configurable via argument
- Build summaries from consecutive page windows

### Per-window summary
- Max 1000 words per window summary
- Grounded only in OCR text
- No guessing / no hallucinated details

### Merge step
- Merge all window summaries into a document-level summary
- Use merged summary to derive:
  - 5 W’s
  - character relations
  - mental model
  - objective interpretation
  - concise story flow

### Output structure
- General flow: <= 500 words
- Relations section carries the juicy details
- Separate sections for:
  - who / what / when / why / how
  - story flow
  - relations
  - environments / objects / symbolism
  - mental model
  - interpretation

## Investigator strategy
- User asks a specific question
- Subagent can rewrite/refine the query
- Investigator retrieves top-k chunks from embeddings
- Optional reranking can improve results
- Final answer stays page-grounded

## LLM choice
- Prefer a small/open-source summarizer model
- Qwen2.5 7B Instruct is the current candidate
- Use low temperature
- Keep prompt strict and structured

## Implementation order
1. Add summarization pipeline helpers
2. Add CLI arguments for window size and summary limits
3. Wire in summary LLM config
4. Save window summaries and merged summary artifacts
5. Update README examples and usage notes

## Later checklist
- Build investigator tool
- Build summarizer tool
- Add citations to summaries
- Add verification pass for unsupported claims
