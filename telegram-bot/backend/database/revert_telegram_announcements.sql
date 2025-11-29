-- Revert Telegram Announcement Changes
-- This script removes the announced_at column from verifications and reddit_posts tables
-- Run this SQL in your Supabase SQL Editor

-- ============================================================================
-- PART 1: Remove announced_at from verifications table
-- ============================================================================

-- Drop indexes related to announced_at on verifications table
DROP INDEX IF EXISTS idx_verifications_announced_at;
DROP INDEX IF EXISTS idx_verifications_unannounced_fake;

-- Remove the announced_at column from verifications table
ALTER TABLE verifications DROP COLUMN IF EXISTS announced_at;

-- ============================================================================
-- PART 2: Remove announced_at from reddit_posts table
-- ============================================================================

-- Drop indexes related to announced_at on reddit_posts table
DROP INDEX IF EXISTS idx_reddit_posts_announced_at;
DROP INDEX IF EXISTS idx_reddit_posts_unannounced_fake;

-- Remove the announced_at column from reddit_posts table
ALTER TABLE reddit_posts DROP COLUMN IF EXISTS announced_at;

-- ============================================================================
-- PART 3: Create new telegram_announcements table
-- ============================================================================

-- Create a dedicated table for tracking Telegram announcements
CREATE TABLE IF NOT EXISTS telegram_announcements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Reference to the source (verification or reddit_post)
    source_type TEXT NOT NULL CHECK (source_type IN ('verification', 'reddit_post')),
    source_id UUID NOT NULL,
    
    -- Announcement details
    channel_id TEXT NOT NULL,
    message_id BIGINT,  -- Telegram message ID (if available)
    announcement_status TEXT NOT NULL DEFAULT 'pending' CHECK (announcement_status IN ('pending', 'sent', 'failed')),
    
    -- Error tracking
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    announced_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure we don't announce the same item twice to the same channel
    UNIQUE(source_type, source_id, channel_id)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_telegram_announcements_source 
ON telegram_announcements(source_type, source_id);

CREATE INDEX IF NOT EXISTS idx_telegram_announcements_status 
ON telegram_announcements(announcement_status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_telegram_announcements_channel 
ON telegram_announcements(channel_id, announced_at DESC);

-- Create composite index for finding pending announcements
CREATE INDEX IF NOT EXISTS idx_telegram_announcements_pending 
ON telegram_announcements(announcement_status, created_at ASC) 
WHERE announcement_status = 'pending';

-- Add comments for documentation
COMMENT ON TABLE telegram_announcements IS 'Tracks Telegram channel announcements for verifications and Reddit posts';
COMMENT ON COLUMN telegram_announcements.source_type IS 'Type of source: verification or reddit_post';
COMMENT ON COLUMN telegram_announcements.source_id IS 'UUID of the verification or reddit_post record';
COMMENT ON COLUMN telegram_announcements.channel_id IS 'Telegram channel ID where announcement was/will be sent';
COMMENT ON COLUMN telegram_announcements.message_id IS 'Telegram message ID (if successfully sent)';
COMMENT ON COLUMN telegram_announcements.announcement_status IS 'Status: pending, sent, or failed';
COMMENT ON COLUMN telegram_announcements.announced_at IS 'Timestamp when successfully announced';

-- Disable RLS for simplicity (matching the pattern of other tables)
ALTER TABLE telegram_announcements DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify the changes
DO $$
BEGIN
    -- Check if announced_at was removed from verifications
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'verifications' 
        AND column_name = 'announced_at'
    ) THEN
        RAISE NOTICE 'WARNING: announced_at column still exists in verifications table';
    ELSE
        RAISE NOTICE 'SUCCESS: announced_at column removed from verifications table';
    END IF;
    
    -- Check if announced_at was removed from reddit_posts
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'reddit_posts' 
        AND column_name = 'announced_at'
    ) THEN
        RAISE NOTICE 'WARNING: announced_at column still exists in reddit_posts table';
    ELSE
        RAISE NOTICE 'SUCCESS: announced_at column removed from reddit_posts table';
    END IF;
    
    -- Check if telegram_announcements table was created
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'telegram_announcements'
    ) THEN
        RAISE NOTICE 'SUCCESS: telegram_announcements table created';
    ELSE
        RAISE NOTICE 'WARNING: telegram_announcements table not found';
    END IF;
END $$;
