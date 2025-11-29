-- Add author column to community_archives
ALTER TABLE community_archives 
ADD COLUMN IF NOT EXISTS author TEXT;
