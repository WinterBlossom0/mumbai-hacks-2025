#!/usr/bin/env python3
"""
Telegram Bot for Truth Lens - AI-Powered Fact Verification
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Add backend directory to path (go up two levels: bot/ -> telegram-bot/ -> project root -> backend/)
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from main.claim_extractor import ClaimExtractor
from main.claim_discoverer import ClaimDiscoverer
from main.reasoning import ClaimReasoner
from database.supabase_client import SupabaseClient
from bot.announcement_service import AnnouncementService


# Load .env from project root (go up two levels: bot/ -> telegram-bot/ -> project root)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TruthLensBot:
    """Telegram bot for fact verification using Truth Lens pipeline."""

    def __init__(self):
        """Initialize the bot with API token."""
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        # Initialize announcement service if channel ID is configured
        self.announcement_service = None
        channel_id = os.getenv("TELEGRAM_ANNOUNCEMENT_CHANNEL_ID")
        if channel_id:
            try:
                self.announcement_service = AnnouncementService(self.token, channel_id)
                logger.info("Announcement service enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize announcement service: {e}")
        else:
            logger.info("Announcement service disabled (no channel ID configured)")


    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """
🔍 *Welcome to Truth Lens Bot!*

I can help you verify claims and detect misinformation using advanced AI analysis.

*How to use:*
• Send me any text claim to verify
• Send me a URL to analyze the content
• I'll extract claims, find sources, and provide a verdict

*Commands:*
/start - Show this welcome message
/help - Get help and usage tips

Just send me something to verify and I'll get started! 🚀
"""
        await update.message.reply_text(
            welcome_message,
            parse_mode="Markdown",
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📖 *Help - How to Use Truth Lens Bot*

*What I Do:*
I analyze claims using AI to determine if they're true or false.

*How It Works:*
1️⃣ Extract key claims from your input
2️⃣ Find credible sources online
3️⃣ Analyze evidence using advanced AI
4️⃣ Provide a verdict with detailed reasoning

*Examples:*

*Text Verification:*
Send: "The Earth is flat"
I'll verify this claim for you

*URL Verification:*
Send: https://example.com/article
I'll scrape and verify the content

*Tips:*
• Be specific with your claims
• Verification takes 30-60 seconds
• I provide sources for transparency

*Commands:*
/start - Welcome message
/help - This help message

Have questions? Just send me your claim! 💡
"""
        await update.message.reply_text(
            help_message,
            parse_mode="Markdown",
        )

    def is_url(self, text: str) -> bool:
        """Check if text is a URL."""
        return text.startswith("http://") or text.startswith("https://")

    async def verify_content(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle text/URL messages and verify content."""
        # Handle both regular messages and channel posts
        message = update.message or update.channel_post
        if not message:
            return
        user_input = message.text
        
        # Get user/channel info
        if update.effective_user:
            user_id = str(update.effective_user.id)
            user_name = update.effective_user.username or update.effective_user.first_name
        elif update.effective_chat:
            user_id = str(update.effective_chat.id)
            user_name = update.effective_chat.title or "Channel"

        # Determine input type
        input_type = "url" if self.is_url(user_input) else "text"

        # Send processing message
        processing_msg = await message.reply_text(
            "🔍 *Analyzing your content...*\n\n"
            "This may take 30-60 seconds. Please wait...",
            parse_mode="Markdown",
        )

        try:
            logger.info(f"Processing {input_type} from user {user_name}: {user_input[:100]}")

            # Step 1: Extract claims
            await processing_msg.edit_text(
                "🔍 *Step 1/4:* Extracting claims...",
                parse_mode="Markdown",
            )

            extractor = ClaimExtractor(max_tokens_per_chunk=15000)

            if input_type == "url":
                result = extractor.extract_claims_from_url(user_input, key_name="user")
            else:
                result = extractor.extract_claims(user_input, key_name="user")

            if not result["user"]:
                await processing_msg.edit_text(
                    "❌ *Error:* No claims could be extracted from the content.\n\n"
                    "Please try with different content.",
                    parse_mode="Markdown",
                )
                return

            claims = result["user"]
            logger.info(f"Extracted {len(claims)} claims")

            # Step 2: Discover sources
            await processing_msg.edit_text(
                f"🔍 *Step 2/4:* Finding credible sources...\n\n"
                f"Found {len(claims)} claims",
                parse_mode="Markdown",
            )

            discoverer = ClaimDiscoverer()
            sources = discoverer.discover_sources(claims)

            all_urls = []
            for urls in sources.values():
                all_urls.extend(urls)
            all_urls = list(set(all_urls))

            if not all_urls:
                await processing_msg.edit_text(
                    "❌ *Error:* No credible sources found for verification.\n\n"
                    "Please check your API keys or try different content.",
                    parse_mode="Markdown",
                )
                return

            logger.info(f"Discovered {len(all_urls)} unique sources")

            # Step 3: Extract website claims
            await processing_msg.edit_text(
                f"🔍 *Step 3/4:* Analyzing sources...\n\n"
                f"Found {len(all_urls)} sources",
                parse_mode="Markdown",
            )

            website_claims = extractor.extract_website_claims(all_urls, claims)

            all_website_claims_flat = {}
            for url, wclaims in website_claims.items():
                if wclaims:
                    all_website_claims_flat[url] = wclaims

            if not all_website_claims_flat:
                await processing_msg.edit_text(
                    "❌ *Error:* Could not extract claims from sources.\n\n"
                    "Please try again later.",
                    parse_mode="Markdown",
                )
                return

            logger.info(f"Extracted claims from {len(all_website_claims_flat)} websites")

            # Step 4: Reasoning
            await processing_msg.edit_text(
                f"🔍 *Step 4/4:* AI reasoning and verification...",
                parse_mode="Markdown",
            )

            reasoner = ClaimReasoner()
            final_result = reasoner.reason_all_claims(claims, all_website_claims_flat)

            logger.info(f"Final verdict: {final_result['verdict']}")

            # Save to database
            try:
                db = SupabaseClient()
                db.save_verification(
                    user_id=user_id,
                    user_email=f"{user_name}@telegram",
                    input_content=user_input,
                    input_type=input_type,
                    verdict=final_result["verdict"],
                    reasoning=final_result["reasoning"],
                    claims=claims,
                    sources=sources,
                )
            except Exception as e:
                logger.warning(f"Failed to save to database: {e}")

            # Format and send result
            verdict_emoji = "✅" if final_result["verdict"] else "❌"
            verdict_text = "TRUE" if final_result["verdict"] else "FALSE"

            # Bitly URL shortening
            def shorten_url(url: str) -> str:
                """Shorten URL using Bitly API with fallback to Rebrandly and then truncation."""
                import requests
                
                # 1. Try Bitly
                bitly_token = os.getenv("BITLY_ACCESS_TOKEN")
                if bitly_token:
                    try:
                        # Bitly API endpoint
                        api_url = "https://api-ssl.bitly.com/v4/shorten"
                        
                        headers = {
                            "Authorization": f"Bearer {bitly_token}",
                            "Content-Type": "application/json"
                        }
                        
                        payload = {
                            "long_url": url
                        }
                        
                        # Make request to Bitly API
                        response = requests.post(api_url, json=payload, headers=headers, timeout=5)
                        
                        if response.status_code in [200, 201]:
                            data = response.json()
                            short_url = data.get("link", "")
                            if short_url:
                                logger.info(f"Shortened URL using Bitly: {short_url}")
                                return short_url
                        else:
                            logger.warning(f"Bitly API error: {response.status_code} - {response.text[:200]}")
                            
                    except Exception as e:
                        logger.warning(f"Failed to shorten URL with Bitly: {e}")
                else:
                    logger.warning("BITLY_ACCESS_TOKEN not configured")

                # 2. Try Rebrandly (Fallback)
                rebrandly_token = os.getenv("REBRANDLY_ACCESS_TOKEN")
                if rebrandly_token:
                    try:
                        logger.info("Attempting fallback to Rebrandly...")
                        api_url = "https://api.rebrandly.com/v1/links"
                        
                        headers = {
                            "apikey": rebrandly_token,
                            "Content-Type": "application/json"
                        }
                        
                        payload = {
                            "destination": url
                        }
                        
                        response = requests.post(api_url, json=payload, headers=headers, timeout=5)
                        
                        if response.status_code == 200:
                            data = response.json()
                            short_url = data.get("shortUrl", "")
                            if short_url:
                                # Rebrandly returns shortUrl without protocol usually, ensure it has https://
                                if not short_url.startswith("http"):
                                    short_url = "https://" + short_url
                                logger.info(f"Shortened URL using Rebrandly: {short_url}")
                                return short_url
                        else:
                            logger.warning(f"Rebrandly API error: {response.status_code} - {response.text[:200]}")

                    except Exception as e:
                        logger.warning(f"Failed to shorten URL with Rebrandly: {e}")
                else:
                    logger.warning("REBRANDLY_ACCESS_TOKEN not configured")
                
                # 3. Fallback to truncated URL
                logger.info("Using truncated URL as fallback")
                return url[:50] + "..." if len(url) > 50 else url


            # Build concise response
            response = f"{verdict_emoji} *VERDICT: {verdict_text}*\n\n"
            
            # Shortened reasoning (max 400 chars)
            reasoning = final_result['reasoning']
            if len(reasoning) > 400:
                # Find last complete sentence within 400 chars
                truncated = reasoning[:400]
                last_period = truncated.rfind('.')
                if last_period > 200:  # Only use if we found a period reasonably far in
                    reasoning = reasoning[:last_period + 1]
                else:
                    reasoning = truncated + "..."
            
            response += f"*📊 Analysis:*\n{reasoning}\n\n"
            
            # Show only top 3 claims, max 80 chars each
            response += f"*🔍 Key Claims ({len(claims)}):*\n"
            for i, claim in enumerate(claims[:3], 1):
                short_claim = claim[:80] + "..." if len(claim) > 80 else claim
                response += f"{i}. {short_claim}\n"
            
            if len(claims) > 3:
                response += f"_+{len(claims) - 3} more_\n"
            
            # Sources with shortened URLs
            response += f"\n*📚 Sources:* {len(all_website_claims_flat)}\n"
            response += "*🔗 Checked:*\n"
            for i, url in enumerate(list(all_website_claims_flat.keys())[:3], 1):
                short_url = shorten_url(url)
                response += f"• {short_url}\n"

            await processing_msg.edit_text(response, parse_mode="Markdown")
            logger.info(f"Successfully verified content for user {user_name}")

        except Exception as e:
            logger.error(f"Error during verification: {e}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ *Error during verification:*\n\n{str(e)[:200]}\n\n"
                "Please try again or contact support.",
                parse_mode="Markdown",
            )

    async def error_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle errors."""
        logger.error(f"Update {update} caused error {context.error}")

    def run(self):
        """Run the bot."""
        logger.info("Starting Truth Lens Telegram Bot...")

        # Create application
        application = Application.builder().token(self.token).build()

        # Add handlers for private messages
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Handler for private messages
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.verify_content)
        )
        
        # Handler for channel posts (when bot is admin in a channel)
        from telegram.ext import MessageHandler as MH
        application.add_handler(
            MH(filters.UpdateType.CHANNEL_POST & filters.TEXT, self.verify_content)
        )

        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Add announcement background task if enabled
        if self.announcement_service:
            job_queue = application.job_queue
            job_queue.run_repeating(
                self.announcement_task,
                interval=60,  # Run every 60 seconds
                first=10,  # Start after 10 seconds
                name="announcement_task"
            )
            logger.info("Announcement background task scheduled (60s interval)")

        # Start the bot
        logger.info("Bot is running! Press Ctrl+C to stop.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def announcement_task(self, context: ContextTypes.DEFAULT_TYPE):
        """Background task for announcement service."""
        if self.announcement_service:
            try:
                await self.announcement_service.process_unannounced_items()
            except Exception as e:
                logger.error(f"Error in announcement task: {e}", exc_info=True)



def main():
    """Main entry point."""
    try:
        bot = TruthLensBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
