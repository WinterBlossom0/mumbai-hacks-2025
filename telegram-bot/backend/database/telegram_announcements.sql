CREATE TABLE telegram_announcements (
    id UUID PRIMARY KEY,
    source_type TEXT CHECK (source_type IN ('verification', 'reddit_post')),
    source_id UUID NOT NULL,
    channel_id TEXT NOT NULL,
    message_id BIGINT,
    announcement_status TEXT CHECK (announcement_status IN ('pending', 'sent', 'failed')),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE,
    announced_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(source_type, source_id, channel_id)
);