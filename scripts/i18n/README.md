# i18n Translation Pipeline

1. **Extract**: Run `extract3.py` to extract atomic CJK runs from `web/src`.
2. **Translate**: Run `retry2.py` to batch-translate strings via `agy gpt-oss-120b-medium` with `gemini-3.8-flash-low` fallback.
3. **Apply**: Run `apply3.py` for atomic, longest-first replacement of localized strings back into source files.
4. **Verify**: Verify changes with Biome formatting/linting, TypeScript compiler checks (`tsc`), and `next build`.
5. **Dictionary**: The single source runtime dictionary lives in `scripts/i18n/locale-zh.json` (and `orch/locale-zh.json`).
