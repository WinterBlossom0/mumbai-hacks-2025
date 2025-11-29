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
    sources?: Record<string, string[]>;
    user_email: string;
    created_at: string;
    upvotes: number;
    downvotes: number;
    category?: string;
    image_url?: string;
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

    const colors = [
        'bg-cyan-500 shadow-cyan-500/50',
        'bg-purple-500 shadow-purple-500/50',
        'bg-rose-500 shadow-rose-500/50',
        'bg-amber-500 shadow-amber-500/50',
        'bg-emerald-500 shadow-emerald-500/50',
    ];

    const renderBand = (items: NewsItem[], direction: 'left' | 'right') => (
        <div className={`ticker-band ${direction}`}>
            {/* Repeat items multiple times to ensure seamless scrolling */}
            {[...items, ...items, ...items, ...items, ...items, ...items].map((item, i) => {
                const colorClass = colors[i % colors.length];
                return (
                    <div
                        key={`${item.id}-${i}`}
                        className="ticker-item"
                        onClick={() => onArticleClick(item)}
                    >
                        <span className={`w-3 h-3 rounded-full mr-4 shrink-0 shadow-[0_0_15px] ${colorClass}`} />
                        {item.headline || item.input_content.substring(0, 50) + '...'}
                    </div>
                );
            })}
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
