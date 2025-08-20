"""
Bot Configuration Module
"""

import os
from typing import Optional

class BotConfig:
    """Configuration class for the OTP Bot"""
    
    def __init__(self):
        self.BOT_TOKEN = self._get_env_var("BOT_TOKEN")
        self.MONGODB_URI = self._get_env_var("MONGODB_URI", "mongodb://localhost:27017/otp_bot")
        self.MONGODB_DATABASE = self._get_env_var("MONGODB_DATABASE", "otp_bot")
        self.SUPPORT_USERNAME = self._get_env_var("SUPPORT_USERNAME", "@support")
        self.ADMIN_USER_ID = self._get_env_var("ADMIN_USER_ID")
        
        # Validate required environment variables
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
    
    def _get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable with optional default value"""
        value = os.getenv(key, default)
        if value is None:
            print(f"Warning: {key} environment variable not set")
        return value
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("NODE_ENV", "development") == "production"
    
    @property
    def debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return os.getenv("DEBUG", "false").lower() == "true"
