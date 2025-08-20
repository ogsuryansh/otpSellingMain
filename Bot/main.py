#!/usr/bin/env python3
"""
Telegram OTP Bot - Main Entry Point
"""

import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from src.handlers.start_handler import handle_start
from src.handlers.callback_handler import handle_callback, handle_promocode_reply
from src.handlers.admin_handler import handle_admin
from src.config.bot_config import BotConfig
from src.database.user_db import UserDatabase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class OTPBot:
    def __init__(self):
        self.config = BotConfig()
        self.user_db = UserDatabase()
        self.application = None
    
    async def start_bot(self):
        """Initialize and start the bot"""
        try:
            logger.info("🔧 Creating application...")
            # Create application
            self.application = Application.builder().token(self.config.BOT_TOKEN).build()
            logger.info("✅ Application created")
            
            # Add handlers
            logger.info("📝 Adding handlers...")
            start_handler = CommandHandler("start", handle_start)
            callback_handler = CallbackQueryHandler(handle_callback)
            
            self.application.add_handler(start_handler)
            self.application.add_handler(callback_handler)
            
            logger.info(f"✅ Handlers added: {len(self.application.handlers)} handler groups")
            logger.info(f"📋 Handler details: {self.application.handlers}")
            
            # Initialize database
            logger.info("📊 Initializing database...")
            await self.user_db.initialize()
            logger.info("✅ Database initialized")
            
            logger.info("🚀 Bot started successfully!")
            
            # Start polling with simpler approach
            logger.info("🔄 Starting polling...")
            
            # Test bot token first
            try:
                bot_info = await self.application.bot.get_me()
                logger.info(f"🤖 Bot info: @{bot_info.username} ({bot_info.first_name})")
            except Exception as e:
                logger.error(f"❌ Failed to get bot info: {e}")
                return
            
            # Use run_polling instead of manual setup
            logger.info("🔄 Starting run_polling...")
            await self.application.run_polling(
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            raise

def main():
    """Main function to start the bot"""
    # Run the bot
    try:
        import asyncio
        from telegram.ext import Application
        
        # Simple approach - create and run directly
        application = Application.builder().token(os.getenv('BOT_TOKEN')).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", handle_start))
        application.add_handler(CommandHandler("admin", handle_admin))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_promocode_reply))
        
        print("Bot starting...")
        print("Bot is running... Send /start to test!")
        
        # Run polling
        application.run_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
