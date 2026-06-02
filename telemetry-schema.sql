-- gidflow telemetry — add to the incredible-ai-deals Supabase project
-- Apply once: paste into the SQL editor in Supabase dashboard

create table if not exists skill_events (
  id uuid primary key default gen_random_uuid(),
  skill text not null,
  version text,
  outcome text check (outcome in ('success','error','abort','unknown')),
  duration_s integer,
  ts timestamptz not null default now(),
  device_hash text,   -- anonymous stable device identifier (md5 of local uuid)
  user_id text        -- optional user label, set by the user themselves
);

-- RLS: anyone can insert (anon key), only service role can read
alter table skill_events enable row level security;

create policy "anon_insert_skill_events"
  on skill_events for insert
  to anon
  with check (true);

-- Service role bypasses RLS by default, so no read policy needed.
-- Query your telemetry from the Supabase dashboard or via service key:
--   select skill, outcome, count(*), avg(duration_s)
--   from skill_events
--   group by skill, outcome
--   order by count desc;

create index if not exists skill_events_skill_idx on skill_events(skill);
create index if not exists skill_events_ts_idx on skill_events(ts desc);
