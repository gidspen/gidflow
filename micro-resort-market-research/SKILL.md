---
name: micro-resort-market-research
description: Evaluate whether a market is strong enough to buy a micro resort, boutique resort, or glamping property, BEFORE underwriting any deal. Runs a 6-gate market funnel that aggregates micro resort, glamping, and STR data (plus CoStar hotel data the user provides), weighted micro-resort-primary. Use when asked to evaluate, analyze, or research a market or location for a micro resort / boutique hotel acquisition, "is this a good market", or when the user runs /micro-resort-market-research.
allowed-tools:
  - Bash
  - Read
  - WebSearch
  - WebFetch
  - Agent
---

<!-- SIZE CEILING: SKILL.md <= 200 lines. Slow-changing engine only: the gate loop, the data-layer model, the principles. The detailed source catalog (URLs, costs, how-to, flags, benchmarks) lives in sources.md, the product layer. Charter rule 3: engine and product never fuse. Charter rule 2: new machinery defaults to NO. This skill is knowledge, not code. -->

# Micro Resort Market Research

A fast market-evaluation funnel. Decide whether a location is strong enough to buy a micro resort or boutique resort, before underwriting any specific deal. Market first. Without a strong market, the deal does not matter.

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
if [ "$_LC" -gt 0 ]; then tail -3 "$_LEARN_FILE" 2>/dev/null; fi
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
_TEL=$("$_GIDFLOW_DIR/bin/gidflow-config" get telemetry 2>/dev/null || echo "on")
_TEL_PROMPTED=$("$_GIDFLOW_DIR/bin/gidflow-config" get tel_prompted 2>/dev/null || echo "false")
echo "TELEMETRY: $_TEL | TEL_PROMPTED: $_TEL_PROMPTED"
echo "$(date +%s)" > "$_GIDFLOW_HOME/.session-start"
_GIDFLOW_VERSION=$(cat "$_GIDFLOW_DIR/VERSION" 2>/dev/null || echo "unknown")
echo "VERSION: $_GIDFLOW_VERSION"
```

If `LEARNINGS` shows entries, read them and apply any relevant market patterns or source notes to this run before proceeding.

If `UPGRADE_AVAILABLE` appears, mention it once to the user.

If `TEL_PROMPTED` is `false`: tell the user once — "Usage data is shared anonymously to improve gidflow. To opt out: `~/.claude/skills/gidflow/bin/gidflow-config set telemetry off`" — then run:
```bash
~/.claude/skills/gidflow/bin/gidflow-config set tel_prompted true
```

## When to invoke

- "Is this a good market for a micro resort / boutique hotel?"
- "Evaluate / analyze / research this market (or property location)."
- The user runs `/micro-resort-market-research <location or property address>`.

This produces a market read, NOT a deal underwrite. The deal (price, structure, NOI) is downstream and separate. If the market fails, stop before the deal.

## Input

`/micro-resort-market-research <location or address>`. Optionally the user pastes the property's unit mix (e.g. "12 hotel rooms + 19 cabins") and any CoStar hotel submarket numbers they already have. If unit mix is unknown, ask once, then proceed with what you have.

## The data-layer model (read this first)

Three layers measure different things. A micro resort often walks the line between them, so name which layer drives each number and weight micro-resort-primary.

| Layer | Measures | Sources | Use for |
|---|---|---|---|
| Micro resort / glamping (PRIMARY) | purpose-built outdoor-hospitality ADR by unit type, supply density, category demand | Sage, Hipcamp, Glamping Hub, KOA | experiential units (A-frames, domes, safari tents, cabins) and the category tailwind |
| STR (SECONDARY) | whole-home / cabin / unique-stay occupancy, ADR, RevPAR on Airbnb + Vrbo | AirDNA, AirROI, Airbtics, Rabbu | cabins, villas, unique units booked like short-term rentals |
| Hotel (CEILING / sanity) | branded + independent hotel occupancy, ADR, RevPAR, supply pipeline | CoStar / STR (Smith Travel) / HVS | the hotel-room block and the submarket ADR ceiling |

**Aggregation rule.** Build the expectation by unit type. Hotel rooms priced off hotel comps; cabins and villas off STR plus glamping comps; tents, domes, and RV off glamping comps. Lead with the micro resort and glamping layer. Use hotel data as a ceiling and a reality check only. Do NOT deep-dive hotel data: this skill is micro-resort-primary. The user pulls hotel data from CoStar (better than anything you can scrape), so do not burn tokens on inferior hotel sources. Prompt the user to paste the CoStar submarket figures when the property has hotel keys.

**Excluded:** PriceLabs is a pricing and operations tool, not a market-evaluation tool. Do not use it here.

## Geography discipline

Pin the exact geography before pulling anything. City does not equal county does not equal metro (MSA) does not equal STR submarket. A property can sit in a small town that rides a famous metro's brand (for example a town inside a larger MSA). Underwrite to the LOCAL submarket numbers, not the big-brand halo, and note which geography each figure represents.

## The loop: 6 gates

Run in order. Kill the market the moment a gate fails. Do not spend on the next gate. Most gates are free. Fan out subagents for the web pulls to stay token-efficient (one agent per gate or per cluster). Prioritize reputable sources and label confidence.

1. **CATCHMENT** — can people get here? Drive-time isochrone (Google Maps / TravelTime) + Census population and growth. Pass: 1M+ metro within ~90 min (a strong anchor stretches this to 2 to 3 hours). Kill: under 500k within 2 hours and no destination anchor.
2. **ANCHOR** — is demand proven? NPS Visitor Spending Effects + county tourism authority / occupancy-tax data. Pass: measurable, ideally growing lodging demand from a real draw (park, water, wine, mountains, destination town). Kill: no evidence visitors already pay to sleep here.
3. **DIRECTION** — rising or fading? Google Trends (destination + "glamping" / "cabin rental", 3 to 5 year window) + KOA macro tailwind. Pass: rising multi-year interest with a clear season. Kill: multi-year decline with no offset. Always flag recent shocks (natural disasters, regulation changes).
4. **SUPPLY** — who is already here? Hipcamp / Glamping Hub census + the STR layer. Read saturation. Thin comps are NORMAL for micro resorts and are not a kill. Dense, well-reviewed, rate-cutting supply is the real caution.
5. **RATE & OCCUPANCY** — does it pencil? Glamping ADR (Sage) + STR occupancy / ADR / RevPAR (AirDNA) + the hotel ceiling (CoStar, user-provided). Compute RevPAR yourself (ADR x occupancy). Remember the micro resort edge: breakeven near 25 to 40 percent occupancy versus 55 to 65 percent for a hotel, so premium-tier rates are where it works.
6. **SYNTHESIS** — GO / NO / CONDITIONAL. Preponderance of evidence: do the independent signals converge?

## Thin-comp playbook (the micro resort default)

When there are fewer than 20 comps: widen the radius, use an analog market (similar terrain and drive-time from a similar-sized metro), discount the analog's ADR and occupancy 15 to 20 percent for immaturity, and lean harder on the demand proxies (NPS, tourism authority, airport, Trends), which exist in every market regardless of comp density.

## Output format

```
# Market Read: <location>   (geography: <city / county / MSA / STR submarket>)
Verdict: GO / NO / CONDITIONAL — <one line>

| Gate | What we found | Read |
|------|---------------|------|
| 1 Catchment    | ... | PASS / CAUTION / FAIL |
| 2 Anchor       | ... | ... |
| 3 Direction    | ... | ... |
| 4 Supply       | ... | ... |
| 5 Rate & Occ   | ... | ... |

Positioning by asset class:
| Asset class | Layer | ADR | Occ | RevPAR | Supply | Call |
|---|---|---|---|---|---|---|
| <commodity cabin> | STR      | $... | ..% | $... | saturated | AVOID |
| <luxury dome>     | glamping | $... | ..% | $... | thin      | BUILD |

Best positioning: <one line — what to build, target ADR/occ, what to avoid>
Aggregation note: <which layer drove rate/occ; blended expectation by unit type>
Confidence: <high / med / low, and why>
Still need: <CoStar hotel submarket numbers; premium-tier occupancy; etc.>
```

## Persist the read (every completed run)

Upsert to the `markets` table (deals DB), keyed on `slug`, so re-runs refresh in place and a read under 90 days old is reused instead of re-run. Set `SLUG` to the STR-submarket / destination name, not the tiny town (e.g. Mineral Bluff → `blue-ridge-fannin-county-ga`). First write the four markdown slices to temp files, then upsert. Fail-soft if creds are missing (never crash the read).

- `/tmp/mr_summary.md` — verdict + synthesis + confidence + still-need (the brief)
- `/tmp/mr_gates.md` — the 6-gate table
- `/tmp/mr_positioning.md` — the asset-class table + best-positioning line
- `/tmp/mr_report.md` — the full read

```bash
SLUG="..."; LOC="..."; GEO="..."; VERDICT="GO|NO|CONDITIONAL"; CONF="high|medium|low"  # set per run
_ef=""; for f in ./.env "$HOME/dealhound-pro/.env"; do [ -f "$f" ] && { _ef="$f"; break; }; done
_p(){ grep -E "^$1=" "$_ef" 2>/dev/null | head -1 | cut -d= -f2-; }
URL="$(_p SUPABASE_URL)"; KEY="$(_p SUPABASE_SERVICE_KEY)"
if [ -z "$URL" ] || [ -z "$KEY" ]; then echo "PERSIST SKIPPED — no Supabase creds in env; read not saved"; else
  jq -n --arg slug "$SLUG" --arg location "$LOC" --arg geography "$GEO" --arg verdict "$VERDICT" \
    --arg confidence "$CONF" --arg as_of "$(date +%F)" \
    --rawfile summary_md /tmp/mr_summary.md --rawfile gates_md /tmp/mr_gates.md \
    --rawfile positioning_md /tmp/mr_positioning.md --rawfile report_md /tmp/mr_report.md \
    '{slug:$slug,location:$location,geography:$geography,verdict:$verdict,confidence:$confidence,as_of:$as_of,summary_md:$summary_md,gates_md:$gates_md,positioning_md:$positioning_md,report_md:$report_md,updated_at:(now|todate)}' > /tmp/mr_row.json
  curl -sS -X POST "$URL/rest/v1/markets?on_conflict=slug" -H "apikey: $KEY" -H "Authorization: Bearer $KEY" \
    -H "Content-Type: application/json" -H "Prefer: resolution=merge-duplicates,return=minimal" \
    --data @/tmp/mr_row.json && echo "PERSISTED: $SLUG"
fi
```

## Principles

- **Market before deal.** A great market can still be a bad deal; a bad market kills every deal.
- **Preponderance of evidence.** Five converging free signals beat one paid number.
- **Reputable sources first** (CoStar, STR, HVS, NPS, Census, BEA, county tourism authority, airport authority). Label confidence. SEO blog stats are a last resort and flagged as such.
- **Name the layer and the geography** behind every figure.
- **Token-efficient.** Fan out subagents for the free web pulls; do not re-pull what the user gets better from CoStar.

## Sources

Detailed catalog (what each tool is for, cost, how to use, what to look for, green and red flags, benchmarks): see `sources.md` in this skill folder.

## Operational self-improvement

Before completing: if you discovered a durable market pattern, a source that worked especially well, or a benchmark worth remembering for future runs, log it:

```bash
~/.claude/skills/gidflow/bin/gidflow-learnings-log '{"skill":"micro-resort-market-research","key":"SHORT_KEY","insight":"DESCRIPTION"}'
```

Do not log obvious facts or one-time anomalies.

## Telemetry (run at completion)

Replace `OUTCOME` with `success`, `error`, or `abort`.

```bash
_GIDFLOW_DIR="${GIDFLOW_DIR:-$HOME/.claude/skills/gidflow}"
_GIDFLOW_HOME="${GIDFLOW_HOME:-$HOME/.gidflow}"
_TEL_END=$(date +%s)
_TEL_START=$(cat "$_GIDFLOW_HOME/.session-start" 2>/dev/null || echo "$_TEL_END")
_TEL_DUR=$(( _TEL_END - _TEL_START ))
_VERSION=$(cat "$_GIDFLOW_DIR/VERSION" 2>/dev/null || echo "unknown")
"$_GIDFLOW_DIR/bin/gidflow-telemetry-log" \
  --skill "micro-resort-market-research" \
  --outcome "OUTCOME" \
  --duration "$_TEL_DUR" \
  --version "$_VERSION" 2>/dev/null &
```
