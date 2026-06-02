-- Deal Partner / find-deals — 4-table schema
-- searches: one row per run.
-- listings: one row per unique URL — universal facts about the listing.
-- search_listings: per-search verdict (score + tier) on (search, listing).
-- properties: cross-source entity, populated by the deferred match cron job.

create extension if not exists "pgcrypto";

create table if not exists properties (
  id uuid primary key default gen_random_uuid(),
  canonical_address text,
  created_at timestamptz not null default now()
);

create table if not exists searches (
  id uuid primary key default gen_random_uuid(),
  user_email text,
  buy_box jsonb not null,
  status text not null default 'running' check (status in ('running','complete','failed')),
  started_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists listings (
  id uuid primary key default gen_random_uuid(),
  url text unique not null,
  title text,
  price numeric,
  acreage numeric,
  address text,
  location text,
  source text,
  property_type text,
  description text,
  image_url text,
  first_seen_at timestamptz not null default now(),
  last_verified_at timestamptz not null default now(),
  status text not null default 'active' check (status in ('active','sold','pending','stale','unknown')),
  property_id uuid references properties(id)
);

create table if not exists search_listings (
  id uuid primary key default gen_random_uuid(),
  search_id uuid not null references searches(id) on delete cascade,
  listing_id uuid not null references listings(id) on delete cascade,
  tier text check (tier in ('hot','strong','watch')),
  location_match text check (location_match in ('match','miss','unknown')),
  price_match text check (price_match in ('match','miss','unknown')),
  acreage_match text check (acreage_match in ('match','miss','unknown')),
  type_match text check (type_match in ('match','miss','unknown')),
  structure_match text check (structure_match in ('match','miss','unknown')),
  revenue_match text check (revenue_match in ('match','miss','unknown')),
  scored_at timestamptz not null default now(),
  unique(search_id, listing_id)
);

create index if not exists listings_property_idx on listings(property_id);
create index if not exists search_listings_search_idx on search_listings(search_id);
create index if not exists search_listings_listing_idx on search_listings(listing_id);
create index if not exists search_listings_tier_idx on search_listings(tier);
