'use client';

import { motion } from 'framer-motion';

const categories = [
    { id: 'all', label: 'All', icon: '📋' },
    { id: 'technology', label: 'Technology', icon: '💻' },
    { id: 'politics', label: 'Politics', icon: '🏛️' },
    { id: 'sports', label: 'Sports', icon: '⚽' },
    { id: 'finance', label: 'Finance', icon: '💰' },
    { id: 'crime', label: 'Crime', icon: '🚨' },
];

interface CategoryFilterProps {
    activeCategory: string;
    onSelect: (category: string) => void;
}

export default function CategoryFilter({ activeCategory, onSelect }: CategoryFilterProps) {
    return (
        <div className="flex flex-wrap gap-3 justify-center py-8">
            {categories.map((cat) => (
                <button
                    key={cat.id}
                    onClick={() => onSelect(cat.id)}
                    className={`relative px-6 py-3 rounded-full flex items-center gap-2 transition-all duration-300 glass-panel border backdrop-blur-xl ${activeCategory === cat.id
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50 shadow-[0_0_25px_rgba(0,242,255,0.4)]'
                        : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10 hover:text-white hover:border-white/30 hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]'
                        }`}
                >
                    <span className="text-lg relative z-10">{cat.icon}</span>
                    <span className="font-medium relative z-10">{cat.label}</span>
                    {activeCategory === cat.id && (
                        <motion.div
                            layoutId="active-pill"
                            className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-500/20"
                            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        />
                    )}
                </button>
            ))}
        </div>
    );
}
