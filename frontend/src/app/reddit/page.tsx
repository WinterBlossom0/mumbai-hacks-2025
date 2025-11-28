'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchAPI } from '@/lib/api';
import { MessageSquare, ExternalLink } from 'lucide-react';

export default function RedditPage() {
    const [feed, setFeed] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadRedditFeed();
    }, []);

    async function loadRedditFeed() {
        try {
            const data = await fetchAPI('/api/reddit-posts?limit=50');
            setFeed(data);
        } catch (error) {
            console.error('Failed to load Reddit feed:', error);
        } finally {
            setLoading(false);
        }
    }

    if (loading) return <div className="text-center py-20 text-cyan-400 animate-pulse">Loading Reddit feed...</div>;

    return (
        <div className="max-w-4xl mx-auto px-4 py-12 relative">
            {/* Background Elements */}
            <div className="fixed inset-0 bg-grid-white/[0.02] bg-[size:50px_50px] pointer-events-none" />
            <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-[#FF4500]/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="fixed bottom-0 left-0 w-[500px] h-[500px] bg-orange-600/10 rounded-full blur-[120px] pointer-events-none" />

            <div className="relative z-10">
                <div className="flex items-center gap-4 mb-8">
                    <div className="w-12 h-12 bg-[#FF4500] rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(255,69,0,0.3)]">
                        <MessageSquare className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-4xl font-bold">r/eyeoftruth Feed</h1>
                        <p className="text-gray-400">Live verified posts from our subreddit.</p>
                    </div>
                </div>

                <div className="space-y-6">
                    {feed.map((item, index) => (
                        <RedditCard key={item.id} item={item} index={index} />
                    ))}
                </div>
            </div>
        </div>
    );
}

function RedditCard({ item, index }: { item: any, index: number }) {
    const [expanded, setExpanded] = useState(false);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="glass-panel p-6 hover:bg-white/5 transition-colors cursor-pointer group relative overflow-hidden"
            onClick={() => setExpanded(!expanded)}
        >
            <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-[#FF4500] font-medium flex items-center gap-2">
                        u/{item.author}
                    </span>
                    <span className="text-xs text-gray-500">{new Date(item.created_at).toLocaleDateString()}</span>
                </div>

                {item.headline && (
                    <h3 className="text-xl font-bold mb-3 text-white group-hover:text-[#FF4500] transition-colors">{item.headline}</h3>
                )}

                <div className={`text-gray-300 leading-relaxed ${!expanded && !item.headline ? 'line-clamp-3' : ''}`}>
                    {item.body || item.url || item.title}
                </div>

                <AnimatePresence>
                    {expanded && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                        >
                            <div className="pt-6 mt-6 border-t border-white/10 space-y-6">
                                <div className="bg-white/5 rounded-lg p-4 border border-white/5">
                                    <h4 className="text-cyan-400 font-medium mb-2 flex items-center gap-2">
                                        <span>🤖</span> AI Analysis
                                    </h4>
                                    <p className="text-gray-400 text-sm leading-relaxed">{item.reasoning}</p>
                                </div>

                                <div>
                                    <h4 className="text-cyan-400 font-medium mb-2 flex items-center gap-2">
                                        <span>📌</span> Key Claims
                                    </h4>
                                    <ul className="space-y-2">
                                        {item.claims.map((claim: string, i: number) => (
                                            <li key={i} className="text-gray-400 text-sm flex items-start gap-2">
                                                <span className="mt-1.5 w-1 h-1 rounded-full bg-cyan-500/50" />
                                                {claim}
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                {item.url && (
                                    <a
                                        href={item.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm hover:underline"
                                        onClick={(e) => e.stopPropagation()}
                                    >
                                        <ExternalLink className="w-4 h-4" />
                                        View Original Source
                                    </a>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
}
