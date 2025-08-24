import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BotConfig:
    
    def __init__(self):
        self.BOT_TOKEN = self._get_required_env_var("BOT_TOKEN")
        self.MONGODB_URI = self._get_env_var("MONGODB_URI", "mongodb://localhost:27017/otp_bot")
        self.MONGODB_DATABASE = self._get_env_var("MONGODB_DATABASE", "otp_bot")
        self.MONGODB_COLLECTION = self._get_env_var("MONGODB_COLLECTION", "users")
        self.SUPPORT_USERNAME = self._get_env_var("SUPPORT_USERNAME", "@support")
        self.ADMIN_USER_ID = self._get_env_var("ADMIN_USER_ID")
        self.BACKEND_URL = self._get_env_var("BACKEND_URL", "http://localhost:3000")
        
        self.DB_MAX_POOL_SIZE = int(self._get_env_var("DB_MAX_POOL_SIZE", "10"))
        self.DB_MIN_POOL_SIZE = int(self._get_env_var("DB_MIN_POOL_SIZE", "1"))
        self.DB_MAX_IDLE_TIME_MS = int(self._get_env_var("DB_MAX_IDLE_TIME_MS", "30000"))
        self.DB_CONNECT_TIMEOUT_MS = int(self._get_env_var("DB_CONNECT_TIMEOUT_MS", "10000"))
        self.DB_SOCKET_TIMEOUT_MS = int(self._get_env_var("DB_SOCKET_TIMEOUT_MS", "10000"))
        
        self.MAX_REQUESTS_PER_MINUTE = int(self._get_env_var("MAX_REQUESTS_PER_MINUTE", "60"))
        self.RATE_LIMIT_WINDOW = int(self._get_env_var("RATE_LIMIT_WINDOW", "60"))
        
        self.LOG_LEVEL = self._get_env_var("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = self._get_env_var("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        if not self.MONGODB_URI.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError("Invalid MONGODB_URI format")
    
    def _get_required_env_var(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"{key} environment variable is required")
        return value
    
    def _get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        value = os.getenv(key, default)
        if value is None:
            logger.warning(f"Warning: {key} environment variable not set, using default: {default}")
        return value
    
    @property
    def is_production(self) -> bool:
        return os.getenv("NODE_ENV", "development") == "production"
    
    @property
    def debug_mode(self) -> bool:
        return os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def database_config(self) -> dict:
        return {
            "uri": self.MONGODB_URI,
            "database": self.MONGODB_DATABASE,
            "collection": self.MONGODB_COLLECTION,
            "max_pool_size": self.DB_MAX_POOL_SIZE,
            "min_pool_size": self.DB_MIN_POOL_SIZE,
            "max_idle_time_ms": self.DB_MAX_IDLE_TIME_MS,
            "connect_timeout_ms": self.DB_CONNECT_TIMEOUT_MS,
            "socket_timeout_ms": self.DB_SOCKET_TIMEOUT_MS
        }
    
    def validate_config(self) -> bool:
        try:
            if not self.BOT_TOKEN or ':' not in self.BOT_TOKEN:
                logger.error("Invalid BOT_TOKEN format")
                return False
            
            if self.ADMIN_USER_ID and not self.ADMIN_USER_ID.isdigit():
                logger.error("ADMIN_USER_ID must be a numeric value")
                return False
            
            if self.DB_MAX_POOL_SIZE < 1 or self.DB_MIN_POOL_SIZE < 1:
                logger.error("Database pool sizes must be positive integers")
                return False
            
            if self.DB_MIN_POOL_SIZE > self.DB_MAX_POOL_SIZE:
                logger.error("DB_MIN_POOL_SIZE cannot be greater than DB_MAX_POOL_SIZE")
                return False
            
            logger.info("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
