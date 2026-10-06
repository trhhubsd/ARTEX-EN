# Used to produce the ARTEX English UI build.
import json, subprocess, time, os

BASE = os.environ.get("ARTEX_I18N_BASE", "/Users/sungminnetworks/prj/ARTEX-web-en")
DB = os.path.join(BASE, "db")

def run_agy(prompt, timeout=2400):
    """Run agy with model fallback: gpt-oss-120b-medium -> gemini-3.8-flash-low."""
    models = ["gpt-oss-120b-medium", "gemini-3.8-flash-low"]
    for m in models:
        cmd = ["agy", "--model", m, "--dangerously-skip-permissions", "-p", prompt]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=BASE)
        except subprocess.TimeoutExpired:
            print(f"[{m}] timeout", flush=True)
            continue
        out = (r.stdout or "").strip()
        if out:
            return out, m
        print(f"[{m}] empty", flush=True)
    return "", None

rows = json.load(open(os.path.join(DB, "prompts.json"), encoding='utf-8'))
outp = os.path.join(DB, "prompts_en.json")
done = {}
if os.path.exists(outp):
    done = json.load(open(outp, encoding='utf-8'))
print(f"total={len(rows)} cached={len(done)}", flush=True)

def one(text, key):
    prompt = (
        "Translate this LLM agent system prompt from Chinese to English.\n"
        "Rules: preserve ALL structure exactly - markdown headings, lists, tables, code blocks, "
        "tool names, placeholder variables, JSON examples, numbered steps, blank lines. "
        "Translate only the natural-language Chinese prose. Do NOT add or remove sections. "
        "Output ONLY the translated prompt, no commentary.\n\n---\n\n" + text
    )
    for attempt in range(3):
        out, used = run_agy(prompt, timeout=2400)
        if used == "gemini-3.8-flash-low":
            print(f"  [{key}] fallback model in use", flush=True)
        if out.startswith("{"):
            import json as _j
            best = ""
            for line in out.splitlines():
                line = line.strip()
                if not line.startswith("{"): continue
                try: j = _j.loads(line)
                except Exception: continue
                resp = j.get("response", "")
                if len(resp) > len(best): best = resp
            out = best.strip()
        if len(out) > len(text) * 0.35:
            return out
        print(f"  [{key}] retry {attempt+1} (len {len(out)} vs {len(text)})", flush=True)
        time.sleep(3)
    return None

for key, pid, text in rows:
    if pid in done: continue
    print(f"translating {key} (id {pid}, {len(text)} chars)...", flush=True)
    en = one(text, key)
    if en:
        done[pid] = {"key": key, "en": en}
        json.dump(done, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(f"  -> OK", flush=True)
    else:
        print(f"  -> FAILED", flush=True)
print("ALL DONE", len(done), "/", len(rows), flush=True)
