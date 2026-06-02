---
name: find-deals
description: Use when searching for on-market real estate deals, running /find-deals, or when the user wants to find, source, or evaluate micro resort, glamping, boutique hotel, or STR investment properties. Phase 1 of the Deal Partner pipeline.
allowed-tools:
  - Bash
  - Read
  - WebSearch
  - WebFetch
  - Agent
---

<!-- SIZE CEILING: SKILL.md <= 300 lines. Engine only. Knowledge lives in buy-box.md, sources.md, scoring.md, persistence.md. Charter rule 3: engine and product never fuse. -->

# Find Deals

Phase 1 of the Deal Partner pipeline. Takes a buy box, searches the open web, and writes scored property listings into the ledger as tiers — HOT / STRONG / WATCH.

The engine is a 4-level nested loop driven by the model. No Python pipeline, no scraper fleet, no state machine. Two tools — `WebSearch` and `WebFetch` — and four flat knowledge files.

## Preamble (run first)

```bash
_GIDFLOW_HOME="${GIDFLOW_HOME:-$HOME/.gidflow}"
_GIDFLOW_DIR="${GIDFLOW_DIR:-$HOME/.claude/skills/gidflow}"
_WORK_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
_WORK_SLUG=$(basename "$_WORK_DIR" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
mkdir -p "$_GIDFLOW_HOME/projects/$_WORK_SLUG"
_LEARN_FILE="$_GIDFLOW_HOME/projects/$_WORK_SLUG/learnings.jsonl"
[ -f "$_LEARN_FILE" ] && _LC=$(wc -l < "$_LEARN_FILE" | tr -d ' ') || _LC=0
echo "LEARNINGS: $_LC | PROJECT: $_WORK_SLUG"
if [ "$_LC" -gt 0 ]; then tail -5 "$_LEARN_FILE" 2>/dev/null; fi
_CKFILE="$_GIDFLOW_HOME/.last-update-check"
_NOW=$(date +%s)
_DO_CHECK=1
[ -f "$_CKFILE" ] && [ $(( _NOW - $(cat "$_CKFILE" 2>/dev/null || echo 0) )) -lt 86400 ] && _DO_CHECK=0
if [ "$_DO_CHECK" = "1" ] && [ -d "$_GIDFLOW_DIR/.git" ]; then
  git -C "$_GIDFLOW_DIR" fetch origin --quiet 2>/dev/null || true
  _LOCAL=$(git -C "$_GIDFLOW_DIR" rev-parse HEAD 2>/dev/null)
  _REMOTE=$(git -C "$_GIDFLOW_DIR" rev-parse origin/main 2>/dev/null)
  [ -n "$_REMOTE" ] && [ "$_LOCAL" != "$_REMOTE" ] && echo "UPGRADE_AVAILABLE — run /gidflow-upgrade" || true
  echo "$_NOW" > "$_CKFILE"
fi
# Check for cursor from a prior run
_CURSOR_FILE="$HOME/.claude/skills/find-deals/.cursor"
[ -f "$_CURSOR_FILE" ] && echo "PRIOR_RUN_CURSOR: $(cat "$_CURSOR_FILE")" || true
# Check for unflushed pending writes
_PENDING="$HOME/.claude/skills/find-deals/pending-writes.jsonl"
[ -f "$_PENDING" ] && [ -s "$_PENDING" ] && echo "PENDING_WRITES: $(wc -l < "$_PENDING" | tr -d ' ') rows to flush before starting"
```

If `LEARNINGS` shows entries, read them. Apply any noted blocked sources (skip those sources immediately) and any useful search phrases to this run.

If `UPGRADE_AVAILABLE` appears, mention it once to the user.

If `PENDING_WRITES` appears: flush `pending-writes.jsonl` to Supabase before starting the loop. See `persistence.md`.

If `PRIOR_RUN_CURSOR` appears: offer to resume from that cursor or start fresh.

---

## Non-negotiable: no fabricated data

Investors will call sellers and write offers off of what's in the ledger. Fabricated URLs, hallucinated prices, or AI-compiled "research" entries destroy credibility on the first wrong call.

**Hard rules:**

1. **Search snippets are leads, not data.** WebSearch returns links and previews — those are leads. A listing only enters the ledger if you actually `WebFetch`-ed its page and read the data from the response.
2. **Never construct URLs from a pattern.** If a source didn't return a URL for a listing, that listing doesn't enter the ledger.
3. **Never compile from multiple sources.** If you can't trace every field in a row to one fetched page, the row doesn't exist.
4. **If a source gives nothing, report zero — never fill the gap with synthesized rows.** The fix is more sources, not invented ones.

Every row in the `listings` table must trace to a real fetched URL.

---

## Tools

- **WebSearch** — broad discovery. Returns ~10 ranked links per query.
- **WebFetch** — pull a page, parse to markdown, extract fields. Where all real data comes from.

No browser automation. No login sessions. No per-site tooling. If a source's HTML can't be fetched cleanly, the source is treated as blocked for this run.

---

## How a run is structured

**Setup (runs once):**
- Stage 1 — Buy Box Intake
- Stage 2 — Keyword Expansion

**The nested loop (the engine):**
- Stages 3–6 — for each keyword → for each source → for each set → for each deal

**Finish (runs once):**
- Stage 7 — mark complete, notify

The four loop levels are bounded — 4 loops whether the run processes 70 deals or 10 million. The scaling lives in the lists (keywords, sources, deals, the ledger), not the procedure.

---

## Stage 1 — Buy Box Intake

Parse the user's request into a structured buy box. Two forms accepted: a raw prompt string (e.g. "micro resort in east texas, 8+ acres, $500k to $3m, existing structure required, value-add ok") or a JSON object matching the `searches.buy_box` shape.

Extract:
- **Locations** (list — empty = no location filter)
- **Price min / max**
- **Min acreage**
- **Property types** (drawn from the allowed set in `buy-box.md`)
- **Revenue requirement** (e.g. `value_add_ok`, `stabilized_only`)
- **Exclusions** (e.g. "no raw land", "fee simple required")

If the user omitted a field, fall back to the default in `buy-box.md`. Echo the parsed buy box back to the user **before the loop starts** so they can correct misreads. Create the `searches` row at this point (status `running`) and capture the returned `search_id` — every subsequent write references it.

---

## Stage 2 — Keyword Expansion

Translate the property types into the vocabulary used in real listing titles. Generate **8–15 search phrasings per run**, seeded from the buy box plus domain knowledge.

**Seed examples:**

| Seed type | Phrasings |
|---|---|
| micro resort | glamping resort · glamping property · glamping business |
| RV park | RV park resort · RV park and cabins · campground |
| cabin resort | cabin resort · cabin rental business |
| retreat / lodge | retreat center · lodge resort · fishing camp |
| boutique hotel | boutique hotel · boutique inn · country inn |
| bed and breakfast | bed and breakfast · inn for sale |

Append the location (or sub-region) and a price hint ("$1M–$3M") to each phrasing.

---

## Stages 3–6 — The nested loop

### LOOP 4 — for each KEYWORD

1. **Search.** Call `WebSearch` with the keyword + location + price hint. Returns ~10 ranked links. Merge with other phrasings of the same keyword group → deduplicated, ranked list of sources.
2. Enter LOOP 3 over those sources.

**Exit:** every keyword from Stage 2 has been searched → run complete.

### LOOP 3 — for each SOURCE

1. **Accessibility check.** Look up the source in `sources.md`.
   - If `blocked` → **pass** (skip entirely — no `WebFetch`, no retry). Blocked sources do NOT count toward the streak.
   - If `accessible` → continue. Runtime: if `WebFetch` returns non-2xx, treat as blocked for this run.
2. Enter LOOP 2 over the source's listings, in batches of 20.

**Exit:** **3 accessible sources in a row return 0 passing deals** → next keyword.

### LOOP 2 — for each SET of deals (≤20)

1. Pull the source's listing index page (or the next paginated batch).
2. Enter LOOP 1 over the 20 deals.
3. After LOOP 1: batch write passing deals to Supabase + save cursor. See `persistence.md`.

**Exit:** fewer than **5** deals passed in the just-finished set → stop sets for this source, next source.

### LOOP 1 — for each DEAL in the set

**a. Dedup.** Has this URL been seen in the `listings` table already? Yes → skip.

**b. Pull.** `WebFetch` the listing page. Extract: price, acreage, address, location, property type, description, and leading image URL. If the index page didn't carry key fields, fetch the detail page.

**c. Score.** Apply the 6 criteria from `scoring.md`. Each resolves to MATCH / MISS / UNKNOWN. Assign tier: HOT / STRONG / WATCH / Drop.

**d. Hold for batch write.** Loop 1 does no I/O. Write happens at the LOOP 2 set boundary.

**Exit:** all ≤20 deals are pulled and scored.

---

## Stage 7 — Finish

1. Update the `searches` row: `status = 'complete'`, `completed_at = now()`.
2. Report results: "N deals found: X HOT, Y STRONG, Z WATCH."

---

## Resuming a run

On run start:
1. Check for `pending-writes.jsonl`. If non-empty, flush before doing anything else.
2. If a cursor exists for an in-progress search, resume from it. Otherwise start at keyword 0.

See `persistence.md` for the full mechanism.

---

## Knowledge files (read on every run)

- **`buy-box.md`** — defaults: price range, min acreage, allowed property types, STR-market rules. Overridden by the user's per-run buy box.
- **`sources.md`** — known listing sources + blocked list. Grows by appending new rows.
- **`scoring.md`** — the 6 criteria with MATCH/MISS/UNKNOWN rules, tier definitions, and hard-drop exclusions.
- **`persistence.md`** — Supabase wiring: per-set write, fallback, cursor.
- **`schema.sql`** — the 4-table Supabase schema.

These files are data the procedure reads. They grow by appending rows or tuning thresholds. This file does not grow.

---

## Operational self-improvement

Before completing: if you discovered a durable fact (a source that was blocked or returned unusually good results, a search phrase that found deals the standard phrases missed, a region pattern), log it:

```bash
~/.claude/skills/gidflow/bin/gidflow-learnings-log '{"skill":"find-deals","key":"SHORT_KEY","insight":"DESCRIPTION"}'
```

Examples of good logs: `{"skill":"find-deals","key":"innshopper_accessible","insight":"InnShopper returns full listing detail on first fetch — no pagination needed"}`. Do not log obvious facts or one-time anomalies.
