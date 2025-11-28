'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { UserButton, SignInButton, useUser } from '@clerk/nextjs';
import { Home, Search, History, MessageSquare, Menu, X, Eye } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar() {
    const pathname = usePathname();
    const { isSignedIn, isLoaded } = useUser();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const navLinks = [
        { href: '/', label: 'Home', icon: Home },
        { href: '/verify', label: 'Verify', icon: Search },
        { href: '/history', label: 'History', icon: History },
        { href: '/reddit', label: 'Reddit', icon: MessageSquare },
    ];

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-black/10 backdrop-blur-xl border-b border-white/5 supports-[backdrop-filter]:bg-black/5">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-20">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-3 group cursor-hover">
                        <div className="relative w-10 h-10 flex items-center justify-center">
                            <div className="absolute inset-0 bg-cyan-500/20 rounded-xl blur-lg group-hover:blur-xl transition-all" />
                            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400/10 to-blue-600/10 border border-white/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-300 backdrop-blur-md">
                                <Eye className="w-6 h-6 text-cyan-400" />
                            </div>
                        </div>
                        <span className="font-bold text-2xl tracking-tight">
                            Truth<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Lens</span>
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center gap-4">
                        {navLinks.map((link) => {
                            const Icon = link.icon;
                            const isActive = pathname === link.href;
                            return (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    className={`relative px-5 py-2.5 rounded-full flex items-center gap-2 text-sm font-medium transition-all duration-300 cursor-hover glass-panel border backdrop-blur-md ${isActive
                                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50 shadow-[0_0_20px_rgba(0,242,255,0.3)]'
                                        : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10 hover:text-white hover:border-white/30 hover:shadow-[0_0_15px_rgba(255,255,255,0.1)]'
                                        }`}
                                >
                                    <Icon className="w-4 h-4 relative z-10" />
                                    <span className="relative z-10">{link.label}</span>
                                    {isActive && (
                                        <motion.div
                                            layoutId="nav-pill"
                                            className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-500/20"
                                            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                                        />
                                    )}
                                </Link>
                            );
                        })}
                    </div>

                    {/* Auth & Mobile Menu Button */}
                    <div className="flex items-center gap-4">
                        {isLoaded && (
                            <div className="flex items-center cursor-hover">
                                {isSignedIn ? (
                                    <UserButton
                                        afterSignOutUrl="/"
                                        appearance={{
                                            elements: {
                                                avatarBox: "w-9 h-9 border-2 border-white/10 hover:border-cyan-400 transition-colors"
                                            }
                                        }}
                                    />
                                ) : (
                                    <SignInButton mode="modal">
                                        <button className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm font-medium transition-colors border border-white/10">
                                            Sign In
                                        </button>
                                    </SignInButton>
                                )}
                            </div>
                        )}

                        <button
                            className="md:hidden p-2 text-gray-400 hover:text-white cursor-hover"
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        >
                            {isMobileMenuOpen ? <X /> : <Menu />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden bg-black/90 border-b border-white/10 overflow-hidden"
                    >
                        <div className="px-4 py-4 space-y-2">
                            {navLinks.map((link) => {
                                const Icon = link.icon;
                                const isActive = pathname === link.href;
                                return (
                                    <Link
                                        key={link.href}
                                        href={link.href}
                                        onClick={() => setIsMobileMenuOpen(false)}
                                        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive ? 'bg-white/10 text-cyan-400' : 'text-gray-400 hover:bg-white/5 hover:text-white'
                                            }`}
                                    >
                                        <Icon className="w-5 h-5" />
                                        {link.label}
                                    </Link>
                                );
                            })}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
}
