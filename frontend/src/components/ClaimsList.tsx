'use client';

/**
 * ClaimsList — renders a plain list of extracted claims.
 *
 * IMPACT TRACE:
 *   Used by: verify/page.tsx, history/page.tsx, PublicFeed.tsx (modal),
 *            app/page.tsx (homepage hero)
 *   Claim colour highlights live in ReasoningText (inline markers in reasoning text).
 *   If changed: claim list display changes everywhere simultaneously.
 */

interface ClaimsListProps {
    claims?: string[];
    compact?: boolean;
}

export default function ClaimsList({ claims, compact = false }: ClaimsListProps) {
    if (!claims || claims.length === 0) return null;

    if (compact) {
        return (
            <ul className="space-y-1.5">
                {claims.map((claim, i) => (
                    <li key={i} className="px-3 py-2 rounded-md border border-white/5 bg-white/5 text-sm leading-relaxed text-gray-400">
                        {claim}
                    </li>
                ))}
            </ul>
        );
    }

    return (
        <ul className="space-y-2.5">
            {claims.map((claim, i) => (
                <li key={i} className="px-4 py-3 rounded-lg border border-white/5 bg-white/5 text-sm leading-relaxed text-gray-300 transition-colors">
                    {claim}
                </li>
            ))}
        </ul>
    );
}
