# Used to produce the ARTEX English UI build.
import json, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor

BASE = os.environ.get("ARTEX_I18N_BASE", "/Users/sungminnetworks/prj/ARTEX-web-en")
ROOT = BASE
STRINGS = os.path.join(ROOT, "retry2.jsonl")
OUT = os.path.join(ROOT, "translations2.json")
CHUNK = 12
PARALLEL = 3
SCHEMA = json.dumps({
    "type": "object",
    "properties": {"t": {"type": "array", "items": {"type": "string"}}},
    "required": ["t"],
})

def run_agy_json(prompt, schema, timeout=1800):
    """Run agy with model fallback; returns raw stdout (may embed NDJSON)."""
    import subprocess
    for m in ["gpt-oss-120b-medium", "gemini-3.8-flash-low"]:
        cmd = ["agy", "--model", m, "--dangerously-skip-permissions",
               "--output-format", "json", "--json-schema", schema, "-p", prompt]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                               cwd=BASE)
        except subprocess.TimeoutExpired:
            print(f"[{m}] timeout", flush=True)
            continue
        out = (r.stdout or "").strip()
        if out and '"structured_output"' in out:
            return out, m
        print(f"[{m}] bad/empty output", flush=True)
    return "", None


strings = [json.loads(l) for l in open(STRINGS, encoding="utf-8")]
trans = {}
if os.path.exists(OUT):
    trans = json.load(open(OUT, encoding="utf-8"))
todo = [s for s in strings if s["id"] not in trans]
print(f"todo={len(todo)}", flush=True)

def parse_structured(out):
    for line in out.splitlines()[::-1]:
        line = line.strip()
        if not line.startswith("{"): continue
        try: j = json.loads(line)
        except Exception: continue
        if isinstance(j, dict) and j.get("structured_output"):
            return j["structured_output"]
    return None

def translate_batch(batch, idx):
    lines = "\n".join(f'{s["id"]}\t{s["zh"]}' for s in batch)
    prompt = (
        "You are localizing a pentest web UI from Chinese to English. "
        "For each input line (ID<TAB>Chinese), translate the whole run into concise natural English "
        "for a UI label/sentence. Keep tech terms, product names, paths, placeholders as-is. "
        f'Return JSON object {{"t":[...]}} where the array has EXACTLY {len(batch)} strings, '
        "in the same order as the input IDs.\n\nInput:\n" + lines
    )
    cmd = ["agy", "--model", "gpt-oss-120b-medium", "--dangerously-skip-permissions",
           "--output-format", "json", "--json-schema", SCHEMA, "-p", prompt]
    for attempt in range(5):
        try:
            out_raw, used_m = run_agy_json(prompt, SCHEMA, timeout=900)
            parsed = parse_structured(out_raw)
            if parsed and isinstance(parsed.get("t"), list) and len(parsed["t"]) == len(batch):
                return {s["id"]: (t or "").strip() for s, t in zip(batch, parsed["t"])}
        except subprocess.TimeoutExpired:
            pass
        time.sleep(2)
    return None

batches = [todo[i:i+CHUNK] for i in range(0, len(todo), CHUNK)]
print(f"batches: {len(batches)} x {CHUNK}", flush=True)

def run_one(idx):
    res = translate_batch(batches[idx], idx)
    if res:
        trans.update(res)
        json.dump(trans, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"[t{idx}] ok {len(trans)}", flush=True)
    else:
        print(f"[t{idx}] FAILED", flush=True)
    return idx

with ThreadPoolExecutor(max_workers=PARALLEL) as ex:
    list(ex.map(run_one, range(len(batches))))

json.dump(trans, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
missing = [s["id"] for s in strings if s["id"] not in trans]
print(f"ALL DONE missing={len(missing)}", flush=True)
