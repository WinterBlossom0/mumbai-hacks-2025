'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function CustomCursor() {
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [isHovering, setIsHovering] = useState(false);

    useEffect(() => {
        const updateMousePosition = (e: MouseEvent) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
        };

        const handleMouseOver = (e: MouseEvent) => {
            if ((e.target as HTMLElement).tagName === 'BUTTON' ||
                (e.target as HTMLElement).tagName === 'A' ||
                (e.target as HTMLElement).closest('.cursor-hover') ||
                (e.target as HTMLElement).closest('[role="button"]')) {
                setIsHovering(true);
            } else {
                setIsHovering(false);
            }
        };

        window.addEventListener('mousemove', updateMousePosition);
        window.addEventListener('mouseover', handleMouseOver);

        return () => {
            window.removeEventListener('mousemove', updateMousePosition);
            window.removeEventListener('mouseover', handleMouseOver);
        };
    }, []);

    return (
        <motion.div
            className="fixed top-0 left-0 pointer-events-none z-[9999] flex items-center justify-center"
            animate={{
                x: mousePosition.x,
                y: mousePosition.y,
                scale: isHovering ? 1.5 : 1,
                rotate: 45,
                translateX: '-50%',
                translateY: '-50%'
            }}
            transition={{
                type: 'spring',
                stiffness: 500,
                damping: 28,
                mass: 0.5
            }}
            style={{
                width: '30px',
                height: '30px',
                border: '2px solid #00f2ff', // Using the primary cyan color
                borderRadius: '75% 0',
                background: 'rgba(0, 0, 0, 0.2)',
                boxShadow: '0 0 20px rgba(0, 242, 255, 0.4)',
                mixBlendMode: 'difference',
            }}
        >
            {/* The pupil */}
            <div
                style={{
                    width: '12px',
                    height: '12px',
                    background: '#00f2ff',
                    borderRadius: '50%',
                    boxShadow: '0 0 15px #00f2ff',
                }}
            />
        </motion.div>
    );
}
