#!/usr/bin/env python3
"""
Simple test to verify the workflow without bot configuration
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_workflow():
    """Test the bot workflow"""
    try:
        # Connect directly to MongoDB
        mongodb_uri = "mongodb+srv://vishalgiri0044:kR9oUspxQUtYdund@cluster0.zdudgbg.mongodb.net/otp_bot?retryWrites=true&w=majority&appName=Cluster0"
        client = AsyncIOMotorClient(mongodb_uri)
        db = client['otp_bot']
        services_collection = db['services']
        
        # Get all services
        cursor = services_collection.find({})
        services = await cursor.to_list(length=None)
        logger.info(f"✅ Found {len(services)} services in database")
        
        # Display services (this is what users see in the bot)
        logger.info("\n📦 Available Services:")
        for i, service in enumerate(services, 1):
            name = service.get('name', 'Unknown')
            desc = service.get('description', 'No description')
            server = service.get('server_name', 'Unknown Server')
            price = service.get('price', '₹0')
            service_id = str(service.get('_id', 'NO_ID'))
            
            logger.info(f"{i}. {name} (ID: {service_id})")
            logger.info(f"   Description: {desc}")
            logger.info(f"   Server: {server}")
            logger.info(f"   Price: {price}")
            logger.info("")
        
        # Test service selection workflow
        logger.info("\n🔄 Testing Service Selection Workflow:")
        
        # Group services by name
        service_groups = {}
        for service in services:
            name = service.get('name', 'Unknown')
            if name not in service_groups:
                service_groups[name] = []
            service_groups[name].append(service)
        
        # Show what happens when user selects a service
        for service_name, variants in service_groups.items():
            logger.info(f"\n➤ Selected Service: {service_name}")
            logger.info("↓ Available Servers:")
            
            for variant in variants:
                server_name = variant.get('server_name', 'Unknown Server')
                price = variant.get('price', '₹0')
                variant_id = str(variant.get('_id', 'NO_ID'))
                
                logger.info(f"   [{server_name} - {price} 💎] (ID: {variant_id})")
        
        logger.info("\n✅ Workflow test completed!")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"❌ Error in workflow test: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
