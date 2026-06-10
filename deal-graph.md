# Deal Graph — node register

*Last updated: 2026-06-10*

How a deal computes itself. Each **fact (node)** has exactly one owner skill, a
list of input nodes, and a type. The deal stays current because changing a node
makes everything downstream stale, and the owner skill of each stale node reruns.

This file is the **dependency map**. The skills and dealhound-pro both read it.
It grows one node at a time as skills get built — never add a node for a skill
that doesn't exist yet.

---

## The 3 invariants

1. **One node, one owner skill.** Only that skill writes the node. Nothing else.
2. **Status is derived, never stored.** A node is *active/stale* when its inputs
   changed since it last computed, or it has open tasks. Otherwise it's *complete*.
   You never set a status — you read it.
3. **The graph is a DAG.** A node's inputs may never point back upstream. No cycles.

Cascade rule: rerun an owner skill only when an input *materially* changed (the
value actually differs). Every material change gets one log line the owner reads.

---

## Node format

Every node declares exactly four things:

- **id** — snake_case fact name
- **owner** — the one skill that writes it (or `raw` for a human/external leaf)
- **inputs** — the node ids it reads (`—` if none)
- **type** — `raw` (set by human/external) or `derived` (computed by a skill)

**A skill is not done until its node is registered here.** Owner, inputs, type —
all three. That is what keeps the dependency map current as we build.

---

## Register

| node | owner skill | inputs | type | maturity |
|------|-------------|--------|------|----------|
| `location` | raw (human) | — | raw | n/a |
| `buy_box` | raw (human) | — | raw | n/a |
| `market_score` | micro-resort-market-research | location | derived | forming |
| `listing` | find-deals | location, buy_box | derived | forming |

*Two owned nodes today, because two skills exist. `location` and `buy_box` are
raw leaves they read. As underwriting, offer, finance, raise, and diligence
skills get built, each adds its node here on the day it ships.*

---

## Promotion: skill-enforced → app-enforced

A node starts **skill-enforced** (convention, fast to change) and graduates to
**app-enforced** (DB constraints, the paywall, the change log) only when its
shape stops moving. Maturity column tracks the journey:

- **forming** — inputs/owner/output still changing as the skill is built. Stays
  skill-enforced. Do *not* put it in the DB yet.
- **stable** — ran across ~3 real deals with **no change to its inputs row** here.
  Candidate for promotion.
- **promoted** — enforced in dealhound: one-writer constraint, subscription gate,
  writes logged to the `deal_stage_transitions`-style log.

**Promotion trigger:** a node flips `forming → stable`. That's the signal, not a
calendar date. Review promotions when the register has stable nodes waiting —
not on a fixed schedule while there are only a couple of nodes.
