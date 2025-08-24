"""
User Database Module
"""

import asyncio
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging
from contextlib import asynccontextmanager
from src.utils.cache_manager import cached

logger = logging.getLogger(__name__)

class UserDatabase:
    """Database handler for user operations with connection pooling"""
    _instance = None
    _initialized = False
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserDatabase, cls).__new__(cls)
            cls._instance.client: Optional[AsyncIOMotorClient] = None
            cls._instance.db = None
            cls._instance.users_collection = None
            cls._instance._max_pool_size = 10
            cls._instance._min_pool_size = 1
            cls._instance._max_idle_time_ms = 30000
        return cls._instance
    
    def __init__(self):
        pass
    
    async def initialize(self):
        """Initialize database connection with connection pooling"""
        if self._initialized and self.client:
            return
            
        try:
            from src.config.bot_config import BotConfig
            config = BotConfig()
            
            logger.info(f"🔗 Connecting to MongoDB with connection pooling...")
            
            # Create client with connection pooling settings
            self.client = AsyncIOMotorClient(
                config.MONGODB_URI,
                maxPoolSize=self._max_pool_size,
                minPoolSize=self._min_pool_size,
                maxIdleTimeMS=self._max_idle_time_ms,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            self.db = self.client[config.MONGODB_DATABASE]
            self.users_collection = self.db[config.MONGODB_COLLECTION]
            
            # Test connection with timeout
            await asyncio.wait_for(
                self.client.admin.command('ping'),
                timeout=5.0
            )
            
            logger.info("✅ MongoDB connected successfully with connection pooling!")
            self._initialized = True
            
        except asyncio.TimeoutError:
            logger.error("❌ MongoDB connection timeout")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections"""
        if not self._initialized:
            await self.initialize()
        
        try:
            yield self.client
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    async def _ensure_connection(self):
        """Ensure database connection is available"""
        if not self._initialized or not self.client:
            await self.initialize()
        
        # Test connection
        try:
            await asyncio.wait_for(
                self.client.admin.command('ping'),
                timeout=2.0
            )
        except (asyncio.TimeoutError, Exception):
            logger.warning("Database connection lost, reconnecting...")
            await self.initialize()
    
    @cached(ttl=300, key_prefix="user")
    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None) -> Dict[str, Any]:
        """Get user from database or create if not exists with connection management and caching"""
        try:
            await self._ensure_connection()
            
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

    @cached(ttl=60, key_prefix="services")
    async def get_services(self) -> List[Dict[str, Any]]:
        """Get all services from the website's MongoDB with caching"""
        try:
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            logger.info("🔍 Fetching services from database...")
            logger.info(f"🔍 Database connection status: {self.client is not None}")
            logger.info(f"🔍 Database name: {self.db.name}")
            
            # Use existing database connection but different collection
            services_collection = self.db['services']
            logger.info(f"🔍 Services collection: {services_collection}")
            
            # First, let's check if the collection exists and has any documents
            total_services = await services_collection.count_documents({})
            logger.info(f"📊 Total services in collection: {total_services}")
            
            # Get all services (not just active ones for now)
            cursor = services_collection.find({})
            all_services = await cursor.to_list(length=None)
            
            logger.info(f"📦 Found {len(all_services)} total services")
            
            # Debug: Print each service
            for i, service in enumerate(all_services):
                logger.info(f"🔍 Service {i+1}:")
                logger.info(f"  - ID: {service.get('_id')}")
                logger.info(f"  - Name: {service.get('name')}")
                logger.info(f"  - Description: {service.get('description')}")
                logger.info(f"  - Price: {service.get('price')}")
                logger.info(f"  - Server Name: {service.get('server_name')}")
                logger.info(f"  - Is Active: {service.get('is_active')}")
                logger.info(f"  - Full service data: {service}")
            
            # Filter for active services if the field exists
            active_services = []
            for service in all_services:
                # Check if service is active (default to True if field doesn't exist)
                is_active = service.get("is_active", True)
                logger.info(f"🔍 Service '{service.get('name', 'Unknown')}' active status: {is_active}")
                if is_active:
                    active_services.append(service)
                    logger.info(f"  - ✅ Added to active services")
                else:
                    logger.info(f"  - ❌ Skipped (inactive)")
            
            logger.info(f"✅ Found {len(active_services)} active services")
            
            # Format services for bot
            formatted_services = []
            for service in active_services:
                service_id = str(service.get("_id"))
                service_name = service.get("name", "Unknown Service")
                service_desc = service.get("description", "No description available")
                service_price = service.get("price", "₹0")
                service_server = service.get("server_name", "Unknown Server")
                
                logger.info(f"🔍 Formatting service: {service_name}")
                logger.info(f"  - ID: {service_id}")
                logger.info(f"  - Name: {service_name}")
                logger.info(f"  - Description: {service_desc}")
                logger.info(f"  - Price: {service_price}")
                logger.info(f"  - Server: {service_server}")
                
                formatted_service = {
                    "id": service_id,
                    "name": service_name,
                    "description": service_desc,
                    "price": service_price,
                    "server": service_server
                }
                formatted_services.append(formatted_service)
                logger.info(f"  - ✅ Formatted service added")
            
            logger.info(f"✅ Formatted {len(formatted_services)} services for bot display")
            
            # If no services found, add some sample services for testing
            if len(formatted_services) == 0:
                logger.info("📝 No services found, adding sample services for testing...")
                await self.add_sample_services()
                # Try to get services again
                cursor = services_collection.find({})
                all_services = await cursor.to_list(length=None)
                active_services = [s for s in all_services if s.get("is_active", True)]
                
                for service in active_services:
                    formatted_service = {
                        "id": str(service.get("_id")),
                        "name": service.get("service_name", "Unknown Service"),
                        "description": service.get("service_description", "No description available"),
                        "price": service.get("service_price", "0"),
                        "server": service.get("server_name", "Unknown Server")
                    }
                    formatted_services.append(formatted_service)
                
                logger.info(f"✅ Added {len(formatted_services)} sample services")
            
            logger.info(f"🔍 Final formatted services: {formatted_services}")
            return formatted_services
            
        except Exception as e:
            logger.error(f"❌ Error fetching services: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return []

    async def get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific service by ID"""
        try:
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            logger.info(f"🔍 Fetching service with ID: {service_id}")
            
            # Use existing database connection but different collection
            services_collection = self.db['services']
            
            # Import ObjectId for MongoDB query
            from bson import ObjectId
            
            try:
                # Convert string ID to ObjectId
                object_id = ObjectId(service_id)
                
                # Find the service
                service = await services_collection.find_one({"_id": object_id})
                
                if service:
                    logger.info(f"✅ Found service: {service.get('name', 'Unknown')}")
                    
                    # Format service for bot
                    formatted_service = {
                        "id": str(service.get("_id")),
                        "name": service.get("name", "Unknown Service"),
                        "description": service.get("description", "No description available"),
                        "price": service.get("price", "₹0"),
                        "server": service.get("server_name", "Unknown Server"),
                        "service_id": service.get("service_id", ""),
                        "code": service.get("code", ""),
                        "cancel_disable": service.get("cancel_disable", "5"),
                        "is_active": service.get("is_active", True)
                    }
                    
                    return formatted_service
                else:
                    logger.warning(f"⚠️ Service not found with ID: {service_id}")
                    return None
                    
            except Exception as e:
                logger.error(f"❌ Error converting service ID {service_id}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching service by ID {service_id}: {e}")
            return None

    async def add_transaction(self, user_id: int, transaction: Dict[str, Any]):
        """Add a transaction to user's history"""
        try:
            logger.info(f"📝 Adding transaction for user {user_id}")
            
            # Add transaction to user's transaction history
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$push": {"transaction_history": transaction},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Transaction added for user {user_id}")
            else:
                logger.warning(f"⚠️ No user found to add transaction for user {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error adding transaction for user {user_id}: {e}")

    async def update_user_stats(self, user_id: int, amount: float):
        """Update user statistics after purchase"""
        try:
            logger.info(f"📊 Updating stats for user {user_id}")
            
            # Update total purchased amount
            result = await self.users_collection.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"total_purchased": amount},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Stats updated for user {user_id}")
            else:
                logger.warning(f"⚠️ No user found to update stats for user {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error updating stats for user {user_id}: {e}")

    async def add_sample_services(self):
        """Add sample services for testing"""
        try:
            services_collection = self.db['services']
            
            sample_services = [
                {
                    "name": "WhatsApp",
                    "description": "Get OTP for WhatsApp verification. Fast and reliable service.",
                    "price": "₹5.00",
                    "server_name": "India Server",
                    "is_active": True,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Telegram",
                    "description": "Get OTP for Telegram verification. Instant delivery.",
                    "price": "₹3.00",
                    "server_name": "India Server",
                    "is_active": True,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Instagram",
                    "description": "Get OTP for Instagram verification. High success rate.",
                    "price": "₹4.00",
                    "server_name": "India Server",
                    "is_active": True,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Facebook",
                    "description": "Get OTP for Facebook verification. Secure and reliable.",
                    "price": "₹2.00",
                    "server_name": "India Server",
                    "is_active": True,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                },
                {
                    "name": "Gmail",
                    "description": "Get OTP for Gmail verification. Premium service.",
                    "price": "₹4.50",
                    "server_name": "India Server",
                    "is_active": True,
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
            ]
            
            result = await services_collection.insert_many(sample_services)
            logger.info(f"✅ Added {len(result.inserted_ids)} sample services to database")
            
        except Exception as e:
            logger.error(f"❌ Error adding sample services: {e}")

    async def sync_user_data_with_website(self, user_id: int) -> bool:
        """
        Sync user data with website database to ensure consistency
        
        Args:
            user_id: User ID to sync
            
        Returns:
            bool: True if sync successful, False otherwise
        """
        try:
            logger.info(f"🔄 Syncing user data for user {user_id} with website...")
            
            # Get user data from bot database
            user = await self.users_collection.find_one({"user_id": user_id})
            if not user:
                logger.warning(f"⚠️ User {user_id} not found in bot database")
                return False
            
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Sync with website's users collection (if different from bot's)
            website_users_collection = self.db['website_users']
            
            # Prepare user data for website
            website_user_data = {
                "user_id": user["user_id"],
                "username": user.get("username"),
                "first_name": user.get("first_name"),
                "balance": user.get("balance", 0.0),
                "total_purchased": user.get("total_purchased", 0),
                "total_used": user.get("total_used", 0),
                "banned": user.get("banned", False),
                "created_at": user.get("created_at"),
                "updated_at": datetime.utcnow(),
                "last_sync": datetime.utcnow()
            }
            
            # Upsert user data in website collection
            result = await website_users_collection.update_one(
                {"user_id": user_id},
                {"$set": website_user_data},
                upsert=True
            )
            
            if result.modified_count > 0 or result.upserted_id:
                logger.info(f"✅ User {user_id} data synced with website successfully")
                return True
            else:
                logger.warning(f"⚠️ No changes made during sync for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error syncing user {user_id} data with website: {e}")
            return False

    async def sync_all_users_with_website(self) -> Dict[str, Any]:
        """
        Sync all users data with website database
        
        Returns:
            dict: Sync results with counts
        """
        try:
            logger.info("🔄 Starting full user data sync with website...")
            
            # Get all users from bot database
            cursor = self.users_collection.find({})
            all_users = await cursor.to_list(length=None)
            
            if not all_users:
                logger.info("ℹ️ No users found in bot database")
                return {"success": True, "total_users": 0, "synced_users": 0, "failed_users": 0}
            
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Sync with website's users collection
            website_users_collection = self.db['website_users']
            
            synced_count = 0
            failed_count = 0
            
            for user in all_users:
                try:
                    # Prepare user data for website
                    website_user_data = {
                        "user_id": user["user_id"],
                        "username": user.get("username"),
                        "first_name": user.get("first_name"),
                        "balance": user.get("balance", 0.0),
                        "total_purchased": user.get("total_purchased", 0),
                        "total_used": user.get("total_used", 0),
                        "banned": user.get("banned", False),
                        "created_at": user.get("created_at"),
                        "updated_at": datetime.utcnow(),
                        "last_sync": datetime.utcnow()
                    }
                    
                    # Upsert user data
                    result = await website_users_collection.update_one(
                        {"user_id": user["user_id"]},
                        {"$set": website_user_data},
                        upsert=True
                    )
                    
                    if result.modified_count > 0 or result.upserted_id:
                        synced_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error syncing user {user.get('user_id')}: {e}")
                    failed_count += 1
            
            logger.info(f"✅ Full sync completed: {synced_count} synced, {failed_count} failed out of {len(all_users)} total")
            
            return {
                "success": True,
                "total_users": len(all_users),
                "synced_users": synced_count,
                "failed_users": failed_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error during full user sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_users": 0,
                "synced_users": 0,
                "failed_users": 0
            }

    async def get_website_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user data from website database
        
        Args:
            user_id: User ID
            
        Returns:
            dict: User data from website or None if not found
        """
        try:
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Get from website's users collection
            website_users_collection = self.db['website_users']
            user = await website_users_collection.find_one({"user_id": user_id})
            
            return user
            
        except Exception as e:
            logger.error(f"❌ Error getting website user data for {user_id}: {e}")
            return None

    async def update_website_user_balance(self, user_id: int, new_balance: float) -> bool:
        """
        Update user balance in website database
        
        Args:
            user_id: User ID
            new_balance: New balance amount
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Update in website's users collection
            website_users_collection = self.db['website_users']
            
            result = await website_users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "balance": new_balance,
                        "updated_at": datetime.utcnow(),
                        "last_sync": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Updated balance for user {user_id} in website database: {new_balance}")
                return True
            else:
                logger.warning(f"⚠️ No user found to update balance for user {user_id} in website database")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating website user balance for {user_id}: {e}")
            return False
