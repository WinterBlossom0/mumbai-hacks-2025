-- Create verifications table in Supabase
-- Run this SQL in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS verifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL,
    user_email TEXT NOT NULL,
    input_content TEXT NOT NULL,
    input_type TEXT NOT NULL CHECK (input_type IN ('text', 'url')),
    verdict BOOLEAN NOT NULL,
    reasoning TEXT NOT NULL,
    claims JSONB NOT NULL DEFAULT '[]'::jsonb,
    sources JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_verifications_user_id ON verifications(user_id);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_verifications_created_at ON verifications(created_at DESC);

-- Create index on user_email for future Clerk integration
CREATE INDEX IF NOT EXISTS idx_verifications_user_email ON verifications(user_email);

-- Create index on is_public for public feed queries
CREATE INDEX IF NOT EXISTS idx_verifications_is_public ON verifications(is_public, created_at DESC);

-- DISABLE Row Level Security (RLS) for hackathon simplicity
-- Since backend uses the anon key but handles auth via Clerk, 
-- we trust the backend to manage data access.
ALTER TABLE verifications DISABLE ROW LEVEL SECURITY;

-- If you prefer to keep RLS enabled, you would need to use the Service Role Key in the backend.
-- For now, disabling it is the fastest way to get everything working.
