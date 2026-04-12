'use client';

/**
 * Test Mode Context — global toggle for test/production mode.
 *
 * =============================================================
 * IMPACT TRACE
 * =============================================================
 * FILE: contexts/TestModeContext.tsx
 * LAST UPDATED: created with change: "moved TEST_MODE from run.py to frontend"
 *
 * WHAT THIS FILE DOES:
 *   Provides a global React Context for test_mode state. Test mode is
 *   ON by default (gpt-5.4-mini, Tavily 1 result, max 2 URLs).
 *   Users must explicitly toggle OFF to use production models.
 *
 * BEHAVIOR CONTRACTS:
 *   • TestModeProvider({ children }) — Wraps app to provide context.
 *   • useTestMode() — Hook returning { testMode, setTestMode, toggleTestMode }.
 *      testMode: boolean (true = test mode ON)
 *      setTestMode: (bool) => void
 *      toggleTestMode: () => void (flips boolean)
 *
 * PROVIDES TO OTHER FILES:
 *   → app/layout.tsx        |  TestModeProvider wrapper
 *   → app/verify/page.tsx   |  useTestMode hook for verification calls
 *   → lib/api.ts            |  testMode flag for API requests
 *
 * NEEDS FROM OTHER FILES:
 *   (none — self-contained React context)
 *
 * IMPACT: If this file changes, it directly affects:
 *   ⚡ verify/page.tsx  — verification uses test_mode from this context
 *   ⚡ lib/api.ts       — all API calls may include test_mode param
 *
 * ASSUMPTIONS THIS FILE MAKES:
 *   - Test mode ON by default (safer/cheaper for development)
 *   - localStorage persists user preference across sessions
 * =============================================================
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

interface TestModeContextType {
  testMode: boolean;
  setTestMode: (value: boolean) => void;
  toggleTestMode: () => void;
}

const TestModeContext = createContext<TestModeContextType | undefined>(undefined);

const STORAGE_KEY = 'truth-lens-test-mode';

export function TestModeProvider({ children }: { children: React.ReactNode }) {
  // Test mode ON by default (safer for development)
  const [testMode, setTestModeState] = useState<boolean>(true);

  // Load from localStorage on mount (but default to true if not set)
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored !== null) {
      setTestModeState(stored === 'true');
    }
  }, []);

  // Persist to localStorage whenever it changes
  const setTestMode = useCallback((value: boolean) => {
    setTestModeState(value);
    localStorage.setItem(STORAGE_KEY, String(value));
    console.log(`[TestMode] Switched to ${value ? 'TEST' : 'PRODUCTION'} mode`);
  }, []);

  const toggleTestMode = useCallback(() => {
    setTestMode(!testMode);
  }, [testMode, setTestMode]);

  // Always provide context (even during SSR), localStorage loads after hydration
  return (
    <TestModeContext.Provider value={{ testMode, setTestMode, toggleTestMode }}>
      {children}
    </TestModeContext.Provider>
  );
}

export function useTestMode() {
  const context = useContext(TestModeContext);
  if (context === undefined) {
    throw new Error('useTestMode must be used within a TestModeProvider');
  }
  return context;
}
