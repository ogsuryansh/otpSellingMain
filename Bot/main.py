#!/usr/bin/env python3

import logging
import os
import asyncio
import signal
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, InlineQueryHandler, ChosenInlineResultHandler, filters

from src.handlers.start_handler import handle_start
from src.handlers.callback_handler import handle_callback, handle_promocode_reply
from src.handlers.admin_handler import handle_admin
from src.handlers.inline_handler import handle_inline_query, handle_chosen_inline_result
from src.handlers.service_handler import handle_show_server
from src.handlers.admin_commands import (
    handle_add_balance, handle_cut_balance, handle_transaction_history,
    handle_number_history, handle_smm_history, handle_ban_user,
    handle_unban_user, handle_broadcast, handle_delete_all_data,
    handle_sync_data, handle_sync_users, handle_sync_services, handle_check_sync_status
)
from src.config.bot_config import BotConfig
from src.database.user_db import UserDatabase
from src.utils.rate_limiter import initialize_rate_limiter, shutdown_rate_limiter
from src.utils.cache_manager import initialize_cache, shutdown_cache

load_dotenv()

from src.config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

class OTPBot:
    
    def __init__(self):
        self.config = BotConfig()
        self.user_db = UserDatabase()
        self.application = None
        
        if not self.config.validate_config():
            raise ValueError("Invalid bot configuration")
    
    async def initialize(self):
        try:
            logger.info("🔧 Initializing bot components...")
            
            await self.user_db.initialize()
            logger.info("✅ Database initialized")
            
            # Initialize utilities
            await initialize_rate_limiter()
            await initialize_cache()
            logger.info("✅ Utilities initialized")
            
            # Create application without job queue to avoid weak reference issues
            self.application = Application.builder().token(self.config.BOT_TOKEN).job_queue(None).build()
            logger.info("✅ Application created")
            
            await self._setup_handlers()
            logger.info("✅ Handlers configured")
            
            self._setup_signal_handlers()
            
            # Initialize the application
            await self.application.initialize()
            logger.info("✅ Application initialized")
            
            logger.info("🚀 Bot initialization completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            raise
    
    def _setup_signal_handlers(self):
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            # Use the current event loop to create the task
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.shutdown())
            except RuntimeError:
                # No running loop, just log the signal
                logger.info("Signal received but no event loop running")
            except Exception as e:
                logger.error(f"Error in signal handler: {e}")
        
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except Exception as e:
            logger.warning(f"Could not set up signal handlers: {e}")
    
    async def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", handle_start))
        self.application.add_handler(CommandHandler("admin", handle_admin))
        self.application.add_handler(CommandHandler("show_server", handle_show_server))
        
        self.application.add_handler(CommandHandler("add", handle_add_balance))
        self.application.add_handler(CommandHandler("cut", handle_cut_balance))
        self.application.add_handler(CommandHandler("trnx", handle_transaction_history))
        self.application.add_handler(CommandHandler("nums", handle_number_history))
        self.application.add_handler(CommandHandler("smm_history", handle_smm_history))
        self.application.add_handler(CommandHandler("ban", handle_ban_user))
        self.application.add_handler(CommandHandler("unban", handle_unban_user))
        self.application.add_handler(CommandHandler("broadcast", handle_broadcast))
        self.application.add_handler(CommandHandler("delalldata", handle_delete_all_data))
        self.application.add_handler(CommandHandler("sync", handle_sync_data))
        self.application.add_handler(CommandHandler("syncusers", handle_sync_users))
        self.application.add_handler(CommandHandler("syncservices", handle_sync_services))
        self.application.add_handler(CommandHandler("syncstatus", handle_check_sync_status))
        
        self.application.add_handler(CallbackQueryHandler(handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_promocode_reply))
        self.application.add_handler(InlineQueryHandler(handle_inline_query))
        self.application.add_handler(ChosenInlineResultHandler(handle_chosen_inline_result))
        
        logger.info(f"📝 Added {len(self.application.handlers)} handler groups")
    
    async def start_polling(self):
        try:
            logger.info("🔄 Starting bot polling...")
            
            bot_info = await self.application.bot.get_me()
            logger.info(f"🤖 Bot info: @{bot_info.username} ({bot_info.first_name})")
            
            # Start the application and updater
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=['message', 'callback_query', 'inline_query', 'chosen_inline_result'],
                drop_pending_updates=True,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30,
                pool_timeout=30
            )
            
            # Keep the bot running with a simple loop
            logger.info("✅ Bot is now running and listening for messages...")
            while True:
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"❌ Error starting bot polling: {e}")
            raise
    
    async def shutdown(self):
        try:
            logger.info("🛑 Shutting down bot...")
            
            if self.application:
                try:
                    if hasattr(self.application, 'updater') and self.application.updater:
                        await self.application.updater.stop()
                    await self.application.stop()
                    await self.application.shutdown()
                except Exception as e:
                    logger.warning(f"Application shutdown warning: {e}")
            
            if self.user_db:
                try:
                    await self.user_db.close()
                except Exception as e:
                    logger.warning(f"Database shutdown warning: {e}")
            
            # Shutdown utilities with proper error handling
            try:
                await shutdown_rate_limiter()
            except Exception as e:
                logger.warning(f"Rate limiter shutdown warning: {e}")
            
            try:
                await shutdown_cache()
            except Exception as e:
                logger.warning(f"Cache shutdown warning: {e}")
            
            logger.info("✅ Bot shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    


async def main():
    bot = None
    try:
        bot = OTPBot()
        await bot.initialize()
        
        logger.info("Bot is running... Send /start to test!")
        
        # Start polling
        await bot.start_polling()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    finally:
        if bot:
            await bot.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"❌ Failed to run bot: {e}")
        raise
