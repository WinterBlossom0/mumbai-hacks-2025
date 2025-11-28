-- Create ratings table
CREATE TABLE IF NOT EXISTS ratings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    verification_id UUID REFERENCES verifications(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL, -- Clerk User ID
    vote_type INTEGER NOT NULL CHECK (vote_type IN (1, -1)), -- 1 for upvote, -1 for downvote
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(verification_id, user_id) -- One vote per user per post
);

-- Add counters to verifications table
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS upvotes INTEGER DEFAULT 0;
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS downvotes INTEGER DEFAULT 0;

-- Disable RLS for ratings (as requested for simplicity)
ALTER TABLE ratings DISABLE ROW LEVEL SECURITY;

-- Add headline column to verifications
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS headline TEXT;
