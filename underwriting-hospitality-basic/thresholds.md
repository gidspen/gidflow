<!-- Verdict criteria for the underwriting check. Recommended defaults + how a user sets their own via gidflow-config. The skill reads these to map computed metrics → pass/fail/conditional/inconclusive. -->

# Underwriting thresholds — hospitality (basic)

The verdict is **the user's call, encoded as thresholds.** This file holds the recommended defaults and the keys. A user sets their own at onboarding (below); if none are set, the skill uses the recommended defaults and says so in the verdict reason.

## Recommended defaults

| Key (gidflow-config) | Recommended | Metric | Rule |
|---|---|---|---|
| `underwriting.lp_irr_min` | 0.15 | `lp_irr` | **Primary.** LP IRR must clear the floor. Gideon's headline: 15%. |
| `underwriting.dscr_min` | 1.25 | `dscr` | Lender-style floor — debt service coverage. |
| `underwriting.yoc_spread_min` | 0.00 | `prop_yield_on_cost` − `stabilized_cap` | Yield-on-cost should beat the market cap (spread ≥ 0). |
| `underwriting.equity_created_min` | 0 | `equity_created` | Stabilized value must exceed total cost. |

**Primary = `lp_irr`.** The others are secondary guards. A user can disable any secondary check by leaving its key unset and the skill treating it as advisory (reported, not gating) — but `lp_irr_min` always gates.

## Verdict mapping

- **pass** — primary met AND all set secondary thresholds met.
- **fail** — primary missed by a clear margin (e.g. `lp_irr` below floor at the asking price with no defensible lever).
- **conditional** — primary just short, or met only under researched (not actual) financials, or a secondary guard fails while the primary passes. Pair with a terms scaffold showing the levers to clear it.
- **inconclusive** — required inputs missing or RevPAR/ADR unsourceable. Name what's missing.

Always write a one-line reason naming the binding metric: `"LP IRR 11.2% < 15% floor at ask; clears at $2.9M (−17%)"`.

## Onboarding (set a user's thresholds)

When a user first underwrites hospitality, ask — with the recommendation pre-filled — and store their answers:

1. **"Minimum LP IRR you'll accept on a hospitality deal? (most investors here use 15%)"**
2. **"Minimum DSCR your lender requires? (typical 1.20–1.30)"**
3. **"Require the stabilized value to beat cost (equity created > 0)? (recommended yes)"**

Store each:

```bash
~/.claude/skills/gidflow/bin/gidflow-config set underwriting.lp_irr_min 0.15
~/.claude/skills/gidflow/bin/gidflow-config set underwriting.dscr_min 1.25
~/.claude/skills/gidflow/bin/gidflow-config set underwriting.equity_created_min 0
```

Read them at run time:

```bash
IRR_MIN=$(~/.claude/skills/gidflow/bin/gidflow-config get underwriting.lp_irr_min)
IRR_MIN=${IRR_MIN:-0.15}   # fall back to recommended default
```

## Note for the family

These thresholds are hospitality-basic. The advanced hospitality skill (waterfall, pref/promote) will distinguish LP IRR from project IRR and add MOIC/equity-multiple thresholds. Other asset classes (STR, self-storage, multifamily) get their own thresholds files. Keep this one hospitality-only.
