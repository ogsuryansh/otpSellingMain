"""
Cache Manager for performance optimization
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable
import logging
from functools import wraps
import json

logger = logging.getLogger(__name__)

class CacheManager:
    """Simple in-memory cache with TTL and automatic cleanup"""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000, cleanup_interval: int = 60):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.last_cleanup = time.time()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the cache manager with periodic cleanup"""
        if self._initialized:
            return
        
        try:
            loop = asyncio.get_running_loop()
            self._cleanup_task = loop.create_task(self._periodic_cleanup())
            self._initialized = True
            logger.debug("Cache manager initialized with periodic cleanup")
        except RuntimeError:
            # No event loop, cleanup will be done on-demand
            logger.debug("Cache manager initialized without periodic cleanup (no event loop)")
            self._initialized = True
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired entries"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired()
                logger.debug(f"Cache cleanup completed. Active entries: {len(self.cache)}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time > entry['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
    
    def _make_key(self, *args, **kwargs) -> str:
        """Create a cache key from function arguments"""
        # Convert args and kwargs to a string representation
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return "|".join(key_parts)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Periodic cleanup check
            current_time = time.time()
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_expired()
                self.last_cleanup = current_time
            
            if key in self.cache:
                entry = self.cache[key]
                if current_time <= entry['expires_at']:
                    entry['hits'] += 1
                    return entry['value']
                else:
                    # Remove expired entry
                    del self.cache[key]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            # Check cache size limit
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl
            
            self.cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time(),
                'hits': 0
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def _evict_oldest(self):
        """Evict the oldest cache entry"""
        if not self.cache:
            return
        
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['created_at'])
        del self.cache[oldest_key]
    
    def delete(self, key: str) -> bool:
        """Delete a cache entry"""
        try:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.cache.clear()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            self._cleanup_expired()
            
            total_entries = len(self.cache)
            total_hits = sum(entry['hits'] for entry in self.cache.values())
            avg_hits = total_hits / total_entries if total_entries > 0 else 0
            
            return {
                'total_entries': total_entries,
                'total_hits': total_hits,
                'average_hits': round(avg_hits, 2),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
                'memory_usage_mb': self._estimate_memory_usage()
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        try:
            # Rough estimation
            total_size = 0
            for key, entry in self.cache.items():
                # Key size + entry overhead + value size estimation
                total_size += len(key) + 64 + len(str(entry['value']))
            
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0
    
    async def shutdown(self):
        """Shutdown the cache manager"""
        try:
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            self.cache.clear()
            logger.info("Cache manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during cache shutdown: {e}")

# Global cache instance
cache_manager = CacheManager()

def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{cache_manager._make_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, cached result")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{cache_manager._make_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, cached result")
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Utility functions
def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return cache_manager.get_stats()

def clear_cache() -> bool:
    """Clear all cache entries"""
    return cache_manager.clear()

def delete_cache_key(key: str) -> bool:
    """Delete a specific cache key"""
    return cache_manager.delete(key)

async def initialize_cache():
    """Initialize the cache manager"""
    await cache_manager.initialize()

async def shutdown_cache():
    """Shutdown the cache manager"""
    await cache_manager.shutdown()
