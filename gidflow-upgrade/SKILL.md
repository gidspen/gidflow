---
name: gidflow-upgrade
asset_classes: all
description: Pull the latest gidflow from the remote repo and report what changed. Use when UPGRADE_AVAILABLE appears in a preamble, or when the user asks to update or upgrade gidflow.
allowed-tools:
  - Bash
  - Read
---

# gidflow-upgrade

Pulls the latest from the remote repo, reports what changed, and confirms the installed version.

## Step 1: Check current state

```bash
_GIDFLOW_DIR="${GIDFLOW_DIR:-$HOME/.claude/skills/gidflow}"
cd "$_GIDFLOW_DIR" || { echo "ERROR: gidflow not found at $_GIDFLOW_DIR"; exit 1; }
git status --short
git log --oneline -1
echo "LOCAL_VERSION: $(cat VERSION 2>/dev/null || echo unknown)"
```

## Step 2: Pull

```bash
_GIDFLOW_DIR="${GIDFLOW_DIR:-$HOME/.claude/skills/gidflow}"
cd "$_GIDFLOW_DIR"
git pull origin main 2>&1
echo "UPDATED_VERSION: $(cat VERSION 2>/dev/null || echo unknown)"
```

If the pull reports "Already up to date." — tell the user gidflow is already current and stop.

If the pull succeeds with new commits:

## Step 3: Report what changed

```bash
_GIDFLOW_DIR="${GIDFLOW_DIR:-$HOME/.claude/skills/gidflow}"
cd "$_GIDFLOW_DIR"
git log --oneline ORIG_HEAD..HEAD 2>/dev/null | head -10
```

Read `CHANGELOG.md` and show the top entry (the newest version block). That's what just landed.

Tell the user: "gidflow updated to v{VERSION}. {one-line summary of what changed}."

## Step 4: Refresh the update-check timestamp

```bash
_GIDFLOW_HOME="${GIDFLOW_HOME:-$HOME/.gidflow}"
date +%s > "$_GIDFLOW_HOME/.last-update-check"
```
