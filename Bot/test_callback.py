#!/usr/bin/env python3
"""
Test script to verify callback handling
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_callback_data():
    """Test callback data generation"""
    try:
        # Connect to MongoDB
        mongodb_uri = "mongodb+srv://vishalgiri0044:kR9oUspxQUtYdund@cluster0.zdudgbg.mongodb.net/otp_bot?retryWrites=true&w=majority&appName=Cluster0"
        client = AsyncIOMotorClient(mongodb_uri)
        db = client['otp_bot']
        services_collection = db['services']
        
        # Get all services
        cursor = services_collection.find({})
        services = await cursor.to_list(length=None)
        logger.info(f"✅ Found {len(services)} services in database")
        
        # Test callback data generation
        logger.info("\n🔧 Testing callback data generation:")
        for i, service in enumerate(services[:3], 1):  # Test first 3 services
            service_id = str(service.get('_id', 'NO_ID'))
            service_name = service.get('name', 'Unknown')
            server_name = service.get('server_name', 'Unknown Server')
            
            # Generate callback data like the bot does
            callback_data = f"service_{service_id}"
            
            logger.info(f"  {i}. Service: {service_name}")
            logger.info(f"     Server: {server_name}")
            logger.info(f"     Service ID: {service_id}")
            logger.info(f"     Callback Data: {callback_data}")
            logger.info(f"     Callback Length: {len(callback_data)} characters")
            logger.info("")
        
        # Test callback data parsing
        logger.info("🔍 Testing callback data parsing:")
        for i, service in enumerate(services[:3], 1):
            service_id = str(service.get('_id', 'NO_ID'))
            callback_data = f"service_{service_id}"
            
            # Parse like the bot does
            if callback_data.startswith("service_"):
                extracted_id = callback_data.replace("service_", "")
                logger.info(f"  {i}. Original: {callback_data}")
                logger.info(f"     Extracted ID: {extracted_id}")
                logger.info(f"     Match: {extracted_id == service_id}")
            logger.info("")
        
        client.close()
        logger.info("✅ Callback test completed!")
        
    except Exception as e:
        logger.error(f"❌ Error in callback test: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_callback_data())
