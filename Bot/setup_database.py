#!/usr/bin/env python3

import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

load_dotenv()

async def setup_database():
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/otp_bot')
    database_name = os.getenv('MONGODB_DATABASE', 'otp_bot')
    
    print(f"🔗 Connecting to MongoDB: {mongodb_uri}")
    print(f"📊 Database: {database_name}")
    
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[database_name]
    
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return
    
    services_collection = db['services']
    servers_collection = db['servers']
    
    sample_services = [
        {
            "_id": ObjectId(),
            "name": "WHATSAPP",
            "description": "Get OTP for WhatsApp verification. Fast and reliable service.",
            "price": "₹5.00",
            "server_name": "SERVER 1",
            "code": "WA001",
            "cancel_disable": "5",
            "is_active": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "TELEGRAM",
            "description": "Get OTP for Telegram verification. Instant delivery.",
            "price": "₹3.00",
            "server_name": "SERVER 2",
            "code": "TG001",
            "cancel_disable": "5",
            "is_active": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "GMAIL",
            "description": "Get OTP for Gmail verification. High success rate.",
            "price": "₹4.00",
            "server_name": "SERVER 3",
            "code": "GM001",
            "cancel_disable": "5",
            "is_active": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "name": "FACEBOOK",
            "description": "Get OTP for Facebook verification. Secure and reliable.",
            "price": "₹2.00",
            "server_name": "SERVER 1",
            "code": "FB001",
            "cancel_disable": "5",
            "is_active": True,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    ]
    
    sample_servers = [
        {
            "_id": ObjectId(),
            "name": "SERVER 1",
            "country_code": "US",
            "rating": 4.5,
            "enabled_services": [str(service["_id"]) for service in sample_services],
            "api": {
                "api_base_url": "https://api.example1.com",
                "api_key": "your_api_key_here",
                "endpoints": {
                    "fetch_number": "/api/v1/get_number"
                },
                "http_method": "GET",
                "default_params": {
                    "format": "json"
                },
                "headers": {
                    "User-Agent": "OTP-Bot/1.0"
                },
                "timeout_ms": 30000
            }
        },
        {
            "_id": ObjectId(),
            "name": "SERVER 2",
            "country_code": "IN",
            "rating": 4.2,
            "enabled_services": [str(sample_services[0]["_id"]), str(sample_services[1]["_id"])],
            "api": {
                "api_base_url": "https://api.example2.com",
                "api_key": "your_api_key_here",
                "endpoints": {
                    "fetch_number": "/numbers/get"
                },
                "http_method": "POST",
                "default_params": {
                    "type": "virtual"
                },
                "headers": {
                    "Content-Type": "application/json"
                },
                "timeout_ms": 25000
            }
        },
        {
            "_id": ObjectId(),
            "name": "SERVER 3",
            "country_code": "GB",
            "rating": 4.8,
            "enabled_services": [str(sample_services[2]["_id"])],
            "api": {
                "api_base_url": "https://api.example3.com",
                "api_key": "your_api_key_here",
                "endpoints": {
                    "fetch_number": "/v2/phone"
                },
                "http_method": "GET",
                "default_params": {
                    "country": "GB"
                },
                "headers": {
                    "Accept": "application/json"
                },
                "timeout_ms": 20000
            }
        }
    ]
    
    try:
        print("🧹 Clearing existing data...")
        await services_collection.delete_many({})
        await servers_collection.delete_many({})
        
        print("📦 Inserting sample services...")
        await services_collection.insert_many(sample_services)
        print(f"✅ Inserted {len(sample_services)} services")
        
        print("🖥️ Inserting sample servers...")
        await servers_collection.insert_many(sample_servers)
        print(f"✅ Inserted {len(sample_servers)} servers")
        
        print("\n📊 Database Summary:")
        service_count = await services_collection.count_documents({})
        server_count = await servers_collection.count_documents({})
        
        print(f"   Services: {service_count}")
        print(f"   Servers: {server_count}")
        
        print("\n📋 Sample Services:")
        async for service in services_collection.find():
            print(f"   - {service['name']} (ID: {service['_id']})")
        
        print("\n📋 Sample Servers:")
        async for server in servers_collection.find():
            print(f"   - {server['name']} ({server['country_code']}) - Rating: {server['rating']}💎")
            print(f"     Enabled services: {len(server['enabled_services'])}")
        
        print("\n✅ Database setup completed successfully!")
        print("\n🎯 You can now test the bot with:")
        print("   /show_server WHATSAPP")
        print("   /show_server TELEGRAM")
        print("   /show_server GMAIL")
        print("   /show_server FACEBOOK")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
    
    finally:
        client.close()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    asyncio.run(setup_database())
