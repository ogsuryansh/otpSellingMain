#!/usr/bin/env python3
"""
Test script to verify the bot workflow
"""

import asyncio
import logging
from src.database.user_db import UserDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_workflow():
    """Test the bot workflow"""
    try:
        # Initialize database
        user_db = UserDatabase()
        await user_db.initialize()
        
        # Get all services
        services = await user_db.get_services()
        logger.info(f"✅ Found {len(services)} services")
        
        # Display services (this is what users see in the bot)
        logger.info("\n📦 Available Services:")
        for i, service in enumerate(services, 1):
            name = service.get('name', 'Unknown')
            desc = service.get('description', 'No description')
            server = service.get('server', 'Unknown Server')
            price = service.get('price', '₹0')
            service_id = service.get('id', 'NO_ID')
            
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
                server_name = variant.get('server', 'Unknown Server')
                price = variant.get('price', '₹0')
                variant_id = variant.get('id', 'NO_ID')
                
                logger.info(f"   [{server_name} - {price} 💎] (ID: {variant_id})")
        
        logger.info("\n✅ Workflow test completed!")
        
    except Exception as e:
        logger.error(f"❌ Error in workflow test: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
