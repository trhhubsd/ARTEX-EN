---
name: api-recon
description: Invoke this skill when collecting website API endpoints.
---

# API Recon (Frontend Interface Reconnaissance)

Under **authorized** conditions, discover as completely as possible: **backend APIs** (paths, methods, parameters, response bodies), **frontend routes**, **UI functional trigger points** (tabs, dialogs, table actions, etc.).

---

## Scope and Prohibitions (Agent Must‑Read · Violations = Out‑of‑Bounds)

This skill **only performs API/parameter surface reconnaissance**, not vulnerability discovery or exploitation.

### Task Scope

| Scope | Allowed | Prohibited |
|---|---|---|
| **Target** | Enumerate paths, methods, parameters, routes, UI trigger points | SQLi/XSS/privilege escalation/brute‑force/fuzz vulnerabilities, request tampering, destructive actions |
| **Auth** | Hook + stub/mock to bypass **client‑side** login | Ask users for or guess credentials; attempt real login form submissions |
| **Runtime** | Hook APIs without credentials, using mock responses to let the SPA reach the post‑login shell | Rely on real backend sessions to continue the flow |

### Credential‑Free Dynamic---
name: api-recon
description: Invoke this skill when collecting website API endpoints.
---

# API Recon (Frontend Interface Reconnaissance)

Under **authorized** conditions, discover as completely as possible: **backend APIs** (paths, methods, parameters, response bodies), **frontend routes**, **UI functional trigger points** (tabs, dialogs, table actions, etc.).

---

## Scope and Prohibitions (Agent Must‑Read · Violations = Out‑of‑Bounds)

This skill **only performs API/parameter surface reconnaissance**, not vulnerability discovery or exploitation.

### Task Scope

| Scope | Allowed | Prohibited |
|---|---|---|
| **Target** | Enumerate paths, methods, parameters, routes, UI trigger points | SQLi/XSS/privilege escalation/brute‑force/fuzz vulnerabilities, request tampering, destructive actions |
| **Auth** | Hook + stub/mock to bypass **client‑side** login | Ask users for or guess credentials; attempt real login form submissions |
| **Runtime** | Hook APIs without credentials, using mock responses to let the SPA reach the post‑login shell | Rely on real backend sessions to continue the flow |

### Credential‑Free Dynamic Analysis (Phase 3 default)

1. Intercept and stub login, auth, menu, and other bootstrap endpoints via `preload.js` / `runtime_harvest.js`;
2. Provide mock bodies for business query endpoints with **correct structure, success codes, and possibly empty data**;
3. Allow the frontend to render post‑login pages even when the backend is unreachable or returns 401, thereby triggering more XHR/fetch/WebSocket calls;
4. **Empty data, blank tables, placeholder UI are expected**—do **not** switch to real login or vulnerability testing because of them.

**In a sentence**: Use mocks to keep frontend routes and component mounting alive, **record only outbound requests**; the backend’s actual responses are irrelevant, what matters is which additional requests the frontend issues.

### Hard Prohibitions in the Flow

| Prohibited | Alternative Approach |
|---|---|
| Grep/curl/read the main entry `index-*.js` to extract API paths before Phase 1 completes | Run `OUTDIR/harvest_static.py` |
| Write custom `extract_apis.py` scripts to replace harvest | Modify `OUTDIR/harvest_static.py` and rerun |
| Re‑run the same grep/command ≥2 times after failure | Switch strategy: read `tool_logs`, adjust harvest, consult reference |
| Skip gate A/B and run the original `scripts/` directly | Copy to OUTDIR and adapt per target |
| Use real usernames/passwords, OTP, OAuth, etc. for auth | Stub/mock (see above) |
| Claim “real data” as justification to skip stubs and perform privilege escalation/injection testing | Record only outbound traffic; this stays within recon scope |
| Perform irreversible actions such as deleting, exporting sensitive data, bulk writes | Treat coverage clicks similarly |
| Claim to have collected all pages and APIs without completing runtime + dynamic enumeration | Refer to the “Completion Definition” or note limitations |
| Claim to have mastered all parameters without completing the parameter‑trigger matrix + diff | Complete Phase 3b matrix and Phase 5 diff |
| Infer required/optional parameters from a single runtime sample | Use multiple samples diff or validation rules/error back‑propagation |

---

## Two‑Layer Model + Execution Modes

| Layer | Output | Upper Limit |
|---|---|---|
| **Static** (JS bundle) | Full list of endpoint paths, draft routes, candidate fields for packaging points | No HTTP methods; parameters require Phase 1b; runtime‑constructed URLs may be missed |
| **Runtime** (live session) | Method + body + response + dynamic URL + WS/SSE; multi‑sample diff fills missing parameters | Requests are only made after pages render; a single sample is insufficient to determine required vs optional |

| Execution Mode | Engine | Applicable |
|---|---|---|
| **depth** | `runtime_harvest.js` (Puppeteer) | API list, METHOD/params/response, WS/SSE, reproducible batch runs |
| **coverage** | browser + `preload.js` | Click tabs/dialogs/tables for deeper functional coverage |
| **both** | depth then coverage | Most complete, longest runtime |

**Parameter Methodology** (no universal script): use harvest/regex for paths; for parameters use **anchor expansion + UI binding chain + multi‑sample diff + error back‑propagation** (grep recipe in [reference.md](reference.md) Section J).

---

## Completion Definition

All items must be satisfied before claiming recon is finished:

- [ ] **Static**: Phase 1 harvest produces `api_static.txt`, `routes.txt`, `js/`;
- [ ] **Runtime**: At least one of depth or coverage executed; coverage/both must have **effective hooks + dynamic enumeration loop**;
- [ ] **Shell Entry**: Business paths are reachable without `/login` (watch out for hash routing);
- [ ] **Parameters**: coverage/both completes the parameter‑trigger matrix + `param_samples.json`; Phase 5 merges into `params_merged.json`;
- [ ] **Depth** (if module pages are blank): Phase 4 restores the permission tree and reruns until **module‑level APIs** appear (not just locale/bootstrap);
- [ ] **Delivery**: Phase 5 outputs are complete (see Phase 5 Output Table); `insert_assets` writes all discovered services and endpoint assets—no asset may be omitted.

---

## Scripts and Gates

`scripts/` are reference templates only; **do not** run the original versions as final results.

**Rule**: Read → adapt per target → write to `OUTDIR` (e.g., `recon/`) → record changes in `CHANGES.md`; if mismatches remain, rewrite according to the methodology, using only the structure.

| Gate | When | Reference Script → OUTDIR Copy | Common Changes Needed |
|---|---|---|---|
| **A (Static)** | After Phase 0, **before the first** harvest/spider run | `harvest_static.py` / `spider_mpa.py` | Most sites work with default regex; only adjust endpoint regex, webpack/Vite `publicPath`, MPA excludes/cookies when manifest or dialect mismatches |
| **B (Runtime)** | After Phase 2, before depth/coverage runs | `runtime_harvest.js` / `preload.js` + `config.json` | Cookie/localStorage keys, success‑value neutralization, stubs, login regex, API prefixes, hash/history handling |

**SPA Mandatory Sequence** (non‑swap; Phase numbers take precedence over “explore then script”):

| Step | Must | Must Not |
|---|---|---|
| After Phase 0 | Next Bash command: `python3 OUTDIR/harvest_static.py <URL> OUTDIR` | curl/grep/read the main entry `index-*.js` (usually > 500 KB) |
| Gate A | Copy script → make minor tweaks → **run immediately** | Extract APIs manually first, then decide whether to harvest |
| Before Phase 1 completes | Verify output with `wc -l`; if 404, adjust harvest and retry | Hand‑write extract scripts; repeatedly grep URLs that weren’t downloaded |
| From Phase 1b onward | Grep only `OUTDIR/js/*.js` | Use the main bundle instead of harvest |

- ✅ Copy `harvest_static.py` → (optionally) tweak regex → **run immediately**  
- ❌ curl the main bundle → grep repeatedly → write temporary extract → harvest at the end  
- **MPA**: After Phase 0 the next Bash command is `python3 OUTDIR/spider_mpa.py ...`

---

## Tools and Output Constraints

| Constraint | Description |
|---|---|
| Large files | `index-*.js` > 100 KB **must not** be read/grepped in context; use OUTDIR scripts for batch processing |
| Grep output | Must include `\| head -20` or `-m 5`; only keep path summaries in conversation, never paste bundle fragments |
| Validation | Use `wc -l`, `ls \| wc -l`; do **not** read entire directories |
| Regex probing | Optional, ≤ 1 time, only on ≤ 50 KB chunks or HTML; static results rely on harvest |
| Reference | Recipes/templates/troubleshooting are in [reference.md](reference.md); do not repeat the full text inline |

---

## Execution Roadmap

```
Phase 0 Classification + OUTDIR
  → Gate A → Phase 1 harvest (★ run immediately ★)
  → Phase 1b parameter reverse‑engineering
  → Phase 2 three‑gate auth → config.json
  → Gate B → Phase 3 runtime + parameter matrix
  → Phase 4 permission tree (if needed) → rerun Phase 3
  → Phase 5 merge report + insert_assets batch‑insert all discovered services and endpoint assets; no asset may be omitted during insertion
```

Proceed sequentially; **do not advance to the next Phase without completing the prior one**.

1. [ ] **Phase 0**: Initial SPA/MPA scouting; create `OUTDIR` → [Phase 0](#phase-0--classification)  
2. [ ] **Gate A + Phase 1**: Copy scripts → **run** harvest → `wc -l` verification → [Phase 1](#phase-1--static)  
3. [ ] **Phase 1b**: Anchor expansion + binding layer → `param_candidates.json` → [Phase 1b](#phase-1b--parameter-reverse)  
4. [ ] **Phase 2**: Three‑gate auth → `config.json` → [Phase 2](#phase-2--three‑gate-auth)  
5. [ ] **Gate B**: Adjust runtime scripts → [Phase 3](#phase-3--runtime)  
6. [ ] **Phase 3**: depth / coverage / both; confirm shell entry; parameter‑trigger matrix → `param_samples.json`  
7. [ ] **Phase 4** (if needed): Permission tree → patch stubs → rerun Phase 3 → [Phase 4](#phase-4--permission-tree)  
8. [ ] **Phase 5**: Merge outputs + report + `insert_assets` → [Phase 5](#phase-5--merge-and-report)

---

## Phase 0 — Classification

Fetch the entry HTML and **create `OUTDIR`** (do **not** modify the `scripts/` inside the skill):

- **SPA**: empty shell + `<div id=app>` + chunk → Phases 1–5  
- **MPA**: SSR + `<form>`, no endpoint bundle → after Gate A:

```bash
python3 recon/spider_mpa.py <BASE_URL> <OUTDIR> [--cookie "session=..."] [--max 300] [--depth 5] [--exclude "logout|delete|destroy"]
```

Produces `forms.txt`, `links.txt`, `api_inline.txt`. If SPA `forms ≈ 0`, switch to Phase 1.

---

## Phase 1 — Static

Follow the **Scripts & Gates** and **Tools & Output Constraints** sections.

```bash
python3 recon/harvest_static.py <BASE_URL> <OUTDIR>
```

`harvest` parses HTML `<script>` tags → webpack/Vite manifest → downloads all lazy chunks → outputs `js/`, `api_static.txt`, `routes.txt`, `chunkmap.txt`.

```bash
wc -l OUTDIR/api_static.txt OUTDIR/routes.txt
ls OUTDIR/js | wc -l
```

- Chunk count vs manifest: 404 errors require harvest retry; **do not** curl each chunk manually.  
- Too few entries in `api_static.txt` → loosen endpoint regex in OUTDIR and rerun (see reference).

### Phase 1b — Parameter Reverse‑Engineering

Paths come from Phase 1; parameter fields must be recon‑ed separately. Grep rules are in **Tools & Output Constraints**.

**Completion criteria**: Key endpoints must yield – field names, transmission location, inferred type, required flag, sample values, confidence level.

#### 1b.0 — Transmission Forms

| Form | Where Parameters Appear | Static‑Side Clues |
|---|---|---|
| REST JSON | body + query | Look for `(params|data|body)\s*:\s*\{` next to the path |
| GraphQL | `variables` | gql templates, `$page: Int` |
| Traditional form | url‑encoded | `<form>`, `FormData` |
| File upload | multipart | `FormData.append` |
| Path param | `/user/:id` | Route table + `useParams` / `$route.params` |
| Encrypted/signature | wrapped in `sign`/`data` | Hook‑level encryption function arguments (see reference Section D) |

Output: annotate each endpoint with `transport: query|json|form|graphql|encrypted`.

#### 1b.1 — Anchor Expansion

Using known paths as anchors, expand the window to find packaging objects:

```bash
grep -n '"/api/user/list"' OUTDIR/js/*.js | head -20
grep -rhoaE '.{0,120}("/api[^"]+").{0,200}' OUTDIR/js/*.js | head -20
grep -rhoaE '(params|data|body|payload)\s*:\s*\{' OUTDIR/js/*.js | head -20
```

| Packaging Layer | Parameter Clues |
|---|---|
| axios instance | `data` / `params` |
| Unified request | interceptor‑injected global fields |
| OpenAPI client | generated method signatures |
| React Query / SWR | second argument of hook |
| Vue composable | composable arguments |

Residual types: `yup`/`zod`/rules, `Form.Item name=`, embedded Swagger.

→ `param_candidates.json`: `{ path, fields[], source: "static-callsite", confidence }`

#### 1b.2 — Binding Layer

```
Form field → onFinish/handleSubmit → transform → API payload
```

| Binding Source | Technique |
|---|---|
| Form submit | Submit → transform → API |
| Table search | `getFieldsValue()` → `params` |
| Route | `:id` / `?tab=` |
| Interceptor | Global `tenantId`, pagination, sign |
| Enum select | `options` → API enum values |

Use DevTools call stack from `fetch`/`XHR.send` upward to locate the packaging function.

#### 1b.3 — Packaging Triple Check (≠ Phase 2 auth gates)

| Question | Expected Answer |
|---|---|
| **Assembly** | Where the payload is built / transformed |
| **Validation** | Required, pattern, enum constraints |
| **Transport** | Path / query / body / multipart / headers |

The interceptor gate (Phase 2) also reads globally injected fields (Authorization, `X‑Tenant‑Id`, sign).

#### 1b.4 — Handoff to Phase 3

Candidate fields come from static and binding layers; **required/optional/conditional** status must be resolved in Phase 3’s parameter matrix + diff + Phase 5 error back‑propagation.

---

## Phase 2 — Three‑Gate Auth

Grep within `OUTDIR/js/` (using `head`) and write `config.json` (recipe in reference):

| Gate | Question | Keywords |
|---|---|---|
| **Render Gate** | How to tell if the user is logged in? | `isLogin`, `getToken`, Cookie/localStorage |
| **Interceptor Gate** | What triggers a redirect to `/login`? | `response_code`, `errno`, axios interceptor |
| **Content Gate** | Where do menus/permissions come from? | `menu`, `permission`, `role`, `acl`, `routes` |

Do **not** treat localStorage key names as credentials—confirm them from chunks/request chains.

**Exit = Gate B**: Results go into `config.json`, then adapt `OUTDIR/runtime_harvest.js` / `preload.js`.

### Phase 2b — API Observation (Optional)

Use `preload.js` inside OUTDIR to confirm session key names, Authorization headers, nested API URLs:

| Config | Output |
|---|---|
| `recordDetail: true` | `__API_RECON_DETAIL__` |
| `observe.xhrHeaders: true` | observed headers |
| `extractUrlsFromResponse: true` | sub‑API URLs inside responses |
| `observe.storageReads/cookieReads: true` | fills `config.json` |
| `neutralizeVueRouter: true` | `__API_RECON_ROUTES__` |

Each coverage run exports: `__API_RECON_LOG__`, `__API_RECON_DETAIL__`, `__API_RECON_ROUTES__`, `__API_RECON_OBSERVE__`.

---

## Phase 3 — Runtime

Gate B must be passed; follow **Scope and Prohibitions** and the credential‑free mock strategy.

Set `"runtimeMode": "depth" | "coverage" | "both"` in `config.json` (template in reference).

### Hook and Stub (shared by depth & coverage)

| Layer | Scope | Purpose |
|---|---|---|
| L1 Precise | auth/permission/bootstrap stubs | Pass first‑screen auth |
| L2 Negative correction | all JSON responses | Convert unauthenticated codes to success |
| L3 Fallback | unmatched `/api` etc. | Empty success body to keep UI alive |

- **depth**: fake auth + `forward` to modify business codes + `stubs`; traverse `routes` (hash/history); output `runtime_api.json`  
- **coverage**: inject `preload.js` at **document‑start** (CDP `addScriptToEvaluateOnNewDocument` or Userscript)

Validate: `window.__API_RECON_PRELOAD__` exists; business paths no longer redirect to `/login`.

```bash
cd recon && npm install
node runtime_harvest.js config.json
```

### 3b — Coverage Dynamic Enumeration (mandatory)

1. Main navigation / sidebar – click each item, wait 1–3 s for network   |
2. Tabs – elements with `role=tab` or `.ant-tabs-tab` |
3. Tables – view/edit/detail of the first row |
4. Toolbar – export, filter, create (avoid irreversible deletes) |
5. Enter each module – merge APIs/routes |
6. SPA – for paths not covered in `routes.txt`, invoke controlled `pushState` (MPA prohibited) |

**Parameter Trigger Matrix** (mandatory): Record each module’s operation type once, then **diff multi‑sample**:

| Operation | Usually added parameters |
|---|---|
| List first page | pagination + default filters |
| Search | `keyword`, `filter` |
| Advanced filter | many optional fields |
| Create / Edit | full entity payload |
| Bulk / Export / Sort | `ids[]`, `exportType`, `sortField` |

Even with stubs, outbound body/headers remain real—record them. Outputs: `scan_raw.json`, `param_samples.json`, `api_detail.json`.

- **Vue**: `neutralizeVueRouter: true` + document‑start preload  
- **React**: use `routes.txt` + sidebar clicks + `pushState`  
- **both**: run depth first, then coverage

---

## Phase 4 — Permission Tree Restoration

**Trigger**: module page blank or each route only returns bootstrap (e.g., locale) → content gate not passed.

| Symptom | Meaning |
|---|---|
| Shell entry succeeds | Render gate + interceptor gate passed |
| Sidebar missing items / click leads to blank | Stub shape or permission code incomplete |
| Same API across routes, very few endpoints | `v‑if permission` not satisfied |
| `routes.txt` far fewer than bundle | Need to supplement from auth module |

```bash
grep -rhoaE '"/api[^"]*(permission|perm|role|menu|acl)[^"]*"' OUTDIR/js/*.js | sort -u | head -30
grep -rhoaE 'userRouteAuth|getResultTree|routeMap|routeLink|menuList|authList' OUTDIR/js/*.js | head -20
```

Typical chain: `role_permissions` (flat codes) + `permissions/all` (tree) → `getResultTree` → `userRouteAuth[CODE].url`.

```bash
python3 recon/extract_route_map.py recon/js recon/
python3 recon/build_perm_tree.py recon/js recon/ --config recon/config.json
```

Intermediate outputs: `route_map.json`, `userRouteAuth.json`, `permissions_tree.json`, `*_stub.json`, `perm_codes_all.txt`.

Stub verification: outer `response_code` aligns with interceptor gate; flat codes match tree; `routes` cover every link in `route_map`.

After updating `config.json`, **rerun Phase 3**. Large SPAs may need to adjust `waitUntil`, `routeTimeout`, `perRouteMs` (see reference Sections A3/I).

---

## Phase 5 — Merge and Report

### Output Table

| File | Phase | Content |
|---|---|---|
| `js/`, `api_static.txt`, `routes.txt`, `chunkmap.txt` | 1 | Static bundle and paths |
| `param_candidates.json` | 1b | Static parameter field candidates |
| `config.json` | 2 | Three‑gate auth + runtime config |
| `runtime_api.json` | 3a | Depth detailed recording (incl. WS/SSE) |
| `param_samples.json`, `scan_raw.json`, `api_detail.json` | 3b | Multi‑sample, click logs, details |
| `route_map.json` … | 4 | Permission‑tree intermediate files (if executed) |
| `params_merged.json` | 5 | Merged parameter fields + confidence |
| `api_merged.txt` | 5 | `METHOD /path [params] [static|runtime|both]` |
| `site_map.json` | 5 | Routes, APIs, params, functional points, limitations |
| **insert_assets** | 5 | Batch insert all discovered services and endpoint assets into the asset library (no asset may be omitted) |

### 5b — Parameter Merging

Diff `param_samples.json`; **no universal merge script**. Confidence rules are in reference Section J7 (high/medium/low/pending).

### 5c — Error Back‑Propagation

Within authorized scope, you may send incomplete requests and read 400 responses (**this is parameter recon, not vulnerability testing**): e.g., `field 'x' is required`, enum errors, etc. Watch for `data` wrappers, `variables`, and pre‑encryption `bizData`.

The report must note: runtimeMode, static vs runtime API counts, parameter confidence, uncovered modules, and a summary of changes compared to reference scripts (`CHANGES.md` excerpt).

Suggested `site_map.json` structure:

```json
{
  "site": "https://example.com",
  "runtimeMode": "both",
  "appType": "vue-spa",
  "routeGuardStrategy": ["nav-neutralize", "L1-auth", "L2-patch", "forward"],
  "apisFromStatic": [],
  "apisFromRuntime": [],
  "apis": [],
  "params": [
    {
      "method": "POST",
      "path": "/api/user/list",
      "transport": "json",
      "fields": []
    }
  ],
  "frontendRoutes": [],
  "routesVerifiedByClick": [],
  "featuresTriggered": [],
  "limitations": ""
}
```

Additional fields and grep recipes are in [reference.md](reference.md).

---

## General Notes

- **Framework‑agnostic**: webpack/Vite/Angular lazy‑load mechanisms are handled uniformly.  
- **Transport**: REST/JSON, GraphQL, WebSocket, SSE; gRPC‑web is out of scope.  
- **SSR**: Client‑side fetches can be recorded; RSC/Server Actions are not fully enumerable.  
- **Blind Spots**: JSVMP, WASM, HMAC/mTLS strong checks → static + annotate limitations.  
- **Parameter Blind Spots**: Conditional dependencies, hidden params, WASM packaging → mark as “pending trigger” / “unreachable”.  
- **Static as Safety Net**: When runtime is blocked, static can still enumerate endpoints.

---

## Additional Resources

- Grep recipes, `config.json` template, troubleshooting, hooks, parameter reverse‑engineering (Section J), `site_map` template: **[reference.md](reference.md)**  
- Reference script paths are listed in the **Scripts and Gates** table above.
