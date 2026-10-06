# i18n Pipeline

Model chain: `gpt-oss-120b-medium` (primary) -> `gemini-3.8-flash-low` (fallback).
Every translator tool auto-falls-back per call when the primary errors/empties/times out.

- `extract3.py`  — extract atomic CJK runs from web/src -> strings3.jsonl
- `retry2.py`    — batch-translate strings (JSON-schema, resumable) -> translations2.json
- `apply3.py`    — apply longest-first whole-run replacement to web/src
- `translate_md.py`       — single markdown file translator (skills etc.)
- `translate_prompts2.py` — DB agent prompt templates -> prompts_en.json
