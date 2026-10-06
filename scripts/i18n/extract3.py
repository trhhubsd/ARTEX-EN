# Used to produce the ARTEX English UI build.
import os, re, json, hashlib

BASE = os.environ.get("ARTEX_I18N_BASE", "/Users/sungminnetworks/prj/ARTEX-web-en")
SRC = os.environ.get("ARTEX_SRC", "/Users/sungminnetworks/prj/ARTEX/web/src")
OUT = os.path.join(BASE, "strings3.jsonl")
cjk = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
run = re.compile(
    r'[\u4e00-\u9fff\u3400-\u4dbf](?:[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff01-\uff5e\u2010-\u2027\u3000\u3001\u3002'
    r' \t a-zA-Z0-9_.:/\-+()%\[\]<>=,;\'&*#~^])*[\u4e00-\u9fff\u3400-\u4dbf]'
    r'|[\u4e00-\u9fff\u3400-\u4dbf]'
)

items = {}
for root, dirs, fns in os.walk(SRC):
    if 'node_modules' in root: continue
    for fn in fns:
        if not fn.endswith(('.ts', '.tsx')): continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, SRC)
        if rel.startswith('mock/'): continue
        try: text = open(p, encoding='utf-8').read()
        except Exception: continue
        for i, ln in enumerate(text.splitlines(), 1):
            if not cjk.search(ln): continue
            nocom = re.sub(r'(^|[^:])//.*$', r'\1', ln)
            nocom = re.sub(r'/\*.*?\*/', '', nocom)
            if not cjk.search(nocom): continue
            for m in run.finditer(ln):
                s = m.group(0).strip()
                while s and not cjk.search(s[-1]): s = s[:-1]
                if not s: continue
                h = hashlib.sha1(s.encode()).hexdigest()[:12]
                if h not in items:
                    items[h] = {"id": h, "zh": s, "files": []}
                loc = f"{rel}:{i}"
                if loc not in items[h]["files"] and len(items[h]["files"]) < 6:
                    items[h]["files"].append(loc)

with open(OUT, "w", encoding="utf-8") as f:
    for it in items.values():
        f.write(json.dumps(it, ensure_ascii=False) + "\n")
print("strict runs:", len(items))
