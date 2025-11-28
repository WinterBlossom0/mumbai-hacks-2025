-- Create reddit_posts table
CREATE TABLE IF NOT EXISTS reddit_posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    reddit_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    body TEXT,
    url TEXT,
    scraped_content TEXT,
    headline TEXT,
    verdict BOOLEAN,
    reasoning TEXT,
    claims JSONB DEFAULT '[]'::jsonb,
    sources JSONB DEFAULT '{}'::jsonb,
    author TEXT,
    subreddit TEXT DEFAULT 'eyeoftruth',
    is_removed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on reddit_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_reddit_posts_reddit_id ON reddit_posts(reddit_id);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_reddit_posts_created_at ON reddit_posts(created_at DESC);

-- Disable RLS for simplicity
ALTER TABLE reddit_posts DISABLE ROW LEVEL SECURITY;
