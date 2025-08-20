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
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Use default user data for faster response
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "balance": 0.0,
            "total_purchased": 0,
            "total_used": 0,
            "transaction_history": [],
            "number_history": [],
            "smm_history": [],
            "banned": False
        }
        
        # Try to get user data from database in background
        try:
            user_db = UserDatabase()
            if not hasattr(user_db, 'client') or user_db.client is None:
                await user_db.initialize()
            
            db_user_data = await user_db.get_or_create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name
            )
            # Update with real data if available
            if db_user_data:
                user_data.update(db_user_data)
                
                # Check if user is banned
                if db_user_data.get("banned", False):
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="🚫 You have been banned from using this bot. Please contact support for assistance."
                    )
                    return
                    
        except Exception as db_error:
            logger.warning(f"Database error (using default data): {db_error}")
        
        # Create welcome message
        welcome_message = create_welcome_message(user_data)
        
        # Create inline keyboard
        keyboard = create_main_keyboard()
        
        # Send message immediately
        await context.bot.send_message(
            chat_id=chat_id,
            text=welcome_message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        logger.info(f"✅ Start command handled for user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ ERROR in start handler: {e}")
        
        try:
            # Send fallback message
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="👋 Welcome! Something went wrong. Please try again later."
            )
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
