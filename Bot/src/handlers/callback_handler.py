"""
Callback Query Handler
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
from datetime import datetime

from src.utils.keyboard_utils import create_main_keyboard, create_back_keyboard, create_services_keyboard, create_payment_keyboard, create_balance_keyboard, create_transactions_keyboard

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    try:
        logger.info("🎯 CALLBACK HANDLER TRIGGERED!")
        query = update.callback_query
        callback_data = query.data
        
        logger.info(f"🔍 DEBUG: Callback data: {callback_data}")
        logger.info(f"🔍 DEBUG: From user: {update.effective_user.id}")
        
        # Answer callback immediately for better UX
        await query.answer()
        
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
        elif callback_data.startswith("transactions_page_"):
            # Handle transaction pagination
            try:
                page = int(callback_data.split("_")[-1])
                await handle_transaction_page(update, context, page)
            except ValueError:
                await handle_transactions(update, context)
        elif callback_data.startswith("history_transactions_page_"):
            # Handle history transaction pagination
            try:
                page = int(callback_data.split("_")[-1])
                await handle_history_transaction_page(update, context, page)
            except ValueError:
                await handle_transaction_history(update, context)
        elif callback_data == "transaction_history":
            await handle_transaction_history(update, context)
        elif callback_data == "number_history":
            await handle_number_history(update, context)
        # Service selection callback handlers
        elif callback_data.startswith("service_"):
            await handle_service_selection(update, context)
        # Purchase callback handlers
        elif callback_data.startswith("purchase_"):
            await handle_purchase_service(update, context)
        # Server callback handlers
        elif callback_data.startswith("srv:"):
            await handle_server_callback(update, context)
        # Admin callback handlers
        elif callback_data.startswith("admin_"):
            await handle_admin_callback(update, context)
        else:
            await handle_unknown_callback(update, context)
            
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        try:
            await update.callback_query.answer("Something went wrong. Please try again.")
        except:
            pass

async def handle_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle services button - Show services list"""
    query = update.callback_query
    
    try:
        # Get services from database
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        logger.info("🔍 Fetching services from database...")
        services = await user_db.get_services()
        
        logger.info(f"📊 Services result: {len(services) if services else 0} services found")
        
        if not services:
            logger.warning("⚠️ No services found in database")
            await query.edit_message_text(
                text="📦 No services available at the moment.\n\nPlease check back later!",
                reply_markup=create_back_keyboard()
            )
            return
        
        logger.info(f"✅ Found {len(services)} services in database")
        
        # Create services list message
        message = f"📦 <b>Available Services</b>\n\n"
        message += f"✅ Found {len(services)} services\n\n"
        message += "🔽 <b>Choose a service below:</b>\n\n"
        
        # Create interactive keyboard with service buttons
        keyboard = []
        
        # Add service buttons (limit to 8 services per page for better UX)
        for i, service in enumerate(services[:8], 1):
            service_name = service.get('name', f'Service {i}')
            service_price = service.get('price', '₹0')
            service_server = service.get('server', 'Unknown Server')
            service_id = service.get('id', str(i))
            
            logger.info(f"🔧 Creating button for service: {service_name} (ID: {service_id}) on server: {service_server}")
            
            # Create button text with server information
            button_text = f"{service_name} - {service_price} ({service_server})"
            
            keyboard.append([
                InlineKeyboardButton(
                    button_text, 
                    callback_data=f"service_{service_id}"
                )
            ])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_main")])
        
        logger.info(f"🎯 Created keyboard with {len(keyboard)-1} service buttons")
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"❌ Error in handle_services: {e}")
        await query.edit_message_text(
            text="❌ Error loading services. Please try again later.",
            reply_markup=create_back_keyboard()
        )

async def handle_service_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service selection from user"""
    query = update.callback_query
    user = query.from_user
    
    try:
        logger.info(f"🔍 Service selection triggered by user {user.id}")
        
        # Extract service ID from callback data
        callback_data = query.data
        service_id = callback_data.replace("service_", "")
        
        logger.info(f"🎯 Selected service ID: {service_id}")
        
        # Get service details from database
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        logger.info(f"🔍 Fetching service details for ID: {service_id}")
        service = await user_db.get_service_by_id(service_id)
        
        if not service:
            logger.error(f"❌ Service not found with ID: {service_id}")
            await query.edit_message_text(
                text="❌ Service not found. Please try again.",
                reply_markup=create_back_keyboard()
            )
            return
        
        logger.info(f"✅ Found service: {service.get('name', 'Unknown')}")
        
        # Get user data to check balance
        user_data = await user_db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        user_balance = user_data.get("balance", 0.0)
        service_price = float(service.get('price', '0').replace('₹', ''))
        
        logger.info(f"💰 User balance: {user_balance}, Service price: {service_price}")
        
        # Create service details message
        message = f"📦 <b>Service Details</b>\n\n"
        message += f"🔹 <b>Name:</b> {service.get('name', 'Unknown')}\n"
        message += f"🔹 <b>Description:</b> {service.get('description', 'No description')}\n"
        message += f"🔹 <b>Price:</b> {service.get('price', '₹0')}\n"
        message += f"🔹 <b>Server:</b> {service.get('server', 'Unknown')}\n\n"
        message += f"💰 <b>Your Balance:</b> {user_balance:.2f} 💎\n"
        
        # Check if user has sufficient balance
        if user_balance >= service_price:
            message += f"✅ <b>Status:</b> Sufficient balance\n\n"
            message += "🎯 <b>Ready to purchase!</b>"
            
            # Create purchase keyboard
            keyboard = [
                [InlineKeyboardButton("🛒 Purchase Now", callback_data=f"purchase_{service_id}")],
                [InlineKeyboardButton("« Back to Services", callback_data="services")],
                [InlineKeyboardButton("« Main Menu", callback_data="back_to_main")]
            ]
        else:
            message += f"❌ <b>Status:</b> Insufficient balance\n\n"
            message += f"💡 You need {service_price - user_balance:.2f} more 💎 to purchase this service."
            
            # Create recharge keyboard
            keyboard = [
                [InlineKeyboardButton("💳 Recharge Balance", callback_data="recharge")],
                [InlineKeyboardButton("« Back to Services", callback_data="services")],
                [InlineKeyboardButton("« Main Menu", callback_data="back_to_main")]
            ]
        
        logger.info(f"📝 Sending service details to user {user.id}")
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"❌ Error in handle_service_selection: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        
        await query.edit_message_text(
            text="❌ Error loading service details. Please try again later.",
            reply_markup=create_back_keyboard()
        )

async def handle_purchase_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service purchase"""
    query = update.callback_query
    user = query.from_user
    
    try:
        logger.info(f"🛒 Purchase triggered by user {user.id}")
        
        # Extract service ID from callback data
        callback_data = query.data
        service_id = callback_data.replace("purchase_", "")
        
        logger.info(f"🎯 Purchase service ID: {service_id}")
        
        # Get service details from database
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        logger.info(f"🔍 Fetching service details for purchase: {service_id}")
        service = await user_db.get_service_by_id(service_id)
        
        if not service:
            logger.error(f"❌ Service not found for purchase: {service_id}")
            await query.edit_message_text(
                text="❌ Service not found. Please try again.",
                reply_markup=create_back_keyboard()
            )
            return
        
        logger.info(f"✅ Found service for purchase: {service.get('name', 'Unknown')}")
        
        # Get user data to check balance
        user_data = await user_db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        user_balance = user_data.get("balance", 0.0)
        service_price = float(service.get('price', '0').replace('₹', ''))
        
        logger.info(f"💰 Purchase check - User balance: {user_balance}, Service price: {service_price}")
        
        # Check if user has sufficient balance
        if user_balance < service_price:
            logger.warning(f"❌ Insufficient balance for user {user.id}")
            message = f"❌ <b>Insufficient Balance</b>\n\n"
            message += f"💰 Your balance: {user_balance:.2f} 💎\n"
            message += f"💳 Service price: {service_price:.2f} 💎\n"
            message += f"💡 You need {service_price - user_balance:.2f} more 💎"
            
            keyboard = [
                [InlineKeyboardButton("💳 Recharge Balance", callback_data="recharge")],
                [InlineKeyboardButton("« Back to Services", callback_data="services")],
                [InlineKeyboardButton("« Main Menu", callback_data="back_to_main")]
            ]
            
            await query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            return
        
        # Process the purchase
        logger.info(f"✅ Processing purchase for user {user.id}")
        
        # Deduct balance
        new_balance = user_balance - service_price
        await user_db.update_user_balance(user_id, -service_price)
        
        # Add transaction record
        transaction = {
            "type": "debit",
            "amount": service_price,
            "reason": f"Service purchase: {service.get('name', 'Unknown')}",
            "closing_balance": new_balance,
            "created_at": datetime.utcnow()
        }
        
        await user_db.add_transaction(user_id, transaction)
        
        # Update user stats
        await user_db.update_user_stats(user_id, service_price)
        
        logger.info(f"✅ Purchase completed for user {user.id}")
        
        # Send success message
        message = f"🎉 <b>Purchase Successful!</b>\n\n"
        message += f"📦 <b>Service:</b> {service.get('name', 'Unknown')}\n"
        message += f"💰 <b>Price:</b> {service.get('price', '₹0')}\n"
        message += f"💳 <b>New Balance:</b> {new_balance:.2f} 💎\n\n"
        message += f"✅ Your service has been activated!\n\n"
        message += f"📞 <b>Next Steps:</b>\n"
        message += f"1. You will receive the service details shortly\n"
        message += f"2. Check your transaction history for details\n"
        message += f"3. Contact support if you need help"
        
        keyboard = [
            [InlineKeyboardButton("📋 Transaction History", callback_data="transactions")],
            [InlineKeyboardButton("🛒 Buy More Services", callback_data="services")],
            [InlineKeyboardButton("« Main Menu", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"❌ Error in handle_purchase_service: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        
        await query.edit_message_text(
            text="❌ Error processing purchase. Please try again later.",
            reply_markup=create_back_keyboard()
        )

async def handle_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle balance button"""
    query = update.callback_query
    user = query.from_user
    
    try:
        # Get user data from database
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        user_data = await user_db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        balance = user_data.get("balance", 0.0)
        
        # Calculate total recharged (sum of all credit transactions)
        transaction_history = user_data.get("transaction_history", [])
        total_recharged = sum(
            tx.get("amount", 0) for tx in transaction_history 
            if tx.get("type") == "credit"
        )
        
        message = f"💰 Balance Overview :\n"
        message += f"💸 Available: {balance:.2f} 💎\n"
        message += f"📩 Total Recharged: {total_recharged:.2f} 💎\n\n"
        message += "~~ Check transaction below."
        
        keyboard = create_balance_keyboard()
        
        await query.edit_message_text(
            text=message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        # Fallback to default values
        message = f"💰 Balance Overview :\n"
        message += f"💸 Available: 0.00 💎\n"
        message += f"📩 Total Recharged: 0.00 💎\n\n"
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
    
    try:
        # Get user data from database
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        user_data = await user_db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        balance = user_data.get("balance", 0.0)
        total_purchased = user_data.get("total_purchased", 0)
        total_used = user_data.get("total_used", 0)
        total_cancelled = 0  # Placeholder - can be calculated from number_history
        total_smm_orders = len(user_data.get("smm_history", []))
        
        message = "━━━━━━━━━━━\n"
        message += "👤 USER PROFILE\n"
        message += f"🧑 Name : {user.first_name}\n"
        message += f"🆔 User ID : {user.id}\n"
        message += f"💰 Balance : {balance:.2f} 💎\n"
        message += f"📊 Total Numbers Purchased : {total_purchased}\n"
        message += f"📋 Total Numbers Used : {total_used}\n"
        message += f"🚫 Total Numbers Cancelled : {total_cancelled}\n"
        message += f"📦 Total SMM Orders : {total_smm_orders}\n"
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
        
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        # Fallback to default values
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
    """Handle transactions button - show first page"""
    await handle_transaction_page(update, context, page=1)

async def handle_transaction_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1):
    """Handle transaction page display with pagination"""
    query = update.callback_query
    await query.answer()
    
    try:
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        # Get user transactions with pagination
        result = await user_db.get_user_transactions(query.from_user.id, page=page, per_page=4)
        
        if not result or result["total_transactions"] == 0:
            await query.edit_message_text(
                text="🙈 You don't have any transaction history",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("« Back", callback_data="balance")]
                ])
            )
            return
        
        # Build transaction message
        message = f"📩 Page {result['current_page']} of {result['total_pages']}\n\n"
        
        for i, transaction in enumerate(result["transactions"], 1):
            # Format the transaction
            tx_type = transaction.get("type", "unknown")
            reason = transaction.get("reason", "No description")
            amount = transaction.get("amount", 0.0)
            closing_balance = transaction.get("closing_balance", 0.0)
            created_at = transaction.get("created_at")
            
            # Format date
            if isinstance(created_at, str):
                date_str = created_at
            else:
                try:
                    date_str = created_at.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
                except:
                    date_str = str(created_at)
            
            # Format amount display
            amount_text = f"Amount credited" if tx_type == "credit" else f"Amount debited"
            
            message += f"✉️ {reason}\n"
            message += f"<b>{amount_text}</b>: {amount} 💰\n"
            message += f"<b>Closing balance</b>: {closing_balance} 💎\n"
            message += f"📅 Created On: {date_str}\n\n"
        
        # Create pagination keyboard
        keyboard = []
        
        # Navigation buttons (only if multiple pages)
        if result["total_pages"] > 1:
            nav_row = []
            if result["current_page"] > 1:
                nav_row.append(InlineKeyboardButton("◀️ Prev", callback_data=f"transactions_page_{result['current_page'] - 1}"))
            if result["current_page"] < result["total_pages"]:
                nav_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"transactions_page_{result['current_page'] + 1}"))
            if nav_row:
                keyboard.append(nav_row)
        
        # Back button
        keyboard.append([InlineKeyboardButton("« Back", callback_data="balance")])
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error displaying transactions: {e}")
        await query.edit_message_text(
            text="❌ Error loading transaction history",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("« Back", callback_data="balance")]
            ])
        )

async def handle_history_transaction_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1):
    """Handle history transaction page display with pagination"""
    query = update.callback_query
    await query.answer()
    
    try:
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        # Get user transactions with pagination
        result = await user_db.get_user_transactions(query.from_user.id, page=page, per_page=4)
        
        if not result or result["total_transactions"] == 0:
            await query.edit_message_text(
                text="💎 Transaction History\n\n🙈 You don't have any transaction history",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("« Back", callback_data="history")]
                ])
            )
            return
        
        # Build transaction message
        message = f"💎 Transaction History\n📩 Page {result['current_page']} of {result['total_pages']}\n\n"
        
        for i, transaction in enumerate(result["transactions"], 1):
            # Format the transaction
            tx_type = transaction.get("type", "unknown")
            reason = transaction.get("reason", "No description")
            amount = transaction.get("amount", 0.0)
            closing_balance = transaction.get("closing_balance", 0.0)
            created_at = transaction.get("created_at")
            
            # Format date
            if isinstance(created_at, str):
                date_str = created_at
            else:
                try:
                    date_str = created_at.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
                except:
                    date_str = str(created_at)
            
            # Format amount display
            amount_text = f"Amount credited" if tx_type == "credit" else f"Amount debited"
            
            message += f"✉️ {reason}\n"
            message += f"<b>{amount_text}</b>: {amount} 💰\n"
            message += f"<b>Closing balance</b>: {closing_balance} 💎\n"
            message += f"📅 Created On: {date_str}\n\n"
        
        # Create pagination keyboard
        keyboard = []
        
        # Navigation buttons (only if multiple pages)
        if result["total_pages"] > 1:
            nav_row = []
            if result["current_page"] > 1:
                nav_row.append(InlineKeyboardButton("◀️ Prev", callback_data=f"history_transactions_page_{result['current_page'] - 1}"))
            if result["current_page"] < result["total_pages"]:
                nav_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"history_transactions_page_{result['current_page'] + 1}"))
            if nav_row:
                keyboard.append(nav_row)
        
        # Back button
        keyboard.append([InlineKeyboardButton("« Back", callback_data="history")])
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error displaying history transactions: {e}")
        await query.edit_message_text(
            text="💎 Transaction History\n\n❌ Error loading transaction history",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("« Back", callback_data="history")]
            ])
        )

async def handle_promocode_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle promocode reply messages"""
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        promocode = update.message.text.strip()
        
        # Send processing message
        processing_msg = await context.bot.send_message(
            chat_id=chat_id,
            text="⏳ Processing your promocode..."
        )
        
        # Wait 2 seconds as requested
        import asyncio
        await asyncio.sleep(2)
        
        # Check and use promocode from database
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        # Use the promocode
        result = await user_db.use_promocode(promocode, user.id)
        
        if result["valid"]:
            # Get updated user balance for success message
            from src.database.user_db import UserDatabase
            user_db = UserDatabase()
            if not hasattr(user_db, 'client') or user_db.client is None:
                await user_db.initialize()
            
            # Get user's current balance
            user = await user_db.users_collection.find_one({"user_id": user.id})
            current_balance = user.get("balance", 0.0) if user else 0.0
            
            # Exciting success message with party emojis
            success_message = f"""🎉🎊🎉 HURAYYYYYYY! 🎉🎊🎉

🎁 Your promocode <b>{promocode.upper()}</b> has been successfully applied!

💰 Amount added to your account: <b>{result['amount']} 💎</b>

💳 Your wallet balance is now: <b>{current_balance} 💎</b>

✨ Enjoy your instant credit! ✨"""
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=success_message,
                parse_mode='HTML'
            )
        else:
            # Error message
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ {result['message']}"
            )
        
    except Exception as e:
        logger.error(f"❌ Error in promocode reply handler: {e}")
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Something went wrong processing your promocode."
            )
        except:
            pass

async def handle_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle transaction history button"""
    query = update.callback_query
    
    try:
        from src.database.user_db import UserDatabase
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        # Get user transactions with pagination
        result = await user_db.get_user_transactions(query.from_user.id, page=1, per_page=4)
        
        if not result or result["total_transactions"] == 0:
            message = "💎 Transaction History\n\n🙈 You don't have any transaction history"
            keyboard = [
                [InlineKeyboardButton("« Back", callback_data="history")]
            ]
        else:
            # Build transaction message
            message = f"💎 Transaction History\n📩 Page {result['current_page']} of {result['total_pages']}\n\n"
            
            for i, transaction in enumerate(result["transactions"], 1):
                # Format the transaction
                tx_type = transaction.get("type", "unknown")
                reason = transaction.get("reason", "No description")
                amount = transaction.get("amount", 0.0)
                closing_balance = transaction.get("closing_balance", 0.0)
                created_at = transaction.get("created_at")
                
                # Format date
                if isinstance(created_at, str):
                    date_str = created_at
                else:
                    try:
                        date_str = created_at.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
                    except:
                        date_str = str(created_at)
                
                # Format amount display
                amount_text = f"Amount credited" if tx_type == "credit" else f"Amount debited"
                
                message += f"✉️ {reason}\n"
                message += f"<b>{amount_text}</b>: {amount} 💰\n"
                message += f"<b>Closing balance</b>: {closing_balance} 💎\n"
                message += f"📅 Created On: {date_str}\n\n"
            
            # Create pagination keyboard
            keyboard = []
            
            # Navigation buttons (only if multiple pages)
            if result["total_pages"] > 1:
                nav_row = []
                if result["current_page"] > 1:
                    nav_row.append(InlineKeyboardButton("◀️ Prev", callback_data=f"history_transactions_page_{result['current_page'] - 1}"))
                if result["current_page"] < result["total_pages"]:
                    nav_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"history_transactions_page_{result['current_page'] + 1}"))
                if nav_row:
                    keyboard.append(nav_row)
            
            # Back button
            keyboard.append([InlineKeyboardButton("« Back", callback_data="history")])
        
        await query.edit_message_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error displaying transaction history: {e}")
        message = "💎 Transaction History\n\n❌ Error loading transaction history"
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
    elif callback_data == "admin_users":
        await handle_admin_users(update, context)
    elif callback_data == "admin_auto_import":
        await handle_admin_auto_import(update, context)
    elif callback_data == "admin_add_promocode":
        await handle_admin_add_promocode(update, context)
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
    message += "Admin Commands:\n\n"
    message += "👉 Add Balance - /add 1980442239 100\n"
    message += "👉 Cut Balance - /cut 1980442239 100\n"
    message += "👉 User Transaction History - /trnx 1980442239\n"
    message += "👉 User Number History - /nums 1980442239\n"
    message += "👉 User SMM service History - /smm_history 1980442239\n"
    message += "👉 Ban User - /ban 1980442239\n"
    message += "👉 Unban User - /unban 1980442239\n"
    message += "👉 Broadcast a message - /broadcast hello everyone\n\n"
    message += "⚠️ Remember to replace 1980442239 with actual user id."
    
    # Create admin keyboard with Web App buttons
    from src.config.bot_config import BotConfig
    config = BotConfig()
    backend_url = config.BACKEND_URL
    
    keyboard = [
        [
            InlineKeyboardButton("Dashboard", web_app={"url": f"{backend_url}/admin-dashboard"}),
            InlineKeyboardButton("Users", callback_data="admin_users")
        ],
        [InlineKeyboardButton("Auto Import API Services", callback_data="admin_auto_import")],
        [
            InlineKeyboardButton("Add Server", web_app={"url": f"{backend_url}/add-server"}),
            InlineKeyboardButton("Add Service", web_app={"url": f"{backend_url}/add-service"})
        ],
        [
            InlineKeyboardButton("Connect API", web_app={"url": f"{backend_url}/connect-api"}),
            InlineKeyboardButton("Edit Bot Settings", web_app={"url": f"{backend_url}/bot-settings"})
        ],
        [InlineKeyboardButton("View My Services", web_app={"url": f"{backend_url}/my-services"})],
        [InlineKeyboardButton("QR Code", web_app={"url": f"{backend_url}/qr-code"})],
        [InlineKeyboardButton("Add Promocode", callback_data="admin_add_promocode")],
        [InlineKeyboardButton("View Manual Payments", callback_data="admin_manual_payments")]
    ]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
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

async def handle_server_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle server selection callback"""
    try:
        logger.info("🎯 SERVER CALLBACK HANDLER TRIGGERED!")
        query = update.callback_query
        
        # Parse callback data
        callback_data = query.data
        logger.info(f"🔍 DEBUG: Server callback data: {callback_data}")
        
        if not callback_data.startswith('srv:'):
            logger.info(f"🔍 DEBUG: Callback doesn't start with 'srv:', skipping")
            return
        
        parts = callback_data.split(':')
        if len(parts) != 3:
            await query.edit_message_text("❌ Invalid callback data")
            return
        
        service_id = parts[1]
        server_id = parts[2]
        
        logger.info(f"🔍 User {update.effective_user.id} selected server {server_id} for service {service_id}")
        
        # Initialize service database
        from src.database.service_db import ServiceDatabase
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

async def handle_unknown_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown callback data"""
    query = update.callback_query
    
    await query.answer("This feature is not available yet!")
    
    # Go back to main menu
    await handle_back_to_main(update, context)
