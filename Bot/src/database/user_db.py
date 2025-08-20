"""
User Database Module
"""

import asyncio
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserDatabase:
    """Database handler for user operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.users_collection = None
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            from src.config.bot_config import BotConfig
            config = BotConfig()
            
            logger.info(f"🔗 Connecting to MongoDB...")
            logger.info(f"📊 Database: {config.MONGODB_DATABASE}")
            logger.info(f"📋 Collection: {config.MONGODB_COLLECTION}")
            
            self.client = AsyncIOMotorClient(config.MONGODB_URI)
            self.db = self.client[config.MONGODB_DATABASE]
            self.users_collection = self.db[config.MONGODB_COLLECTION]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB connected successfully!")
            logger.info(f"📊 Connected to database: {config.MONGODB_DATABASE}")
            logger.info(f"📋 Using collection: {config.MONGODB_COLLECTION}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None) -> Dict[str, Any]:
        """Get user from database or create if not exists"""
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            
            if not user:
                # Create new user
                user_data = {
                    "user_id": user_id,
                    "username": username,
                    "first_name": first_name,
                    "balance": 0.0,
                    "total_purchased": 0,
                    "total_used": 0,
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
                "total_used": 0
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
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
