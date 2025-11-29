-- Create table for community archived posts
CREATE TABLE IF NOT EXISTS community_archives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reddit_id TEXT NOT NULL UNIQUE,
    title TEXT,
    body TEXT,
    subreddit TEXT NOT NULL,
    verdict BOOLEAN,
    reasoning TEXT,
    claims JSONB,
    sources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_url TEXT
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_community_archives_subreddit ON community_archives(subreddit);
CREATE INDEX IF NOT EXISTS idx_community_archives_created_at ON community_archives(created_at DESC);
