-- Create a table for storing A/B test history
create table if not exists ab_test_history (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id),
  test_name text,
  a_successes integer,
  a_total integer,
  b_successes integer,
  b_total integer,
  a_conversion_rate numeric,
  b_conversion_rate numeric,
  mean_uplift numeric,
  ci_lower numeric,
  ci_upper numeric,
  ci_width numeric,
  prob_b_better numeric,
  expected_loss numeric,
  n_simulations integer,
  alpha_prior numeric,
  beta_prior numeric,
  target_width numeric,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Create an index on user_id for faster queries
create index if not exists idx_ab_test_history_user_id on ab_test_history (user_id);

-- Create a function to update the updated_at column
create or replace function update_updated_at_column()
returns trigger as $$
begin
   NEW.updated_at = now(); 
   return NEW; 
end;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
create trigger update_ab_test_history_updated_at 
  before update on ab_test_history 
  for each row 
  execute procedure update_updated_at_column();

-- Enable Row Level Security (RLS)
alter table ab_test_history enable row level security;

-- Create policies for RLS
create policy "Users can view their own test history"
  on ab_test_history for select
  using ( auth.uid() = user_id );

create policy "Users can insert their own test history"
  on ab_test_history for insert
  using ( auth.uid() = user_id );

create policy "Users can update their own test history"
  on ab_test_history for update
  using ( auth.uid() = user_id );

create policy "Users can delete their own test history"
  on ab_test_history for delete
  using ( auth.uid() = user_id );

-- Create a view for simplified access to test history data
create or replace view user_test_history as
  select 
    id,
    test_name,
    a_successes,
    a_total,
    b_successes,
    b_total,
    a_conversion_rate,
    b_conversion_rate,
    mean_uplift,
    ci_lower,
    ci_upper,
    ci_width,
    prob_b_better,
    expected_loss,
    n_simulations,
    alpha_prior,
    beta_prior,
    target_width,
    created_at
  from ab_test_history
  where user_id = auth.uid()
  order by created_at desc;