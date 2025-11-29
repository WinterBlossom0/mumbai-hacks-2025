'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchAPI } from '@/lib/api';
import { MessageSquare, ExternalLink, Code, Search } from 'lucide-react';

export default function RedditPage() {
    const [activeTab, setActiveTab] = useState<'eyeoftruth' | 'community'>('eyeoftruth');
    const [feed, setFeed] = useState<any[]>([]);
    const [communityFeed, setCommunityFeed] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [communityLoading, setCommunityLoading] = useState(false);
    const [subreddit, setSubreddit] = useState('');

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

    async function loadCommunityFeed(subredditName: string) {
        if (!subredditName.trim()) return;

        setCommunityLoading(true);
        try {
            const data = await fetchAPI(`/api/reddit-community?subreddit=${encodeURIComponent(subredditName)}&limit=10`);
            setCommunityFeed(data);
        } catch (error) {
            console.error('Failed to load community feed:', error);
            alert('Failed to load subreddit. Please check the name and try again.');
        } finally {
            setCommunityLoading(false);
        }
    }

    const handleSubredditSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        loadCommunityFeed(subreddit);
    };

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
                        <h1 className="text-4xl font-bold">Reddit Feed</h1>
                        <p className="text-gray-400">Browse verified posts and community content</p>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-4 mb-8">
                    <button
                        onClick={() => setActiveTab('eyeoftruth')}
                        className={`px-6 py-3 rounded-full font-semibold transition-all ${activeTab === 'eyeoftruth'
                            ? 'bg-[#FF4500] text-white shadow-[0_0_20px_rgba(255,69,0,0.3)]'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                            }`}
                    >
                        r/eyeoftruth
                    </button>
                    <button
                        onClick={() => setActiveTab('community')}
                        className={`px-6 py-3 rounded-full font-semibold transition-all ${activeTab === 'community'
                            ? 'bg-[#FF4500] text-white shadow-[0_0_20px_rgba(255,69,0,0.3)]'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                            }`}
                    >
                        Community Reddit
                    </button>
                </div>

                {activeTab === 'eyeoftruth' ? (
                    loading ? (
                        <div className="text-center py-20 text-cyan-400 animate-pulse">Loading Reddit feed...</div>
                    ) : (
                        <div className="space-y-6">
                            {feed.map((item, index) => (
                                <RedditCard key={item.id} item={item} index={index} />
                            ))}
                        </div>
                    )
                ) : (
                    <div>
                        {/* Subreddit Search */}
                        <form onSubmit={handleSubredditSubmit} className="glass-panel p-6 mb-8">
                            <label className="text-sm font-semibold text-gray-400 mb-3 block">
                                Enter Subreddit Name
                            </label>
                            <div className="flex gap-4">
                                <div className="flex-1 relative">
                                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">r/</span>
                                    <input
                                        type="text"
                                        value={subreddit}
                                        onChange={(e) => setSubreddit(e.target.value)}
                                        placeholder="AskReddit"
                                        className="w-full bg-white/5 border border-white/10 rounded-full px-4 pl-10 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#FF4500] transition-colors"
                                    />
                                </div>
                                <button
                                    type="submit"
                                    disabled={communityLoading}
                                    className="px-8 py-3 bg-[#FF4500] text-white rounded-full font-semibold hover:shadow-[0_0_20px_rgba(255,69,0,0.3)] transition-all disabled:opacity-50 flex items-center gap-2"
                                >
                                    <Search className="w-5 h-5" />
                                    {communityLoading ? 'Loading...' : 'Search'}
                                </button>
                            </div>
                        </form>

                        {/* Community Feed */}
                        {communityLoading ? (
                            <div className="text-center py-20 text-cyan-400 animate-pulse">Loading subreddit...</div>
                        ) : communityFeed.length > 0 ? (
                            <div className="space-y-6">
                                {communityFeed.map((item, index) => (
                                    <RedditCard key={item.id} item={item} index={index} />
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-20 text-gray-500">
                                Enter a subreddit name above to browse its latest posts
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

function RedditCard({ item, index }: { item: any, index: number }) {
    const [expanded, setExpanded] = useState(false);
    const [showJson, setShowJson] = useState(false);

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
                                {/* Show AI Analysis only if reasoning exists (verified posts) */}
                                {item.reasoning && (
                                    <div className="bg-white/5 rounded-lg p-4 border border-white/5">
                                        <h4 className="text-cyan-400 font-medium mb-2 flex items-center gap-2">
                                            <span>🤖</span> AI Analysis
                                        </h4>
                                        <div className="space-y-3">
                                            {item.reasoning.split('\n').map((paragraph: string, i: number) => (
                                                paragraph.trim() && (
                                                    <div key={i} className="bg-black/20 p-3 rounded-lg border border-white/5 text-gray-400 text-sm leading-relaxed">
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
                                )}

                                {/* Show Claims only if they exist (verified posts) */}
                                {item.claims && item.claims.length > 0 && (
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
                                )}

                                {/* Sources Section - only if they exist */}
                                {item.sources && Object.keys(item.sources).length > 0 && (
                                    <div>
                                        <h4 className="text-cyan-400 font-medium mb-2 flex items-center gap-2">
                                            <span>🔗</span> Sources
                                        </h4>
                                        <div className="space-y-3">
                                            {Object.entries(item.sources).map(([source, urls]: [string, any], i) => (
                                                <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/5">
                                                    <h5 className="text-xs font-semibold text-gray-300 mb-1 capitalize">{source}</h5>
                                                    <ul className="space-y-1">
                                                        {Array.isArray(urls) && urls.map((url: string, j: number) => (
                                                            <li key={j}>
                                                                <a
                                                                    href={url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-xs text-cyan-400 hover:text-cyan-300 hover:underline break-all flex items-center gap-2"
                                                                    onClick={(e) => e.stopPropagation()}
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

                                {/* Community Post Stats */}
                                {(item.score !== undefined || item.num_comments !== undefined) && (
                                    <div className="bg-white/5 rounded-lg p-4 border border-white/5">
                                        <h4 className="text-cyan-400 font-medium mb-3 flex items-center gap-2">
                                            <span>📊</span> Reddit Stats
                                        </h4>
                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            {item.score !== undefined && (
                                                <div>
                                                    <span className="text-gray-500">Score:</span>
                                                    <span className="ml-2 text-white font-semibold">{item.score}</span>
                                                </div>
                                            )}
                                            {item.num_comments !== undefined && (
                                                <div>
                                                    <span className="text-gray-500">Comments:</span>
                                                    <span className="ml-2 text-white font-semibold">{item.num_comments}</span>
                                                </div>
                                            )}
                                            {item.subreddit && (
                                                <div>
                                                    <span className="text-gray-500">Subreddit:</span>
                                                    <span className="ml-2 text-[#FF4500] font-semibold">r/{item.subreddit}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

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

                                {/* Raw JSON View */}
                                <div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setShowJson(!showJson);
                                        }}
                                        className="flex items-center gap-2 text-xs font-mono text-gray-500 hover:text-cyan-400 transition-colors mb-4"
                                    >
                                        <Code className="w-3 h-3" />
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
                                                <pre className="text-xs font-mono text-green-400/80 overflow-x-auto p-4 bg-black/50 rounded-xl border border-white/5 custom-scrollbar" onClick={(e) => e.stopPropagation()}>
                                                    {JSON.stringify(item, null, 2)}
                                                </pre>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
}
