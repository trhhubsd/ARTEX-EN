# Used to produce the ARTEX English UI build.
import json, os, re

BASE = os.environ.get("ARTEX_I18N_BASE", "/Users/sungminnetworks/prj/ARTEX-web-en")
ROOT = os.environ.get("ARTEX_SRC", "/Users/sungminnetworks/prj/ARTEX/web/src")
MERGED = os.path.join(BASE, "merged.json")
MISSING = os.path.join(BASE, "missing3b.jsonl")

merged = json.load(open(MERGED, encoding="utf-8"))
for l in open(MISSING, encoding="utf-8"):
    s = json.loads(l)
    en = s.get("en", "").strip()
    if en:
        en = en.replace('"', '\u201c' if False else '"')  # sanitize straight quotes alternately below
        out=[]; open_q=True
        for ch in en:
            if ch=='"':
                out.append('\u201c' if open_q else '\u201d'); open_q = not open_q
            else: out.append(ch)
        en = ''.join(out).replace('`',"'").replace('${','$').replace("：",": ").strip()
        if en: merged[s["zh"]] = en

pairs = sorted(merged.items(), key=lambda x: len(x[0]), reverse=True)
print(f"pairs: {len(pairs)}")
cjk = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
changed_files = changed_lines = 0
remaining = []
for root, dirs, fns in os.walk(ROOT):
    if 'node_modules' in root: continue
    for fn in fns:
        if not fn.endswith(('.ts', '.tsx')): continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, ROOT)
        if rel.startswith('mock/'): continue
        try: text = open(p, encoding='utf-8').read()
        except Exception: continue
        if not cjk.search(text): continue
        orig = text
        out_lines = []
        for ln in text.splitlines(keepends=True):
            body = ln.rstrip('\n'); eol = ln[len(body):]
            nocom = re.sub(r'(^|[^:])//.*$', r'\1', body)
            nocom = re.sub(r'/\*.*?\*/', '', nocom)
            if not cjk.search(nocom):
                out_lines.append(ln); continue
            nb = body
            for zh, en in pairs:
                if zh in nb: nb = nb.replace(zh, en)
            if nb != body: changed_lines += 1
            out_lines.append(nb + eol)
        new = ''.join(out_lines)
        if new != orig:
            open(p, 'w', encoding='utf-8').write(new)
            changed_files += 1
        for i, ln in enumerate(new.splitlines(), 1):
            nc = re.sub(r'(^|[^:])//.*$', r'\1', ln)
            nc = re.sub(r'/\*.*?\*/', '', nc)
            if cjk.search(nc):
                remaining.append(f"{rel}:{i}: {ln.strip()[:110]}")
print(f"files changed: {changed_files}, lines changed: {changed_lines}")
print(f"remaining: {len(remaining)}")
for s in remaining[:10]: print(" ", s)
