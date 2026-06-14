<!-- Default inputs for hospitality_underwriting_model_basic.py. Every key is an input to the model; every value is the default used when the user/deal doesn't supply one. Defaults mirror the source Quick Sheet's variable cells. Overridden per-run by the --inputs JSON. -->

# Underwriting assumptions — hospitality (basic)

Defaults live in code (`DEFAULTS` in `hospitality_underwriting_model_basic.py`) so the script runs with zero config. This file is the human-readable map: what each input means, its default, and the sheet cell it came from. **Any input can be overridden per run** — pass it in the `--inputs` JSON.

## Tier 1 — human-required (no safe default; default shown is the sheet's sample)

| Input | Default | Cell | Meaning |
|---|---|---|---|
| `purchase_price` | 3,500,000 | F6 | The price under analysis. Always confirm with the user / listing. |

## Tier 2 — default-able (assume, but state it; user overrides)

| Input | Default | Cell | Meaning |
|---|---|---|---|
| `reno_costs` | 180,000 | F7 | Renovation / value-add budget. |
| `closing_pct` | 0.02 | E8 | Closing costs as % of purchase price. |
| `acq_fee_pct` | 0.03 | E9 | Acquisition fee as % of purchase price. |
| `financing_pct` | 0.01 | E10 | Financing cost as % of purchase price. |
| `ltv` | 0.80 | H20 | Loan-to-value. Loan = ltv × purchase price. |
| `gp_split` | 0.40 | E15 | GP share of equity (LP = 1 − gp_split). Does **not** affect IRR in this model. |
| `interest_rate` | 0.08 | H21 | Annual loan rate. |
| `term_years` | 25 | H22 | Amortization term. |
| `amort_type` | "Amort" | H23 | "Amort" or "IO" (interest-only). |
| `current_cap` | 0.10 | H27 | Cap rate applied to in-place NOI for current value. |
| `current_noi` | 213,000 | H28 | In-place NOI (use real P&L when available). |
| `expense_ratio` | 0.60 | N18 | Total opex as % of total revenue (→ 40% margin). |
| `cap_reserve_pct` | 0.15 | N24 | Capital reserve (FF&E) as % of revenue. |
| `stabilized_cap` | 0.08 | N36 | Market cap rate used to value stabilized NOI. |
| `fnb_driver` | 0.00 | N14 | F&B revenue as % of rooms revenue. |
| `misc_driver` | 0.07 | N15 | Misc revenue as % of rooms revenue. |

## Tier 3 — stabilized operating inputs (from financials, else researched)

| Input | Default | Cell | Meaning |
|---|---|---|---|
| `keys` | 24 | O5 | Number of rentable units. |
| `days_available` | 365 | O6 | Days per year available. |
| `occupancy` | 0.60 | O9 | Stabilized occupancy. Research from market read. |
| `adr` | 190 | O10 | Stabilized average daily rate. Research from market read. |

### No-financials quick fallback (only when financials unknown)

When there's no P&L and only a key count + market RevPAR are available:

| Input | Default | Cell | Meaning |
|---|---|---|---|
| `nofin_key_count` | 15 | H32 | Key count for the quick estimate. |
| `nofin_revpar` | 97.26 | H33 | Market RevPAR (cite the source). |
| `nofin_noi_margin` | 0.40 | H35 | Assumed NOI as % of gross. **40% is the documented default.** |

`gross = nofin_revpar × nofin_key_count × 365`, `assumed NOI = nofin_noi_margin × gross`.

## IRR module (additions — not in the source sheet)

The sheet stops at single-year stabilized metrics. These inputs drive the levered-IRR projection. All overridable.

| Input | Default | Meaning |
|---|---|---|
| `hold_years` | 5 | Hold period. |
| `noi_growth` | 0.03 | Annual revenue/NOI growth. |
| `exit_cap` | `null` → stabilized_cap | Terminal cap rate at sale. |
| `sale_cost_pct` | 0.02 | Cost of sale as % of exit value. |

Exit value = `NOI × (1+growth)^hold ÷ exit_cap`; net of sale cost and remaining loan balance. LP IRR equals project levered IRR here (pro-rata; no promote/waterfall in the basic model).

## How to override

```bash
echo '{"purchase_price": 2900000, "ltv": 0.75, "occupancy": 0.65, "adr": 210}' > deal.json
python3 hospitality_underwriting_model_basic.py --inputs deal.json
```
