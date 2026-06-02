# Persistence — Engineering Wiring

Product-layer mechanics. Not procedure — see SKILL.md for the engine.

---

## Schema Overview

Four tables. See `schema.sql` for the SQL.

| Table | Purpose |
|-------|---------|
| `searches` | One row per run. Holds `buy_box` (jsonb), `status`, `started_at`, `completed_at`. |
| `listings` | One row per unique URL. Universal facts about a listing — price, acreage, address, type, description, image. Re-found listings update `last_verified_at` rather than duplicating (upsert on `url`). |
| `search_listings` | Per-search verdict. Links a search to a listing; carries the tier and per-criterion match values as flat enum columns. No JSON blobs. |
| `properties` | Cross-source entity (cron-populated, empty for now). A deferred cron job groups listings into canonical properties by normalized address. |

---

## Per-Set Write

At each LOOP 2 set boundary, the engine hands its passing deals to this layer. **One Supabase call per set — never per deal.**

Steps:
1. Upsert `listings` rows ON CONFLICT (`url`). Re-found listings update `last_verified_at`, `price`, `status`, and any fields that may have changed.
2. Insert `search_listings` rows for this run's verdict (tier + per-criterion match columns).

All rows in a set go in a single batch request.

---

## Cursor

After each set, save to `~/.claude/skills/find-deals/.cursor`:

```json
{"search_id": "...", "keyword_index": 2, "source_index": 1, "set_index": 4}
```

On run start: if a cursor file exists for the current `search_id`, resume the nested loop from those indices. Otherwise start at keyword 0.

---

## Local-File Fallback

On any Supabase write failure (non-2xx response):
1. Append the set's intended rows as JSONL to `~/.claude/skills/find-deals/pending-writes.jsonl`.
2. The run continues — do not halt.

On next run start, **before resuming the loop**, flush `pending-writes.jsonl` to Supabase. Append-only. No retry logic. No schema massaging. If the flush also fails, leave the file in place and proceed.

---

## Env Vars

| Variable | Required | Purpose |
|----------|----------|---------|
| `SUPABASE_DEALS_URL` | Yes | Project URL |
| `SUPABASE_DEALS_SERVICE_KEY` | Yes | Writes — service role key. Never fall back to anon key for writes. |
| `SUPABASE_DEALS_ANON_KEY` | No | Reads only |

Project: `incredible-ai-deals`.

---

## Notification (Stage 7)

The product layer subscribes to `searches.status` changes. The skill only sets `status = 'complete'` on the `searches` row when LOOP 4 ends. Notification logic lives in the product layer — not in this skill.
