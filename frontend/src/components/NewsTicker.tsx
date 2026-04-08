'use client';

import { useEffect, useRef, useState } from 'react';
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

const FONT = '900 1.5rem/1 "Inter", sans-serif';
const LETTER_SPACING = 2;

function GlassTickerItem({ text, colorClass, onClick }: { text: string; colorClass: string; onClick: () => void }) {
    const glassLayerRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [itemWidth, setItemWidth] = useState(0);

    useEffect(() => {
        const container = containerRef.current;
        const glassLayer = glassLayerRef.current;
        if (!container || !glassLayer) return;

        const h = container.offsetHeight || 40;
        const dpr = window.devicePixelRatio || 1;

        // Measure text width
        const measureCanvas = document.createElement('canvas');
        const mctx = measureCanvas.getContext('2d')!;
        mctx.font = FONT;
        (mctx as any).letterSpacing = `${LETTER_SPACING}px`;
        const dotW = 24;
        const measured = mctx.measureText(text.toUpperCase());
        const w = Math.ceil(measured.width) + dotW + 40;

        setItemWidth(w);

        // Draw text mask
        const canvas = document.createElement('canvas');
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        const ctx = canvas.getContext('2d')!;
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, w, h);
        ctx.font = FONT;
        (ctx as any).letterSpacing = `${LETTER_SPACING}px`;
        ctx.fillStyle = '#ffffff';
        ctx.textBaseline = 'middle';
        ctx.fillText(text.toUpperCase(), dotW + 8, h / 2);

        const dataUrl = canvas.toDataURL();
        glassLayer.style.webkitMaskImage = `url(${dataUrl})`;
        (glassLayer.style as any).maskImage = `url(${dataUrl})`;
        glassLayer.style.webkitMaskSize = `${w}px ${h}px`;
        (glassLayer.style as any).maskSize = `${w}px ${h}px`;
        glassLayer.style.webkitMaskRepeat = 'no-repeat';
        (glassLayer.style as any).maskRepeat = 'no-repeat';
    }, [text]);

    return (
        <div
            ref={containerRef}
            className="ticker-item-glass"
            style={itemWidth ? { width: itemWidth } : undefined}
            onClick={onClick}
        >
            {/* Coloured dot bullet */}
            <span className={`ticker-dot ${colorClass}`} />

            {/* Blurred glass layer masked to letter shapes */}
            <div ref={glassLayerRef} className="ticker-glass-layer" />

            {/* Outline-only text on top for the rim/edge of the glass letters */}
            <span className="ticker-glass-text" aria-label={text}>
                {text.toUpperCase()}
            </span>
        </div>
    );
}

export default function NewsTicker({ onArticleClick }: { onArticleClick: (item: NewsItem) => void }) {
    const [headlines, setHeadlines] = useState<NewsItem[]>([]);

    useEffect(() => {
        fetchAPI('/api/top-headlines?limit=9')
            .then(setHeadlines)
            .catch(err => console.error('Failed to load headlines:', err));
    }, []);

    if (headlines.length === 0) return null;

    let chunk1: NewsItem[] = [], chunk2: NewsItem[] = [], chunk3: NewsItem[] = [];
    if (headlines.length >= 3) {
        chunk1 = headlines.slice(0, 3);
        chunk2 = headlines.slice(3, 6);
        chunk3 = headlines.slice(6, 9);
    } else {
        chunk1 = chunk2 = chunk3 = headlines;
    }
    if (chunk2.length === 0) chunk2 = headlines;
    if (chunk3.length === 0) chunk3 = headlines;

    const dotColors = ['bg-cyan-400/50', 'bg-purple-400/50', 'bg-rose-400/50', 'bg-amber-400/50', 'bg-emerald-400/50'];

    const renderBand = (items: NewsItem[], direction: 'left' | 'right') => (
        <div className={`ticker-band ${direction}`}>
            {[...items, ...items, ...items, ...items, ...items, ...items].map((item, i) => (
                <GlassTickerItem
                    key={`${item.id}-${i}`}
                    text={item.headline || item.input_content.substring(0, 50) + '...'}
                    colorClass={dotColors[i % dotColors.length]}
                    onClick={() => onArticleClick(item)}
                />
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
