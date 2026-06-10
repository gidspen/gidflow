---
name: gidflow
description: Deal sourcing and market evaluation toolkit for micro resort, glamping, boutique hotel, and STR acquisitions. Entry point — routes to sub-skills. Use when the user asks what gidflow can do, needs help choosing a skill, or runs /gidflow with no sub-command.
allowed-tools:
  - Bash
  - Read
---

# gidflow — Deal Partner Toolkit

Two skills for hospitality real estate investors:

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/micro-resort-market-research` | 6-gate market funnel — evaluates whether a location is strong enough to buy a micro resort or boutique hotel | Before underwriting any deal. Market first. |
| `/find-deals` | Searches the open web for on-market listings, scores them against a buy box (HOT / STRONG / WATCH), and writes them to the ledger | When actively sourcing deals |
| `/gidflow-upgrade` | Pulls latest from the remote repo and reports what changed | When UPGRADE_AVAILABLE appears in a preamble |

## When to invoke which skill

- "Is [location] a good market for a micro resort?" → `/micro-resort-market-research`
- "Find micro resort deals in [location/state]" → `/find-deals`
- "What micro resort deals have you found?" → `/find-deals` (check the ledger)
- "Update / upgrade gidflow" → `/gidflow-upgrade`
