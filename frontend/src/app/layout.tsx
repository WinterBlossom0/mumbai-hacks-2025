import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ClerkProvider } from '@clerk/nextjs';
import Navbar from '@/components/Navbar';
import CustomCursor from '@/components/CustomCursor';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'Truth Lens - AI Fact Verification',
    description: 'Uncover the truth behind any claim with advanced AI analysis.',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <ClerkProvider>
            <html lang="en" className="dark">
                <body className={`${inter.className} min-h-screen bg-black text-white selection:bg-cyan-500/30 cursor-none`}>
                    <CustomCursor />
                    <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-black to-black pointer-events-none" />
                    <Navbar />
                    <main className="pt-20 min-h-screen">
                        {children}
                    </main>
                </body>
            </html>
        </ClerkProvider>
    );
}
