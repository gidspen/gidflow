# gidflow

Deal sourcing and market evaluation toolkit for micro resort, glamping, boutique hotel, and STR acquisitions.

## Skills

| Command | Purpose |
|---------|---------|
| `/micro-resort-market-research` | 6-gate market funnel — is this a good market to buy? |
| `/find-deals` | Search the web for on-market listings, score against your buy box (HOT / STRONG / WATCH) |
| `/gidflow-upgrade` | Pull the latest from this repo |

## Install

```bash
git clone git@github.com:gideonspencer/gidflow.git ~/.claude/skills/gidflow
cd ~/.claude/skills/gidflow && ./setup
```

## Upgrade

```bash
# Either run the skill:
/gidflow-upgrade

# Or manually:
cd ~/.claude/skills/gidflow && git pull
```

## How it works

Each skill is a `SKILL.md` file that Claude Code reads as instructions. The preamble in each skill loads session learnings (patterns discovered in prior runs) and checks for updates once per day.

To log a discovery during a run so it's available next time:
```bash
~/.claude/skills/gidflow/bin/gidflow-learnings-log '{"skill":"find-deals","key":"KEY","insight":"WHAT YOU LEARNED"}'
```

## Charter

See `skills-charter.md` for the 6 rules that govern all skills in this repo.
