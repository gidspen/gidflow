<!-- Verdict criteria for the underwriting check. Recommended defaults + how a user sets their own via gidflow-config. The skill reads these to map computed metrics → pass/fail/conditional/inconclusive. -->

# Underwriting thresholds — hospitality (basic)

The verdict is **the user's call, encoded as thresholds.** This file holds the recommended defaults and the keys. A user sets their own at onboarding (below); if none are set, the skill uses the recommended defaults and says so in the verdict reason.

## Recommended defaults

### User-set thresholds (asked at onboarding)

| Key (gidflow-config) | Recommended | Metric | Rule |
|---|---|---|---|
| `underwriting.lp_irr_min` | 0.15 | `lp_irr` | **Primary.** LP IRR must clear the floor. The user's headline number. |
| `underwriting.dscr_min` | 1.25 | `dscr` | Secondary lender-style floor — debt service coverage. |

**Primary = `lp_irr`.** `dscr` is a secondary guard. A user can leave `dscr_min` unset and the skill treats it as advisory (reported, not gating) — but `lp_irr_min` always gates.

### Automatic flags (not asked — always on)

These aren't preferences; they're conditions that always get surfaced.

| Condition | Metric | Behavior |
|---|---|---|
| Stabilized value below total cost | `equity_created < 0` | **Always flag.** Never silently passes — the deal isn't creating equity. Pushes the verdict to at most `conditional` and names it in the reason. |
| Yield-on-cost below market cap | `prop_yield_on_cost` − `stabilized_cap` < 0 | Advisory note in the report (you're paying up vs. the cap you'd resell at). |

## Verdict mapping

- **pass** — primary met, `dscr` (if set) met, AND no automatic flag tripped.
- **fail** — primary missed by a clear margin (e.g. `lp_irr` below floor at the asking price with no defensible lever).
- **conditional** — primary just short, or met only under researched (not actual) financials, or `dscr` fails, or an automatic flag tripped (e.g. negative equity created) while the primary passes. Pair with a terms scaffold showing the levers to clear it.
- **inconclusive** — required inputs missing or RevPAR/ADR unsourceable. Name what's missing.

Always write a one-line reason naming the binding metric: `"LP IRR 11.2% < 15% floor at ask; clears at $2.9M (−17%)"`.

## Onboarding (set a user's thresholds)

When a user first underwrites hospitality, ask two questions — with the recommendation pre-filled and a one-line explainer of what the metric is and why it matters:

1. **"Minimum LP IRR you'll accept on a hospitality deal? (most investors here use 15%)"**
   *LP IRR is the annualized return to the equity over the hold, accounting for timing — it's the single number that says whether the deal is worth your capital vs. the next one.*
2. **"Minimum DSCR your lender requires? (typical 1.20–1.30)"**
   *DSCR is net operating income ÷ debt service — how many times the property's income covers the loan payment; below ~1.2x lenders won't fund and a bad month can't cover debt.*

Store each:

```bash
~/.claude/skills/gidflow/bin/gidflow-config set underwriting.lp_irr_min 0.15
~/.claude/skills/gidflow/bin/gidflow-config set underwriting.dscr_min 1.25
```

Read them at run time:

```bash
IRR_MIN=$(~/.claude/skills/gidflow/bin/gidflow-config get underwriting.lp_irr_min)
IRR_MIN=${IRR_MIN:-0.15}   # fall back to recommended default
```

## Note for the family

These thresholds are hospitality-basic. The advanced hospitality skill (waterfall, pref/promote) will distinguish LP IRR from project IRR and add MOIC/equity-multiple thresholds. Other asset classes (STR, self-storage, multifamily) get their own thresholds files. Keep this one hospitality-only.
