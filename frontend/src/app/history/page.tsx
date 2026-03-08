'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchAPI } from '@/lib/api';
import { useUser } from '@clerk/nextjs';
import { CheckCircle, AlertCircle, ChevronDown, ChevronUp, Lock, Globe, Code } from 'lucide-react';

export default function HistoryPage() {
    const { user, isLoaded, isSignedIn } = useUser();
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isLoaded && isSignedIn && user) {
            loadHistory();
        } else if (isLoaded && !isSignedIn) {
            setLoading(false);
        }
    }, [isLoaded, isSignedIn, user]);

    async function loadHistory() {
        try {
            const data = await fetchAPI(`/api/history/${user?.id}`);
            setHistory(data);
        } catch (error) {
            console.error('Failed to load history:', error);
        } finally {
            setLoading(false);
        }
    }

    async function togglePublic(id: string, currentStatus: boolean) {
        try {
            // Optimistic update
            setHistory(history.map(h => h.id === id ? { ...h, is_public: !currentStatus } : h));

            await fetchAPI(`/api/toggle-public/${id}?is_public=${!currentStatus}`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Failed to toggle public status:', error);
            // Revert on error
            setHistory(history.map(h => h.id === id ? { ...h, is_public: currentStatus } : h));
        }
    }

    if (!isLoaded || loading) return <div className="text-center py-20 text-cyan-400 animate-pulse">Loading history...</div>;

    if (!isSignedIn) {
        return (
            <div className="text-center py-20">
                <h2 className="text-2xl font-bold mb-4">Please Sign In</h2>
                <p className="text-gray-400">You need to be signed in to view your verification history.</p>
            </div>
        );
    }

    if (history.length === 0) {
        return (
            <div className="text-center py-20">
                <h2 className="text-2xl font-bold mb-4">No History Yet</h2>
                <p className="text-gray-400">Start verifying content to build your history.</p>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 py-12 relative">
            {/* Background Elements */}
            <div className="fixed inset-0 bg-grid-white/[0.02] bg-[size:50px_50px] pointer-events-none" />
            <div className="fixed top-20 left-0 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none" />
            <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none" />

            <h1 className="text-4xl font-bold mb-8 relative z-10">Verification History</h1>
            <div className="space-y-4">
                {history.map((item, index) => (
                    <HistoryItem
                        key={item.id}
                        item={item}
                        index={index}
                        onTogglePublic={() => togglePublic(item.id, item.is_public)}
                    />
                ))}
            </div>
        </div>
    );
}

function HistoryItem({ item, index, onTogglePublic }: { item: any, index: number, onTogglePublic: () => void }) {
    const [expanded, setExpanded] = useState(false);
    const [showJson, setShowJson] = useState(false);
    const isTrue = item.verdict;

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="glass-panel p-6 hover:bg-white/5 transition-colors"
        >
            <div className="flex items-center justify-between gap-4 cursor-pointer" onClick={() => setExpanded(!expanded)}>
                <div className="flex items-center gap-4 flex-1 min-w-0">
                    <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isTrue ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                        }`}>
                        {isTrue ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-white font-medium truncate">{item.input_content}</p>
                        <p className="text-xs text-gray-500">{new Date(item.created_at).toLocaleString()}</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onTogglePublic();
                        }}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${item.is_public
                            ? 'bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30'
                            : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                            }`}
                    >
                        {item.is_public ? <Globe className="w-3 h-3" /> : <Lock className="w-3 h-3" />}
                        {item.is_public ? 'Public' : 'Private'}
                    </button>
                    {expanded ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
                </div>
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="pt-6 mt-6 border-t border-white/10 space-y-4">
                            {item.image_url && (
                                <div className="w-full h-48 rounded-lg overflow-hidden relative border border-white/10 shadow-lg shadow-cyan-500/10">
                                    <img src={item.image_url} alt="Verification context" className="w-full h-full object-cover" />
                                </div>
                            )}
                            <div>
                                <h4 className="text-cyan-400 text-sm font-bold mb-2">AI Analysis</h4>
                                <div className="space-y-3">
                                    {item.reasoning.split('\n').map((paragraph: string, i: number) => (
                                        paragraph.trim() && (
                                            <div key={i} className="bg-white/5 p-3 rounded-lg border border-white/5 text-gray-300 text-sm leading-relaxed">
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
                                <h4 className="text-cyan-400 text-sm font-bold mb-2">Key Claims</h4>
                                <ul className="space-y-1">
                                    {item.claims.map((claim: string, i: number) => (
                                        <li key={i} className="text-gray-400 text-sm flex items-start gap-2">
                                            <span className="mt-1.5 w-1 h-1 rounded-full bg-gray-600" />
                                            {claim}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Sources Section */}
                            {item.sources && Object.keys(item.sources).length > 0 && (
                                <div>
                                    <h4 className="text-cyan-400 text-sm font-bold mb-2">Sources</h4>
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
                )
                }
            </AnimatePresence >
        </motion.div >
    );
}
