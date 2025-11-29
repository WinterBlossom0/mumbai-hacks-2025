'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Search, Eye, X, ThumbsUp, ThumbsDown } from 'lucide-react';
import { useUser } from '@clerk/nextjs';
import CategoryFilter from '@/components/CategoryFilter';
import PublicFeed from '@/components/PublicFeed';
import NewsTicker from '@/components/NewsTicker';
import { fetchAPI } from '@/lib/api';

export default function Home() {
    const [activeCategory, setActiveCategory] = useState('all');
    const [heroArticle, setHeroArticle] = useState<any>(null);
    const [heroUpvotes, setHeroUpvotes] = useState(0);
    const [heroDownvotes, setHeroDownvotes] = useState(0);
    const [heroUserVote, setHeroUserVote] = useState<number | null>(null);
    const { user } = useUser();
    const currentUserEmail = user?.primaryEmailAddress?.emailAddress;

    const handleHeroArticleClick = (item: any) => {
        setHeroArticle(item);
        setHeroUpvotes(item.upvotes || 0);
        setHeroDownvotes(item.downvotes || 0);
        setHeroUserVote(null);
    };

    const handleHeroVote = async (voteType: number) => {
        if (!currentUserEmail) {
            alert('Please sign in to vote');
            return;
        }
        if (!heroArticle) return;

        try {
            if (heroUserVote === voteType) {
                setHeroUserVote(null);
                if (voteType === 1) setHeroUpvotes(heroUpvotes - 1);
                else setHeroDownvotes(heroDownvotes - 1);
            } else {
                if (heroUserVote === 1) setHeroUpvotes(heroUpvotes - 1);
                if (heroUserVote === -1) setHeroDownvotes(heroDownvotes - 1);

                setHeroUserVote(voteType);
                if (voteType === 1) setHeroUpvotes(heroUpvotes + 1);
                else setHeroDownvotes(heroDownvotes + 1);
            }

            await fetchAPI('/api/vote', {
                method: 'POST',
                body: JSON.stringify({
                    verification_id: heroArticle.id,
                    user_id: currentUserEmail,
                    vote_type: voteType
                })
            });
        } catch (error) {
            console.error('Vote failed:', error);
            setHeroUpvotes(heroArticle.upvotes || 0);
            setHeroDownvotes(heroArticle.downvotes || 0);
            setHeroUserVote(null);
        }
    };

    const isOwnHeroPost = currentUserEmail && heroArticle && heroArticle.user_email === currentUserEmail;

    return (
        <div className="min-h-screen relative overflow-hidden">
            {/* Background Elements */}
            <div className="fixed inset-0 bg-grid-white/[0.02] bg-[size:50px_50px] pointer-events-none" />
            <div className="fixed top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-600/30 rounded-full blur-[120px] animate-pulse" />
            <div className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-cyan-600/30 rounded-full blur-[120px] animate-pulse delay-1000" />

            <div className="pb-4">
                <NewsTicker onArticleClick={handleHeroArticleClick} />
            </div>

            {/* Hero Section */}
            <section className="relative pt-10 pb-20 px-4 overflow-hidden min-h-[600px] flex items-center justify-center -mt-10">
                <div className="max-w-5xl mx-auto text-center space-y-8 relative z-10 w-full">
                    <AnimatePresence mode="wait">
                        {heroArticle ? (
                            <motion.div
                                key="article"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                transition={{ duration: 0.3 }}
                                className="text-left glass-panel p-8 md:p-12 relative !border-cyan-500/30 !shadow-[0_0_50px_rgba(0,242,255,0.1)]"
                            >
                                <button
                                    onClick={() => setHeroArticle(null)}
                                    className="absolute top-6 right-6 p-2 bg-white/5 hover:bg-white/10 rounded-full text-gray-400 hover:text-white transition-colors"
                                >
                                    <X className="w-6 h-6" />
                                </button>

                                <div className="flex items-start gap-6 mb-8">
                                    <div className={`flex-shrink-0 w-16 h-16 rounded-2xl flex items-center justify-center text-2xl ${heroArticle.verdict ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'}`}>
                                        {heroArticle.verdict ? '✓' : '✗'}
                                    </div>
                                    <div>
                                        <h2 className="text-3xl md:text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">
                                            {heroArticle.headline || 'Verification Result'}
                                        </h2>
                                        <div className="flex items-center gap-4 text-sm text-gray-500">
                                            <span>by {heroArticle.user_email.split('@')[0]}</span>
                                            <span>•</span>
                                            <span>{new Date(heroArticle.created_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="prose prose-invert max-w-none mb-8">
                                    <div className="bg-white/5 p-6 rounded-xl border border-white/10 text-lg leading-relaxed text-gray-200">
                                        {heroArticle.input_content}
                                    </div>
                                </div>

                                <div className="grid md:grid-cols-2 gap-8">
                                    <div>
                                        <h4 className="text-cyan-400 font-bold mb-3 flex items-center gap-2">
                                            <span>🤖</span> AI Analysis
                                        </h4>
                                        <p className="text-gray-400 leading-relaxed">
                                            {heroArticle.reasoning}
                                        </p>
                                    </div>
                                    <div>
                                        <h4 className="text-cyan-400 font-bold mb-3 flex items-center gap-2">
                                            <span>📌</span> Key Claims
                                        </h4>
                                        <ul className="space-y-2">
                                            {heroArticle.claims.map((claim: string, i: number) => (
                                                <li key={i} className="flex items-start gap-2 text-gray-400">
                                                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-cyan-500 flex-shrink-0" />
                                                    {claim}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>

                                <div className="mt-8 pt-8 border-t border-white/10 flex items-center gap-6">
                                    {isOwnHeroPost ? (
                                        <>
                                            <div className="text-gray-400">
                                                <span className="text-cyan-400 font-semibold">{heroUpvotes}</span> upvotes
                                            </div>
                                            <div className="text-gray-400">
                                                <span className="text-red-400 font-semibold">{heroDownvotes}</span> downvotes
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            <button
                                                className={`flex items-center gap-2 transition-colors ${heroUserVote === 1 ? 'text-cyan-400' : 'text-gray-400 hover:text-cyan-400'}`}
                                                onClick={() => handleHeroVote(1)}
                                            >
                                                <ThumbsUp className="w-5 h-5" /> {heroUpvotes}
                                            </button>
                                            <button
                                                className={`flex items-center gap-2 transition-colors ${heroUserVote === -1 ? 'text-red-400' : 'text-gray-400 hover:text-red-400'}`}
                                                onClick={() => handleHeroVote(-1)}
                                            >
                                                <ThumbsDown className="w-5 h-5" /> {heroDownvotes}
                                            </button>
                                        </>
                                    )}
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="default"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                transition={{ duration: 0.3 }}
                            >
                                <motion.div
                                    initial={{ scale: 0.5, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    transition={{ type: "spring", duration: 0.8 }}
                                    className="w-24 h-24 mx-auto bg-gradient-to-br from-cyan-400 to-blue-600 rounded-3xl flex items-center justify-center shadow-[0_0_60px_rgba(0,242,255,0.4)] mb-8 rotate-3 hover:rotate-6 transition-transform duration-300"
                                >
                                    <Eye className="w-12 h-12 text-white" />
                                </motion.div>

                                <motion.h1
                                    initial={{ y: 30, opacity: 0 }}
                                    animate={{ y: 0, opacity: 1 }}
                                    transition={{ delay: 0.2 }}
                                    className="text-6xl md:text-8xl font-bold tracking-tighter"
                                >
                                    Truth <span className="text-gradient">Lens</span>
                                </motion.h1>

                                <motion.p
                                    initial={{ y: 30, opacity: 0 }}
                                    animate={{ y: 0, opacity: 1 }}
                                    transition={{ delay: 0.3 }}
                                    className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto leading-relaxed"
                                >
                                    The AI-powered arbiter of truth. Verify claims instantly with military-grade precision.
                                </motion.p>

                                <motion.div
                                    initial={{ y: 30, opacity: 0 }}
                                    animate={{ y: 0, opacity: 1 }}
                                    transition={{ delay: 0.4 }}
                                    className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8"
                                >
                                    <Link
                                        href="/verify"
                                        className="group relative px-8 py-4 bg-white text-black rounded-full font-bold text-lg overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_40px_rgba(255,255,255,0.4)]"
                                    >
                                        <span className="relative z-10 flex items-center gap-2">
                                            Start Verifying <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                        </span>
                                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-500 opacity-0 group-hover:opacity-10 transition-opacity" />
                                    </Link>

                                    <Link
                                        href="/history"
                                        className="px-8 py-4 rounded-full font-bold text-lg text-white border border-white/10 hover:bg-white/5 hover:border-white/20 transition-all"
                                    >
                                        View History
                                    </Link>
                                </motion.div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </section>

            {/* Feed Section */}
            <section className="max-w-[1600px] mx-auto px-4 pb-20 relative z-10">
                <div className="glass-panel p-8 md:p-12">
                    <div className="text-center mb-12">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4">Live Verification Feed</h2>
                        <p className="text-gray-400">Real-time analysis from across the globe</p>
                    </div>

                    <CategoryFilter activeCategory={activeCategory} onSelect={setActiveCategory} />

                    <div className="mt-12">
                        <PublicFeed category={activeCategory} />
                    </div>
                </div>
            </section>
        </div>
    );
}
