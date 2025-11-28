-- Add category column to verifications table
-- Run this SQL in your Supabase SQL Editor

-- Add category column (nullable initially for existing records)
ALTER TABLE verifications 
ADD COLUMN IF NOT EXISTS category TEXT;

-- Create index on category for filtering queries
CREATE INDEX IF NOT EXISTS idx_verifications_category ON verifications(category);

-- Optional: Add a check constraint if you want to limit categories to specific values
-- Uncomment and modify the line below if you want to enforce specific categories
-- ALTER TABLE verifications 
-- ADD CONSTRAINT check_category CHECK (category IN ('politics', 'health', 'science', 'technology', 'business', 'entertainment', 'sports', 'other'));

-- Update trigger to ensure updated_at is maintained
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger if it doesn't exist
DROP TRIGGER IF EXISTS update_verifications_updated_at ON verifications;
CREATE TRIGGER update_verifications_updated_at
    BEFORE UPDATE ON verifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
