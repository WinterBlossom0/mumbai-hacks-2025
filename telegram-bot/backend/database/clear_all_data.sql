-- Delete all data from tables (keeps table structure)

-- Delete all ratings first (due to foreign key constraint)
DELETE FROM ratings;

-- Delete all verifications
DELETE FROM verifications;

-- Delete all reddit posts
DELETE FROM reddit_posts;

-- Verify deletion
SELECT 'verifications' as table_name, COUNT(*) as remaining_rows FROM verifications
UNION ALL
SELECT 'ratings' as table_name, COUNT(*) as remaining_rows FROM ratings
UNION ALL
SELECT 'reddit_posts' as table_name, COUNT(*) as remaining_rows FROM reddit_posts;