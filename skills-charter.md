# Skills Charter

*Last updated: 2026-05-22*

---

## Why this exists

The find-deals skill bloated to 7,000+ lines of Python, scrapers, evals, and spec docs — and still produced 400 errors on Supabase writes. The rebuild gutted it to a model-driven loop in under 300 lines of SKILL.md. These rules kept it lean. Future skills follow them.

---

## The 6 Rules

**1. Every skill declares a size ceiling BEFORE the first line is written.**
For example: `SKILL.md ≤ 300 lines`. The ceiling is the brake. Without it, scope creep is invisible until it's irreversible.

**2. New machinery defaults to NO. Argue it in.**
What comes off the plate to pay for it? A new tool, a new table, a new integration — all require displacement. If nothing comes off, it doesn't go in.

**3. Engine and product layer in SEPARATE files.**
`SKILL.md` is the engine — the procedure the model executes. Persistence wiring, dashboard glue, and notification logic live in their own file. They never fuse. Fused files become untestable and untouchable.

**4. "It works" means STOP. Ship it. Use it.**
Features only get added from real observed pain, never from brainstorms. If the loop runs and produces ranked listings, that's done. Resist the pull toward completeness.

**5. Sick skills get REWRITTEN, not patched.**
A clean rewrite beats untangling. Budget for it. Patch cycles compound debt; rewrites reset the clock. The find-deals rebuild took one session. The prior patch cycle took weeks and made things worse.

**6. Every improvement asks: machinery or knowledge?**
Knowledge (data files — sources, thresholds, scoring rules) lands freely. Machinery (new code, new tables, new integrations) has to fight in under Rule 2. When the answer is "add a row to sources.md," that's free. When the answer is "add a new Python module," that's not.

---

## Docs Discipline

- Document only the slow-changing layer — loop structure, data model, principles. Never thresholds or source lists (those go in data files where they can be updated without touching code).
- `SKILL.md` governs. HTML explainers in `docs/architecture/` are views. If they disagree, the skill is right and the HTML gets re-rendered.
- Date every doc. Plain folder of self-contained HTMLs — no framework, no build step.

---

*To make this bite, reference it from `~/.claude/CLAUDE.md`.*
