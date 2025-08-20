"""
Start Command Handler
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from src.database.user_db import UserDatabase
from src.utils.keyboard_utils import create_main_keyboard

logger = logging.getLogger(__name__)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    logger.info("🚀 START COMMAND RECEIVED!")
    logger.info(f"Update object: {update}")
    logger.info(f"Context object: {context}")
    
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        logger.info(f"👤 User: {user.id} - {user.first_name} (@{user.username})")
        logger.info(f"💬 Chat ID: {chat_id}")
        
        # Get or create user in database
        logger.info("📊 Initializing database...")
        user_db = UserDatabase()
        await user_db.initialize()
        logger.info("✅ Database initialized")
        
        logger.info("👤 Getting or creating user...")
        user_data = await user_db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        logger.info(f"✅ User data: {user_data}")
        
        # Create welcome message
        logger.info("📝 Creating welcome message...")
        welcome_message = create_welcome_message(user_data)
        logger.info(f"✅ Welcome message: {welcome_message}")
        
        # Create inline keyboard
        logger.info("⌨️ Creating keyboard...")
        keyboard = create_main_keyboard()
        logger.info(f"✅ Keyboard created: {keyboard}")
        
        # Send message
        logger.info("📤 Sending message...")
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        logger.info(f"✅ Start command handled successfully for user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ ERROR in start handler: {e}")
        logger.error(f"❌ Exception type: {type(e)}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        
        try:
            # Send fallback message
            logger.info("📤 Sending fallback message...")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="👋 Welcome! Something went wrong. Please try again later."
            )
            logger.info("✅ Fallback message sent")
        except Exception as fallback_error:
            logger.error(f"❌ Failed to send fallback message: {fallback_error}")

def create_welcome_message(user_data: dict) -> str:
    """Create welcome message with user stats"""
    first_name = user_data.get('first_name', 'User')
    balance = user_data.get('balance', 0.0)
    total_purchased = user_data.get('total_purchased', 0)
    total_used = user_data.get('total_used', 0)
    
    message = f"""👋 Hello {first_name} !

💰 Your Balance: {balance:.2f} 💎
📊 Total Numbers Purchased: {total_purchased}
📋 Total Numbers Used: {total_used}

~~You can use this 💎 for purchasing Numbers..
~~For Support Click on Support below."""
    
    return message
