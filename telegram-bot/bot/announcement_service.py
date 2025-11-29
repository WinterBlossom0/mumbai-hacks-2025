#!/usr/bin/env python3
"""
Telegram Announcement Service for Truth Lens
Broadcasts newly detected fake news to a configured Telegram channel
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from dotenv import load_dotenv
from datetime import datetime

from telegram import Bot
from telegram.error import TelegramError, RetryAfter, TimedOut
from telegram.helpers import escape_markdown

# Add backend directory to path (go up two levels: bot/ -> telegram-bot/ -> project root -> backend/)
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from database.supabase_client import SupabaseClient

# Load .env from project root (go up two levels: bot/ -> telegram-bot/ -> project root)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class AnnouncementService:
    """Service for announcing fake news detections to Telegram channel."""

    def __init__(self, bot_token: str, channel_id: str):
        """
        Initialize the announcement service.
        
        Args:
            bot_token: Telegram bot token
            channel_id: Channel ID to post announcements (format: -100xxxxxxxxxx)
        """
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        self.db = SupabaseClient()
        logger.info(f"Announcement service initialized for channel: {channel_id}")


# ... (imports remain the same)

    def format_announcement_message(self, verification: Dict) -> str:
        """
        Format a verification record into an announcement message.
        
        Args:
            verification: Verification record from database
            
        Returns:
            Formatted message string
        """
        # Extract data
        input_content = verification.get("input_content", "")
        reasoning = verification.get("reasoning", "")
        claims = verification.get("claims", [])
        sources = verification.get("sources", {})
        created_at = verification.get("created_at", "")
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            timestamp = dt.strftime("%B %d, %Y at %I:%M %p UTC")
        except:
            timestamp = "Recently"
            
        # Helper for escaping
        def esc(text):
            return escape_markdown(str(text), version=1)
        
        # Build message
        message = "🚨 *FAKE NEWS ALERT* 🚨\n\n"
        message += "❌ *VERDICT: FALSE*\n\n"
        
        # Add headline/content preview
        message += "*📰 Content:*\n"
        content_preview = input_content[:200] + "..." if len(input_content) > 200 else input_content
        message += f"{esc(content_preview)}\n\n"
        
        # Add reasoning (shortened)
        message += "*🔍 Why This is Fake:*\n"
        reasoning_short = reasoning[:300] + "..." if len(reasoning) > 300 else reasoning
        message += f"{esc(reasoning_short)}\n\n"
        
        # Add key claims (max 3)
        if claims:
            message += f"*📋 Key Claims ({len(claims)}):*\n"
            for i, claim in enumerate(claims[:3], 1):
                claim_short = claim[:80] + "..." if len(claim) > 80 else claim
                message += f"{i}. {esc(claim_short)}\n"
            if len(claims) > 3:
                message += f"_+{len(claims) - 3} more claims_\n"
            message += "\n"
        
        # Add sources count
        all_sources = []
        for urls in sources.values():
            all_sources.extend(urls)
        unique_sources = list(set(all_sources))
        
        if unique_sources:
            message += f"*📚 Verified Against {len(unique_sources)} Sources*\n\n"
        
        # Footer
        message += f"⏰ Detected: {esc(timestamp)}\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n"
        message += "🔔 Stay informed\. Stay safe\. Share this alert\!"
        
        return message

    async def broadcast_to_channel(self, message: str, retry_count: int = 3) -> bool:
        """
        Broadcast a message to the configured channel.
        
        Args:
            message: Message to broadcast
            retry_count: Number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(retry_count):
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                )
                logger.info(f"Successfully broadcast message to channel {self.channel_id}")
                return True
                
            except RetryAfter as e:
                # Telegram rate limiting
                wait_time = e.retry_after + 1
                logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
            except TimedOut:
                logger.warning(f"Timeout on attempt {attempt + 1}/{retry_count}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except TelegramError as e:
                logger.error(f"Telegram error on attempt {attempt + 1}/{retry_count}: {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return False
                    
            except Exception as e:
                logger.error(f"Unexpected error broadcasting message: {e}", exc_info=True)
                return False
        
        return False

    async def process_unannounced_items(self) -> int:
        """
        Process and announce all unannounced fake news items from both tables.
        
        Returns:
            Number of items successfully announced
        """
        try:
            announced_count = 0
            
            # Process verifications
            verifications = self.db.get_unannounced_fake_news(channel_id=self.channel_id, limit=5)
            if verifications:
                logger.info(f"Found {len(verifications)} unannounced fake news verifications")
                
                for item in verifications:
                    try:
                        message = self.format_announcement_message(item)
                        success = await self.broadcast_to_channel(message)
                        
                        if success:
                            verification_id = item.get("id")
                            if self.db.mark_as_announced(verification_id, self.channel_id):
                                announced_count += 1
                                logger.info(f"Announced verification {verification_id}")
                            else:
                                logger.error(f"Failed to mark verification {verification_id} as announced")
                        else:
                            logger.error(f"Failed to broadcast verification {item.get('id')}")
                        
                        await asyncio.sleep(2)  # Delay between announcements
                        
                    except Exception as e:
                        logger.error(f"Error processing verification {item.get('id')}: {e}", exc_info=True)
                        continue
            
            # Process Reddit posts
            reddit_posts = self.db.get_unannounced_reddit_fake_news(channel_id=self.channel_id, limit=5)
            if reddit_posts:
                logger.info(f"Found {len(reddit_posts)} unannounced fake Reddit posts")
                
                for post in reddit_posts:
                    try:
                        message = self.format_reddit_announcement(post)
                        success = await self.broadcast_to_channel(message)
                        
                        if success:
                            post_id = post.get("id")
                            if self.db.mark_reddit_post_as_announced(post_id, self.channel_id):
                                announced_count += 1
                                logger.info(f"Announced Reddit post {post_id}")
                            else:
                                logger.error(f"Failed to mark Reddit post {post_id} as announced")
                        else:
                            logger.error(f"Failed to broadcast Reddit post {post.get('id')}")
                        
                        await asyncio.sleep(2)  # Delay between announcements
                        
                    except Exception as e:
                        logger.error(f"Error processing Reddit post {post.get('id')}: {e}", exc_info=True)
                        continue
            
            if announced_count == 0:
                logger.debug("No unannounced fake news found")
            
            return announced_count
            
        except Exception as e:
            logger.error(f"Error in process_unannounced_items: {e}", exc_info=True)
            return 0

    def format_reddit_announcement(self, post: Dict) -> str:
        """
        Format a Reddit post into an announcement message.
        
        Args:
            post: Reddit post record from database
            
        Returns:
            Formatted message string
        """
        # Extract data
        title = post.get("title", "")
        body = post.get("body", "")
        url = post.get("url", "")
        headline = post.get("headline", "")
        reasoning = post.get("reasoning", "")
        claims = post.get("claims", [])
        sources = post.get("sources", {})
        author = post.get("author", "Unknown")
        subreddit = post.get("subreddit", "eyeoftruth")
        created_at = post.get("created_at", "")
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            timestamp = dt.strftime("%B %d, %Y at %I:%M %p UTC")
        except:
            timestamp = "Recently"
            
        # Helper for escaping
        def esc(text):
            return escape_markdown(str(text), version=1)
        
        # Build message
        message = "🚨 *FAKE NEWS ALERT - REDDIT POST* 🚨\n\n"
        message += "❌ *VERDICT: FALSE*\n\n"
        
        # Add headline if available
        if headline:
            message += f"*📰 Headline:*\n{esc(headline)}\n\n"
        
        # Add title
        message += f"*📝 Post Title:*\n{esc(title[:200])}{'...' if len(title) > 200 else ''}\n\n"
        
        # Add body preview if available
        if body:
            body_preview = body[:200] + "..." if len(body) > 200 else body
            message += f"*📄 Content:*\n{esc(body_preview)}\n\n"
        
        # Add URL if available
        if url:
            message += f"*🔗 Source URL:*\n{esc(url)}\n\n"
        
        # Add reasoning
        if reasoning:
            reasoning_short = reasoning[:300] + "..." if len(reasoning) > 300 else reasoning
            message += f"*🔍 Why This is Fake:*\n{esc(reasoning_short)}\n\n"
        
        # Add key claims (max 3)
        if claims:
            message += f"*📋 Key Claims ({len(claims)}):*\n"
            for i, claim in enumerate(claims[:3], 1):
                claim_short = claim[:80] + "..." if len(claim) > 80 else claim
                message += f"{i}. {esc(claim_short)}\n"
            if len(claims) > 3:
                message += f"_+{len(claims) - 3} more claims_\n"
            message += "\n"
        
        # Add sources count
        all_sources = []
        for urls in sources.values():
            all_sources.extend(urls)
        unique_sources = list(set(all_sources))
        
        if unique_sources:
            message += f"*📚 Verified Against {len(unique_sources)} Sources*\n\n"
        
        # Footer with Reddit info
        message += f"*👤 Posted by:* u/{esc(author)} on r/{esc(subreddit)}\n"
        message += f"⏰ Detected: {esc(timestamp)}\n"
        message += "━━━━━━━━━━━━━━━━━━━━\n"
        message += "🔔 Stay informed\. Stay safe\. Share this alert\!"
        
        return message

    async def poll_and_announce(self, interval: int = 60):
        """
        Continuously poll for new fake news and announce them.
        
        Args:
            interval: Polling interval in seconds (default: 60)
        """
        logger.info(f"Starting announcement polling (interval: {interval}s)")
        
        while True:
            try:
                announced = await self.process_unannounced_items()
                if announced > 0:
                    logger.info(f"Announced {announced} items in this cycle")
                
                # Wait for next cycle
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Announcement service stopped by user")
                break
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)
                # Continue after error with a longer delay
                await asyncio.sleep(interval * 2)


async def main():
    """Main entry point for standalone testing."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_ANNOUNCEMENT_CHANNEL_ID")
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        sys.exit(1)
    
    if not channel_id:
        logger.error("TELEGRAM_ANNOUNCEMENT_CHANNEL_ID not found in environment variables")
        sys.exit(1)
    
    service = AnnouncementService(bot_token, channel_id)
    await service.poll_and_announce()


if __name__ == "__main__":
    asyncio.run(main())
