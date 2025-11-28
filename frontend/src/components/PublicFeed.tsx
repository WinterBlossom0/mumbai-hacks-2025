'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchAPI } from '@/lib/api';
import { useUser } from '@clerk/nextjs';
import { ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, AlertCircle, CheckCircle, Eye, Share2 } from 'lucide-react';

interface FeedItem {
    id: string;
    input_content: string;
    verdict: boolean;
    reasoning: string;
    claims: string[];
    user_email: string;
    created_at: string;
    category: string;
    headline?: string;
    upvotes: number;
    downvotes: number;
}

export default function PublicFeed({ category }: { category: string }) {
    const [feed, setFeed] = useState<FeedItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [expandedId, setExpandedId] = useState<string | null>(null);
    const { user } = useUser();

    useEffect(() => {
        loadFeed();
    }, [category]);

    async function loadFeed() {
        setLoading(true);
        try {
            const data = await fetchAPI('/api/public-feed?limit=50');
            let filtered = data;
            if (category !== 'all') {
                filtered = data.filter((item: FeedItem) => item.category === category);
            }
            setFeed(filtered);
        } catch (err) {
            setError('Failed to load feed');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    const handleToggle = (id: string) => {
        setExpandedId(expandedId === id ? null : id);
    };

    if (loading) return <div className="text-center py-20 text-cyan-400 animate-pulse">Loading feed...</div>;
    if (error) return <div className="text-center py-20 text-red-400">{error}</div>;
    if (feed.length === 0) return <div className="text-center py-20 text-gray-500">No verifications found</div>;

    return (
        <div className="max-w-[1600px] mx-auto">
            <div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
                <AnimatePresence mode='popLayout'>
                    {feed.map((item, index) => (
                        <FeedCard
                            key={item.id}
                            item={item}
                            index={index}
                            currentUserEmail={user?.primaryEmailAddress?.emailAddress}
                            isExpanded={expandedId === item.id}
                            onToggle={() => handleToggle(item.id)}
                        />
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
}

function FeedCard({ item, index, currentUserEmail, isExpanded, onToggle }: {
    item: FeedItem;
    index: number;
    currentUserEmail?: string;
    isExpanded: boolean;
    onToggle: () => void;
}) {
    const [isHovered, setIsHovered] = useState(false);
    const isTrue = item.verdict;
    const isOwnPost = currentUserEmail && item.user_email === currentUserEmail;
    const showVerdict = isOwnPost || isExpanded || isHovered;

    // Random gradient for visual variety based on ID
    const gradients = [
        'from-purple-500/10 to-blue-500/10',
        'from-cyan-500/10 to-teal-500/10',
        'from-rose-500/10 to-orange-500/10',
        'from-emerald-500/10 to-green-500/10',
    ];
    const gradient = gradients[item.id.charCodeAt(0) % gradients.length];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`glass-panel group relative p-6 cursor-hover transition-all duration-500 break-inside-avoid mb-6 hover:shadow-[0_0_30px_rgba(0,242,255,0.2)] overflow-hidden`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            onClick={onToggle}
        >
            {/* Dynamic Background Gradient */}
            <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

            {/* Content Wrapper */}
            <div className="relative z-10">
                <div className="flex items-start justify-between gap-4 mb-4">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                            {item.category || 'General'}
                        </span>
                    </div>
                    <span className="text-xs text-gray-500">
                        {new Date(item.created_at).toLocaleDateString()}
                    </span>
                </div>

                {item.headline ? (
                    <h3 className="text-xl font-bold mb-3 text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-cyan-400 group-hover:to-blue-500 transition-all duration-300 leading-tight">
                        {item.headline}
                    </h3>
                ) : (
                    <h3 className="text-lg font-medium mb-3 text-gray-200 line-clamp-2 group-hover:text-cyan-300 transition-colors">
                        {item.input_content}
                    </h3>
                )}

                {/* Verdict Badge */}
                <div className="mb-4">
                    <motion.div
                        className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold border backdrop-blur-md transition-all duration-500 ${showVerdict
                            ? (isTrue ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-red-500/20 text-red-400 border-red-500/30')
                            : 'bg-white/5 text-gray-400 border-white/10'
                            }`}
                        animate={{
                            filter: showVerdict ? 'blur(0px)' : 'blur(4px)',
                        }}
                    >
                        {showVerdict ? (
                            <>
                                {isTrue ? <CheckCircle className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                                {isTrue ? 'VERIFIED TRUE' : 'VERIFIED FALSE'}
                            </>
                        ) : (
                            <span className="flex items-center gap-2">
                                <Eye className="w-3 h-3" /> HOVER TO REVEAL
                            </span>
                        )}
                    </motion.div>
                </div>

                <div className={`text-gray-400 text-sm leading-relaxed ${!isExpanded ? 'line-clamp-3' : ''}`}>
                    {item.input_content}
                </div>

                <AnimatePresence>
                    {isExpanded && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                        >
                            <div className="pt-4 mt-4 border-t border-white/10 space-y-4">
                                <div className="bg-black/20 rounded-lg p-3 border border-white/5">
                                    <h4 className="text-cyan-400 text-xs font-bold uppercase mb-2 flex items-center gap-2">
                                        <span>🤖</span> AI Analysis
                                    </h4>
                                    <p className="text-gray-300 text-sm leading-relaxed">{item.reasoning}</p>
                                </div>

                                <div>
                                    <h4 className="text-cyan-400 text-xs font-bold uppercase mb-2 flex items-center gap-2">
                                        <span>📌</span> Key Claims
                                    </h4>
                                    <ul className="space-y-2">
                                        {item.claims.map((claim, i) => (
                                            <li key={i} className="text-gray-400 text-xs flex items-start gap-2">
                                                <span className="mt-1 w-1 h-1 rounded-full bg-cyan-500/50 shrink-0" />
                                                {claim}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="mt-4 flex items-center justify-between text-xs text-gray-500 border-t border-white/5 pt-3">
                    <div className="flex items-center gap-4">
                        <button className="flex items-center gap-1 hover:text-cyan-400 transition-colors">
                            <ThumbsUp className="w-3 h-3" /> {item.upvotes || 0}
                        </button>
                        <button className="flex items-center gap-1 hover:text-red-400 transition-colors">
                            <ThumbsDown className="w-3 h-3" /> {item.downvotes || 0}
                        </button>
                    </div>
                    <div className="flex items-center gap-3">
                        <button className="hover:text-white transition-colors">
                            <Share2 className="w-3 h-3" />
                        </button>
                        <button className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 transition-colors font-medium">
                            {isExpanded ? 'LESS' : 'MORE'}
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
