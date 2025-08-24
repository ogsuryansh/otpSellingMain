"""
Inline Query Handler for Services
"""

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from src.database.user_db import UserDatabase
from src.database.service_db import ServiceDatabase

logger = logging.getLogger(__name__)

# Country flag emojis mapping
COUNTRY_FLAGS = {
    'IN': '🇮🇳', 'US': '🇺🇸', 'GB': '🇬🇧', 'CA': '🇨🇦', 'AU': '🇦🇺',
    'DE': '🇩🇪', 'FR': '🇫🇷', 'IT': '🇮🇹', 'ES': '🇪🇸', 'NL': '🇳🇱',
    'BR': '🇧🇷', 'MX': '🇲🇽', 'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴',
    'PE': '🇵🇪', 'VE': '🇻🇪', 'EC': '🇪🇨', 'BO': '🇧🇴', 'PY': '🇵🇾',
    'UY': '🇺🇾', 'GY': '🇬🇾', 'SR': '🇸🇷', 'GF': '🇬🇫', 'FK': '🇫🇰',
    'RU': '🇷🇺', 'CN': '🇨🇳', 'JP': '🇯🇵', 'KR': '🇰🇷', 'SG': '🇸🇬',
    'MY': '🇲🇾', 'TH': '🇹🇭', 'VN': '🇻🇳', 'PH': '🇵🇭', 'ID': '🇮🇩',
    'PK': '🇵🇰', 'BD': '🇧🇩', 'LK': '🇱🇰', 'NP': '🇳🇵', 'BT': '🇧🇹',
    'MV': '🇲🇻', 'MM': '🇲🇲', 'LA': '🇱🇦', 'KH': '🇰🇭', 'MN': '🇲🇳',
    'KZ': '🇰🇿', 'UZ': '🇺🇿', 'KG': '🇰🇬', 'TJ': '🇹🇯', 'TM': '🇹🇲',
    'AF': '🇦🇫', 'IR': '🇮🇷', 'IQ': '🇮🇶', 'SA': '🇸🇦', 'AE': '🇦🇪',
    'QA': '🇶🇦', 'KW': '🇰🇼', 'BH': '🇧🇭', 'OM': '🇴🇲', 'YE': '🇾🇪',
    'JO': '🇯🇴', 'LB': '🇱🇧', 'SY': '🇸🇾', 'IL': '🇮🇱', 'PS': '🇵🇸',
    'EG': '🇪🇬', 'SD': '🇸🇩', 'LY': '🇱🇾', 'TN': '🇹🇳', 'DZ': '🇩🇿',
    'MA': '🇲🇦', 'EH': '🇪🇭', 'MR': '🇲🇷', 'ML': '🇲🇱', 'BF': '🇧🇫',
    'NE': '🇳🇪', 'TD': '🇹🇩', 'NG': '🇳🇬', 'CM': '🇨🇲', 'CF': '🇨🇫',
    'CG': '🇨🇬', 'CD': '🇨🇩', 'GA': '🇬🇦', 'GQ': '🇬🇶', 'ST': '🇸🇹',
    'GW': '🇬🇼', 'GN': '🇬🇳', 'SL': '🇸🇱', 'LR': '🇱🇷', 'CI': '🇨🇮',
    'GH': '🇬🇭', 'TG': '🇹🇬', 'BJ': '🇧🇯', 'SN': '🇸🇳', 'GM': '🇬🇲',
    'CV': '🇨🇻', 'MZ': '🇲🇿', 'ZW': '🇿🇼', 'BW': '🇧🇼', 'NA': '🇳🇦',
    'ZA': '🇿🇦', 'LS': '🇱🇸', 'SZ': '🇸🇿', 'MG': '🇲🇬', 'MU': '🇲🇺',
    'SC': '🇸🇨', 'KM': '🇰🇲', 'DJ': '🇩🇯', 'SO': '🇸🇴', 'ET': '🇪🇹',
    'ER': '🇪🇷', 'SS': '🇸🇸', 'KE': '🇰🇪', 'UG': '🇺🇬', 'RW': '🇷🇼',
    'BI': '🇧🇮', 'TZ': '🇹🇿', 'MW': '🇲🇼', 'ZM': '🇿🇲', 'AO': '🇦🇴'
}

async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline queries for services"""
    try:
        logger.info("🚀 INLINE QUERY HANDLER STARTED")
        logger.info("🔥🔥🔥 THIS SHOULD APPEAR WHEN YOU SEARCH 🔥🔥🔥")
        logger.info("=" * 60)
        
        # Handle null checks for inline queries
        if update.effective_user:
            logger.info(f"🔍 User ID: {update.effective_user.id}")
        else:
            logger.info("🔍 User ID: None (inline query)")
            
        if update.effective_chat:
            logger.info(f"🔍 Chat ID: {update.effective_chat.id}")
        else:
            logger.info("🔍 Chat ID: None (inline query)")
        
        query = update.inline_query.query
        logger.info(f"🔍 Inline query received: '{query}'")
        logger.info(f"🔍 Query length: {len(query)}")
        
        # Get services from database
        logger.info("📦 Initializing UserDatabase...")
        user_db = UserDatabase()
        logger.info(f"🔍 UserDatabase instance: {user_db}")
        logger.info(f"🔍 UserDatabase client exists: {hasattr(user_db, 'client')}")
        logger.info(f"🔍 UserDatabase client is None: {user_db.client is None if hasattr(user_db, 'client') else 'No client attr'}")
        
        if not hasattr(user_db, 'client') or user_db.client is None:
            logger.info("📦 Initializing database connection...")
            await user_db.initialize()
            logger.info("✅ Database initialized")
        
        logger.info("📦 Fetching services from database...")
        services = await user_db.get_services()
        logger.info(f"🔍 Raw services data: {services}")
        
        if not services:
            logger.warning("⚠️ No services found in database")
            await update.inline_query.answer(
                results=[],
                cache_time=60
            )
            return
        
        logger.info(f"✅ Found {len(services)} services for inline search")
        
        # Debug each service
        for i, service in enumerate(services):
            logger.info(f"🔍 Service {i+1}:")
            logger.info(f"  - ID: {service.get('id', 'NO_ID')}")
            logger.info(f"  - Name: {service.get('name', 'NO_NAME')}")
            logger.info(f"  - Description: {service.get('description', 'NO_DESC')}")
            logger.info(f"  - Price: {service.get('price', 'NO_PRICE')}")
            logger.info(f"  - Full service data: {service}")
        
        # Filter services based on query if provided
        if query:
            logger.info(f"🔍 Filtering services for query: '{query}'")
            filtered_services = []
            query_lower = query.lower()
            for service in services:
                service_name = service.get('name', '').lower()
                service_desc = service.get('description', '').lower()
                logger.info(f"🔍 Checking service: {service.get('name', 'UNKNOWN')}")
                logger.info(f"  - Service name (lower): {service_name}")
                logger.info(f"  - Service desc (lower): {service_desc}")
                logger.info(f"  - Query (lower): {query_lower}")
                logger.info(f"  - Name match: {query_lower in service_name}")
                logger.info(f"  - Desc match: {query_lower in service_desc}")
                
                if (query_lower in service_name or query_lower in service_desc):
                    filtered_services.append(service)
                    logger.info(f"  - ✅ Service matched!")
                else:
                    logger.info(f"  - ❌ Service not matched")
            
            services = filtered_services
            logger.info(f"🔍 Filtered to {len(services)} services matching '{query}'")
        
        # Filter out services with empty or "Unknown" names
        if services:
            valid_services = []
            for service in services:
                service_name = service.get('name', '').strip()
                if service_name and service_name.lower() != 'unknown' and service_name != '':
                    valid_services.append(service)
                else:
                    logger.info(f"🔍 Filtering out invalid service: {service_name}")
            
            services = valid_services
            logger.info(f"🔍 After filtering invalid names: {len(services)} valid services")
        
        # If no services after filtering, return empty results
        if not services:
            logger.warning("⚠️ No valid services found after filtering")
            await update.inline_query.answer(
                results=[],
                cache_time=60
            )
            return
        
        # Create inline results - show all services with same name
        results = []
        if services:
            # Group services by name to show all variants
            service_groups = {}
            for service in services:
                service_name = service.get('name', '').strip()
                # Double-check to ensure we don't include invalid service names
                if service_name and service_name.lower() != 'unknown' and service_name != '':
                    if service_name not in service_groups:
                        service_groups[service_name] = []
                    service_groups[service_name].append(service)
            
            logger.info(f"🔍 Found {len(service_groups)} unique service names")
            
            # Create one result per unique service name
            for service_name, service_variants in service_groups.items():
                # Use the first service as the representative
                service = service_variants[0]
                service_id = service.get('id', 'NO_ID')
                service_desc = service.get('description', 'No description available')
                
                logger.info(f"🔍 Creating result for service group: {service_name}")
                logger.info(f"  - Service variants: {len(service_variants)}")
                logger.info(f"  - Representative ID: {service_id}")
                
                result_id = f"service_{service_id}"
                title = f"📦 {service_name}"
                description = f"{service_desc} ({len(service_variants)} servers available)"
                
                logger.info(f"🔍 Creating InlineQueryResultArticle:")
                logger.info(f"  - ID: {result_id}")
                logger.info(f"  - Title: {title}")
                logger.info(f"  - Description: {description}")
                
                result = InlineQueryResultArticle(
                    id=result_id,
                    title=title,
                    description=description,
                    input_message_content=InputTextMessageContent(
                        message_text=f"/show_server {service_name.upper()}",
                        parse_mode="HTML"
                    )
                )
                results.append(result)
                logger.info(f"✅ Result created for {service_name}")
        else:
            logger.warning("⚠️ No services to create results for")
        
        logger.info(f"✅ Created {len(results)} inline search result")
        
        # Answer inline query
        logger.info("📤 Answering inline query...")
        await update.inline_query.answer(
            results=results,
            cache_time=60  # Cache for 1 minute
        )
        logger.info("✅ Inline query answered successfully")
        logger.info("=" * 60)
        
        # Send a test message to verify inline query is working
        if update.effective_user:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text="🔍 DEBUG: Inline query handler is working!"
                )
                logger.info("✅ Test message sent for inline query")
            except Exception as test_error:
                logger.error(f"❌ Failed to send test message: {test_error}")
        
    except Exception as e:
        logger.error(f"❌ Error in inline query handler: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        try:
            await update.inline_query.answer(
                results=[],
                cache_time=60
            )
            logger.info("✅ Sent empty results as fallback")
        except Exception as inner_e:
            logger.error(f"❌ Failed to answer inline query: {inner_e}")
            logger.error(f"❌ Inner traceback: {traceback.format_exc()}")

async def handle_chosen_inline_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user selects an inline result"""
    try:
        logger.info("🎯 CHOSEN INLINE RESULT HANDLER TRIGGERED!")
        logger.info("🔥🔥🔥 THIS SHOULD APPEAR WHEN YOU CLICK ON A SERVICE 🔥🔥🔥")
        logger.info("=" * 60)
        
        # Send immediate test message to verify handler is working
        if update.effective_user:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="🔍 DEBUG: Inline result handler is working!"
            )
            logger.info("✅ Test message sent")
        
        # Handle null checks for inline queries
        if update.effective_user:
            logger.info(f"🔍 User ID: {update.effective_user.id}")
        else:
            logger.info("🔍 User ID: None (inline query)")
            
        if update.effective_chat:
            logger.info(f"🔍 Chat ID: {update.effective_chat.id}")
        else:
            logger.info("🔍 Chat ID: None (inline query)")
            
        logger.info(f"🔍 DEBUG: Update type: {type(update)}")
        
        chosen_result = update.chosen_inline_result
        logger.info(f"🔍 DEBUG: Chosen result: {chosen_result}")
        logger.info(f"🔍 DEBUG: Chosen result type: {type(chosen_result)}")
        
        if not chosen_result:
            logger.error("❌ No chosen result found!")
            return
            
        result_id = chosen_result.result_id
        logger.info(f"🔍 DEBUG: Chosen result_id: {result_id}")
        logger.info(f"🔍 DEBUG: Result ID type: {type(result_id)}")
        
        if not result_id:
            logger.error("❌ No result_id found!")
            return
            
        if not result_id.startswith("service_"):
            logger.info(f"🔍 DEBUG: Result ID doesn't start with 'service_', skipping")
            logger.info(f"🔍 DEBUG: Result ID: '{result_id}'")
            return
        
        # Extract service ID
        service_id = result_id.replace("service_", "")
        logger.info(f"🔍 DEBUG: Extracted service_id: {service_id}")
        logger.info(f"🔍 DEBUG: Service ID type: {type(service_id)}")
        
        user_id = update.effective_user.id if update.effective_user else "Unknown"
        logger.info(f"🔍 User {user_id} selected service {service_id}")
        logger.info("=" * 50)
        
        # Simple approach: Just show server variants for the selected service
        logger.info("📦 STEP 1: Getting service variants...")
        user_db = UserDatabase()
        await user_db.initialize()
        
        # Get the selected service
        service = await user_db.get_service_by_id(service_id)
        if not service:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="❌ Service not found. Please try again."
            )
            return
        
        service_name = service.get('name', 'Unknown Service')
        logger.info(f"🔍 STEP 2: Found service: {service_name}")
        
        # Get all variants of this service
        all_services = await user_db.get_services()
        service_variants = [s for s in all_services if s.get('name') == service_name]
        
        logger.info(f"🔍 STEP 3: Found {len(service_variants)} variants for {service_name}")
        
        if not service_variants:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=f"❌ No server variants available for {service_name}."
            )
            return
        
        # Directly execute the show_server command
        command = f"/show_server {service_name.upper()}"
        
        logger.info(f"🔧 STEP 4: Directly executing: {command}")
        
        # Create fake context with the service name as argument
        fake_context = type('Context', (), {
            'args': [service_name.upper()],
            'bot': context.bot
        })()
        
        # Create fake update
        fake_update = type('Update', (), {
            'message': type('Message', (), {
                'reply_text': lambda text, **kwargs: context.bot.send_message(
                    chat_id=update.effective_user.id, text=text, **kwargs
                ),
                'text': command,
                'chat': {'id': update.effective_user.id},
                'from_user': update.effective_user
            })(),
            'effective_user': update.effective_user,
            'effective_chat': type('Chat', (), {'id': update.effective_user.id})()
        })()
        
        # Import and call the show_server handler directly
        from src.handlers.service_handler import handle_show_server
        await handle_show_server(fake_update, fake_context)
        
        logger.info(f"✅ Successfully executed command for {service_name}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error in chosen inline result handler: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        try:
            # For inline queries, send to the user's chat
            chat_id = update.effective_user.id if update.effective_user else None
            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ An error occurred while processing your selection.\n"
                         "Please try again later."
                )
                logger.info("✅ Sent error message to user")
        except Exception as send_error:
            logger.error(f"❌ Failed to send error message: {send_error}")
            logger.error(f"❌ Send error traceback: {traceback.format_exc()}")
