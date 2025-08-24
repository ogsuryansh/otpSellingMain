"""
Start Command Handler
"""

import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from src.database.user_db import UserDatabase
from src.utils.keyboard_utils import create_main_keyboard
from src.utils.rate_limiter import check_rate_limit
from src.config.security_config import security_config

logger = logging.getLogger(__name__)

def validate_user_input(user_id: int, username: str = None, first_name: str = None) -> bool:
    """Validate user input for security"""
    try:
        # Use security config for validation
        if not security_config.validate_user_id(user_id):
            security_config.log_security_event("INVALID_USER_ID", user_id, f"User ID: {user_id}")
            return False
        
        # Validate username (optional)
        if username is not None and not security_config.validate_username(username):
            security_config.log_security_event("INVALID_USERNAME", user_id, f"Username: {username}")
            return False
        
        # Validate first_name (optional)
        if first_name is not None and not security_config.validate_first_name(first_name):
            security_config.log_security_event("INVALID_FIRST_NAME", user_id, f"First name: {first_name}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating user input: {e}")
        return False

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Check rate limiting
        is_allowed, remaining = check_rate_limit(user.id)
        if not is_allowed:
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ Rate limit exceeded. Please wait a moment before trying again."
            )
            return
        
        # Validate user input
        if not validate_user_input(user.id, user.username, user.first_name):
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ Invalid user data received. Please try again."
            )
            return
        
        # Sanitize user data using security config
        safe_username = security_config.sanitize_input(user.username or "", security_config.MAX_USERNAME_LENGTH)
        safe_first_name = security_config.sanitize_input(user.first_name or "User", security_config.MAX_FIRST_NAME_LENGTH)
        
        # Use default user data for faster response
        user_data = {
            "user_id": user.id,
            "username": safe_username,
            "first_name": safe_first_name,
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
                username=safe_username,
                first_name=safe_first_name
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
    # Sanitize data to prevent XSS
    first_name = user_data.get('first_name', 'User')
    if not isinstance(first_name, str):
        first_name = 'User'
    
    balance = user_data.get('balance', 0.0)
    if not isinstance(balance, (int, float)):
        balance = 0.0
    
    total_purchased = user_data.get('total_purchased', 0)
    if not isinstance(total_purchased, int):
        total_purchased = 0
    
    total_used = user_data.get('total_used', 0)
    if not isinstance(total_used, int):
        total_used = 0
    
    message = f"""👋 Hello {first_name} !

💰 Your Balance: {balance:.2f} 💎
📊 Total Numbers Purchased: {total_purchased}
📋 Total Numbers Used: {total_used}

~~You can use this 💎 for purchasing Numbers..
~~For Support Click on Support below."""
    
    return message
