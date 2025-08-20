"""
Admin Command Handler
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from src.config.bot_config import BotConfig

logger = logging.getLogger(__name__)

async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(user.id) != str(config.ADMIN_USER_ID):
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ You don't have permission to use admin commands."
            )
            return
        
        logger.info(f"🔧 Admin command used by user {user.id}")
        
        # Create admin message
        username = user.username or user.first_name
        message = f"👋 Hello @{username}\n\n"
        message += "*Admin Commands:*\n\n"
        message += "👉 Add Balance - `/add 1980442239 100`\n"
        message += "👉 Cut Balance - `/cut 1980442239 100`\n"
        message += "👉 User Transaction History - `/trnx 1980442239`\n"
        message += "👉 User Number History - `/nums 1980442239`\n"
        message += "👉 User SMM service History - `/smm_history 1980442239`\n"
        message += "👉 Ban User - `/ban 1980442239`\n"
        message += "👉 Unban User - `/unban 1980442239`\n"
        message += "👉 Broadcast a message - `/broadcast hello everyone`\n\n"
        message += "⚠️ *Remember to replace `1980442239` with actual user ID.*"
        
        # Create admin keyboard
        keyboard = [
            [
                InlineKeyboardButton("Dashboard", callback_data="admin_dashboard"),
                InlineKeyboardButton("Users", callback_data="admin_users")
            ],
            [InlineKeyboardButton("Auto Import API Services", callback_data="admin_auto_import")],
            [
                InlineKeyboardButton("Add Server", callback_data="admin_add_server"),
                InlineKeyboardButton("Add Service", callback_data="admin_add_service")
            ],
            [
                InlineKeyboardButton("Connect API", callback_data="admin_connect_api"),
                InlineKeyboardButton("Edit Bot Settings", callback_data="admin_bot_settings")
            ],
            [InlineKeyboardButton("View My Services", callback_data="admin_view_services")],
            [
                InlineKeyboardButton("Add Promocode", callback_data="admin_add_promocode"),
                InlineKeyboardButton("Add Temp Mail", callback_data="admin_add_temp_mail")
            ],
            [
                InlineKeyboardButton("Add Email", callback_data="admin_add_email"),
                InlineKeyboardButton("SMM Services", callback_data="admin_smm_services")
            ],
            [InlineKeyboardButton("View Manual Payments", callback_data="admin_manual_payments")]
        ]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Admin panel sent to user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in admin handler: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Something went wrong. Please try again."
        )
