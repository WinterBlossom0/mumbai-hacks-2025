'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Link as LinkIcon, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { fetchAPI } from '@/lib/api';
import { useUser } from '@clerk/nextjs';

export default function VerifyPage() {
    const [inputType, setInputType] = useState<'text' | 'url'>('text');
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState('');
    const { user } = useUser();

    const handleVerify = async () => {
        if (!content.trim()) return;

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const data = await fetchAPI('/api/verify', {
                method: 'POST',
                body: JSON.stringify({
                    input_type: inputType,
                    content: content,
                    user_id: user?.id || '0',
                    user_email: user?.primaryEmailAddress?.emailAddress || 'user0@gmail.com'
                })
            });
            setResult(data);
        } catch (err: any) {
            setError(err.message || 'Verification failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-12 relative">
            {/* Background Elements */}
            <div className="fixed inset-0 bg-grid-white/[0.02] bg-[size:50px_50px] pointer-events-none" />
            <div className="fixed top-20 right-0 w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none" />
            <div className="fixed bottom-0 left-0 w-[500px] h-[500px] bg-cyan-600/20 rounded-full blur-[120px] pointer-events-none" />

            <div className="text-center mb-12 relative z-10">
                <h1 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">
                    Verify <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Content</span>
                </h1>
                <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                    Paste text or a URL to check its veracity with military-grade AI analysis.
                </p>
            </div>

            {/* Input Section */}
            <div className="glass-panel p-6 mb-8">
                <div className="flex gap-4 mb-6">
                    <button
                        onClick={() => setInputType('text')}
                        className={`flex-1 py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${inputType === 'text'
                            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                            }`}
                    >
                        <FileText className="w-4 h-4" /> Text
                    </button>
                    <button
                        onClick={() => setInputType('url')}
                        className={`flex-1 py-3 rounded-lg flex items-center justify-center gap-2 transition-all ${inputType === 'url'
                            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                            }`}
                    >
                        <LinkIcon className="w-4 h-4" /> URL
                    </button>
                </div>

                <div className="relative">
                    {inputType === 'text' ? (
                        <textarea
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            placeholder="Paste the text you want to verify here..."
                            className="w-full h-48 bg-black/50 border border-white/10 rounded-xl p-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 resize-none transition-all"
                        />
                    ) : (
                        <input
                            type="url"
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            placeholder="https://example.com/article"
                            className="w-full bg-black/50 border border-white/10 rounded-xl p-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
                        />
                    )}
                </div>

                <div className="mt-6 flex justify-end">
                    <button
                        onClick={handleVerify}
                        disabled={loading || !content.trim()}
                        className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg font-bold text-white shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
                    >
                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                        {loading ? 'Analyzing...' : 'Verify Now'}
                    </button>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 mb-8 flex items-center gap-2"
                >
                    <AlertCircle className="w-5 h-5" />
                    {error}
                </motion.div>
            )}

            {/* Result Section */}
            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-6"
                    >
                        {/* Verdict Card */}
                        <div className={`glass-panel p-8 text-center border-2 ${result.verdict ? 'border-green-500/50 shadow-[0_0_30px_rgba(0,255,157,0.2)]' : 'border-red-500/50 shadow-[0_0_30px_rgba(255,0,85,0.2)]'
                            }`}>
                            <div className={`inline-flex items-center gap-2 px-6 py-2 rounded-full text-lg font-bold mb-4 ${result.verdict ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                                }`}>
                                {result.verdict ? <CheckCircle className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
                                {result.verdict ? 'VERIFIED TRUE' : 'POTENTIALLY FALSE'}
                            </div>
                            <h2 className="text-2xl font-bold mb-2">Analysis Complete</h2>
                            <p className="text-gray-400">Here is what our AI found based on the provided content.</p>
                        </div>

                        {/* Analysis Details */}
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="glass-panel p-6">
                                <h3 className="text-cyan-400 font-bold mb-4 flex items-center gap-2">
                                    <span>🤖</span> AI Reasoning
                                </h3>
                                <p className="text-gray-300 leading-relaxed">
                                    {result.reasoning}
                                </p>
                            </div>

                            <div className="glass-panel p-6">
                                <h3 className="text-cyan-400 font-bold mb-4 flex items-center gap-2">
                                    <span>📌</span> Extracted Claims
                                </h3>
                                <ul className="space-y-3">
                                    {result.claims.map((claim: string, i: number) => (
                                        <li key={i} className="flex items-start gap-3 text-gray-300 text-sm">
                                            <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-cyan-500 flex-shrink-0" />
                                            {claim}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        {/* Sources */}
                        {Object.keys(result.website_claims || {}).length > 0 && (
                            <div className="glass-panel p-6">
                                <h3 className="text-cyan-400 font-bold mb-4 flex items-center gap-2">
                                    <span>🌐</span> Sources Analyzed
                                </h3>
                                <div className="space-y-4">
                                    {Object.entries(result.website_claims).map(([url, claims]: [string, any], i) => (
                                        <div key={i} className="bg-white/5 rounded-lg p-4">
                                            <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline break-all block mb-2">
                                                {url}
                                            </a>
                                            <p className="text-xs text-gray-500">{claims.length} claims verified against this source</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
