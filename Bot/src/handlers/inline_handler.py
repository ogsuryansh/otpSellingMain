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
        
        # Create inline results - limit to 1 result to prevent overflow
        results = []
        if services:
            # Only create 1 result for the first service
            service = services[0]
            logger.info(f"🔍 Creating result for service: {service.get('name', 'UNKNOWN')}")
            
            service_id = service.get('id', 'NO_ID')
            service_name = service.get('name', 'Unknown Service')
            service_desc = service.get('description', 'No description available')
            
            logger.info(f"🔍 Service details for result:")
            logger.info(f"  - ID: {service_id}")
            logger.info(f"  - Name: {service_name}")
            logger.info(f"  - Description: {service_desc}")
            
            result_id = f"service_{service_id}"
            title = f"📦 {service_name}"
            description = service_desc
            
            logger.info(f"🔍 Creating InlineQueryResultArticle:")
            logger.info(f"  - ID: {result_id}")
            logger.info(f"  - Title: {title}")
            logger.info(f"  - Description: {description}")
            
            result = InlineQueryResultArticle(
                id=result_id,
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text=f"➤ Selected Service : {service_name}\n"
                               f"↓ Choose Server Below",
                    parse_mode="HTML"
                )
            )
            results.append(result)
            logger.info(f"✅ Result created successfully")
            logger.info(f"🔍 Result ID that will be used: {result_id}")
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
        
        # Send immediate test message to see if handler is working
        if update.effective_user:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text="🔍 DEBUG: Chosen inline result handler is working!"
                )
                logger.info("✅ Test message sent successfully")
            except Exception as test_error:
                logger.error(f"❌ Failed to send test message: {test_error}")
        
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
        
        # Get service data from UserDatabase (same source as inline query)
        logger.info("📦 STEP 1: Initializing UserDatabase for service lookup...")
        user_db = UserDatabase()
        logger.info(f"🔍 UserDatabase instance: {user_db}")
        
        if not hasattr(user_db, 'client') or user_db.client is None:
            logger.info("📦 Initializing database connection...")
            await user_db.initialize()
            logger.info("✅ Database initialized")
        
        logger.info(f"🔍 STEP 2: Looking up service with ID: {service_id}")
        service = await user_db.get_service_by_id(service_id)
        logger.info(f"🔍 Service lookup result: {service}")
        
        if not service:
            logger.error(f"❌ Service {service_id} not found in UserDatabase")
            # For inline queries, we need to send to the user's chat
            if update.effective_user:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"❌ Service not found. Please try again."
                )
            return
        
        service_name = service.get('name', 'Unknown Service')
        service_price = service.get('price', '₹0')
        logger.info(f"🔍 STEP 3: Found service: {service_name} with price: {service_price}")
        logger.info(f"🔍 Full service data: {service}")
        logger.info("=" * 50)
        
        # Initialize service database for getting servers
        logger.info("📦 STEP 4: Initializing ServiceDatabase for server lookup...")
        service_db = ServiceDatabase()
        logger.info(f"🔍 ServiceDatabase instance: {service_db}")
        await service_db.initialize()
        logger.info("✅ ServiceDatabase initialized")
        
        # Debug: Check what's in the servers collection
        logger.info("🔍 STEP 5: Debugging servers collection...")
        await service_db.debug_servers_collection()
        
        # Get servers for this service
        logger.info(f"🔍 STEP 6: Getting servers for service ID: {service_id}")
        logger.info(f"🔍 Service name: {service_name}")
        servers = await service_db.get_servers_for_service(service_id)
        logger.info(f"🔍 STEP 7: Found {len(servers)} servers for service {service_name}")
        logger.info(f"🔍 Servers data: {servers}")
        logger.info("=" * 50)
        
        # Debug: Print each server data
        logger.info(f"🔍 STEP 8: Analyzing {len(servers)} servers for {service_name}:")
        for i, server in enumerate(servers):
            logger.info(f"🔍 Server {i+1}:")
            logger.info(f"  - ID: {server.get('_id')}")
            logger.info(f"  - Name: {server.get('name')}")
            logger.info(f"  - Country Code: {server.get('country_code')}")
            logger.info(f"  - Rating: {server.get('rating')}")
            logger.info(f"  - Enabled Services: {server.get('enabled_services')}")
            logger.info(f"  - Full server data: {server}")
        
        if not servers:
            # Send message without keyboard if no servers
            logger.info(f"🔍 STEP 9: No servers found for {service_name}, sending error message")
            if update.effective_user:
                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=f"➤ Selected Service : {service_name}\n"
                         f"↓ Choose Server Below\n\n"
                         f"❌ No servers available for this service.\n"
                         f"🔍 Debug: Service ID {service_id} has 0 servers"
                )
            return
        
        # Create inline keyboard with servers showing price and diamond emoji
        logger.info(f"🔧 STEP 10: Creating inline keyboard with {len(servers)} servers for {service_name}")
        keyboard = []
        for i, server in enumerate(servers):
            server_id = str(server['_id'])
            server_name = server.get('name', 'Unknown Server')
            country_code = server.get('country_code', 'US')
            rating = server.get('rating', 0)
            
            logger.info(f"🔍 Processing server {i+1} for {service_name}:")
            logger.info(f"  - Server ID: {server_id}")
            logger.info(f"  - Server Name: {server_name}")
            logger.info(f"  - Country Code: {country_code}")
            logger.info(f"  - Rating: {rating}")
            
            # Get country flag
            flag = COUNTRY_FLAGS.get(country_code.upper(), '🌍')
            logger.info(f"  - Flag: {flag}")
            
            # Create button text with price and diamond emoji
            button_text = f"{server_name} - {service_price} 💎"
            logger.info(f"  - Button Text: {button_text}")
            
            # Create callback data
            callback_data = f"srv:{service_id}:{server_id}"
            logger.info(f"  - Callback Data: {callback_data}")
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            logger.info(f"  - ✅ Button {i+1} added to keyboard")
        
        logger.info(f"🔍 STEP 11: Created keyboard with {len(keyboard)} buttons")
        logger.info(f"🔍 Keyboard structure: {keyboard}")
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        logger.info(f"🔍 Reply markup created: {reply_markup}")
        
        # Send response with inline keyboard
        message_text = f"➤ Selected Service : {service_name}\n↓ Choose Server Below\n\n🔍 Found {len(servers)} servers for {service_name}:"
        logger.info(f"🔍 STEP 12: Message text: {message_text}")
        
        # For inline queries, send to the user's chat
        chat_id = update.effective_user.id if update.effective_user else None
        if chat_id:
            logger.info(f"🔍 STEP 13: Sending to chat ID: {chat_id}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_markup=reply_markup
            )
            logger.info(f"✅ STEP 14: Successfully sent {len(servers)} servers for {service_name}")
            logger.info("=" * 50)
        else:
            logger.error("❌ No valid chat ID found for sending message")
        
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
