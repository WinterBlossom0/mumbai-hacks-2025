-- Add headline column to reddit_posts table (run this if table already exists)
ALTER TABLE reddit_posts ADD COLUMN IF NOT EXISTS headline TEXT;
