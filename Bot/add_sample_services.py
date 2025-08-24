#!/usr/bin/env python3
"""
Script to add sample services with multiple server variants
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_sample_services():
    """Add sample services with multiple server variants"""
    try:
        # Connect to MongoDB
        mongodb_uri = "mongodb+srv://vishalgiri0044:kR9oUspxQUtYdund@cluster0.zdudgbg.mongodb.net/otp_bot?retryWrites=true&w=majority&appName=Cluster0"
        client = AsyncIOMotorClient(mongodb_uri)
        db = client['otp_bot']
        services_collection = db['services']
        
        # Clear existing services
        await services_collection.delete_many({})
        logger.info("🗑️ Cleared existing services")
        
        # Sample services with multiple server variants
        sample_services = [
            # WhatsApp with multiple servers
            {
                "name": "WhatsApp",
                "description": "Get OTP for WhatsApp verification. Fast and reliable service.",
                "price": "₹5.00",
                "server_name": "Server 1",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "WhatsApp",
                "description": "Get OTP for WhatsApp verification. Premium service with high success rate.",
                "price": "₹7.00",
                "server_name": "Server 2",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "WhatsApp",
                "description": "Get OTP for WhatsApp verification. Express delivery service.",
                "price": "₹9.00",
                "server_name": "Server 3",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            
            # Telegram with multiple servers
            {
                "name": "Telegram",
                "description": "Get OTP for Telegram verification. Instant delivery.",
                "price": "₹3.00",
                "server_name": "Server 1",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Telegram",
                "description": "Get OTP for Telegram verification. Express service.",
                "price": "₹4.50",
                "server_name": "Server 2",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            
            # Instagram with multiple servers
            {
                "name": "Instagram",
                "description": "Get OTP for Instagram verification. High success rate.",
                "price": "₹4.00",
                "server_name": "Server 1",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            {
                "name": "Instagram",
                "description": "Get OTP for Instagram verification. Premium quality.",
                "price": "₹6.00",
                "server_name": "Server 2",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            
            # Facebook with single server
            {
                "name": "Facebook",
                "description": "Get OTP for Facebook verification. Secure and reliable.",
                "price": "₹2.00",
                "server_name": "Server 1",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            },
            
            # Gmail with single server
            {
                "name": "Gmail",
                "description": "Get OTP for Gmail verification. Premium service.",
                "price": "₹4.50",
                "server_name": "Server 1",
                "is_active": True,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
        ]
        
        # Insert services
        result = await services_collection.insert_many(sample_services)
        logger.info(f"✅ Added {len(result.inserted_ids)} sample services")
        
        # Verify the services
        cursor = services_collection.find({})
        services = await cursor.to_list(length=None)
        logger.info(f"✅ Total services in database: {len(services)}")
        
        # Group by service name to show variants
        service_groups = {}
        for service in services:
            name = service.get('name', 'Unknown')
            if name not in service_groups:
                service_groups[name] = []
            service_groups[name].append(service)
        
        logger.info("\n📊 Service Variants Summary:")
        for service_name, variants in service_groups.items():
            logger.info(f"  {service_name}: {len(variants)} server variant(s)")
            for variant in variants:
                server = variant.get('server_name', 'Unknown')
                price = variant.get('price', '₹0')
                logger.info(f"    - {server}: {price}")
        
        # Close connection
        client.close()
        logger.info("✅ Sample services added successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error adding sample services: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(add_sample_services())
