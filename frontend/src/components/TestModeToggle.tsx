'use client';

/**
 * Test Mode Toggle — UI switch for test/production mode.
 *
 * =============================================================
 * IMPACT TRACE
 * =============================================================
 * FILE: components/TestModeToggle.tsx
 * LAST UPDATED: created with change: "moved TEST_MODE from run.py to frontend"
 *
 * WHAT THIS FILE DOES:
 *   Renders a toggle switch showing current mode (TEST or PROD).
 *   Test mode uses cheaper models (gpt-5.4-mini) and fewer API calls.
 *   Production mode uses full models (gpt-5.4) and full API limits.
 *
 * BEHAVIOR CONTRACTS:
 *   • TestModeToggle() — React component rendering the toggle UI.
 *      Returns: JSX.Element with switch, labels, and visual indicators.
 *      Side effects: Calls toggleTestMode() from context on click.
 *
 * PROVIDES TO OTHER FILES:
 *   → Navbar.tsx         |  TestModeToggle component for header
 *   → app/verify/page.tsx |  Visual indicator of current mode
 *
 * NEEDS FROM OTHER FILES:
 *   ← contexts/TestModeContext.tsx  |  useTestMode hook (testMode, toggleTestMode)
 *
 * IMPACT: If this file changes, it directly affects:
 *   ⚡ Navbar.tsx  — may need layout adjustments for toggle placement
 *
 * ASSUMPTIONS THIS FILE MAKES:
 *   - TestModeContext is available (wrapped by provider in layout.tsx)
 *   - Test mode ON = green/yellow indicator (cheaper/safer)
 *   - Production mode = blue/purple indicator (full power)
 * =============================================================
 */

import { useTestMode } from '@/contexts/TestModeContext';
import { FlaskConical, Zap, AlertTriangle } from 'lucide-react';

export default function TestModeToggle() {
  const { testMode, toggleTestMode } = useTestMode();

  return (
    <button
      onClick={toggleTestMode}
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium
        transition-all duration-300 border
        ${testMode 
          ? 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400 hover:bg-yellow-500/30' 
          : 'bg-purple-500/20 border-purple-500/50 text-purple-400 hover:bg-purple-500/30'
        }
      `}
      title={testMode 
        ? 'Test Mode: Using gpt-5.4-mini, limited Tavily results (cheaper)' 
        : 'Production Mode: Using full gpt-5.4, full Tavily results'
      }
    >
      {testMode ? (
        <>
          <FlaskConical className="w-3.5 h-3.5" />
          <span>TEST MODE</span>
        </>
      ) : (
        <>
          <Zap className="w-3.5 h-3.5" />
          <span>PROD MODE</span>
          <AlertTriangle className="w-3 h-3 text-orange-400" />
        </>
      )}
    </button>
  );
}
