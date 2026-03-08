'use client';

import { useEffect, useState } from 'react';
import { fetchAPI } from '@/lib/api';

interface NewsItem {
    id: string;
    headline?: string;
    input_content: string;
    verdict: boolean;
    reasoning: string;
    claims: string[];
    user_email: string;
    created_at: string;
    upvotes: number;
    downvotes: number;
}

export default function NewsTicker({ onArticleClick }: { onArticleClick: (item: NewsItem) => void }) {
    const [headlines, setHeadlines] = useState<NewsItem[]>([]);

    useEffect(() => {
        fetchAPI('/api/top-headlines?limit=9')
            .then(setHeadlines)
            .catch(err => console.error('Failed to load headlines:', err));
    }, []);

    if (headlines.length === 0) return null;

    // Split headlines into 3 chunks for the 3 bands
    let chunk1: NewsItem[] = [], chunk2: NewsItem[] = [], chunk3: NewsItem[] = [];

    if (headlines.length >= 3) {
        chunk1 = headlines.slice(0, 3);
        chunk2 = headlines.slice(3, 6);
        chunk3 = headlines.slice(6, 9);
    } else {
        chunk1 = headlines;
        chunk2 = headlines;
        chunk3 = headlines;
    }

    // Fallback if chunks are empty but we have headlines
    if (chunk2.length === 0 && headlines.length > 0) chunk2 = headlines;
    if (chunk3.length === 0 && headlines.length > 0) chunk3 = headlines;

    const renderBand = (items: NewsItem[], direction: 'left' | 'right') => (
        <div className={`ticker-band ${direction}`}>
            {/* Repeat items multiple times to ensure seamless scrolling */}
            {[...items, ...items, ...items, ...items, ...items, ...items].map((item, i) => (
                <div
                    key={`${item.id}-${i}`}
                    className="ticker-item"
                    onClick={() => onArticleClick(item)}
                >
                    <span>🔥</span> {item.headline || item.input_content.substring(0, 50) + '...'}
                </div>
            ))}
        </div>
    );

    return (
        <div className="news-ticker-container">
            {renderBand(chunk1, 'right')}
            {renderBand(chunk2, 'left')}
            {renderBand(chunk3, 'right')}
        </div>
    );
}
