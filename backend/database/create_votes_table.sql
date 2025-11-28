-- Create votes table to track user votes
CREATE TABLE IF NOT EXISTS votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    vote_type INTEGER NOT NULL CHECK (vote_type IN (1, -1)),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(verification_id, user_id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_votes_verification_id ON votes(verification_id);
CREATE INDEX IF NOT EXISTS idx_votes_user_id ON votes(user_id);
