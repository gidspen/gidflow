# Scoring Rules

Each listing is evaluated on 6 criteria. Each resolves to **MATCH**, **MISS**, or **UNKNOWN**.
Tier is assigned from the result set. Hard-drop exclusions bypass scoring entirely.

---

## Hard-Drop Exclusions (checked before scoring)

| Condition | Action |
|-----------|--------|
| Confirmed wrong-region location | Hard drop. Never a MISS — MISS allows Watch; wrong region does not. Only UNKNOWN location (genuinely ambiguous) keeps a listing in scope. |
| SOLD listing status | Hard drop. Remove entirely. |

**Pending / Under Contract:** Not a hard drop. Listing stays in the set but is **capped at STRONG** regardless of criteria.

---

## The 6 Criteria

### 1. Location

| Verdict | Rule |
|---------|------|
| MATCH | Address / description places the listing in a region that matches the buy box locations (or buy box has no location filter). STR market signal is YES (lakefront, mountain, coastal, destination, near national park, wine/hill country). |
| MISS | Confirmed wrong region. Triggers hard drop — see above. OR confirmed STR market signal NO (urban, STR-restricted). |
| UNKNOWN | Region is genuinely ambiguous from the listing data. STR market signal cannot be determined. Keep in scope. |

### 2. Price

| Verdict | Rule |
|---------|------|
| MATCH | Asking price is within PRICE_MIN–PRICE_MAX. |
| MISS | Outside range by more than 10%. |
| UNKNOWN | Price not listed. |

> **"Slightly out" rule:** within 10% of either threshold = "slightly out" → eligible for STRONG if all other criteria MATCH. Outside 10% = clear MISS.

### 3. Acreage

| Verdict | Rule |
|---------|------|
| MATCH | Total owned acreage meets or exceeds MIN_ACREAGE. |
| MISS | Confirmed acreage below threshold by more than 10%. |
| UNKNOWN | Acreage not stated. |

> **"Slightly out" rule:** within 10% of MIN_ACREAGE = "slightly out" → eligible for STRONG if all other criteria MATCH. Outside 10% = clear MISS.

> **Leasehold acreage:** scores UNKNOWN unless lease terms are confirmed favorable (long-term, renewable). Do not score as MATCH on leasehold without confirmed terms.

### 4. Type

| Verdict | Rule |
|---------|------|
| MATCH | Property type is in the allowed set from buy-box.md (micro resort, glamping resort, boutique hotel, cabin resort / cabin rental, B&B / inn, lodge, STR-capable residential, vacation property with land). |
| MISS | Property type is explicitly outside the allowed set and no conversion path is evident. |
| UNKNOWN | Type ambiguous or not described. |

### 5. Structure

| Verdict | Rule |
|---------|------|
| MATCH | An existing structure is present (structures, keys, cabins, rooms, or a main residence described). |
| MISS | Confirmed raw land with no structures and no structure plans described. |
| UNKNOWN | No description of structures; neither confirmed present nor confirmed absent. |

### 6. Revenue

| Verdict | Rule |
|---------|------|
| MATCH | Operating property with a revenue signal (gross revenue, NOI, occupancy mentioned) OR listing explicitly describes a value-add opportunity (e.g. "ready to develop", "permitted for glamping", "6 cabins ready to rent"). |
| MISS | Confirmed no income possible — raw land with no operations described and no value-add path. |
| UNKNOWN | Zero income signal AND no operations described — but property is not confirmed raw land. |

---

## Tier Definitions

| Tier | Rule |
|------|------|
| **HOT** | All 6 criteria MATCH. No hard-drop exclusion. |
| **STRONG** | ≥5 MATCH, remaining UNKNOWN (zero MISS). No hard-drop exclusion. Also: Pending/Under Contract listings are capped at STRONG regardless of criteria. Also: listings "slightly out" on one price/acreage criterion that otherwise score all-MATCH qualify for STRONG. |
| **WATCH** | ≥4 MATCH and ≤1 MISS. No hard-drop exclusion. |
| **Drop** | Anything below WATCH — fewer than 4 MATCH, or 2+ MISS, or a hard-drop exclusion applies. Do not write to the ledger. |

---

## Tier Overrides (applied AFTER computing baseline tier)

### Waterfront + Cash-Flowing → minimum STRONG

If a listing is BOTH:
- **On the water** — direct frontage: riverfront, creek-front, lakefront, bayfront, oceanfront, or sound-front. "Near a lake" or "lake area" does NOT count; the listing must confirm the property itself touches water.
- **Cash-flowing day 1** — current operating revenue at close (gross revenue / NOI / occupancy / "established operating business"). Value-add, "recently operated", or "permitted to operate" do NOT count.

Then `tier = max(computed_tier, STRONG)`. The override applies even with price MISS or acreage MISS. Note the override explicitly in `score_breakdown.notes`.

Rationale: waterfront + immediate cash flow is the dominant value driver in the micro-resort buy box; promoting these to STRONG ensures they surface for review even when other criteria are uncertain.

---

*Last updated: 2026-05-24. Scoring rules are STABLE — thresholds belong here. Procedure lives in SKILL.md.*
