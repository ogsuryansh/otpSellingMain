"""
Callback Query Handler
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

from src.utils.keyboard_utils import create_main_keyboard, create_back_keyboard, create_services_keyboard, create_payment_keyboard, create_balance_keyboard, create_transactions_keyboard

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    try:
        query = update.callback_query
        await query.answer()  # Answer the callback query
        
        callback_data = query.data
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        
        # Handle different callback data
        if callback_data == "services":
            await handle_services(update, context)
        elif callback_data == "balance":
            await handle_balance(update, context)
        elif callback_data == "recharge":
            await handle_recharge(update, context)
        elif callback_data == "promocode":
            await handle_promocode(update, context)
        elif callback_data == "profile":
            await handle_profile(update, context)
        elif callback_data == "support":
            await handle_support(update, context)
        elif callback_data == "history":
            await handle_history(update, context)
        elif callback_data == "back_to_main":
            await handle_back_to_main(update, context)
        elif callback_data == "transactions":
            await handle_transactions(update, context)
        elif callback_data == "transaction_history":
            await handle_transaction_history(update, context)
        elif callback_data == "number_history":
            await handle_number_history(update, context)
        # Admin callback handlers
        elif callback_data.startswith("admin_"):
            await handle_admin_callback(update, context)
        else:
            await handle_unknown_callback(update, context)
            
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await update.callback_query.answer("Something went wrong. Please try again.")

async def handle_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle services button"""
    query = update.callback_query
    message = "📦 Available Services:\n\n"
    message += "🔸 WhatsApp - ₹5.00\n"
    message += "🔸 Telegram - ₹3.00\n"
    message += "🔸 Instagram - ₹4.00\n"
    message += "🔸 Facebook - ₹2.00\n"
    message += "🔸 Twitter - ₹3.50\n"
    message += "🔸 Gmail - ₹4.50\n\n"
    message += "Select a service to purchase:"
    
    # Create services keyboard (placeholder data)
    services = [
        {"id": 1, "name": "WhatsApp", "price": "5.00"},
        {"id": 2, "name": "Telegram", "price": "3.00"},
        {"id": 3, "name": "Instagram", "price": "4.00"},
        {"id": 4, "name": "Facebook", "price": "2.00"},
        {"id": 5, "name": "Twitter", "price": "3.50"},
        {"id": 6, "name": "Gmail", "price": "4.50"}
    ]
    
    keyboard = create_services_keyboard(services)
    
    await query.edit_message_text(
        text=message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def handle_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle balance button"""
    query = update.callback_query
    user = query.from_user
    
    # Get user data from database (placeholder)
    balance = 0.00  # This should come from database
    
    message = f"💰 Balance Overview :\n"
    message += f"💸 Available: {balance:.2f} 💎\n"
    message += f"📩 Total Recharged: 0 💎\n\n"
    message += "~~ Check transaction below."
    
    keyboard = create_balance_keyboard()
    
    await query.edit_message_text(
        text=message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def handle_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle recharge button"""
    query = update.callback_query
    
    message = "💳 Recharge Options\n\n"
    message += "Select your preferred payment method:\n\n"
    message += "🔸 UPI Payment - Instant\n"
    message += "🔸 Card Payment - Secure\n"
    message += "🔸 Crypto Payment - Anonymous\n\n"
    message += "Minimum recharge amount: ₹10"
    
    keyboard = create_payment_keyboard()
    
    await query.edit_message_text(
        text=message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def handle_promocode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle promocode button"""
    query = update.callback_query
    
    message = "📝 Enter Your Promocode:"
    
    # Create ForceReply keyboard
    from telegram import ForceReply
    keyboard = ForceReply(selective=True)
    
    # Send a new message instead of editing, since ForceReply can't be used with edit_message_text
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    # Answer the callback query
    await query.answer()

async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile button"""
    query = update.callback_query
    user = query.from_user
    
    message = "━━━━━━━━━━━\n"
    message += "👤 USER PROFILE\n"
    message += f"🧑 Name : {user.first_name}\n"
    message += f"🆔 User ID : {user.id}\n"
    message += "💰 Balance : 0.00 💎\n"
    message += "📊 Total Numbers Purchased : 0\n"
    message += "📋 Total Numbers Used : 0\n"
    message += "🚫 Total Numbers Cancelled : 0\n"
    message += "📦 Total SMM Orders : 0\n"
    message += "━━━━━━━━━━━\n"
    message += "📂 USER NUMBERS HISTORY\n"
    message += "🍒 You don't have any recent number history.\n"
    message += "━━━━━━━━━━━"
    
    keyboard = create_back_keyboard()
    
    await query.edit_message_text(
        text=message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support button"""
    query = update.callback_query
    
    # Get support username from environment variable
    import os
    support_username = os.getenv('SUPPORT_USERNAME', 'support')
    
    # Create URL button to directly message support
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("💬 Contact Support", url=f"https://t.me/{support_username}")],
        [InlineKeyboardButton("« Back", callback_data="back_to_main")]
    ]
    
    message = "🆘 Need Help?\n\nClick the button below to contact our support team directly."
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle history button"""
    query = update.callback_query
    
    message = "🧾 History\nClick on any button below to view its History."
    
    # Create history keyboard with the specified buttons
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [
            InlineKeyboardButton("💎 Transaction", callback_data="transaction_history"),
            InlineKeyboardButton("🛒 Number", callback_data="number_history")
        ],
        [InlineKeyboardButton("« Back", callback_data="back_to_main")]
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to main menu"""
    query = update.callback_query
    user = query.from_user
    
    # Recreate the start message
    from src.handlers.start_handler import create_welcome_message
    
    # Get user data (placeholder)
    user_data = {
        "first_name": user.first_name,
        "balance": 0.0,
        "total_purchased": 0,
        "total_used": 0
    }
    
    welcome_message = create_welcome_message(user_data)
    keyboard = create_main_keyboard()
    
    await query.edit_message_text(
        text=welcome_message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def handle_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle transactions button"""
    query = update.callback_query
    
    message = "🙈 You don't have any transaction history"
    
    keyboard = create_transactions_keyboard()
    
    await query.edit_message_text(
        text=message,
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def handle_promocode_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle promocode reply messages"""
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        message_id = update.message.message_id
        promocode = update.message.text.strip()
        
        logger.info(f"🎫 Promocode reply from user {user.id}: {promocode}")
        
        # Send processing message
        processing_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="⏳ Processing your promocode..."
        )
        
        # Wait 2 seconds
        import asyncio
        await asyncio.sleep(2)
        
        # Send error message
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Looks like this promocode does not exist."
        )
        
        logger.info(f"✅ Promocode processing completed for user {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in promocode reply handler: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Something went wrong processing your promocode."
        )

async def handle_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle transaction history button"""
    query = update.callback_query
    
    message = "💎 Transaction History\n\n🙈 You don't have any transaction history"
    
    # Create back button to return to history menu
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("« Back", callback_data="history")]
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_number_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle number history button"""
    query = update.callback_query
    
    message = "🛒 Number History\n\n🍒 You don't have any recent number history."
    
    # Create back button to return to history menu
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("« Back", callback_data="history")]
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin callback queries"""
    query = update.callback_query
    callback_data = query.data
    
    # Check if user is admin
    from src.config.bot_config import BotConfig
    config = BotConfig()
    if not config.ADMIN_USER_ID or str(query.from_user.id) != str(config.ADMIN_USER_ID):
        await query.answer("❌ You don't have admin permissions!")
        return
    
    # Handle different admin callbacks
    if callback_data == "admin_back":
        await handle_admin_back(update, context)
    elif callback_data == "admin_dashboard":
        await handle_admin_dashboard(update, context)
    elif callback_data == "admin_users":
        await handle_admin_users(update, context)
    elif callback_data == "admin_auto_import":
        await handle_admin_auto_import(update, context)
    elif callback_data == "admin_add_server":
        await handle_admin_add_server(update, context)
    elif callback_data == "admin_add_service":
        await handle_admin_add_service(update, context)
    elif callback_data == "admin_connect_api":
        await handle_admin_connect_api(update, context)
    elif callback_data == "admin_bot_settings":
        await handle_admin_bot_settings(update, context)
    elif callback_data == "admin_view_services":
        await handle_admin_view_services(update, context)
    elif callback_data == "admin_add_promocode":
        await handle_admin_add_promocode(update, context)
    elif callback_data == "admin_add_temp_mail":
        await handle_admin_add_temp_mail(update, context)
    elif callback_data == "admin_add_email":
        await handle_admin_add_email(update, context)
    elif callback_data == "admin_smm_services":
        await handle_admin_smm_services(update, context)
    elif callback_data == "admin_manual_payments":
        await handle_admin_manual_payments(update, context)
    else:
        await query.answer("This admin feature is not implemented yet!")

async def handle_admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin back button"""
    query = update.callback_query
    
    # Recreate the admin message
    username = query.from_user.username or query.from_user.first_name
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
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin dashboard"""
    query = update.callback_query
    
    message = "📊 Admin Dashboard\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin users"""
    query = update.callback_query
    
    message = "👥 Users Management\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_auto_import(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin auto import"""
    query = update.callback_query
    
    message = "🔄 Auto Import API Services\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_add_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin add server"""
    query = update.callback_query
    
    message = "🖥️ Add Server\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_add_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin add service"""
    query = update.callback_query
    
    message = "📦 Add Service\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_connect_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin connect API"""
    query = update.callback_query
    
    message = "🔗 Connect API\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_bot_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin bot settings"""
    query = update.callback_query
    
    message = "⚙️ Edit Bot Settings\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_view_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin view services"""
    query = update.callback_query
    
    message = "👀 View My Services\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_add_promocode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin add promocode"""
    query = update.callback_query
    
    message = "🎫 Add Promocode\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_add_temp_mail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin add temp mail"""
    query = update.callback_query
    
    message = "📧 Add Temp Mail\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_add_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin add email"""
    query = update.callback_query
    
    message = "📮 Add Email\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_smm_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin SMM services"""
    query = update.callback_query
    
    message = "📈 SMM Services\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_admin_manual_payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin manual payments"""
    query = update.callback_query
    
    message = "💳 View Manual Payments\n\nThis feature is coming soon!"
    
    keyboard = [[InlineKeyboardButton("« Back to Admin", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def handle_unknown_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown callback data"""
    query = update.callback_query
    
    await query.answer("This feature is not available yet!")
    
    # Go back to main menu
    await handle_back_to_main(update, context)
