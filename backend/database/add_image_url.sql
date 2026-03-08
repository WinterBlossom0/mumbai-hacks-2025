-- Add image_url column to verifications table
ALTER TABLE verifications ADD COLUMN IF NOT EXISTS image_url TEXT;

-- Optional: Add an index if you plan to query by image_url often (though unlikely)
-- CREATE INDEX idx_verifications_image_url ON verifications(image_url);
