#!/usr/bin/env python3
"""Basic hospitality underwriting model — exact replica of "WK 2: Underwriting Quick Sheet"
(Model tab) plus a levered-IRR module and a goal-seek/lever solver.

The replica (`underwrite`) is a cell-for-cell port of the sheet's enforced formulas;
the IRR module and the solvers are additions the sheet does not contain. See SKILL.md
for invocation and assumptions.md for the meaning/defaults of every input.

Pure standard library. No third-party deps at runtime.
"""
from __future__ import annotations

import argparse
import json
import sys

# ---------------------------------------------------------------------------
# Defaults — mirror the blue/variable cells of the sheet (see assumptions.md).
# Every key here is overridable via the --inputs JSON.
# ---------------------------------------------------------------------------
DEFAULTS = {
    # Uses
    "purchase_price": 3_500_000.0,   # F6  (required in practice; default = sheet scenario)
    "reno_costs":       180_000.0,   # F7
    "closing_pct":          0.02,    # E8
    "acq_fee_pct":          0.03,    # E9
    "financing_pct":        0.01,    # E10
    # Sources / equity
    "ltv":                  0.80,    # H20
    "gp_split":             0.40,    # E15  (lp_split = 1 - gp_split)
    # Loan terms
    "interest_rate":        0.08,    # H21
    "term_years":          25.0,     # H22
    "amort_type":      "Amort",      # H23  ("Amort" | "IO")
    # Current valuation
    "current_cap":          0.10,    # H27
    "current_noi":      213_000.0,   # H28
    # Stabilized operating assumptions
    "keys":                24.0,     # O5
    "days_available":     365.0,     # O6
    "occupancy":            0.60,    # O9
    "adr":                190.0,     # O10
    "fnb_driver":           0.0,     # N14  (F&B revenue as % of rooms revenue)
    "misc_driver":          0.07,    # N15  (misc revenue as % of rooms revenue)
    "expense_ratio":        0.60,    # N18  (total opex as % of total revenue)
    "cap_reserve_pct":      0.15,    # N24  (capital reserve as % of total revenue)
    "stabilized_cap":       0.08,    # N36  (market cap used to value stabilized NOI)
    # "If no financials" quick block (only used when financials are unknown)
    "nofin_key_count":     15.0,     # H32
    "nofin_revpar":        97.26027397,  # H33  (=35500/365 in the sheet)
    "nofin_noi_margin":     0.40,    # H35 uses 0.4 of gross
    # IRR module (NOT in the sheet — additions, all overridable)
    "hold_years":           5.0,
    "noi_growth":           0.03,
    "exit_cap":             None,    # None => use stabilized_cap
    "sale_cost_pct":        0.02,
}

# Which inputs are valid levers for the solver, and the searchable range for each.
LEVER_BOUNDS = {
    "purchase_price": (50_000.0, 50_000_000.0),
    "ltv":            (0.0, 0.95),
    "gp_split":       (0.0, 1.0),
    "reno_costs":     (0.0, 20_000_000.0),
    "adr":            (1.0, 5_000.0),
    "occupancy":      (0.01, 1.0),
    "interest_rate":  (0.0, 0.25),
    "stabilized_cap": (0.01, 0.25),
}


def _pmt(rate: float, nper: float, pv: float) -> float:
    """Excel PMT: payment per period for a loan. Returns a negative number."""
    if rate == 0:
        return -pv / nper
    return -pv * rate * (1 + rate) ** nper / ((1 + rate) ** nper - 1)


def _loan_balance(loan: float, annual_rate: float, term_years: float,
                  years_elapsed: float, amort_type: str) -> float:
    """Remaining principal after `years_elapsed` years of monthly amortization."""
    if amort_type.upper() == "IO" or annual_rate == 0:
        return loan if amort_type.upper() == "IO" else max(loan - 0.0, 0.0)
    r = annual_rate / 12
    n = term_years * 12
    k = min(years_elapsed * 12, n)
    return loan * ((1 + r) ** n - (1 + r) ** k) / ((1 + r) ** n - 1)


def underwrite(user_inputs: dict | None = None) -> dict:
    """Run the model. Returns every line item and the eight stabilized metrics,
    plus the IRR additions. Cell references in comments map to the sheet."""
    i = dict(DEFAULTS)
    if user_inputs:
        i.update(user_inputs)

    pp = i["purchase_price"]
    lp_split = 1 - i["gp_split"]

    # --- Uses (C5:H11) ---
    closing = i["closing_pct"] * pp          # F8
    acq_fee = i["acq_fee_pct"] * pp          # F9
    financing = i["financing_pct"] * pp      # F10
    total_uses = pp + i["reno_costs"] + closing + acq_fee + financing  # F11

    # --- Sources (C13:H17) ---
    loan = i["ltv"] * pp                      # F14
    equity_total = total_uses - loan          # F11 - F14
    gp_equity = equity_total * i["gp_split"]  # F15
    lp_equity = equity_total * lp_split       # F16
    total_sources = loan + gp_equity + lp_equity  # F17

    # --- Current valuation (C25:H29) ---
    current_value = i["current_noi"] / i["current_cap"]  # H29

    # --- If-no-financials quick block (C31:H35) ---
    nofin_gross = i["nofin_revpar"] * i["nofin_key_count"] * 365  # H34
    nofin_noi = nofin_gross * i["nofin_noi_margin"]               # H35

    # --- Stabilized operating assumptions (J/N/O) ---
    rooms_available = i["keys"] * i["days_available"]   # O7
    rooms_sold = rooms_available * i["occupancy"]       # O8
    rooms_revpar = i["adr"] * i["occupancy"]            # O11
    rooms_revenue = rooms_revpar * rooms_available      # O13
    fnb_revenue = i["fnb_driver"] * rooms_revenue       # O14
    misc_revenue = i["misc_driver"] * rooms_revenue     # O15
    total_revenue = rooms_revenue + fnb_revenue + misc_revenue  # O16
    total_expenses = -i["expense_ratio"] * total_revenue        # O18
    noi = total_revenue + total_expenses                # O20 (=SUM(O16:O19))

    if i["amort_type"].upper() == "IO":                 # O23
        debt_service = -loan * i["interest_rate"]
    else:
        debt_service = _pmt(i["interest_rate"] / 12,
                            i["term_years"] * 12, loan) * 12
    cap_reserve = -i["cap_reserve_pct"] * total_revenue  # O24
    levered_cf = noi + debt_service + cap_reserve        # O25

    # --- Stabilized metrics (J30:O37) ---
    prop_yield_on_cost = noi / total_sources                     # O30
    lp_yield_on_cost = noi / total_sources * lp_split            # O31
    prop_cash_on_cash = levered_cf / (gp_equity + lp_equity)     # O32
    lp_cash_on_cash = levered_cf / (gp_equity + lp_equity) * lp_split  # O33
    cap_rate_on_purchase = noi / pp                              # O34
    dscr = noi / -debt_service if debt_service != 0 else float("inf")  # O35
    stabilized_value = noi / i["stabilized_cap"]                 # O36
    equity_created = stabilized_value - total_sources            # O37

    # --- IRR module (additions; not in the sheet) ---
    exit_cap = i["exit_cap"] if i["exit_cap"] is not None else i["stabilized_cap"]
    g = i["noi_growth"]
    n = int(round(i["hold_years"]))
    # Year flows for the FULL equity stack (pro-rata, no promote/waterfall in the
    # basic model => LP IRR == project levered IRR; an advanced skill adds a waterfall).
    flows = [-equity_total]
    for t in range(1, n + 1):
        grow = (1 + g) ** (t - 1)
        rev_t = total_revenue * grow
        noi_t = noi * grow
        reserve_t = -i["cap_reserve_pct"] * rev_t
        cf_t = noi_t + debt_service + reserve_t
        if t == n:
            exit_noi = noi * (1 + g) ** n        # forward (year N+1) NOI
            exit_value = exit_noi / exit_cap
            sale_costs = i["sale_cost_pct"] * exit_value
            balance = _loan_balance(loan, i["interest_rate"], i["term_years"],
                                    n, i["amort_type"])
            cf_t += exit_value - sale_costs - balance
        flows.append(cf_t)
    levered_irr = _irr(flows)

    return {
        # uses / sources
        "purchase_price": pp, "reno_costs": i["reno_costs"], "closing_costs": closing,
        "acq_fee": acq_fee, "financing_cost": financing, "total_uses": total_uses,
        "loan": loan, "gp_equity": gp_equity, "lp_equity": lp_equity,
        "equity_total": equity_total, "total_sources": total_sources,
        # valuation
        "current_value": current_value,
        "nofin_gross_revenue": nofin_gross, "nofin_assumed_noi": nofin_noi,
        # operating
        "rooms_available": rooms_available, "rooms_sold": rooms_sold,
        "rooms_revpar": rooms_revpar, "rooms_revenue": rooms_revenue,
        "fnb_revenue": fnb_revenue, "misc_revenue": misc_revenue,
        "total_revenue": total_revenue, "total_expenses": total_expenses,
        "noi": noi, "noi_margin": noi / total_revenue if total_revenue else 0.0,
        "debt_service": debt_service, "capital_reserve": cap_reserve,
        "levered_cash_flow": levered_cf,
        # the eight stabilized metrics
        "prop_yield_on_cost": prop_yield_on_cost,
        "lp_yield_on_cost": lp_yield_on_cost,
        "prop_cash_on_cash": prop_cash_on_cash,
        "lp_cash_on_cash": lp_cash_on_cash,
        "cap_rate_on_purchase": cap_rate_on_purchase,
        "dscr": dscr,
        "stabilized_value": stabilized_value,
        "equity_created": equity_created,
        # IRR additions
        "levered_irr": levered_irr,
        "lp_irr": levered_irr,   # pro-rata == project levered IRR in the basic model
    }


def _irr(flows: list[float], lo: float = -0.9999, hi: float = 10.0) -> float | None:
    """Levered IRR via bisection on NPV. Returns None if no sign change in range."""
    def npv(rate):
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(flows))
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo == 0:
        return lo
    if f_lo * f_hi > 0:
        return None  # no root in [lo, hi] (e.g. never profitable)
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < 1e-7:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


# ---------------------------------------------------------------------------
# Goal-seek / lever analysis
# ---------------------------------------------------------------------------
def solve(target_metric: str, target_value: float, free_var: str,
          base_inputs: dict | None = None, tol: float = 1e-6) -> float | None:
    """Find the value of input `free_var` that makes output `target_metric` equal
    `target_value`, holding everything else fixed. Binary search; assumes the metric
    is monotonic in the lever over its bounds (true for the model's metrics). Returns
    None if the target is unreachable within the lever's bounds."""
    if free_var not in LEVER_BOUNDS:
        raise ValueError(f"'{free_var}' is not a solvable lever. "
                         f"Choose one of: {', '.join(LEVER_BOUNDS)}")
    base = dict(base_inputs or {})
    lo, hi = LEVER_BOUNDS[free_var]

    def metric_at(x):
        trial = dict(base)
        trial[free_var] = x
        m = underwrite(trial).get(target_metric)
        # An unprofitable scenario yields IRR=None; for monotonic bracketing treat
        # that as an IRR below any realistic target (-100%).
        if m is None:
            return -1.0
        return m

    f_lo, f_hi = metric_at(lo), metric_at(hi)
    if f_lo is None or f_hi is None:
        return None
    # bracket: need target between the two endpoints
    if (f_lo - target_value) * (f_hi - target_value) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        fm = metric_at(mid)
        if fm is None:
            return None
        if abs(fm - target_value) < tol:
            return mid
        if (f_lo - target_value) * (fm - target_value) < 0:
            hi, f_hi = mid, fm
        else:
            lo, f_lo = mid, fm
    return (lo + hi) / 2


def levers(target_metric: str, target_value: float, free_vars: list[str],
           base_inputs: dict | None = None) -> dict:
    """One target, many levers. Returns {lever: required_value_or_None} so the agent
    can present the menu of independent paths to the target."""
    out = {}
    for fv in free_vars:
        try:
            out[fv] = solve(target_metric, target_value, fv, base_inputs)
        except ValueError:
            out[fv] = None
    return out


def solve_constrained(constraints: list[tuple], free_var: str,
                      base_inputs: dict | None = None) -> dict:
    """Several output constraints (metric, op, value), one lever. Solve each as an
    equality and return the binding one. op is '>=' or '<='. For a ceiling offer
    price use e.g. [('dscr','>=',1.25), ('lp_irr','>=',0.15)] over 'purchase_price'
    — the binding (lowest passing) price wins."""
    solutions = {}
    for metric, op, value in constraints:
        x = solve(metric, value, free_var, base_inputs)
        solutions[f"{metric}{op}{value}"] = x
    valid = {k: v for k, v in solutions.items() if v is not None}
    # Binding = most restrictive. For a max (ceiling) lever like price, that's the min.
    binding_key = min(valid, key=valid.get) if valid else None
    return {
        "per_constraint": solutions,
        "binding_constraint": binding_key,
        "binding_value": valid.get(binding_key) if binding_key else None,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _load_inputs(path: str | None) -> dict:
    if not path:
        return {}
    with open(path) as f:
        return json.load(f)


def _parse_pair(s: str) -> tuple[str, float]:
    k, v = s.split("=", 1)
    return k.strip(), float(v)


def _parse_constraint(s: str) -> tuple[str, str, float]:
    for op in (">=", "<="):
        if op in s:
            k, v = s.split(op, 1)
            return k.strip(), op, float(v)
    raise ValueError(f"constraint '{s}' must use >= or <=")


# Ground-truth outputs from the source sheet (Model tab, default scenario). Lets us
# verify the replica without shipping the xlsx. Update only if the sheet's math changes.
_SHEET_EXPECTED = {
    "total_uses": 3_890_000.0, "loan": 2_800_000.0, "total_sources": 3_890_000.0,
    "noi": 427_417.92, "debt_service": -259_330.2497, "levered_cash_flow": 7_805.9503,
    "prop_yield_on_cost": 0.109876072, "lp_cash_on_cash": 0.004296853371,
    "cap_rate_on_purchase": 0.1221194057, "dscr": 1.648160677,
    "stabilized_value": 5_342_724.0, "equity_created": 1_452_724.0,
}


def selftest() -> bool:
    got = underwrite()
    ok = True
    for k, exp in _SHEET_EXPECTED.items():
        diff = abs(got[k] - exp)
        passed = diff < 0.01
        ok &= passed
        print(f"  {'OK ' if passed else 'XXX'} {k:22} sheet={exp:>16.4f} got={got[k]:>16.4f}")
    print("REPLICA MATCHES SHEET:" , ok)
    return ok


def main(argv=None):
    p = argparse.ArgumentParser(description="Basic hospitality underwriting model")
    p.add_argument("--inputs", help="path to JSON of input overrides")
    p.add_argument("--solve", help="target as METRIC=VALUE, e.g. lp_irr=0.18")
    p.add_argument("--for", dest="free_var", help="lever to solve, e.g. purchase_price")
    p.add_argument("--levers", help="target METRIC=VALUE for the lever menu")
    p.add_argument("--over", help="comma-separated levers for --levers")
    p.add_argument("--ceiling", help="comma-separated constraints, e.g. 'dscr>=1.25,lp_irr>=0.15'")
    p.add_argument("--selftest", action="store_true", help="verify replica vs the sheet")
    args = p.parse_args(argv)

    if args.selftest:
        sys.exit(0 if selftest() else 1)

    base = _load_inputs(args.inputs)

    if args.solve:
        if not args.free_var:
            p.error("--solve requires --for <lever>")
        metric, value = _parse_pair(args.solve)
        x = solve(metric, value, args.free_var, base)
        print(json.dumps({"target": {metric: value}, "lever": args.free_var,
                          "required_value": x}, indent=2))
        return
    if args.levers:
        if not args.over:
            p.error("--levers requires --over <lever,lever,...>")
        metric, value = _parse_pair(args.levers)
        table = levers(metric, value, [s.strip() for s in args.over.split(",")], base)
        print(json.dumps({"target": {metric: value}, "levers": table}, indent=2))
        return
    if args.ceiling:
        if not args.free_var:
            p.error("--ceiling requires --for <lever>")
        cons = [_parse_constraint(s.strip()) for s in args.ceiling.split(",")]
        print(json.dumps(solve_constrained(cons, args.free_var, base), indent=2))
        return

    print(json.dumps(underwrite(base), indent=2))


if __name__ == "__main__":
    main()
