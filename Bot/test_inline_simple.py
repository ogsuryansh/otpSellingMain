#!/usr/bin/env python3
"""
Simple test for inline queries
"""

import asyncio
import logging
from telegram import Bot, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, InlineQueryHandler, ChosenInlineResultHandler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def handle_inline_query(update, context):
    """Simple inline query handler"""
    logger.info("🔍 Inline query received!")
    logger.info(f"🔍 Query: {update.inline_query.query}")
    
    # Create a simple result
    result = InlineQueryResultArticle(
        id="test_service",
        title="📦 Test Service",
        description="This is a test service",
        input_message_content=InputTextMessageContent(
            message_text="/show_server TEST SERVICE"
        )
    )
    
    await update.inline_query.answer([result])
    logger.info("✅ Inline query answered")

async def handle_chosen_result(update, context):
    """Simple chosen result handler"""
    logger.info("🎯 CHOSEN RESULT HANDLER CALLED!")
    logger.info(f"🎯 Result ID: {update.chosen_inline_result.result_id}")
    
    # Send a simple message
    if update.effective_user:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="✅ You selected a service! This handler is working!"
        )
        logger.info("✅ Test message sent")

async def main():
    """Main function"""
    # Load bot token from env
    import os
    from dotenv import load_dotenv
    load_dotenv('env.bot')
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("❌ BOT_TOKEN not found!")
        return
    
    logger.info("🚀 Starting simple inline test bot...")
    
    # Create application without job queue to avoid weak reference issues
    application = Application.builder().token(bot_token).job_queue(None).build()
    
    # Add handlers
    application.add_handler(InlineQueryHandler(handle_inline_query))
    application.add_handler(ChosenInlineResultHandler(handle_chosen_result))
    
    # Start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("✅ Bot is running! Test the inline search now.")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Stopping bot...")
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
