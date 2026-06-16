---
name: underwriting-hospitality-basic
description: Use when underwriting a hospitality deal (hotel, micro resort, glamping, boutique inn) — running the basic pro forma, asking "what price gets me X% IRR", finding the ceiling offer price, or producing the underwriting verdict. First of the underwriting family (advanced hospitality, STR, self-storage, multifamily come later). Triggers — "underwrite this", "run the model", "what do I need for 15% IRR", "pro forma", "what's this worth".
allowed-tools:
  - Bash
  - Read
  - WebSearch
  - WebFetch
  - Agent
---

<!-- SIZE CEILING: SKILL.md <= 300 lines. Engine only. The math lives in hospitality_underwriting_model_basic.py; defaults in assumptions.md; verdict rules in thresholds.md. Charter rule 3: engine and product never fuse. -->

# Underwriting — Hospitality (Basic)

Owns the `underwriting` check node for hospitality deals. Gathers deal inputs, fills assumptions, researches missing financials, runs a deterministic Python model (an exact replica of the source Quick Sheet), and produces a **verdict** + a **terms scaffold** the agent uses to negotiate.

The math is enforced in code, not reasoning. This file is the procedure around the script — it never re-derives a formula. `hospitality_underwriting_model_basic.py --selftest` proves the replica still matches the source sheet.

## Preamble (run first)

```bash
_GIDFLOW_HOME="${GIDFLOW_HOME:-$HOME/.gidflow}"
_GIDFLOW_DIR="${GIDFLOW_DIR:-$HOME/.claude/skills/gidflow}"
_SKILL_DIR="$_GIDFLOW_DIR/underwriting-hospitality-basic"
_WORK_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
_WORK_SLUG=$(basename "$_WORK_DIR" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
mkdir -p "$_GIDFLOW_HOME/projects/$_WORK_SLUG"
_LEARN_FILE="$_GIDFLOW_HOME/projects/$_WORK_SLUG/learnings.jsonl"
[ -f "$_LEARN_FILE" ] && _LC=$(wc -l < "$_LEARN_FILE" | tr -d ' ') || _LC=0
echo "LEARNINGS: $_LC | PROJECT: $_WORK_SLUG"
if [ "$_LC" -gt 0 ]; then grep '"skill":"underwriting' "$_LEARN_FILE" 2>/dev/null | tail -5; fi
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
echo "VERSION: $(cat "$_GIDFLOW_DIR/VERSION" 2>/dev/null || echo unknown)"
# Verify the model still replicates the source sheet before trusting any number.
python3 "$_SKILL_DIR/hospitality_underwriting_model_basic.py" --selftest >/dev/null 2>&1 \
  && echo "MODEL_SELFTEST: pass" || echo "MODEL_SELFTEST: FAIL — do not trust outputs, investigate"
```

If `LEARNINGS` shows entries, read them and apply. If `UPGRADE_AVAILABLE` appears, mention it once. If `TEL_PROMPTED` is `false`, tell the user once how to opt out (`~/.claude/skills/gidflow/bin/gidflow-config set telemetry off`) then `gidflow-config set tel_prompted true`. **If `MODEL_SELFTEST: FAIL`, stop** — the replica no longer matches the sheet; the math is untrustworthy until fixed.

---

## Non-negotiable: no fabricated inputs

A verdict drives an LOI and an offer price. A made-up RevPAR or cap rate produces a confident, wrong number.

1. **Every researched figure cites a source.** RevPAR, ADR, cap rate, comp — each traces to a fetched page or the deal's `market_research` read. No source → the input is unknown, not guessed.
2. **State every assumption used.** When a default fills a blank, say so ("closing costs assumed 2%"). The user can override any of them.
3. **Missing required inputs with no defensible research → verdict `inconclusive`**, never a fabricated pass. Name what's missing.

---

## The model script

`hospitality_underwriting_model_basic.py` — pure stdlib, four modes. Inputs are a JSON file of overrides (any key in `assumptions.md`); everything unspecified uses the default.

```bash
M="$_SKILL_DIR/hospitality_underwriting_model_basic.py"
python3 "$M" --inputs deal.json                                  # full metrics + IRR
python3 "$M" --inputs deal.json --solve 'lp_irr=0.15' --for purchase_price   # goal-seek one lever
python3 "$M" --inputs deal.json --levers 'lp_irr=0.15' --over purchase_price,ltv,adr,occupancy   # the menu
python3 "$M" --inputs deal.json --ceiling 'dscr>=1.25,lp_irr>=0.15' --for purchase_price          # ceiling price
```

- **Levers** (solvable inputs): `purchase_price`, `ltv`, `gp_split`, `reno_costs`, `adr`, `occupancy`, `interest_rate`, `stabilized_cap`.
- **Metrics** (targets): `lp_irr`, `levered_irr`, `dscr`, `prop_yield_on_cost`, `lp_cash_on_cash`, `cap_rate_on_purchase`, `equity_created`, `stabilized_value`.
- A lever returning `null` means it **cannot reach** that target in its range — an honest answer, not an error. Note: in this basic (pro-rata) model, `gp_split` does **not** move IRR — it only reallocates GP vs LP. Split becomes an IRR lever only in the advanced (waterfall) model.

---

## Mode detection (Stage 0)

Read the user's ask into one mode:

| Ask | Mode |
|---|---|
| "underwrite this deal", "what's this worth", "run the model" | **underwrite** — full metrics + verdict |
| "what price gets me 15% IRR", "what occupancy do I need for X" | **solve** — one lever to one target |
| "how can I get to 15% IRR" | **levers** — the menu of independent paths |
| "what's the most I can pay", "ceiling offer" | **ceiling** — binding-constraint price |

---

## Stage 1 — Gather inputs (three tiers)

**Tier 1 — human-required.** The purchase price (or, in `solve`/`ceiling` mode, the target metric + value and the lever). Pull the **listing price** from the deal if running inside the pipeline; confirm it with the user.

**Tier 2 — default-able.** Closing %, acq fee %, financing %, LTV, interest rate, term, GP/LP split, expense ratio, capital reserve, stabilized cap, IRR exit assumptions (incl. **7-year hold**). Take defaults from `assumptions.md`. `reno_costs` is **derived**, not defaulted — set it from condition × key count + extras (the per-key table and extras rule are in `assumptions.md`); state the condition tier and list the extras. Any value the user gives overrides the default.

**Key count is always required (Tier 1, not researched).** The user must know the number of units — never default it and never silently research it. If it's unknown, ask. For deals where the legal unit scope is unconfirmed (e.g. an AL/STR license that may or may not permit more units), that uncertainty is the headline of the verdict — run a key-count sensitivity (the metrics swing hard on it) and lean `inconclusive` until confirmed.

**Tier 3 — researched-if-missing (the financials).**
- If the deal has actual financials (`deal_financials` node / a P&L), use the real in-place NOI for `current_noi` and real operating numbers.
- If not, build the stabilized pro forma bottom-up: `keys × ADR × occupancy`. Source **ADR, occupancy, and RevPAR** from the deal's `market_research` read first; if absent, WebSearch comps per `../micro-resort-market-research/sources.md` (STR/AirDNA/CoStar tier order). Cite each.
- If you have the key count but only a blended market RevPAR (no separate ADR/occupancy), use the quick fallback: `nofin_revpar` → `gross = keys × RevPAR × 365` → `assumed NOI = 40% × gross`. Uses the real `keys`; 40% margin is the documented default, override if the market says otherwise.
- If RevPAR/ADR cannot be sourced at all → verdict `inconclusive`.

Write the resolved inputs to a JSON file.

---

## Stage 1.5 — Present assumptions, get feedback (before running)

Never run the model on assumptions the user hasn't seen. **Show the full resolved input set as a table** — value + source for each (user-provided · listing · market read · default · derived) — and ask the user what to adjust. Make the defaults and researched figures obvious, since those are what they'll want to challenge.

```
Assumption            Value        Source
purchase_price        €1,296,000   listing
keys                  6            user (villa-only — AL scope unconfirmed)
adr                   €175         market read (base STR/villa)
occupancy             40%          market read
reno_costs            €120k        derived: moderate €20k/key × 6 + €0 extras
stabilized_cap        6.0%         market read (base)
ltv / rate / term     80% / 8% / 25yr   default
hold / exit / growth  7yr / 6.0% / 3%   default
```

Apply any corrections, then run. This gate is required for an interactive run; in the autonomous loop, record the assumption set in the report so it's auditable.

---

## Stage 2 — Run + read the metrics

Run the script in the detected mode. Report the headline block to the user:

- **Current value** (`current_value` = in-place NOI ÷ current cap) and **Stabilized value** (`stabilized_value` = stabilized NOI ÷ market cap) — the two anchors.
- **Returns**: LP IRR, levered IRR, property & LP yield-on-cost, property & LP cash-on-cash, cap-rate on purchase, DSCR, equity created.
- For `solve`/`levers`/`ceiling`: the required lever value(s), and what each implies (e.g. "$4.32M price → 15% IRR" or "DSCR binds before IRR; ceiling is $4.61M").

---

## Stage 3 — Verdict (against thresholds)

Read the user's thresholds from config (`thresholds.md` explains the keys + recommended defaults; primary **LP IRR ≥ 15%**, secondary **DSCR ≥ 1.25**). If a user has none set, use the recommended defaults, say so, and point them to the `onboard` mode to set their own — do **not** run onboarding inline here. Two conditions are **always-on flags**, not user settings: `equity_created < 0` (stabilized value below cost — always flag, caps the verdict at `conditional`) and yield-on-cost below market cap (advisory note).

- **primary met, DSCR met, no flag tripped** → `pass`
- **primary missed clearly, no defensible lever** → `fail`
- **primary just short / DSCR fails / passes only under researched assumptions / a flag tripped** → `conditional`
- **required inputs missing (incl. key count) / RevPAR unsourceable** → `inconclusive`

One-line reason naming the binding metric or flag ("LP IRR 11.2% < 15% floor at ask"; "equity created −€421k — value below cost").

---

## Stage 4 — Terms scaffold (hand-off)

Underwriting feeds terms-setting (the agent's job — see AGENT.md). Always emit, alongside the verdict:

1. **The two values** — current and stabilized.
2. **Full metrics** at the current inputs.
3. **A lever table** toward the user's IRR threshold — run `--levers` over `purchase_price, ltv, adr, occupancy` (and `reno_costs` for value-add). This is the raw material for "here are the ways to get to 15%."

The agent presents the levers with tradeoffs and lets the user choose; this skill only computes them.

### Verdict contract (the agent persists this)

This skill **produces** the verdict; per AGENT.md, the agent writes it via `db.py set-checks`:

```
db.py set-checks <deal_id> '{"underwriting": {"status":"complete","verdict":"<pass|fail|conditional|inconclusive>","as_of":"<today>","report":"<path or inline summary>","reason":"<one line>"}}'
```

Run standalone (not inside the pipeline)? Print the same block for the user; do not write the DB yourself.

---

## Knowledge files (read on every run)

- **`assumptions.md`** — every input, its meaning, and its default. Overridden by user-supplied values per run.
- **`thresholds.md`** — verdict criteria, recommended defaults, and the onboarding questions to set a user's thresholds via `gidflow-config`.

These are data the procedure reads. They grow by tuning values. This file does not grow.

---

## Operational self-improvement

Before completing, if you learned a durable fact (a market's reliable RevPAR source, an assumption that was consistently wrong for a region, a lever that mattered), log it:

```bash
~/.claude/skills/gidflow/bin/gidflow-learnings-log '{"skill":"underwriting-hospitality-basic","key":"SHORT_KEY","insight":"DESCRIPTION"}'
```

Do not log obvious facts or one-off anomalies.

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
  --skill "underwriting-hospitality-basic" \
  --outcome "OUTCOME" \
  --duration "$_TEL_DUR" \
  --version "$_VERSION" 2>/dev/null &
```
