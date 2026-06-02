# Source Catalog (product layer)

The detailed data sources behind the 6 gates in SKILL.md. Organized by the three data layers plus the layer-agnostic demand proxies. Each entry: cost, what it is for, how to use, what to look for. Prices and URLs change. This is the fast-changing product layer; keep the engine (SKILL.md) clean of it.

---

## Demand proxies (layer-agnostic, mostly free)

These exist in every market regardless of comp density. They are how you prove demand when STR and hotel comps are thin, which is the micro resort norm.

**Drive-time isochrone — Google Maps / TravelTime.com** [FREE]
- For: the drive-to catchment (Gate 1).
- How: drop the site, draw 90-minute and 2-hour rings, list every metro inside, pull populations.
- Look for: 1M+ metro within 90 min; growing metros compound demand.

**U.S. Census QuickFacts + BEA** [FREE]
- For: population growth, in-migration, median income, the retiree / second-home / relocation profile of the trade area.
- How: census.gov/quickfacts by county/MSA; BEA for regional income.
- Look for: metros growing faster than the national average; in-migration; second-home demand.

**NPS Visitor Spending Effects (VSE)** [FREE, government data]
- For: proven lodging demand near a national or state park (Gate 2). The most credible demand signal available.
- How: nps.gov/subjects/socialscience/vse.htm, interactive tool, select the nearest park, read the gateway-region lodging spend and year-over-year trend.
- Look for: large and growing lodging spend with thin premium supply. Note: total lodging, not glamping-specific, and not occupancy.

**County tourism authority (DMO) / occupancy-tax data** [FREE]
- For: the RIGHT-geography demand picture (Gate 2). Use this instead of the big-metro proxy.
- How: the county Tourism Development Authority site; occupancy / transient-tax collections are usually public record and show a multi-year trend.
- Look for: rising lodging-tax receipts; published visitor volume and spending for the actual county.

**Regional airport authority traffic** [FREE]
- For: a clean demand and access signal (Gate 1/2). Air access drives destination demand.
- How: the airport authority's enplanement / passenger reports, multi-year.
- Look for: rising passenger counts, new routes and carriers, recovery from any shock.

**Google Trends** [FREE]
- For: demand direction and seasonality (Gate 3).
- How: trends.google.com, search the destination + "glamping" / "cabin rental" as a Topic, 3 to 5 year window, target geography, Travel category. Read "Interest by subregion" and "Rising" related queries.
- Look for: rising multi-year line, a clear seasonal peak, and amenity demand in the rising queries. It is relative interest, not absolute volume.

**KOA North American Camping Report** [FREE]
- For: the macro category tailwind (Gate 3). The "why now" story, not site-specific.
- How: koa.com/north-american-camping-report.
- Look for: glamping share of camping, glamper daily spend, repeat intent, the millennial / higher-income skew.

---

## Micro resort / glamping layer (PRIMARY)

**Sage Outdoor Advisory free quarterly report** [FREE]
- For: glamping ADR benchmarks by state, unit type, amenity, and season (Gate 5). The only free glamping-specific rate dataset.
- How: download from sageoutdooradvisory.com (search "USA glamping market report"). Start from the state ADR, layer unit-type and amenity premiums.
- Look for: state ADR, domes vs treehouses vs cabins, amenity premiums (hot tub, pet-friendly), seasonal spread. No occupancy in the free report.

**Sage Outdoor Advisory feasibility study** [PAID, price on request, ~6 to 8 wk]
- For: lender-grade underwriting only (10-year pro forma, site/zoning analysis, dev cost). Commission only when spending over ~$2M on development or needing SBA/USDA documentation. Not a screening tool.

**Hipcamp + Glamping Hub** [FREE to search]
- For: supply density and live rates (Gate 4). The supply census.
- How: hipcamp.com and glampinghub.com, search the town, switch to map view, filter Glamping / Cabins / Unique stays, count properties within 15 to 20 miles, record unit types, rates, amenities, review counts.
- Look for: 0 to 5 in 15 mi = undersupplied; 6 to 15 = competitive but viable; 15+ = saturated. Review count and velocity is the free occupancy proxy (500+ reviews = books steadily).

---

## STR layer (SECONDARY)

**AirDNA** [FREEMIUM — Rentalizer free/limited, MarketMinder paid ~$20 to $100/mo by market size]
- For: occupancy, ADR, RevPAR for cabin / unique-stay comps (Gate 5).
- How: screen free with Rentalizer (haircut the estimate ~35% for a new rural listing). In MarketMinder, set property-type filters (Unique → Cabin / Glamping) BEFORE reading anything, check the comp count, read Occupancy / ADR / Seasonality at the 25th and 50th percentile, and build a hand-picked custom comp set.
- Caveat: accuracy degrades 15 to 30 percent below ~20 comps. Use the thin-comp playbook. Seasonality shape is more reliable than the absolute number in thin markets.

**AirROI, Airbtics, Rabbu** [FREE public report pages]
- For: directional occupancy / ADR / RevPAR by market without a subscription.
- How: their free market report pages for the town and county.
- Look for: a cross-check on AirDNA. Treat as directional, name the source.

**Key Data** [PAID]
- For: booking-pace and forward-looking demand in thin markets; used by some DMOs.

---

## Hotel layer (CEILING / sanity check only)

**CoStar** [PAID — the USER has access]
- For: branded + independent hotel occupancy, ADR, RevPAR, and the new-supply pipeline for the submarket (Gate 5). The single most important hotel input for a property with real hotel keys, and the best read on competing supply coming online.
- How: the user pulls the submarket comp set and pipeline and pastes the numbers. Do NOT scrape inferior hotel data to substitute. Prompt for it.
- Look for: submarket occupancy / ADR / RevPAR trend, and the rooms pipeline (new supply erodes rate). This is the ceiling for the hotel-room block; do not deep-dive beyond that, this skill is micro-resort-primary.

**STR (Smith Travel Research) / HVS** [PAID / mixed]
- For: hotel performance benchmarks and lodging market commentary; HVS publishes some free regional reports and the annual valuation index.
- How: use published HVS market commentary for context; STR data usually arrives via CoStar or news citing it.

---

## Benchmarks to anchor on (verify current)

- National glamping ADR roughly $146 to $160; by unit type domes ~$257, treehouses ~$217, cabins ~$160 (Sage). Premium / design-forward unique stays clear $300+.
- Glamping breakeven occupancy ~25 to 40 percent, versus ~55 to 65 percent for a hotel. This is why thinner rural markets still pencil for a micro resort.
- Well-run outdoor-hospitality NOI margin ~40 to 60 percent (lower once a full restaurant is in the mix).
- "1M+ metro within 90 minutes" recurs across Sage's 350+ projects as the dominant catchment filter.

---

## Green flags

- 1M+ metro within 90 min, growing.
- National or state park within 30 to 60 mi with quantifiable NPS lodging spend.
- Existing tourism infrastructure at any tier (wine trail, Main Street, festivals, college town).
- Rising 3-year Trends for the destination with no supply response.
- Agritourism layer available (vineyard / farm); these book well above average.
- Institutional operator nearby (Under Canvas, AutoCamp); they did the feasibility work.
- Scattered well-reviewed unique stays already booking above the national ADR.

## Red flags

- Over 3 to 4 hr to the nearest metro with no anchor.
- Under 500k within 2 hr.
- No tourism infrastructure at any price tier.
- Flat or declining 3-year Trends.
- Season shorter than 4 to 5 months with no shoulder story.
- "The land is cheap" (often because it cannot be developed).
- Water / septic caps unit count below ~4 to 6.
- Zoning ambiguity between RV park, campground, and transient lodging.

## Excluded

- **PriceLabs / Wheelhouse:** dynamic pricing and operations tools for properties you already own. Not market-evaluation tools. Do not use them in this skill.
