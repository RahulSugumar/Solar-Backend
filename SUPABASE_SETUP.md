# Supabase Configuration Guide

Since we are using **Supabase** as our database, you need to execute the following SQL to set up the Tables and Enums.

## 1. Get Credentials
Go to your Supabase Project Settings -> API.
Copy these two values and create a `.env` file in the `backend/` folder (I will create a template for you):
- `SUPABASE_URL`
- `SUPABASE_KEY` (use the `service_role` key since our API handles permissions, OR `anon` key if using client-side auth - for this API-centric approach, `service_role` is often easier for admin tasks, but `anon` is safer. Let's use `service_role` for the backend to bypass RLS for now, or `anon` if we act as the user. **Recommendation:** Use `service_role` specifically for the Admin Backend to manage everything).

## 2. Run SQL Schema
Go to **SQL Editor** in Supabase and run this script:

```sql
-- 1. Enum for User Roles
create type user_role as enum ('land_owner', 'investor', 'admin');

-- 2. Enum for Land Status
create type land_status as enum ('available', 'reserved', 'active');

-- 3. Users Table (Extends Supabase Auth or Standalone)
-- Note: If using Supabase Auth, we usually link to auth.users. 
-- For simplicity in this Custom API, we will store user details here.
create table public.users (
  id uuid default gen_random_uuid() primary key,
  email text unique not null,
  full_name text not null,
  role user_role not null default 'investor',
  phone text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. Lands Table
create table public.lands (
  id uuid default gen_random_uuid() primary key,
  owner_id uuid references public.users(id) not null,
  title text not null,
  location text not null,
  area_sqft numeric not null,
  total_price numeric not null,
  status land_status default 'available',
  description text,
  image_url text, -- simplified for now
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 5. Investments / Reservations
create table public.investments (
  id uuid default gen_random_uuid() primary key,
  land_id uuid references public.lands(id) not null,
  investor_id uuid references public.users(id) not null,
  amount numeric not null,
  status text default 'pending', -- 'pending', 'completed', 'cancelled'
  transaction_date timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 6. Enable RLS (Optional if using only Backend API with Service Key)
alter table public.users enable row level security;
alter table public.lands enable row level security;
alter table public.investments enable row level security;

-- 7. Simple Policy (Allow All for now, since Backend handles logic)
create policy "Enable all access for service role" on public.users for all using (true);
create policy "Enable all access for service role" on public.lands for all using (true);
create policy "Enable all access for service role" on public.investments for all using (true);

-- 8. UPDATE: Add Missing Columns for Phase 1b (Run this if you already created tables)
alter table public.lands add column if not exists land_type text;
alter table public.lands add column if not exists ownership_info text;
alter table public.lands add column if not exists potential_capacity_kw numeric default 0.0;
alter table public.lands add column if not exists owner_fixed_payout numeric default 0.0;
alter table public.lands add column if not exists owner_fixed_payout numeric default 0.0;
alter table public.lands add column if not exists owner_revenue_share_percent numeric default 0.0;

-- 9. UPDATE: Add 'pending_approval' to land_status Enum (Fix for 500 Error)
ALTER TYPE land_status ADD VALUE IF NOT EXISTS 'pending_approval';
ALTER TYPE land_status ADD VALUE IF NOT EXISTS 'released';
```

After running this, your database is ready!
