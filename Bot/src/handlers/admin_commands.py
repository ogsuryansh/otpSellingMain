"""
Admin Commands Handler
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging
import re
from src.config.bot_config import BotConfig
from src.database.user_db import UserDatabase

logger = logging.getLogger(__name__)

async def handle_add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command: /add <user_id> <amount>"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Parse command arguments
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("❌ Usage: /add <user_id> <amount>")
            return
        
        try:
            user_id = int(args[0])
            amount = float(args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id or amount. Both must be numbers.")
            return
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be greater than 0.")
            return
        
        # Add balance
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        success = await user_db.add_balance(user_id, amount)
        
        if success:
            await update.message.reply_text(f"✅ Successfully added {amount} balance to user {user_id}")
        else:
            await update.message.reply_text(f"❌ Failed to add balance. User {user_id} might not exist.")
            
    except Exception as e:
        logger.error(f"Error in add_balance command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_cut_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cut command: /cut <user_id> <amount>"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Parse command arguments
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("❌ Usage: /cut <user_id> <amount>")
            return
        
        try:
            user_id = int(args[0])
            amount = float(args[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id or amount. Both must be numbers.")
            return
        
        if amount <= 0:
            await update.message.reply_text("❌ Amount must be greater than 0.")
            return
        
        # Cut balance
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        success = await user_db.cut_balance(user_id, amount)
        
        if success:
            await update.message.reply_text(f"✅ Successfully cut {amount} balance from user {user_id}")
        else:
            await update.message.reply_text(f"❌ Failed to cut balance. User {user_id} might not exist or have insufficient balance.")
            
    except Exception as e:
        logger.error(f"Error in cut_balance command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trnx command: /trnx <user_id>"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Parse command arguments
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌ Usage: /trnx <user_id>")
            return
        
        try:
            user_id = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id. Must be a number.")
            return
        
        # Get transaction history
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        history = await user_db.get_user_history(user_id)
        
        if history is None:
            await update.message.reply_text(f"❌ User {user_id} not found.")
            return
        
        transactions = history.get("transaction_history", [])
        
        if not transactions:
            await update.message.reply_text(f"📊 Transaction History for User {user_id}:\n\n🙈 No transactions found.")
            return
        
        # Format transaction history
        message = f"📊 Transaction History for User {user_id}:\n\n"
        for i, tx in enumerate(transactions[-10:], 1):  # Show last 10 transactions
            tx_type = "➕" if tx.get("type") == "credit" else "➖"
            amount = tx.get("amount", 0)
            reason = tx.get("reason", "No description")
            created_at = tx.get("created_at", "Unknown time")
            
            # Format timestamp
            if isinstance(created_at, str):
                time_str = created_at
            elif hasattr(created_at, 'strftime'):
                time_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = "Unknown time"
            
            message += f"{i}. {tx_type} {amount} 💎 - {reason}\n"
            message += f"   📅 {time_str}\n\n"
        
        await update.message.reply_text(message)
            
    except Exception as e:
        logger.error(f"Error in transaction_history command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_number_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /nums command: /nums <user_id>"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Parse command arguments
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌ Usage: /nums <user_id>")
            return
        
        try:
            user_id = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id. Must be a number.")
            return
        
        # Get number history
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        history = await user_db.get_user_history(user_id)
        
        if history is None:
            await update.message.reply_text(f"❌ User {user_id} not found.")
            return
        
        numbers = history.get("number_history", [])
        
        if not numbers:
            await update.message.reply_text(f"📱 Number History for User {user_id}:\n\n🍒 No number history found.")
            return
        
        # Format number history
        message = f"📱 Number History for User {user_id}:\n\n"
        for i, num in enumerate(numbers[-10:], 1):  # Show last 10 numbers
            number = num.get("number", "Unknown")
            service = num.get("service", "Unknown service")
            status = num.get("status", "Unknown")
            timestamp = num.get("timestamp", "Unknown time")
            
            if isinstance(timestamp, str):
                time_str = timestamp
            else:
                time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            message += f"{i}. 📞 {number} ({service})\n"
            message += f"   📊 Status: {status}\n"
            message += f"   📅 {time_str}\n\n"
        
        await update.message.reply_text(message)
            
    except Exception as e:
        logger.error(f"Error in number_history command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_smm_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /smm_history command: /smm_history <user_id>"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Parse command arguments
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌ Usage: /smm_history <user_id>")
            return
        
        try:
            user_id = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id. Must be a number.")
            return
        
        # Get SMM history
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        history = await user_db.get_user_history(user_id)
        
        if history is None:
            await update.message.reply_text(f"❌ User {user_id} not found.")
            return
        
        smm_orders = history.get("smm_history", [])
        
        if not smm_orders:
            await update.message.reply_text(f"📈 SMM History for User {user_id}:\n\n📦 No SMM orders found.")
            return
        
        # Format SMM history
        message = f"📈 SMM History for User {user_id}:\n\n"
        for i, order in enumerate(smm_orders[-10:], 1):  # Show last 10 orders
            service = order.get("service", "Unknown service")
            link = order.get("link", "No link")
            quantity = order.get("quantity", 0)
            status = order.get("status", "Unknown")
            timestamp = order.get("timestamp", "Unknown time")
            
            if isinstance(timestamp, str):
                time_str = timestamp
            else:
                time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            message += f"{i}. 📦 {service}\n"
            message += f"   🔗 Link: {link}\n"
            message += f"   📊 Quantity: {quantity}\n"
            message += f"   📈 Status: {status}\n"
            message += f"   📅 {time_str}\n\n"
        
        await update.message.reply_text(message)
            
    except Exception as e:
        logger.error(f"Error in smm_history command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ban command: /ban <user_id>"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Parse command arguments
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌ Usage: /ban <user_id>")
            return
        
        try:
            user_id = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id. Must be a number.")
            return
        
        # Ban user
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        success = await user_db.ban_user(user_id)
        
        if success:
            await update.message.reply_text(f"🚫 Successfully banned user {user_id}")
        else:
            await update.message.reply_text(f"❌ Failed to ban user {user_id}. User might not exist.")
            
    except Exception as e:
        logger.error(f"Error in ban_user command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unban command: /unban <user_id>"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Parse command arguments
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌ Usage: /unban <user_id>")
            return
        
        try:
            user_id = int(args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user_id. Must be a number.")
            return
        
        # Unban user
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        success = await user_db.unban_user(user_id)
        
        if success:
            await update.message.reply_text(f"✅ Successfully unbanned user {user_id}")
        else:
            await update.message.reply_text(f"❌ Failed to unban user {user_id}. User might not exist.")
            
    except Exception as e:
        logger.error(f"Error in unban_user command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command: /broadcast <message>"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Get message from command
        if not context.args:
            await update.message.reply_text("❌ Usage: /broadcast <message>")
            return
        
        message = " ".join(context.args)
        if not message.strip():
            await update.message.reply_text("❌ Message cannot be empty.")
            return
        
        # Get all users for broadcast
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        users = await user_db.get_all_users()
        
        if not users:
            await update.message.reply_text("📢 No users found to broadcast to.")
            return
        
        # Send broadcast message
        success_count = 0
        failed_count = 0
        
        for user in users:
            try:
                user_id = user.get("user_id")
                if user_id:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"📢 <b>BROADCAST MESSAGE</b>\n\n{message}"
                    )
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast to user {user.get('user_id')}: {e}")
                failed_count += 1
        
        # Send summary
        summary = f"📢 Broadcast completed!\n\n"
        summary += f"✅ Successfully sent: {success_count}\n"
        summary += f"❌ Failed to send: {failed_count}\n"
        summary += f"📊 Total users: {len(users)}"
        
        await update.message.reply_text(summary)
            
    except Exception as e:
        logger.error(f"Error in broadcast command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_delete_all_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /delalldata command with confirmation"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        # Check if this is a confirmation
        if context.args and context.args[0].lower() == "confirm":
            # User confirmed deletion
            user_db = UserDatabase()
            if not hasattr(user_db, 'client') or user_db.client is None:
                await user_db.initialize()
            
            # Get user count before deletion
            users = await user_db.get_all_users()
            user_count = len(users)
            
            # Clear all data
            cleared_count = await user_db.clear_all_data()
            
            await update.message.reply_text(
                f"🗑️ <b>DATA DELETION COMPLETED</b>\n\n"
                f"✅ Successfully deleted {cleared_count} user records\n"
                f"📊 Total users deleted: {user_count}\n\n"
                f"⚠️ All user data has been permanently removed from the database."
            )
        else:
            # Ask for confirmation
            await update.message.reply_text(
                "⚠️ <b>DANGER ZONE</b> ⚠️\n\n"
                "You are about to delete ALL user data from the database.\n"
                "This action is <b>IRREVERSIBLE</b>!\n\n"
                "To confirm deletion, type:\n"
                "`/delalldata confirm`\n\n"
                "⚠️ This will delete all user records, balances, and history."
            )
            
    except Exception as e:
        logger.error(f"Error in delete_all_data command: {e}")
        await update.message.reply_text("❌ An error occurred while processing the command.")

async def handle_sync_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sync command: Sync all data with website"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        await update.message.reply_text("🔄 Starting data synchronization with website...")
        
        # Import service database for sync
        from src.database.service_db import ServiceDatabase
        service_db = ServiceDatabase()
        
        # Perform complete sync
        sync_result = await service_db.sync_all_data_with_website()
        
        if sync_result["success"]:
            message = "✅ Data synchronization completed!\n\n"
            message += f"📊 Users: {sync_result['users']['synced_users']}/{sync_result['users']['total_users']} synced\n"
            message += f"🔧 Services: {sync_result['services']['synced_services']}/{sync_result['services']['total_services']} synced\n"
            message += f"🖥️ Servers: {sync_result['servers']['synced_servers']}/{sync_result['servers']['total_servers']} synced\n\n"
            message += f"📈 Total synced: {sync_result['total_synced']}\n"
            message += f"❌ Total failed: {sync_result['total_failed']}"
        else:
            message = f"❌ Data synchronization failed: {sync_result.get('error', 'Unknown error')}"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in sync_data command: {e}")
        await update.message.reply_text("❌ Error during data synchronization.")

async def handle_sync_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /syncusers command: Sync only user data with website"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        await update.message.reply_text("🔄 Starting user data synchronization...")
        
        # Perform user sync
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        sync_result = await user_db.sync_all_users_with_website()
        
        if sync_result["success"]:
            message = "✅ User data synchronization completed!\n\n"
            message += f"📊 Total users: {sync_result['total_users']}\n"
            message += f"✅ Synced: {sync_result['synced_users']}\n"
            message += f"❌ Failed: {sync_result['failed_users']}"
        else:
            message = f"❌ User synchronization failed: {sync_result.get('error', 'Unknown error')}"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in sync_users command: {e}")
        await update.message.reply_text("❌ Error during user synchronization.")

async def handle_sync_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /syncservices command: Sync only service data with website"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        await update.message.reply_text("🔄 Starting service data synchronization...")
        
        # Import service database for sync
        from src.database.service_db import ServiceDatabase
        service_db = ServiceDatabase()
        
        # Perform service sync
        sync_result = await service_db.sync_services_with_website()
        
        if sync_result["success"]:
            message = "✅ Service data synchronization completed!\n\n"
            message += f"🔧 Total services: {sync_result['total_services']}\n"
            message += f"✅ Synced: {sync_result['synced_services']}\n"
            message += f"❌ Failed: {sync_result['failed_services']}"
        else:
            message = f"❌ Service synchronization failed: {sync_result.get('error', 'Unknown error')}"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in sync_services command: {e}")
        await update.message.reply_text("❌ Error during service synchronization.")

async def handle_check_sync_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /syncstatus command: Check sync status between bot and website"""
    try:
        # Check if user is admin
        config = BotConfig()
        if not config.ADMIN_USER_ID or str(update.effective_user.id) != str(config.ADMIN_USER_ID):
            await update.message.reply_text("❌ You don't have permission to use admin commands.")
            return
        
        await update.message.reply_text("🔍 Checking sync status...")
        
        # Get counts from bot database
        user_db = UserDatabase()
        if not hasattr(user_db, 'client') or user_db.client is None:
            await user_db.initialize()
        
        bot_users_count = await user_db.users_collection.count_documents({})
        
        # Import service database
        from src.database.service_db import ServiceDatabase
        service_db = ServiceDatabase()
        
        bot_services_count = await service_db.services_collection.count_documents({})
        bot_servers_count = await service_db.servers_collection.count_documents({})
        
        # Get counts from website database
        website_users_count = await user_db.db['website_users'].count_documents({})
        website_services_count = await service_db.db['services'].count_documents({})
        website_servers_count = await service_db.db['servers'].count_documents({})
        
        message = "📊 Sync Status Report\n\n"
        message += f"👥 Users:\n"
        message += f"   Bot: {bot_users_count}\n"
        message += f"   Website: {website_users_count}\n"
        message += f"   Status: {'✅ Synced' if bot_users_count == website_users_count else '⚠️ Out of sync'}\n\n"
        
        message += f"🔧 Services:\n"
        message += f"   Bot: {bot_services_count}\n"
        message += f"   Website: {website_services_count}\n"
        message += f"   Status: {'✅ Synced' if bot_services_count == website_services_count else '⚠️ Out of sync'}\n\n"
        
        message += f"🖥️ Servers:\n"
        message += f"   Bot: {bot_servers_count}\n"
        message += f"   Website: {website_servers_count}\n"
        message += f"   Status: {'✅ Synced' if bot_servers_count == website_servers_count else '⚠️ Out of sync'}"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in check_sync_status command: {e}")
        await update.message.reply_text("❌ Error checking sync status.")
