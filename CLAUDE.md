# CLAUDE.md — Open APP Explorer

Guidance for Claude when working in this repo. Read this first.

## What this is
**Open APP Explorer** compares **Access and Participation Plan (APP) targets** across **English universities**. APPs are an Office for Students requirement and apply only to English HE providers, so say "England" / "English universities" (not "UK") wherever the text refers to APP scope. The tool exists to support collaboration and shared learning — **never to rank or judge institutions**. Built by David Gilani; not affiliated with the OfS. Hosted on GitHub Pages from `main`.

## Architecture (keep to this)
- **Single-file app:** all HTML, CSS, and JavaScript live inline in **`index.html`**. Add new features inline there — do not split into separate JS/CSS files.
- **No build step, no runtime dependencies:** vanilla JS; all charts and the map are hand-rolled inline **SVG**. No frameworks, no external CDNs, no map libraries, no client-side API keys.
- **Data is fetched at runtime** from JSON next to `index.html`:
  - `data.json` — one row per APP target, merged with its institution's data (mission group, region, demographic %s, student numbers, **postcode + lat/lng**).
  - `ofs_ethnicity.json`, `ofs_disability.json`, `ofs_fsm.json`, `ofs_tundra.json`, `ofs_age.json` — OfS equity/indicator data (all lifecycle stages incl. Access; gap rows AND individual-indicator rows).
  - Per-lifecycle IMD files (`ofs_access_imd.json`, `ofs_continuation_imd.json`, …).

## Data pipeline (runs on David's Windows PC — not in CI)
- **`export_json.py`** — pulls the Google Sheet (`APPs`, `Institutions`, `Targets` tabs) via `gspread` + a Google service-account key, geocodes postcodes via **postcodes.io** (free, no key), writes `data.json` next to the script.
  - Reads the `Institutions` tab **by column position** → NEVER insert a column mid-sheet; only append on the right. Exception: **postcode** is found **by header name**.
  - Needs `pip install gspread google-auth`. Credentials at `C:\Users\David278\credentials.json` — **never commit**.
- **`filter_ofs_characteristics.py`** — reads the large OfS `APData_ALL.csv`, writes the `ofs_*.json` files.

## Hard constraints
- **Secrets never in the repo** (`credentials.json`, keys).
- **Feedback** POSTs to a Google Apps Script with `mode:'no-cors'`, `Content-Type: text/plain`, JSON string body. Keep this shape.
- **UI:** primary text `#f2f3f6`; muted `#9a9fac`; accent blue `#7eb8f7`. Use hyphens, not em dashes (en dashes `–` in prose are fine).
- **UKPRN matching:** always `.toString().trim()` (text/number mismatches cause bugs).
- **Workflow:** commit and **push directly to `main`** (Pages auto-deploys) — not PRs. Prefer targeted find-and-replace over rewrites. Confirm ambiguous design decisions before coding.

## UI structure
- **Homepage:** three cards — *Filter by institution*, *Filter by demographic targets*, *APP summary data*. Search inputs live inside each card's panel ("Step 1"), not on the homepage. Caveat + "Provide feedback" nudge below (white text); About/feedback via inline links (no floating buttons).
- **Institution view:** search → targets by lifecycle stage → click a target to find similar institutions (with demographic/mission/region/size filters).
- **Demographic view:** stage + characteristic → matching institutions.
- **APP summary view:** headline stats, lifecycle donut, filterable demographic bar chart (All/Access/Success/Progression), and the **map**.
- **OfS charts** per target: equity **gap** trend with a **Gaps | Indicators** toggle (`ofsViewMode`; `_ofsRenderInto()` dispatches; gap vs indicator rows differ by `split_ind2 === '[N/A]'`).
- **Map** (summary view): inline SVG of England; dots per institution sized by matching-target count; filters for stage/characteristic/region; default zoomed to England; wheel/drag zoom + buttons; immediate hover tooltips; click a dot → side panel → open institution or a target; "Back to the map" button on pages reached via the map; 9 clickable English **region** polygons (embedded simplified EER boundaries) that filter + summarise.

## Making changes
- Edit `index.html` inline; charts stay hand-rolled SVG.
- For embedded geo/data constants: generate, simplify, verify the projection visually, then bake in as a JS constant.
- Syntax-check the `<script>` block and, where practical, run a small headless Node test of new logic before pushing.

## Pending / ideas
- **Senior-leader "at-a-glance" views:** pick a region or mission group, see direction of travel on a measure (region + dot-summary logic already exists to build on).
- **Map density tuning** for the London cluster (lighter region fills, borders-only until selected, or hide dots when a region is highlighted).
- **Open question:** whether the narrowing/widening trend badge should stay first-vs-last-year or become more nuanced.
