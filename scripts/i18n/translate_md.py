# Used to produce the ARTEX English UI build.
import subprocess, sys, os

BASE = os.environ.get("ARTEX_I18N_BASE", "/Users/sungminnetworks/prj/ARTEX-web-en")

def run_agy(prompt, timeout=1800, schema=None):
    """Run agy with model fallback: gpt-oss-120b-medium -> gemini-3.8-flash-low."""
    import subprocess
    models = ["gpt-oss-120b-medium", "gemini-3.8-flash-low"]
    last = ""
    for m in models:
        cmd = ["agy", "--model", m, "--dangerously-skip-permissions"]
        if schema:
            cmd += ["--output-format", "json", "--json-schema", schema]
        cmd += ["-p", prompt]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                               cwd=BASE)
        except subprocess.TimeoutExpired:
            last = f"[{m}] timeout"
            print(last, flush=True)
            continue
        out = (r.stdout or "").strip()
        if out:
            return out, m
        last = f"[{m}] empty"
        print(last, flush=True)
    return "", None


src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding='utf-8').read()
prompt = (
    "Translate the following Markdown document from Chinese to English.\n"
    "Rules: preserve ALL markdown structure (headings, tables, lists, code blocks, backticks), "
    "tech terms, paths, commands, URLs exactly as-is. Natural, concise English. "
    "Output ONLY the translated document, no commentary.\n\n---\n\n" + text
)
for attempt in range(3):
    out, used = run_agy(prompt)
    if used and used != "gpt-oss-120b-medium":
        print(f"[fallback] used {used}", flush=True)
    # strip possible NDJSON metadata lines (keep the longest plain-text block)
    if out.startswith("{"):
        # print mode may wrap; find last big text chunk after "response":"
        import json as _j
        best = ""
        for line in out.splitlines():
            line=line.strip()
            if not line.startswith("{"): continue
            try: j=_j.loads(line)
            except Exception: continue
            resp = j.get("response","")
            if len(resp) > len(best): best = resp
        out = best.strip()
    if len(out) > len(text) * 0.25:  # sanity: English usually not drastically shorter
        open(dst, 'w', encoding='utf-8').write(out + "\n")
        print(f"OK {dst} ({len(out)} chars, attempt {attempt+1})")
        sys.exit(0)
    print(f"attempt {attempt+1} too short ({len(out)}), retrying...")
sys.exit(1)
