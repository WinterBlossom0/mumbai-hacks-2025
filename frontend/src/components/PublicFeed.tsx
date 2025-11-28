'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchAPI } from '@/lib/api';
import { useUser } from '@clerk/nextjs';
import { ChevronRight, ThumbsUp, ThumbsDown, AlertCircle, CheckCircle, Eye, Share2, X, Code } from 'lucide-react';

interface FeedItem {
    id: string;
    input_content: string;
    verdict: boolean;
    reasoning: string;
    claims: string[];
    sources?: Record<string, string[]>;
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
    const [selectedItem, setSelectedItem] = useState<FeedItem | null>(null);
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

    if (error) return <div className="text-center py-20 text-red-400">{error}</div>;

    return (
        <div className="max-w-[1600px] mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {loading ? (
                    // Skeleton Loading State
                    Array.from({ length: 6 }).map((_, i) => (
                        <FeedSkeleton key={i} />
                    ))
                ) : feed.length === 0 ? (
                    <div className="col-span-full text-center py-20 text-gray-500">No verifications found</div>
                ) : (
                    feed.map((item, index) => (
                        <FeedCard
                            key={item.id}
                            item={item}
                            index={index}
                            currentUserEmail={user?.primaryEmailAddress?.emailAddress}
                            onMoreClick={() => setSelectedItem(item)}
                        />
                    ))
                )}
            </div>

            <AnimatePresence>
                {selectedItem && (
                    <FeedModal item={selectedItem} onClose={() => setSelectedItem(null)} />
                )}
            </AnimatePresence>
        </div>
    );
}

function FeedSkeleton() {
    return (
        <div className="glass-panel p-6 h-[350px] flex flex-col animate-pulse border border-white/5">
            <div className="flex justify-between mb-6">
                <div className="h-4 bg-white/10 rounded w-24"></div>
                <div className="h-4 bg-white/10 rounded w-20"></div>
            </div>
            <div className="h-8 bg-white/10 rounded w-3/4 mb-4"></div>
            <div className="h-6 bg-white/5 rounded w-1/3 mb-6"></div>
            <div className="space-y-3 flex-grow">
                <div className="h-3 bg-white/5 rounded w-full"></div>
                <div className="h-3 bg-white/5 rounded w-full"></div>
                <div className="h-3 bg-white/5 rounded w-2/3"></div>
            </div>
            <div className="flex justify-between mt-6 pt-4 border-t border-white/5">
                <div className="h-4 bg-white/10 rounded w-16"></div>
                <div className="h-4 bg-white/10 rounded w-16"></div>
            </div>
        </div>
    );
}

function FeedCard({ item, index, currentUserEmail, onMoreClick }: {
    item: FeedItem;
    index: number;
    currentUserEmail?: string;
    onMoreClick: () => void;
}) {
    const [isHovered, setIsHovered] = useState(false);
    const isTrue = item.verdict;
    const isOwnPost = currentUserEmail && item.user_email === currentUserEmail;
    const showVerdict = isOwnPost || isHovered;

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
            className={`glass-panel group relative p-6 cursor-hover transition-all duration-500 flex flex-col h-full hover:shadow-[0_0_30px_rgba(0,242,255,0.2)] overflow-hidden`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            onClick={onMoreClick}
        >
            {/* Dynamic Background Gradient */}
            <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

            {/* Content Wrapper */}
            <div className="relative z-10 flex flex-col h-full">
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

                <div className="text-gray-400 text-sm leading-relaxed line-clamp-3 mb-4 flex-grow">
                    {item.input_content}
                </div>

                <div className="mt-auto flex items-center justify-between text-xs text-gray-500 border-t border-white/5 pt-3">
                    <div className="flex items-center gap-4">
                        <button className="flex items-center gap-1 hover:text-cyan-400 transition-colors" onClick={(e) => e.stopPropagation()}>
                            <ThumbsUp className="w-3 h-3" /> {item.upvotes || 0}
                        </button>
                        <button className="flex items-center gap-1 hover:text-red-400 transition-colors" onClick={(e) => e.stopPropagation()}>
                            <ThumbsDown className="w-3 h-3" /> {item.downvotes || 0}
                        </button>
                    </div>
                    <div className="flex items-center gap-3">
                        <button className="hover:text-white transition-colors" onClick={(e) => e.stopPropagation()}>
                            <Share2 className="w-3 h-3" />
                        </button>
                        <button className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 transition-colors font-medium">
                            MORE <ChevronRight className="w-3 h-3" />
                        </button>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

function FeedModal({ item, onClose }: { item: FeedItem; onClose: () => void }) {
    const [showJson, setShowJson] = useState(false);

    // Lock body scroll when modal is open
    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, []);

    // Use Portal to render at document body level for perfect centering
    if (typeof window === 'undefined') return null;

    return createPortal(
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
            onClick={onClose}
        >
            <motion.div
                initial={{ scale: 0.95, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.95, opacity: 0, y: 20 }}
                className="relative w-full max-w-3xl glass-panel p-0 max-h-[85vh] flex flex-col border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header - Fixed */}
                <div className="p-6 border-b border-white/10 flex items-start justify-between gap-4 bg-black/20 backdrop-blur-md sticky top-0 z-10">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${item.verdict ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'
                                }`}>
                                {item.verdict ? 'Verified True' : 'Verified False'}
                            </div>
                            <span className="text-gray-500 text-sm">{new Date(item.created_at).toLocaleDateString()}</span>
                        </div>
                        <h2 className="text-xl md:text-2xl font-bold text-white leading-tight line-clamp-2">
                            {item.headline || item.input_content}
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-white transition-colors rounded-full hover:bg-white/10 shrink-0"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="p-6 overflow-y-auto custom-scrollbar space-y-6">
                    <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                        <h3 className="text-cyan-400 font-bold mb-3 flex items-center gap-2">
                            <span>🤖</span> AI Analysis
                        </h3>
                        <div className="space-y-4">
                            {item.reasoning.split('\n').map((paragraph, i) => (
                                paragraph.trim() && (
                                    <div key={i} className="bg-white/5 p-4 rounded-lg border border-white/5 text-gray-300 leading-relaxed">
                                        {paragraph.split(/(\*\*.*?\*\*)/).map((part, index) => {
                                            if (part.startsWith('**') && part.endsWith('**')) {
                                                return <strong key={index} className="text-white font-bold">{part.slice(2, -2)}</strong>;
                                            }
                                            return part;
                                        })}
                                    </div>
                                )
                            ))}
                        </div>
                    </div>

                    <div>
                        <h3 className="text-cyan-400 font-bold mb-4 flex items-center gap-2">
                            <span>📌</span> Key Claims
                        </h3>
                        <ul className="space-y-3">
                            {item.claims.map((claim, i) => (
                                <li key={i} className="flex items-start gap-3 text-gray-300 bg-black/20 p-4 rounded-lg border border-white/5">
                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-cyan-500 shrink-0" />
                                    {claim}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Sources Section */}
                    {item.sources && Object.keys(item.sources).length > 0 && (
                        <div>
                            <h3 className="text-cyan-400 font-bold mb-4 flex items-center gap-2">
                                <span>🔗</span> Sources
                            </h3>
                            <div className="space-y-4">
                                {Object.entries(item.sources).map(([source, urls], i) => (
                                    <div key={i} className="bg-black/20 rounded-lg p-4 border border-white/5">
                                        <h4 className="text-sm font-semibold text-gray-300 mb-2 capitalize">{source}</h4>
                                        <ul className="space-y-2">
                                            {urls.map((url, j) => (
                                                <li key={j}>
                                                    <a
                                                        href={url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-xs text-cyan-400 hover:text-cyan-300 hover:underline break-all flex items-center gap-2"
                                                    >
                                                        <span className="w-1 h-1 rounded-full bg-cyan-500/50 shrink-0" />
                                                        {url}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Raw JSON View */}
                    <div>
                        <button
                            onClick={() => setShowJson(!showJson)}
                            className="flex items-center gap-2 text-xs font-mono text-gray-500 hover:text-cyan-400 transition-colors mb-4"
                        >
                            <Code className="w-4 h-4" />
                            {showJson ? 'HIDE_RAW_DATA' : 'VIEW_RAW_DATA'}
                        </button>

                        <AnimatePresence>
                            {showJson && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="overflow-hidden"
                                >
                                    <pre className="text-xs font-mono text-green-400/80 overflow-x-auto p-4 bg-black/50 rounded-xl border border-white/5 custom-scrollbar">
                                        {JSON.stringify(item, null, 2)}
                                    </pre>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Footer - Fixed */}
                <div className="p-6 border-t border-white/10 flex items-center justify-between bg-black/20 backdrop-blur-md">
                    <div className="flex items-center gap-6">
                        <button className="flex items-center gap-2 text-gray-400 hover:text-cyan-400 transition-colors">
                            <ThumbsUp className="w-5 h-5" /> {item.upvotes || 0}
                        </button>
                        <button className="flex items-center gap-2 text-gray-400 hover:text-red-400 transition-colors">
                            <ThumbsDown className="w-5 h-5" /> {item.downvotes || 0}
                        </button>
                    </div>
                    <button className="flex items-center gap-2 text-cyan-400 hover:text-white transition-colors">
                        <Share2 className="w-5 h-5" /> Share Analysis
                    </button>
                </div>
            </motion.div>
        </motion.div>,
        document.body
    );
}
