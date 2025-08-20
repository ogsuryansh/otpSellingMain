"""
User Database Module
"""

import asyncio
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserDatabase:
    """Database handler for user operations"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserDatabase, cls).__new__(cls)
            cls._instance.client: Optional[AsyncIOMotorClient] = None
            cls._instance.db = None
            cls._instance.users_collection = None
        return cls._instance
    
    def __init__(self):
        pass
    
    async def initialize(self):
        """Initialize database connection"""
        if self._initialized and self.client:
            return
            
        try:
            from src.config.bot_config import BotConfig
            config = BotConfig()
            
            logger.info(f"🔗 Connecting to MongoDB...")
            
            self.client = AsyncIOMotorClient(config.MONGODB_URI)
            self.db = self.client[config.MONGODB_DATABASE]
            self.users_collection = self.db[config.MONGODB_COLLECTION]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB connected successfully!")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None) -> Dict[str, Any]:
        """Get user from database or create if not exists"""
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            
            if not user:
                # Create new user with updated schema
                user_data = {
                    "user_id": user_id,
                    "username": username,
                    "first_name": first_name,
                    "balance": 0.0,
                    "total_purchased": 0,
                    "total_used": 0,
                    "transaction_history": [],
                    "number_history": [],
                    "smm_history": [],
                    "banned": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await self.users_collection.insert_one(user_data)
                user_data["_id"] = result.inserted_id
                logger.info(f"Created new user: {user_id}")
                return user_data
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting/creating user {user_id}: {e}")
            # Return default user data if database fails
            return {
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "balance": 0.0,
                "total_purchased": 0,
                "total_used": 0,
                "transaction_history": [],
                "number_history": [],
                "smm_history": [],
                "banned": False
            }
    
    async def update_user_balance(self, user_id: int, amount: float):
        """Update user balance"""
        try:
            await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"balance": amount},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception as e:
            logger.error(f"Error updating balance for user {user_id}: {e}")
    
    async def increment_purchased_count(self, user_id: int):
        """Increment total purchased count"""
        try:
            await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"total_purchased": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception as e:
            logger.error(f"Error incrementing purchased count for user {user_id}: {e}")
    
    async def increment_used_count(self, user_id: int):
        """Increment total used count"""
        try:
            await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"total_used": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        except Exception as e:
            logger.error(f"Error incrementing used count for user {user_id}: {e}")
    
    async def add_balance(self, user_id: int, amount: float) -> bool:
        """Add balance to user"""
        try:
            # Get current user data
            user = await self.users_collection.find_one({"user_id": user_id})
            if not user:
                return False
            
            current_balance = user.get("balance", 0.0)
            new_balance = current_balance + amount
            
            # Create transaction record
            transaction_record = {
                "type": "credit",
                "reason": f"Admin added {amount} balance",
                "amount": amount,
                "closing_balance": new_balance,
                "created_at": datetime.utcnow()
            }
            
            # Update user document with new balance and transaction
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "balance": new_balance,
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {
                        "transaction_history": transaction_record
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding balance for user {user_id}: {e}")
            return False
    
    async def cut_balance(self, user_id: int, amount: float) -> bool:
        """Cut balance from user (prevent negative balance)"""
        try:
            # First check current balance
            user = await self.users_collection.find_one({"user_id": user_id})
            if not user:
                return False
            
            current_balance = user.get("balance", 0.0)
            if current_balance < amount:
                return False  # Insufficient balance
            
            new_balance = current_balance - amount
            
            # Create transaction record
            transaction_record = {
                "type": "debit",
                "reason": f"Admin cut {amount} balance",
                "amount": amount,
                "closing_balance": new_balance,
                "created_at": datetime.utcnow()
            }
            
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "balance": new_balance,
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {
                        "transaction_history": transaction_record
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error cutting balance for user {user_id}: {e}")
            return False
    
    async def get_user_history(self, user_id: int) -> Dict[str, Any]:
        """Get user's transaction, number, and SMM history"""
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            if not user:
                return None
            
            return {
                "transaction_history": user.get("transaction_history", []),
                "number_history": user.get("number_history", []),
                "smm_history": user.get("smm_history", [])
            }
        except Exception as e:
            logger.error(f"Error getting history for user {user_id}: {e}")
            return None
    
    async def ban_user(self, user_id: int) -> bool:
        """Ban user"""
        try:
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"banned": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            return False
    
    async def unban_user(self, user_id: int) -> bool:
        """Unban user"""
        try:
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"banned": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            return False
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for broadcast"""
        try:
            cursor = self.users_collection.find({})
            users = await cursor.to_list(length=None)
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def clear_all_data(self):
        """Clear all data from the collection"""
        try:
            result = await self.users_collection.delete_many({})
            logger.info(f"Cleared {result.deleted_count} documents from users collection")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            return 0
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

    async def log_transaction(self, user_id: int, transaction_type: str, reason: str, amount: float) -> bool:
        """
        Log a transaction and update user balance
        
        Args:
            user_id: User ID
            transaction_type: "credit" or "debit"
            reason: Description of the transaction
            amount: Transaction amount
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current user data
            user = await self.users_collection.find_one({"user_id": user_id})
            if not user:
                logger.error(f"User {user_id} not found for transaction logging")
                return False
            
            current_balance = user.get("balance", 0.0)
            
            # Calculate new balance
            if transaction_type == "credit":
                new_balance = current_balance + amount
            elif transaction_type == "debit":
                if current_balance < amount:
                    logger.error(f"Insufficient balance for user {user_id}: {current_balance} < {amount}")
                    return False
                new_balance = current_balance - amount
            else:
                logger.error(f"Invalid transaction type: {transaction_type}")
                return False
            
            # Create transaction record
            transaction_record = {
                "type": transaction_type,
                "reason": reason,
                "amount": amount,
                "closing_balance": new_balance,
                "created_at": datetime.utcnow()
            }
            
            # Update user document with new balance and transaction
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "balance": new_balance,
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {
                        "transaction_history": transaction_record
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Transaction logged for user {user_id}: {transaction_type} {amount} - {reason}")
                return True
            else:
                logger.error(f"Failed to update user {user_id} for transaction")
                return False
                
        except Exception as e:
            logger.error(f"Error logging transaction for user {user_id}: {e}")
            return False

    async def get_user_transactions(self, user_id: int, page: int = 1, per_page: int = 4) -> dict:
        """
        Get user transactions with pagination
        
        Args:
            user_id: User ID
            page: Page number (1-based)
            per_page: Transactions per page
            
        Returns:
            dict: {
                "transactions": [...],
                "total_pages": int,
                "current_page": int,
                "total_transactions": int
            }
        """
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            if not user:
                return None
            
            transactions = user.get("transaction_history", [])
            total_transactions = len(transactions)
            
            if total_transactions == 0:
                return {
                    "transactions": [],
                    "total_pages": 0,
                    "current_page": 1,
                    "total_transactions": 0
                }
            
            # Calculate pagination
            total_pages = (total_transactions + per_page - 1) // per_page
            page = max(1, min(page, total_pages))  # Ensure page is within bounds
            
            # Get transactions for current page (most recent first)
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            
            # Reverse to show most recent first
            reversed_transactions = list(reversed(transactions))
            page_transactions = reversed_transactions[start_index:end_index]
            
            return {
                "transactions": page_transactions,
                "total_pages": total_pages,
                "current_page": page,
                "total_transactions": total_transactions
            }
            
        except Exception as e:
            logger.error(f"Error getting transactions for user {user_id}: {e}")
            return None

    async def check_promocode(self, promocode: str) -> Dict[str, Any]:
        """Check if promocode exists and is valid"""
        try:
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Use existing database connection but different collection
            promocodes_collection = self.db['promocodes']
            
            logger.info(f"🔍 Checking promocode: {promocode.upper()}")
            
            # Find promocode
            promocode_data = await promocodes_collection.find_one({
                "code": promocode.upper(),
                "is_active": True
            })
            
            if not promocode_data:
                logger.info(f"❌ Promocode not found: {promocode.upper()}")
                return {"valid": False, "message": "Promocode not found or inactive"}
            
            # Check if promocode has reached max uses
            current_uses = promocode_data.get("current_uses", 0)
            max_uses = promocode_data.get("max_uses", 0)
            
            if current_uses >= max_uses:
                logger.info(f"❌ Promocode usage limit reached: {promocode.upper()} ({current_uses}/{max_uses})")
                return {"valid": False, "message": "Promocode usage limit reached"}
            
            logger.info(f"✅ Promocode valid: {promocode.upper()} - Amount: {promocode_data.get('amount', 0)}")
            
            return {
                "valid": True,
                "amount": promocode_data.get("amount", 0),
                "max_uses": max_uses,
                "current_uses": current_uses,
                "promocode_id": str(promocode_data.get("_id"))
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking promocode: {e}")
            return {"valid": False, "message": "Error checking promocode"}
    
    async def use_promocode(self, promocode: str, user_id: int) -> Dict[str, Any]:
        """Use a promocode and add balance to user"""
        try:
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            logger.info(f"🎫 Using promocode: {promocode.upper()} for user: {user_id}")
            
            # First check if promocode is valid
            check_result = await self.check_promocode(promocode)
            if not check_result["valid"]:
                logger.info(f"❌ Promocode validation failed: {check_result['message']}")
                return check_result
            
            # Use existing database connection but different collection
            promocodes_collection = self.db['promocodes']
            
            # Update promocode usage count
            result = await promocodes_collection.update_one(
                {"code": promocode.upper()},
                {"$inc": {"current_uses": 1}}
            )
            
            if result.modified_count == 0:
                logger.error(f"❌ Failed to update promocode usage count: {promocode.upper()}")
                return {"valid": False, "message": "Failed to update promocode usage"}
            
            logger.info(f"✅ Updated promocode usage count: {promocode.upper()}")
            
            # Add balance to user
            amount = check_result["amount"]
            success = await self.log_transaction(user_id, "credit", f"Promocode: {promocode.upper()}", amount)
            
            if success:
                logger.info(f"✅ Successfully added {amount} 💎 to user {user_id} via promocode {promocode.upper()}")
                return {
                    "valid": True,
                    "amount": amount,
                    "message": f"Successfully added {amount} 💎 to your balance!"
                }
            else:
                logger.error(f"❌ Failed to add balance for user {user_id} via promocode {promocode.upper()}")
                return {"valid": False, "message": "Failed to add balance"}
                
        except Exception as e:
            logger.error(f"❌ Error using promocode: {e}")
            return {"valid": False, "message": "Error processing promocode"}
