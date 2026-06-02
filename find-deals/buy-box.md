# Buy Box — Defaults

> **These are DEFAULTS. A user's per-run buy box overrides via Stage 1 of SKILL.md.**

---

## Hard Filters

```
PRICE_MIN: 300000
PRICE_MAX: 3000000
MIN_ACREAGE: 1.0
STR_MARKET_REQUIRED: true
```

**Allowed property types** (at least one must match):
- micro resort
- glamping / glamping resort
- boutique hotel
- cabin resort / cabin rental
- bed and breakfast / inn
- lodge
- STR-capable residential (vacation rental)
- vacation property with land

---

## STR Market Signal Rules

**Signal YES** (property is in an STR-viable market):
- Lakefront
- Mountain
- Coastal
- Destination market
- Near national park
- Wine country / hill country signal

**Signal NO** (fails STR market filter):
- Urban
- STR-restricted jurisdiction

---

## Strategy Tiers

**Primary:** Micro resort / glamping — acreage + rural + STR-ready.

**Secondary:** Boutique hotel acquisition — operating or value-add, 5–30 keys.

**Tertiary:** STR-capable residential in proven vacation markets.

---

## Runtime Override

If `$DEALHOUND_BUY_BOX_FILE` is set (path to a JSON file), the skill reads the buy
box from that file instead of these defaults. The JSON matches the `searches.buy_box`
shape in Supabase:

```json
{
  "locations": ["Texas"],
  "price_min": 300000,
  "price_max": 3000000,
  "min_acreage": 1.0,
  "str_market_required": true,
  "property_types": ["micro_resort", "glamping"],
  "revenue_requirement": "value_add_ok",
  "exclusions": []
}
```
