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
            
            logger.info(f"🔍 DEBUG: Looking for servers with service_id: {service_id}")
            logger.info(f"🔍 DEBUG: Service ID type: {type(service_id)}")
            
            # First, let's check what's in the servers collection
            logger.info("🔍 DEBUG: Checking all servers in collection...")
            all_servers_cursor = self.servers_collection.find({})
            all_servers = await all_servers_cursor.to_list(length=None)
            logger.info(f"🔍 DEBUG: Total servers in collection: {len(all_servers)}")
            
            for i, server in enumerate(all_servers):
                logger.info(f"🔍 DEBUG: Server {i+1}:")
                logger.info(f"  - ID: {server.get('_id')}")
                logger.info(f"  - Name: {server.get('name')}")
                logger.info(f"  - Enabled services: {server.get('enabled_services')}")
                logger.info(f"  - Enabled services type: {type(server.get('enabled_services'))}")
                if server.get('enabled_services'):
                    for j, enabled_service in enumerate(server.get('enabled_services')):
                        logger.info(f"    - Service {j+1}: {enabled_service} (type: {type(enabled_service)})")
            
            # Now let's check what's in the services collection
            logger.info("🔍 DEBUG: Checking all services in collection...")
            all_services_cursor = self.services_collection.find({})
            all_services = await all_services_cursor.to_list(length=None)
            logger.info(f"🔍 DEBUG: Total services in collection: {len(all_services)}")
            
            for i, service in enumerate(all_services):
                logger.info(f"🔍 DEBUG: Service {i+1}:")
                logger.info(f"  - ID: {service.get('_id')}")
                logger.info(f"  - Name: {service.get('name')}")
                logger.info(f"  - ID type: {type(service.get('_id'))}")
                logger.info(f"  - ID string: {str(service.get('_id'))}")
            
            # Find servers where enabled_services includes the service_id
            logger.info(f"🔍 DEBUG: Searching for servers with enabled_services containing: {service_id}")
            
            # Try different search approaches
            search_query = {"enabled_services": service_id}
            logger.info(f"🔍 DEBUG: Search query: {search_query}")
            
            cursor = self.servers_collection.find(search_query)
            servers = await cursor.to_list(length=None)
            logger.info(f"🔍 DEBUG: Found {len(servers)} servers for service {service_id}")
            
            # Debug: Print each server
            for i, server in enumerate(servers):
                logger.info(f"🔍 DEBUG: Server {i+1} data: {server}")
            
            # If no servers found, try alternative search
            if not servers:
                logger.info("🔍 DEBUG: No servers found with exact match, trying alternative searches...")
                
                # Try searching with ObjectId
                try:
                    from bson import ObjectId
                    object_id = ObjectId(service_id)
                    logger.info(f"🔍 DEBUG: Trying search with ObjectId: {object_id}")
                    cursor2 = self.servers_collection.find({"enabled_services": object_id})
                    servers2 = await cursor2.to_list(length=None)
                    logger.info(f"🔍 DEBUG: Found {len(servers2)} servers with ObjectId search")
                    if servers2:
                        servers = servers2
                except Exception as e:
                    logger.info(f"🔍 DEBUG: ObjectId search failed: {e}")
                
                # Try searching with string conversion
                if not servers:
                    logger.info("🔍 DEBUG: Trying search with string conversion...")
                    cursor3 = self.servers_collection.find({"enabled_services": str(service_id)})
                    servers3 = await cursor3.to_list(length=None)
                    logger.info(f"🔍 DEBUG: Found {len(servers3)} servers with string search")
                    if servers3:
                        servers = servers3
            
            logger.info(f"🔍 DEBUG: Final result: {len(servers)} servers found")
            return servers
            
        except Exception as e:
            logger.error(f"Error getting servers for service {service_id}: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
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
            
            logger.info(f"🔍 DEBUG: Getting service by ID: {service_id}")
            logger.info(f"🔍 DEBUG: Service ID type: {type(service_id)}")
            
            from bson import ObjectId
            service = await self.services_collection.find_one({"_id": ObjectId(service_id)})
            
            if service:
                logger.info(f"🔍 DEBUG: Found service: {service}")
            else:
                logger.info(f"🔍 DEBUG: Service not found with ID: {service_id}")
            
            return service
        except Exception as e:
            logger.error(f"Error getting service {service_id}: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
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
    
    async def debug_servers_collection(self):
        """Debug method to check servers collection"""
        try:
            if not self._initialized:
                await self.initialize()
            
            logger.info("🔍 DEBUG: Checking servers collection...")
            
            # Get all servers
            cursor = self.servers_collection.find({})
            all_servers = await cursor.to_list(length=None)
            
            logger.info(f"🔍 DEBUG: Total servers in collection: {len(all_servers)}")
            
            for i, server in enumerate(all_servers):
                logger.info(f"🔍 DEBUG: Server {i+1}:")
                logger.info(f"  - _id: {server.get('_id')}")
                logger.info(f"  - name: {server.get('name')}")
                logger.info(f"  - enabled_services: {server.get('enabled_services')}")
                logger.info(f"  - country_code: {server.get('country_code')}")
                logger.info(f"  - rating: {server.get('rating')}")
            
        except Exception as e:
            logger.error(f"❌ Error debugging servers collection: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Service database connection closed")

    async def sync_services_with_website(self) -> Dict[str, Any]:
        """
        Sync services data with website database
        
        Returns:
            dict: Sync results with counts
        """
        try:
            logger.info("🔄 Starting services sync with website...")
            
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Get all services from bot database
            cursor = self.services_collection.find({})
            all_services = await cursor.to_list(length=None)
            
            if not all_services:
                logger.info("ℹ️ No services found in bot database")
                return {"success": True, "total_services": 0, "synced_services": 0, "failed_services": 0}
            
            # Sync with website's services collection
            website_services_collection = self.db['services']
            
            synced_count = 0
            failed_count = 0
            
            for service in all_services:
                try:
                    # Prepare service data for website
                    website_service_data = {
                        "name": service.get("name"),
                        "description": service.get("description", ""),
                        "price": service.get("price", "₹0"),
                        "server_name": service.get("server_name", "Unknown Server"),
                        "code": service.get("code", ""),
                        "cancel_disable": service.get("cancel_disable", "5"),
                        "is_active": service.get("is_active", True),
                        "users": service.get("users", 0),
                        "created_at": service.get("created_at", datetime.utcnow()),
                        "updated_at": datetime.utcnow(),
                        "last_sync": datetime.utcnow()
                    }
                    
                    # Upsert service data
                    result = await website_services_collection.update_one(
                        {"name": service.get("name")},
                        {"$set": website_service_data},
                        upsert=True
                    )
                    
                    if result.modified_count > 0 or result.upserted_id:
                        synced_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error syncing service {service.get('name')}: {e}")
                    failed_count += 1
            
            logger.info(f"✅ Services sync completed: {synced_count} synced, {failed_count} failed out of {len(all_services)} total")
            
            return {
                "success": True,
                "total_services": len(all_services),
                "synced_services": synced_count,
                "failed_services": failed_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error during services sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_services": 0,
                "synced_services": 0,
                "failed_services": 0
            }

    async def sync_servers_with_website(self) -> Dict[str, Any]:
        """
        Sync servers data with website database
        
        Returns:
            dict: Sync results with counts
        """
        try:
            logger.info("🔄 Starting servers sync with website...")
            
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Get all servers from bot database
            cursor = self.servers_collection.find({})
            all_servers = await cursor.to_list(length=None)
            
            if not all_servers:
                logger.info("ℹ️ No servers found in bot database")
                return {"success": True, "total_servers": 0, "synced_servers": 0, "failed_servers": 0}
            
            # Sync with website's servers collection
            website_servers_collection = self.db['servers']
            
            synced_count = 0
            failed_count = 0
            
            for server in all_servers:
                try:
                    # Prepare server data for website
                    website_server_data = {
                        "server_name": server.get("name"),
                        "country": server.get("country_code", "IN"),
                        "flag": server.get("flag", "🇮🇳"),
                        "status": server.get("status", "active"),
                        "description": server.get("description", ""),
                        "enabled_services": server.get("enabled_services", []),
                        "rating": server.get("rating", 0),
                        "api": server.get("api", {}),
                        "created_at": server.get("created_at", datetime.utcnow()),
                        "updated_at": datetime.utcnow(),
                        "last_sync": datetime.utcnow()
                    }
                    
                    # Upsert server data
                    result = await website_servers_collection.update_one(
                        {"server_name": server.get("name")},
                        {"$set": website_server_data},
                        upsert=True
                    )
                    
                    if result.modified_count > 0 or result.upserted_id:
                        synced_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error syncing server {server.get('name')}: {e}")
                    failed_count += 1
            
            logger.info(f"✅ Servers sync completed: {synced_count} synced, {failed_count} failed out of {len(all_servers)} total")
            
            return {
                "success": True,
                "total_servers": len(all_servers),
                "synced_servers": synced_count,
                "failed_servers": failed_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error during servers sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_servers": 0,
                "synced_servers": 0,
                "failed_servers": 0
            }

    async def sync_all_data_with_website(self) -> Dict[str, Any]:
        """
        Sync all data (users, services, servers) with website database
        
        Returns:
            dict: Complete sync results
        """
        try:
            logger.info("🔄 Starting complete data sync with website...")
            
            # Import UserDatabase for user sync
            from .user_db import UserDatabase
            user_db = UserDatabase()
            
            # Sync users
            user_sync_result = await user_db.sync_all_users_with_website()
            
            # Sync services
            service_sync_result = await self.sync_services_with_website()
            
            # Sync servers
            server_sync_result = await self.sync_servers_with_website()
            
            # Combine results
            total_synced = (
                user_sync_result.get("synced_users", 0) +
                service_sync_result.get("synced_services", 0) +
                server_sync_result.get("synced_servers", 0)
            )
            
            total_failed = (
                user_sync_result.get("failed_users", 0) +
                service_sync_result.get("failed_services", 0) +
                server_sync_result.get("failed_servers", 0)
            )
            
            logger.info(f"✅ Complete sync finished: {total_synced} total synced, {total_failed} total failed")
            
            return {
                "success": True,
                "users": user_sync_result,
                "services": service_sync_result,
                "servers": server_sync_result,
                "total_synced": total_synced,
                "total_failed": total_failed,
                "sync_timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"❌ Error during complete data sync: {e}")
            return {
                "success": False,
                "error": str(e),
                "sync_timestamp": datetime.utcnow()
            }

    async def get_website_services(self) -> List[Dict[str, Any]]:
        """
        Get services from website database
        
        Returns:
            list: Services from website database
        """
        try:
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Get from website's services collection
            website_services_collection = self.db['services']
            cursor = website_services_collection.find({})
            services = await cursor.to_list(length=None)
            
            return services
            
        except Exception as e:
            logger.error(f"❌ Error getting website services: {e}")
            return []

    async def get_website_servers(self) -> List[Dict[str, Any]]:
        """
        Get servers from website database
        
        Returns:
            list: Servers from website database
        """
        try:
            # Ensure database is initialized
            if not self._initialized:
                await self.initialize()
            
            # Get from website's servers collection
            website_servers_collection = self.db['servers']
            cursor = website_servers_collection.find({})
            servers = await cursor.to_list(length=None)
            
            return servers
            
        except Exception as e:
            logger.error(f"❌ Error getting website servers: {e}")
            return []
