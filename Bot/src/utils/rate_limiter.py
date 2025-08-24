"""
Rate Limiter Utility with improved memory management
"""

import time
import asyncio
from typing import Dict, Tuple, Optional
import logging
from collections import defaultdict
import weakref

logger = logging.getLogger(__name__)

class RateLimiter:
    """Improved in-memory rate limiter with automatic cleanup"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60, cleanup_interval: int = 300):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.cleanup_interval = cleanup_interval
        self.requests: Dict[int, list] = defaultdict(list)
        self.last_cleanup = time.time()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the rate limiter with periodic cleanup"""
        if self._initialized:
            return
        
        try:
            loop = asyncio.get_running_loop()
            self._cleanup_task = loop.create_task(self._periodic_cleanup())
            self._initialized = True
            logger.debug("Rate limiter initialized with periodic cleanup")
        except RuntimeError:
            # No event loop, cleanup will be done on-demand
            logger.debug("Rate limiter initialized without periodic cleanup (no event loop)")
            self._initialized = True
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of old entries"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_all_old_requests()
                logger.debug(f"Rate limiter cleanup completed. Active users: {len(self.requests)}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
    
    def _cleanup_old_requests(self, user_id: int):
        """Remove old requests outside the time window for a specific user"""
        current_time = time.time()
        if user_id in self.requests:
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if current_time - req_time < self.window_seconds
            ]
            
            # Remove user if no requests remain
            if not self.requests[user_id]:
                del self.requests[user_id]
    
    def _cleanup_all_old_requests(self):
        """Cleanup old requests for all users"""
        current_time = time.time()
        users_to_remove = []
        
        for user_id, requests in self.requests.items():
            # Filter out old requests
            self.requests[user_id] = [
                req_time for req_time in requests
                if current_time - req_time < self.window_seconds
            ]
            
            # Mark for removal if no requests remain
            if not self.requests[user_id]:
                users_to_remove.append(user_id)
        
        # Remove users with no requests
        for user_id in users_to_remove:
            del self.requests[user_id]
    
    def is_allowed(self, user_id: int) -> Tuple[bool, int]:
        """
        Check if user is allowed to make a request
        Returns: (allowed, remaining_requests)
        """
        try:
            # Periodic cleanup check
            current_time = time.time()
            if current_time - self.last_cleanup > self.cleanup_interval:
                self._cleanup_all_old_requests()
                self.last_cleanup = current_time
            
            # Cleanup old requests for this user
            self._cleanup_old_requests(user_id)
            
            # Check if user has exceeded the limit
            if len(self.requests[user_id]) >= self.max_requests:
                return False, 0
            
            # Add current request
            self.requests[user_id].append(current_time)
            
            remaining = self.max_requests - len(self.requests[user_id])
            return True, remaining
            
        except Exception as e:
            logger.error(f"Error in rate limiter: {e}")
            # Allow request if rate limiter fails
            return True, 1
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get rate limiting stats for a user"""
        try:
            self._cleanup_old_requests(user_id)
            
            if user_id not in self.requests:
                return {
                    'requests_made': 0,
                    'requests_remaining': self.max_requests,
                    'window_seconds': self.window_seconds,
                    'reset_time': time.time() + self.window_seconds
                }
            
            requests_made = len(self.requests[user_id])
            return {
                'requests_made': requests_made,
                'requests_remaining': max(0, self.max_requests - requests_made),
                'window_seconds': self.window_seconds,
                'reset_time': time.time() + self.window_seconds
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                'requests_made': 0,
                'requests_remaining': self.max_requests,
                'window_seconds': self.window_seconds,
                'reset_time': time.time() + self.window_seconds
            }
    
    def reset_user(self, user_id: int) -> bool:
        """Reset rate limit for a specific user"""
        try:
            if user_id in self.requests:
                del self.requests[user_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Error resetting user rate limit: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get overall rate limiter statistics"""
        try:
            self._cleanup_all_old_requests()
            
            total_users = len(self.requests)
            total_requests = sum(len(requests) for requests in self.requests.values())
            
            return {
                'total_users': total_users,
                'total_requests': total_requests,
                'max_requests_per_user': self.max_requests,
                'window_seconds': self.window_seconds,
                'memory_usage_mb': self._estimate_memory_usage()
            }
        except Exception as e:
            logger.error(f"Error getting rate limiter stats: {e}")
            return {}
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        try:
            # Rough estimation: each user_id (int) + list of timestamps
            total_size = 0
            for user_id, requests in self.requests.items():
                # user_id (int) + list overhead + timestamps
                total_size += 8 + 64 + (len(requests) * 8)  # 8 bytes per timestamp
            
            return round(total_size / (1024 * 1024), 2)  # Convert to MB
        except:
            return 0.0
    
    async def shutdown(self):
        """Shutdown the rate limiter"""
        try:
            if self._cleanup_task and not self._cleanup_task.done():
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Clear all data
            self.requests.clear()
            logger.info("Rate limiter shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during rate limiter shutdown: {e}")

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_rate_limit(user_id: int) -> Tuple[bool, int]:
    """Check if user is within rate limits"""
    return rate_limiter.is_allowed(user_id)

def get_rate_limit_stats(user_id: int) -> Dict:
    """Get rate limiting statistics for a user"""
    return rate_limiter.get_user_stats(user_id)

def reset_user_rate_limit(user_id: int) -> bool:
    """Reset rate limit for a specific user"""
    return rate_limiter.reset_user(user_id)

def get_rate_limiter_stats() -> Dict:
    """Get overall rate limiter statistics"""
    return rate_limiter.get_stats()

async def initialize_rate_limiter():
    """Initialize the rate limiter"""
    await rate_limiter.initialize()

async def shutdown_rate_limiter():
    """Shutdown the rate limiter"""
    await rate_limiter.shutdown()
