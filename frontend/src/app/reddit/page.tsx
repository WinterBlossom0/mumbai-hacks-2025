'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchAPI } from '@/lib/api';
import { MessageSquare, ExternalLink, Code, Search, Archive, ShieldQuestion } from 'lucide-react';
import Link from 'next/link';

export default function RedditPage() {
    const [activeTab, setActiveTab] = useState<'eyeoftruth' | 'community' | 'archive'>('eyeoftruth');
    const [feed, setFeed] = useState<any[]>([]);
    const [communityFeed, setCommunityFeed] = useState<any[]>([]);
    const [archiveFeed, setArchiveFeed] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [communityLoading, setCommunityLoading] = useState(false);
    const [archiveLoading, setArchiveLoading] = useState(false);
    const [subreddit, setSubreddit] = useState('');

    useEffect(() => {
        loadRedditFeed();
        loadArchiveFeed();
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

    async function loadArchiveFeed() {
        setArchiveLoading(true);
        try {
            const data = await fetchAPI('/api/community-archives?limit=50');
            setArchiveFeed(data);
        } catch (error) {
            console.error('Failed to load archive feed:', error);
        } finally {
            setArchiveLoading(false);
        }
    }

    const handleSubredditSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        loadCommunityFeed(subreddit);
    };

    const tabs = [
        { id: 'eyeoftruth', label: 'r/eyeoftruth' },
        { id: 'community', label: 'Community Reddit' },
        { id: 'archive', label: 'Archive', icon: Archive },
    ];

    return (
        <div className="max-w-4xl mx-auto px-4 py-12 relative">
            {/* Background Elements */}
            <div className="fixed inset-0 bg-grid-white/[0.02] bg-[size:50px_50px] pointer-events-none" />
            <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-[#FF4500]/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="fixed bottom-0 left-0 w-[500px] h-[500px] bg-orange-600/10 rounded-full blur-[120px] pointer-events-none" />

            <div className="relative z-10">
                <div className="flex items-center gap-4 mb-8">
                    <div className="w-12 h-12 bg-gradient-to-br from-[#FF4500] to-orange-600 rounded-2xl flex items-center justify-center shadow-[0_0_30px_rgba(255,69,0,0.4)] border border-white/10">
                        <MessageSquare className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                            Reddit Feed
                        </h1>
                        <p className="text-gray-400">Browse verified posts and community content</p>
                    </div>
                </div>

                {/* Tabs with Bubble Animation */}
                <div className="flex flex-wrap gap-2 mb-8 p-1 bg-white/5 rounded-full border border-white/10 w-fit backdrop-blur-md relative">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`px-6 py-2 rounded-full font-semibold transition-colors duration-300 relative z-10 flex items-center gap-2 ${activeTab === tab.id ? 'text-white' : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            {activeTab === tab.id && (
                                <motion.div
                                    layoutId="activeTab"
                                    className="absolute inset-0 bg-[#FF4500] rounded-full shadow-[0_0_20px_rgba(255,69,0,0.3)] -z-10"
                                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                />
                            )}
                            {tab.icon && <tab.icon className="w-4 h-4" />}
                            {tab.label}
                        </button>
                    ))}
                </div>

                {activeTab === 'eyeoftruth' && (
                    loading ? (
                        <div className="text-center py-20 text-[#FF4500] animate-pulse">Loading Reddit feed...</div>
                    ) : (
                        <div className="space-y-6">
                            {feed.map((item, index) => (
                                <RedditCard key={item.id} item={item} index={index} />
                            ))}
                        </div>
                    )
                )}

                {activeTab === 'community' && (
                    <div>
                        {/* Subreddit Search */}
                        <form onSubmit={handleSubredditSubmit} className="glass-panel p-6 mb-8 border-[#FF4500]/20 shadow-[0_0_30px_rgba(255,69,0,0.1)]">
                            <label className="text-sm font-semibold text-gray-400 mb-3 block">
                                Enter Subreddit Name
                            </label>
                            <div className="flex gap-4">
                                <div className="flex-1 relative group">
                                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#FF4500] transition-colors">r/</span>
                                    <input
                                        type="text"
                                        value={subreddit}
                                        onChange={(e) => setSubreddit(e.target.value)}
                                        placeholder="AskReddit"
                                        className="w-full bg-black/20 border border-white/10 rounded-xl px-4 pl-10 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#FF4500] focus:ring-1 focus:ring-[#FF4500] transition-all"
                                    />
                                </div>
                                <button
                                    type="submit"
                                    disabled={communityLoading}
                                    className="px-8 py-3 bg-gradient-to-r from-[#FF4500] to-orange-600 text-white rounded-xl font-semibold hover:shadow-[0_0_20px_rgba(255,69,0,0.4)] transition-all disabled:opacity-50 flex items-center gap-2 border border-white/10"
                                >
                                    <Search className="w-5 h-5" />
                                    {communityLoading ? 'Loading...' : 'Search'}
                                </button>
                            </div>
                        </form>

                        {/* Community Feed */}
                        {communityLoading ? (
                            <div className="text-center py-20 text-[#FF4500] animate-pulse">Loading subreddit...</div>
                        ) : communityFeed.length > 0 ? (
                            <div className="space-y-6">
                                {communityFeed.map((item, index) => (
                                    <RedditCard key={item.id} item={item} index={index} />
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-20 text-gray-500 bg-white/5 rounded-2xl border border-white/5">
                                <Search className="w-12 h-12 mx-auto mb-4 opacity-20" />
                                <p>Enter a subreddit name above to browse its latest posts</p>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'archive' && (
                    archiveLoading ? (
                        <div className="text-center py-20 text-[#FF4500] animate-pulse">Loading archive...</div>
                    ) : archiveFeed.length > 0 ? (
                        <div className="space-y-6">
                            {archiveFeed.map((item, index) => (
                                <RedditCard key={item.id} item={item} index={index} isArchive={true} />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-20 text-gray-500 bg-white/5 rounded-2xl border border-white/5">
                            <Archive className="w-12 h-12 mx-auto mb-4 opacity-20" />
                            <p>No archived posts yet. Verify community posts to add them here!</p>
                        </div>
                    )
                )}
            </div>
        </div>
    );
}

function RedditCard({ item, index, isArchive = false }: { item: any, index: number, isArchive?: boolean }) {
    const [expanded, setExpanded] = useState(false);

    // Construct verify URL with all necessary params
    const verifyUrl = `/verify?text=${encodeURIComponent(item.title + "\n" + (item.body || ""))}&reddit_id=${item.id}&subreddit=${item.subreddit || 'unknown'}&author=${item.author || 'unknown'}&auto=true`;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`glass-panel p-6 transition-all duration-300 cursor-pointer group relative overflow-hidden border-l-4 ${expanded ? 'border-l-[#FF4500] bg-white/10' : 'border-l-transparent hover:bg-white/5'}`}
            onClick={() => setExpanded(!expanded)}
        >
            <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-[#FF4500] font-bold flex items-center gap-2 bg-[#FF4500]/10 px-3 py-1 rounded-full border border-[#FF4500]/20">
                        u/{item.author || 'unknown'}
                    </span>
                    <span className="text-xs text-gray-500">
                        {item.created_at ? new Date(item.created_at * (item.created_at > 10000000000 ? 1 : 1000)).toLocaleDateString() : 'Unknown date'}
                    </span>
                </div>

                {/* Collapsed View Title */}
                {!expanded && (
                    <h3 className="text-xl font-bold mb-3 text-white group-hover:text-[#FF4500] transition-colors line-clamp-2">
                        {item.headline || item.title}
                    </h3>
                )}

                {/* Collapsed View Preview */}
                {!expanded && (
                    <div className="text-gray-400 leading-relaxed line-clamp-3 text-sm">
                        {item.body || item.url || item.title}
                    </div>
                )}

                <AnimatePresence>
                    {expanded && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                        >
                            <div className="pt-4 space-y-6">
                                {/* Full Header & Body for Expanded View */}
                                <div className="bg-black/20 rounded-xl p-6 border border-white/5">
                                    <h3 className="text-2xl font-bold mb-4 text-white">
                                        {item.title}
                                    </h3>
                                    <div className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                                        {item.body || (item.url ? <a href={item.url} target="_blank" className="text-blue-400 hover:underline">{item.url}</a> : "No content")}
                                    </div>

                                    {/* Verify Button - Only show if NOT already verified/archived */}
                                    {!item.reasoning && !isArchive && (
                                        <div className="mt-6 flex justify-end">
                                            <Link
                                                href={verifyUrl}
                                                onClick={(e) => e.stopPropagation()}
                                                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full font-bold hover:shadow-[0_0_20px_rgba(0,242,255,0.4)] transition-all transform hover:scale-105"
                                            >
                                                <ShieldQuestion className="w-5 h-5" />
                                                Verify?
                                            </Link>
                                        </div>
                                    )}
                                </div>

                                {/* Show AI Analysis only if reasoning exists (verified posts) */}
                                {item.reasoning && (
                                    <div className="bg-white/5 rounded-xl p-6 border border-white/5">
                                        <h4 className="text-cyan-400 font-bold mb-4 flex items-center gap-2 text-lg">
                                            <span>🤖</span> AI Analysis
                                        </h4>
                                        <div className="space-y-4">
                                            {item.reasoning.split('\n').map((paragraph: string, i: number) => (
                                                paragraph.trim() && (
                                                    <div key={i} className="bg-black/20 p-4 rounded-lg border border-white/5 text-gray-300 leading-relaxed">
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
                                        <h4 className="text-cyan-400 font-bold mb-3 flex items-center gap-2">
                                            <span>📌</span> Key Claims
                                        </h4>
                                        <ul className="space-y-3">
                                            {item.claims.map((claim: string, i: number) => (
                                                <li key={i} className="text-gray-300 flex items-start gap-3 bg-white/5 p-3 rounded-lg border border-white/5">
                                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-cyan-500 shrink-0" />
                                                    {claim}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {/* Community Post Stats */}
                                {(item.score !== undefined || item.num_comments !== undefined) && (
                                    <div className="bg-[#FF4500]/5 rounded-xl p-6 border border-[#FF4500]/20">
                                        <h4 className="text-[#FF4500] font-bold mb-4 flex items-center gap-2">
                                            <span>📊</span> Reddit Stats
                                        </h4>
                                        <div className="grid grid-cols-2 gap-4">
                                            {item.score !== undefined && (
                                                <div className="bg-black/20 p-3 rounded-lg border border-[#FF4500]/10">
                                                    <span className="text-gray-500 text-sm block mb-1">Score</span>
                                                    <span className="text-white font-bold text-xl">{item.score}</span>
                                                </div>
                                            )}
                                            {item.num_comments !== undefined && (
                                                <div className="bg-black/20 p-3 rounded-lg border border-[#FF4500]/10">
                                                    <span className="text-gray-500 text-sm block mb-1">Comments</span>
                                                    <span className="text-white font-bold text-xl">{item.num_comments}</span>
                                                </div>
                                            )}
                                            {item.subreddit && (
                                                <div className="col-span-2 bg-black/20 p-3 rounded-lg border border-[#FF4500]/10">
                                                    <span className="text-gray-500 text-sm block mb-1">Subreddit</span>
                                                    <span className="text-[#FF4500] font-bold">r/{item.subreddit}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Sources Section - only if they exist */}
                                {item.sources && Object.keys(item.sources).length > 0 && (
                                    <div>
                                        <h4 className="text-cyan-400 font-bold mb-3 flex items-center gap-2">
                                            <span>🔗</span> Sources
                                        </h4>
                                        <div className="space-y-3">
                                            {Object.entries(item.sources).map(([source, urls]: [string, any], i) => (
                                                <div key={i} className="bg-white/5 rounded-lg p-4 border border-white/5">
                                                    <h5 className="text-sm font-bold text-gray-300 mb-2 capitalize">{source}</h5>
                                                    <ul className="space-y-2">
                                                        {Array.isArray(urls) && urls.map((url: string, j: number) => (
                                                            <li key={j}>
                                                                <a
                                                                    href={url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-sm text-cyan-400 hover:text-cyan-300 hover:underline break-all flex items-center gap-2"
                                                                    onClick={(e) => e.stopPropagation()}
                                                                >
                                                                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-500/50 shrink-0" />
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

                                {item.url && (
                                    <div className="pt-4 border-t border-white/10">
                                        <a
                                            href={item.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 hover:underline transition-colors"
                                            onClick={(e) => e.stopPropagation()}
                                        >
                                            <ExternalLink className="w-4 h-4" />
                                            View Original Source
                                        </a>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
}
