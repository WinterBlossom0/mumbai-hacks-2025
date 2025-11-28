#!/usr/bin/env python3
"""
Standalone runner script for the Truth Lens Telegram Bot.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from telegram_bot import TruthLensBot


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
