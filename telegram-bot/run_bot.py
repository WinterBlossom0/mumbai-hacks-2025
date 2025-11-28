#!/usr/bin/env python3
"""
Standalone runner script for the Truth Lens Telegram Bot.
"""

import sys
from pathlib import Path

# Add current directory to path for local backend imports
sys.path.insert(0, str(Path(__file__).parent))

from bot.telegram_bot import TruthLensBot
from health_server import start_health_server


def main():
    print("=" * 70)
    print("Truth Lens - Telegram Bot")
    print("=" * 70)
    print()
    print("Starting Telegram bot...")
    print("The bot will start polling for messages.")
    print()
    print("Press Ctrl+C to stop the bot")
    print("=" * 70)
    print()

    try:
        # Start health check server for Render keep-alive
        start_health_server()
        
        bot = TruthLensBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n\n✓ Bot stopped")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
