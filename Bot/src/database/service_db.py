"""
Service and Server Database Module
"""

import asyncio
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging
import aiohttp
import json

logger = logging.getLogger(__name__)

class ServiceDatabase:
    """Database handler for service and server operations"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceDatabase, cls).__new__(cls)
            cls._instance.client: Optional[AsyncIOMotorClient] = None
            cls._instance.db = None
            cls._instance.services_collection = None
            cls._instance.servers_collection = None
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
            
            logger.info(f"🔗 Connecting to MongoDB for services...")
            
            self.client = AsyncIOMotorClient(config.MONGODB_URI)
            self.db = self.client[config.MONGODB_DATABASE]
            self.services_collection = self.db['services']
            self.servers_collection = self.db['servers']
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB connected successfully for services!")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB for services: {e}")
            raise
    
    async def get_service_by_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service by name"""
        try:
            if not self._initialized:
                await self.initialize()
            
            service = await self.services_collection.find_one({"name": service_name.upper()})
            return service
        except Exception as e:
            logger.error(f"Error getting service {service_name}: {e}")
            return None
    
    async def get_servers_for_service(self, service_id: str) -> List[Dict[str, Any]]:
        """Get all servers that have the specified service enabled"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Find servers where enabled_services includes the service_id
            cursor = self.servers_collection.find({
                "enabled_services": service_id
            })
            
            servers = await cursor.to_list(length=None)
            return servers
        except Exception as e:
            logger.error(f"Error getting servers for service {service_id}: {e}")
            return []
    
    async def get_server_by_id(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get server by ID"""
        try:
            if not self._initialized:
                await self.initialize()
            
            from bson import ObjectId
            server = await self.servers_collection.find_one({"_id": ObjectId(server_id)})
            return server
        except Exception as e:
            logger.error(f"Error getting server {server_id}: {e}")
            return None
    
    async def get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get service by ID"""
        try:
            if not self._initialized:
                await self.initialize()
            
            from bson import ObjectId
            service = await self.services_collection.find_one({"_id": ObjectId(service_id)})
            return service
        except Exception as e:
            logger.error(f"Error getting service {service_id}: {e}")
            return None
    
    async def call_server_api(self, server: Dict[str, Any], service_name: str) -> Dict[str, Any]:
        """Call server API to fetch a number"""
        try:
            api_config = server.get('api', {})
            
            if not api_config:
                return {"success": False, "error": "No API configuration found"}
            
            # Extract API configuration
            api_base_url = api_config.get('api_base_url')
            api_key = api_config.get('api_key')
            endpoints = api_config.get('endpoints', {})
            fetch_number_endpoint = endpoints.get('fetch_number')
            http_method = api_config.get('http_method', 'GET').upper()
            default_params = api_config.get('default_params', {})
            headers = api_config.get('headers', {})
            timeout_ms = api_config.get('timeout_ms', 30000)
            
            if not api_base_url or not fetch_number_endpoint:
                return {"success": False, "error": "Missing API configuration"}
            
            # Prepare request
            url = f"{api_base_url.rstrip('/')}/{fetch_number_endpoint.lstrip('/')}"
            
            # Prepare headers
            request_headers = {
                'Content-Type': 'application/json',
                **headers
            }
            
            if api_key:
                request_headers['Authorization'] = f'Bearer {api_key}'
            
            # Prepare parameters
            params = {
                **default_params,
                'service': service_name.upper()
            }
            
            logger.info(f"🌐 Calling server API: {url}")
            logger.info(f"📋 Method: {http_method}")
            logger.info(f"📋 Params: {params}")
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                if http_method == 'GET':
                    async with session.get(url, params=params, headers=request_headers, timeout=timeout_ms/1000) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ Server API response: {data}")
                            return {"success": True, "data": data}
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ Server API error: {response.status} - {error_text}")
                            return {"success": False, "error": f"API returned {response.status}"}
                
                elif http_method == 'POST':
                    async with session.post(url, json=params, headers=request_headers, timeout=timeout_ms/1000) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"✅ Server API response: {data}")
                            return {"success": True, "data": data}
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ Server API error: {response.status} - {error_text}")
                            return {"success": False, "error": f"API returned {response.status}"}
                
                else:
                    return {"success": False, "error": f"Unsupported HTTP method: {http_method}"}
                    
        except asyncio.TimeoutError:
            logger.error(f"❌ Server API timeout: {server.get('name', 'Unknown')}")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ Server API error: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Service database connection closed")
