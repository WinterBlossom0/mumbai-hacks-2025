'use client';

/**
 * ReasoningText — renders reasoning text with inline claim highlights.
 *
 * The backend embeds unique markers around claim text in the REASONING output:
 *   ««TRUE_START»» ... ««TRUE_END»»        → green highlight
 *   ««FALSE_START»» ... ««FALSE_END»»      → red highlight
 *   ««UNCONFIRMED_START»» ... ««UNCONFIRMED_END»» → yellow highlight
 *
 * These markers cannot appear in any natural language text.
 * Everything outside markers renders as normal grey text.
 *
 * IMPACT TRACE:
 *   Used by: verify/page.tsx, history/page.tsx, PublicFeed.tsx, reddit/page.tsx
 *   Depends on: reasoning string from /api/verify response (stored in DB as-is)
 *   If changed: all reasoning displays change simultaneously
 */

const TRUE_START       = '««TRUE_START»»';
const TRUE_END         = '««TRUE_END»»';
const FALSE_START      = '««FALSE_START»»';
const FALSE_END        = '««FALSE_END»»';
const UNCONFIRMED_START = '««UNCONFIRMED_START»»';
const UNCONFIRMED_END   = '««UNCONFIRMED_END»»';

type Segment =
    | { type: 'text'; content: string }
    | { type: 'true'; content: string }
    | { type: 'false'; content: string }
    | { type: 'unconfirmed'; content: string };

function parseSegments(text: string): Segment[] {
    // Split on all markers, keeping them as delimiters
    const TOKEN_RE = new RegExp(
        `(${escRe(TRUE_START)}|${escRe(TRUE_END)}|${escRe(FALSE_START)}|${escRe(FALSE_END)}|${escRe(UNCONFIRMED_START)}|${escRe(UNCONFIRMED_END)})`,
        'g'
    );
    const parts = text.split(TOKEN_RE);

    const segments: Segment[] = [];
    let currentType: 'true' | 'false' | 'unconfirmed' | null = null;
    let buf = '';

    for (const part of parts) {
        if (part === TRUE_START)       { flush(segments, buf, currentType); buf = ''; currentType = 'true'; }
        else if (part === TRUE_END)    { flush(segments, buf, currentType); buf = ''; currentType = null; }
        else if (part === FALSE_START) { flush(segments, buf, currentType); buf = ''; currentType = 'false'; }
        else if (part === FALSE_END)   { flush(segments, buf, currentType); buf = ''; currentType = null; }
        else if (part === UNCONFIRMED_START) { flush(segments, buf, currentType); buf = ''; currentType = 'unconfirmed'; }
        else if (part === UNCONFIRMED_END)   { flush(segments, buf, currentType); buf = ''; currentType = null; }
        else { buf += part; }
    }
    if (buf) flush(segments, buf, currentType);

    return segments;
}

function flush(out: Segment[], content: string, type: 'true' | 'false' | 'unconfirmed' | null) {
    if (!content) return;
    if (type === 'true')        out.push({ type: 'true', content });
    else if (type === 'false')  out.push({ type: 'false', content });
    else if (type === 'unconfirmed') out.push({ type: 'unconfirmed', content });
    else                        out.push({ type: 'text', content });
}

function escRe(s: string) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

const HIGHLIGHT_CLASSES: Record<string, string> = {
    true:        'bg-green-500/20  text-green-300  rounded px-0.5',
    false:       'bg-red-500/20    text-red-300    rounded px-0.5',
    unconfirmed: 'bg-yellow-500/20 text-yellow-300 rounded px-0.5',
};

function renderSegments(segments: Segment[]) {
    return segments.map((seg, i) => {
        if (seg.type === 'text') return <span key={i}>{seg.content}</span>;
        return (
            <span key={i} className={HIGHLIGHT_CLASSES[seg.type]}>
                {seg.content}
            </span>
        );
    });
}

interface ReasoningTextProps {
    reasoning: string;
    paragraphClassName?: string;
}

export default function ReasoningText({
    reasoning,
    paragraphClassName = 'bg-white/5 p-3 rounded-lg border border-white/5 text-gray-300 text-sm leading-relaxed',
}: ReasoningTextProps) {
    if (!reasoning) return null;

    return (
        <div className="space-y-3">
            {reasoning.split('\n').map((paragraph, i) => {
                if (!paragraph.trim()) return null;
                const segments = parseSegments(paragraph);
                return (
                    <div key={i} className={paragraphClassName}>
                        {renderSegments(segments)}
                    </div>
                );
            })}
        </div>
    );
}
