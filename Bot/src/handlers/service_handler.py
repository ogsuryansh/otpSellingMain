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
        
        # Initialize user database (same as other handlers)
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        await user_db.initialize()
        
        # Get all services and find the one with matching name
        all_services = await user_db.get_services()
        service_variants = [s for s in all_services if s.get('name', '').upper() == service_name]
        
        if not service_variants:
            await update.message.reply_text(
                f"❌ Service '{service_name}' not found.\n"
                "Available services: " + ", ".join(set(s.get('name', '') for s in all_services))
            )
            return
        
        # Use the first variant as representative
        service = service_variants[0]
        service_id = service.get('id', 'NO_ID')
        
        # Create inline keyboard with service variants
        keyboard = []
        for service_variant in service_variants:
            variant_id = service_variant.get('id', 'NO_ID')
            server_name = service_variant.get('server', 'Unknown Server')
            price = service_variant.get('price', '₹0')
            
            # Create button text with price and diamond emoji
            button_text = f"{server_name} - {price} 💎"
            
            # Create callback data for server selection
            callback_data = f"server_{variant_id}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send response
        await update.message.reply_text(
            f"➤ Selected Service : {service_name}\n"
            "↓ Choose Server Below",
            reply_markup=reply_markup
        )
        
        logger.info(f"✅ Sent {len(service_variants)} server variants for service {service_name}")
        
    except Exception as e:
        logger.error(f"❌ Error in handle_show_server: {e}")
        await update.message.reply_text(
            "❌ An error occurred while fetching servers.\n"
            "Please try again later."
        )


