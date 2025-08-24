#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_environment():
    required_vars = [
        'BOT_TOKEN',
        'MONGODB_URI',
        'MONGODB_DATABASE'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        return False
    
    bot_token = os.getenv('BOT_TOKEN')
    if ':' not in bot_token:
        logger.error("❌ Invalid BOT_TOKEN format. Should be in format: <bot_id>:<bot_token>")
        return False
    
    mongo_uri = os.getenv('MONGODB_URI')
    if not mongo_uri.startswith(('mongodb://', 'mongodb+srv://')):
        logger.error("❌ Invalid MONGODB_URI format. Should start with mongodb:// or mongodb+srv://")
        return False
    
    logger.info("✅ Environment validation passed")
    return True

def check_dependencies():
    required_packages = [
        'telegram',
        'motor',
        'pymongo',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install them using: pip install -r requirements.txt")
        return False
    
    logger.info("✅ Dependencies check passed")
    return True

async def test_database_connection():
    try:
        from src.config.bot_config import BotConfig
        from src.database.user_db import UserDatabase
        
        config = BotConfig()
        user_db = UserDatabase()
        
        await user_db.initialize()
        logger.info("✅ Database connection test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

async def test_bot_token():
    try:
        from src.config.bot_config import BotConfig
        from telegram.ext import Application
        
        config = BotConfig()
        app = Application.builder().token(config.BOT_TOKEN).build()
        
        bot_info = await app.bot.get_me()
        logger.info(f"✅ Bot token test passed - Bot: @{bot_info.username}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Bot token test failed: {e}")
        return False

async def main():
    logger.info("🚀 Starting OTP Bot...")
    
    logger.info("📋 Step 1: Validating environment...")
    if not validate_environment():
        sys.exit(1)
    
    logger.info("📦 Step 2: Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    logger.info("🗄️ Step 3: Testing database connection...")
    if not await test_database_connection():
        logger.warning("⚠️ Database connection failed, but continuing...")
    
    logger.info("🤖 Step 4: Testing bot token...")
    if not await test_bot_token():
        sys.exit(1)
    
    logger.info("🎯 Step 5: Starting bot...")
    try:
        from main import OTPBot
        
        bot = OTPBot()
        await bot.initialize()
        
        logger.info("Bot is running... Send /start to test!")
        
        # Start polling in the background
        await bot.start_polling()
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot startup failed: {e}")
        sys.exit(1)
    finally:
        if 'bot' in locals():
            await bot.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Startup interrupted by user")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)
