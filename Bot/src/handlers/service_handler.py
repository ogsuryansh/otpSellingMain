"""
Service Handler Module
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
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
    'IN': '🇮🇳', 'PK': '🇵🇰', 'BD': '🇧🇩', 'LK': '🇱🇰', 'NP': '🇳🇵',
    'BT': '🇧🇹', 'MV': '🇲🇻', 'MM': '🇲🇲', 'LA': '🇱🇦', 'KH': '🇰🇭',
    'MN': '🇲🇳', 'KZ': '🇰🇿', 'UZ': '🇺🇿', 'KG': '🇰🇬', 'TJ': '🇹🇯',
    'TM': '🇹🇲', 'AF': '🇦🇫', 'IR': '🇮🇷', 'IQ': '🇮🇶', 'SA': '🇸🇦',
    'AE': '🇦🇪', 'QA': '🇶🇦', 'KW': '🇰🇼', 'BH': '🇧🇭', 'OM': '🇴🇲',
    'YE': '🇾🇪', 'JO': '🇯🇴', 'LB': '🇱🇧', 'SY': '🇸🇾', 'IL': '🇮🇱',
    'PS': '🇵🇸', 'EG': '🇪🇬', 'SD': '🇸🇩', 'LY': '🇱🇾', 'TN': '🇹🇳',
    'DZ': '🇩🇿', 'MA': '🇲🇦', 'EH': '🇪🇭', 'MR': '🇲🇷', 'ML': '🇲🇱',
    'BF': '🇧🇫', 'NE': '🇳🇪', 'TD': '🇹🇩', 'NG': '🇳🇬', 'CM': '🇨🇲',
    'CF': '🇨🇫', 'CG': '🇨🇬', 'CD': '🇨🇩', 'GA': '🇬🇦', 'GQ': '🇬🇶',
    'ST': '🇸🇹', 'GW': '🇬🇼', 'GN': '🇬🇳', 'SL': '🇸🇱', 'LR': '🇱🇷',
    'CI': '🇨🇮', 'GH': '🇬🇭', 'TG': '🇹🇬', 'BJ': '🇧🇯', 'SN': '🇸🇳',
    'GM': '🇬🇲', 'GN': '🇬🇳', 'GW': '🇬🇼', 'CV': '🇨🇻', 'MZ': '🇲🇿',
    'ZW': '🇿🇼', 'BW': '🇧🇼', 'NA': '🇳🇦', 'ZA': '🇿🇦', 'LS': '🇱🇸',
    'SZ': '🇸🇿', 'MG': '🇲🇬', 'MU': '🇲🇺', 'SC': '🇸🇨', 'KM': '🇰🇲',
    'DJ': '🇩🇯', 'SO': '🇸🇴', 'ET': '🇪🇹', 'ER': '🇪🇷', 'SS': '🇸🇸',
    'KE': '🇰🇪', 'UG': '🇺🇬', 'RW': '🇷🇼', 'BI': '🇧🇮', 'TZ': '🇹🇿',
    'MW': '🇲🇼', 'ZM': '🇿🇲', 'AO': '🇦🇴', 'CG': '🇨🇬', 'CD': '🇨🇩',
    'CF': '🇨🇫', 'CM': '🇨🇲', 'GQ': '🇬🇶', 'GA': '🇬🇦', 'ST': '🇸🇹',
    'SAO': '🇸🇹', 'PRINCIPE': '🇸🇹', 'TOME': '🇸🇹'
}

async def handle_show_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /show_server <SERVICE_NAME> command"""
    try:
        # Get service name from command
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a service name.\n"
                "Usage: /show_server <SERVICE_NAME>\n"
                "Example: /show_server WHATSAPP"
            )
            return
        
        service_name = context.args[0].upper()
        logger.info(f"🔍 User {update.effective_user.id} requested servers for service: {service_name}")
        
        # Initialize service database
        service_db = ServiceDatabase()
        await service_db.initialize()
        
        # Find the service
        service = await service_db.get_service_by_name(service_name)
        if not service:
            await update.message.reply_text(
                f"❌ Service '{service_name}' not found.\n"
                "Please check the service name and try again."
            )
            return
        
        # Get servers for this service
        service_id = str(service['_id'])
        servers = await service_db.get_servers_for_service(service_id)
        
        if not servers:
            await update.message.reply_text(
                f"❌ No servers found for service '{service_name}'.\n"
                "Please try another service or contact admin."
            )
            return
        
        # Create inline keyboard with servers
        keyboard = []
        for server in servers:
            server_id = str(server['_id'])
            server_name = server.get('name', 'Unknown Server')
            country_code = server.get('country_code', 'US')
            rating = server.get('rating', 0)
            
            # Get country flag
            flag = COUNTRY_FLAGS.get(country_code.upper(), '🌍')
            
            # Create button text
            button_text = f"🌟 {server_name} → {flag} {rating}💎"
            
            # Create callback data
            callback_data = f"srv:{service_id}:{server_id}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send response
        await update.message.reply_text(
            f"➤ Selected Service : {service_name}\n"
            "↓ Choose Server Below",
            reply_markup=reply_markup
        )
        
        logger.info(f"✅ Sent {len(servers)} servers for service {service_name}")
        
    except Exception as e:
        logger.error(f"❌ Error in handle_show_server: {e}")
        await update.message.reply_text(
            "❌ An error occurred while fetching servers.\n"
            "Please try again later."
        )

async def handle_server_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle server selection callback"""
    try:
        query = update.callback_query
        await query.answer()
        
        # Parse callback data
        callback_data = query.data
        if not callback_data.startswith('srv:'):
            return
        
        parts = callback_data.split(':')
        if len(parts) != 3:
            await query.edit_message_text("❌ Invalid callback data")
            return
        
        service_id = parts[1]
        server_id = parts[2]
        
        logger.info(f"🔍 User {update.effective_user.id} selected server {server_id} for service {service_id}")
        
        # Initialize service database
        service_db = ServiceDatabase()
        await service_db.initialize()
        
        # Get service and server data
        service = await service_db.get_service_by_id(service_id)
        server = await service_db.get_server_by_id(server_id)
        
        if not service or not server:
            await query.edit_message_text("❌ Service or server not found")
            return
        
        service_name = service.get('name', 'Unknown')
        server_name = server.get('name', 'Unknown Server')
        
        # Show processing message
        await query.edit_message_text(
            f"Processing your request… ⏳\n"
            f"Service: {service_name}\n"
            f"Server: {server_name}"
        )
        
        # Call server API
        logger.info(f"🌐 Calling API for server {server_name}")
        api_result = await service_db.call_server_api(server, service_name)
        
        if api_result['success']:
            # Extract number from API response
            data = api_result['data']
            number = data.get('number') or data.get('phone') or data.get('phone_number')
            
            if number:
                await query.edit_message_text(
                    f"From {server_name} ({service_name}): {number}"
                )
                logger.info(f"✅ Successfully returned number {number} from {server_name}")
            else:
                await query.edit_message_text(
                    f"{server_name} is unavailable or returned no numbers. Try another server."
                )
                logger.warning(f"⚠️ Server {server_name} returned no number in response")
        else:
            await query.edit_message_text(
                f"{server_name} is unavailable or returned no numbers. Try another server."
            )
            logger.error(f"❌ Server {server_name} API failed: {api_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"❌ Error in handle_server_callback: {e}")
        try:
            await query.edit_message_text(
                "❌ An error occurred while processing your request.\n"
                "Please try again later."
            )
        except:
            pass
