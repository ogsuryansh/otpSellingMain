"""
Inline Query Handler for Services
"""

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes
import logging
from src.database.user_db import UserDatabase

logger = logging.getLogger(__name__)

async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline queries for services"""
    try:
        query = update.inline_query.query
        logger.info(f"🔍 Inline query received: '{query}'")
        
        # Get services from database
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        logger.info("📦 Fetching services from database...")
        services = await user_db.get_services()
        
        if not services:
            logger.warning("⚠️ No services found in database")
            await update.inline_query.answer(
                results=[],
                cache_time=60
            )
            return
        
        logger.info(f"✅ Found {len(services)} services for inline search")
        
        # Filter services based on query if provided
        if query:
            filtered_services = []
            query_lower = query.lower()
            for service in services:
                if (query_lower in service['name'].lower() or 
                    query_lower in service['description'].lower() or
                    query_lower in service['server'].lower()):
                    filtered_services.append(service)
            services = filtered_services
            logger.info(f"🔍 Filtered to {len(services)} services matching '{query}'")
        
        # Create inline results
        results = []
        for service in services:
            # Create inline result
            result = InlineQueryResultArticle(
                id=f"service_{service['id']}",
                title=f"📦 {service['name']} - {service['price']}",
                description=service['description'][:100] + "..." if len(service['description']) > 100 else service['description'],
                input_message_content=InputTextMessageContent(
                    message_text=f"📦 <b>Service Selected</b>\n\n"
                               f"🔸 <b>Name:</b> {service['name']}\n"
                               f"🔸 <b>Price:</b> {service['price']}\n"
                               f"🔸 <b>Server:</b> {service['server']}\n"
                               f"🔸 <b>Description:</b> {service['description']}\n\n"
                               f"💡 To purchase this service, contact support.",
                    parse_mode="HTML"
                )
            )
            results.append(result)
        
        logger.info(f"✅ Created {len(results)} inline search results")
        
        # Answer inline query
        await update.inline_query.answer(
            results=results,
            cache_time=60  # Cache for 1 minute
        )
        
    except Exception as e:
        logger.error(f"❌ Error in inline query handler: {e}")
        await update.inline_query.answer(
            results=[],
            cache_time=60
        )
