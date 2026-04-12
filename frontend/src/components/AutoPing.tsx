'use client';

/**
 * AutoPing Component — keeps Render services awake by pinging backend.
 *
 * =============================================================
 * IMPACT TRACE
 * =============================================================
 * FILE: components/AutoPing.tsx
 * LAST UPDATED: created with change: "frontend auto-ping for Render"
 *
 * WHAT THIS FILE DOES:
 *   Client-side component that pings backend health endpoint every 10 min.
 *   Works with backend auto_ping.py for mutual keep-alive.
 *   Silent operation - no UI, only console logs.
 *
 * BEHAVIOR CONTRACTS:
 *   • AutoPing() → React component with no props, no visual output
 *      Runs useEffect on mount, pings every 10 min until unmount
 *      Pings: https://voidtruth.onrender.com/api/health
 *
 * PROVIDES TO OTHER FILES:
 *   → layout.tsx  |  <AutoPing /> included in body (silent)
 *
 * NEEDS FROM OTHER FILES:
 *   (none — self-contained)
 *
 * IMPACT: If this file changes, it directly affects:
 *   ⚡ layout.tsx  — must include this component to activate pinging
 *
 * ASSUMPTIONS THIS FILE MAKES:
 *   - Backend health endpoint is at /api/health
 *   - 10 min interval keeps Render free tier awake
 *   - Runs only in browser (useEffect), safe for SSR
 * =============================================================
 */

import { useEffect } from 'react';

const BACKEND_URL = 'https://voidtruth.onrender.com/api/health';
const INTERVAL_MS = 10 * 60 * 1000; // 10 minutes

export default function AutoPing() {
  useEffect(() => {
    // Ping function
    const pingBackend = async () => {
      try {
        const res = await fetch(BACKEND_URL, { 
          method: 'GET',
          cache: 'no-store'
        });
        console.log(`[Frontend AutoPing] Backend status: ${res.status}`);
      } catch (err) {
        console.log(`[Frontend AutoPing] Backend ping failed: ${err}`);
      }
    };

    // Initial ping on mount
    pingBackend();

    // Set up interval
    const interval = setInterval(pingBackend, INTERVAL_MS);

    // Cleanup on unmount
    return () => clearInterval(interval);
  }, []);

  // No visual output - silent component
  return null;
}
