"""
Security Configuration Module
"""

import os
import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration for the OTP Bot"""
    
    def __init__(self):
        # Rate limiting settings
        self.MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))
        self.RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))  # seconds
        
        # Input validation settings
        self.MAX_USERNAME_LENGTH = int(os.getenv('MAX_USERNAME_LENGTH', '32'))
        self.MAX_FIRST_NAME_LENGTH = int(os.getenv('MAX_FIRST_NAME_LENGTH', '64'))
        self.MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '4096'))
        
        # Admin settings
        self.ADMIN_USER_IDS = self._parse_admin_ids()
        self.ALLOWED_COMMANDS = self._get_allowed_commands()
        
        # Security patterns
        self.DANGEROUS_PATTERNS = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'<form[^>]*>',
            r'<input[^>]*>',
            r'<textarea[^>]*>',
            r'<select[^>]*>',
            r'<button[^>]*>',
            r'<a[^>]*href\s*=\s*["\']javascript:',
            r'<img[^>]*on\w+\s*=',
            r'<div[^>]*on\w+\s*=',
            r'<span[^>]*on\w+\s*=',
            r'<p[^>]*on\w+\s*=',
            r'<h[1-6][^>]*on\w+\s*='
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.DANGEROUS_PATTERNS]
    
    def _parse_admin_ids(self) -> list:
        """Parse admin user IDs from environment variable"""
        admin_ids_str = os.getenv('ADMIN_USER_IDS', '')
        if not admin_ids_str:
            return []
        
        try:
            return [int(uid.strip()) for uid in admin_ids_str.split(',') if uid.strip().isdigit()]
        except Exception as e:
            logger.error(f"Error parsing admin IDs: {e}")
            return []
    
    def _get_allowed_commands(self) -> list:
        """Get list of allowed commands"""
        return [
            'start', 'help', 'balance', 'buy', 'history', 'support',
            'admin', 'add', 'cut', 'trnx', 'nums', 'smm_history',
            'ban', 'unban', 'broadcast', 'delalldata', 'show_server'
        ]
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.ADMIN_USER_IDS
    
    def is_command_allowed(self, command: str) -> bool:
        """Check if command is allowed"""
        return command.lower() in self.ALLOWED_COMMANDS
    
    def sanitize_input(self, text: str, max_length: Optional[int] = None) -> str:
        """Sanitize user input"""
        if not isinstance(text, str):
            return ""
        
        # Apply length limit
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        # Remove dangerous patterns
        for pattern in self.compiled_patterns:
            text = pattern.sub('', text)
        
        # Remove other dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        return text.strip()
    
    def validate_user_id(self, user_id: Any) -> bool:
        """Validate user ID"""
        try:
            return isinstance(user_id, int) and user_id > 0
        except:
            return False
    
    def validate_username(self, username: Any) -> bool:
        """Validate username"""
        if not isinstance(username, str):
            return False
        
        if len(username) > self.MAX_USERNAME_LENGTH:
            return False
        
        # Check for dangerous characters
        if re.search(r'[<>"\']', username):
            return False
        
        return True
    
    def validate_first_name(self, first_name: Any) -> bool:
        """Validate first name"""
        if not isinstance(first_name, str):
            return False
        
        if len(first_name) > self.MAX_FIRST_NAME_LENGTH:
            return False
        
        # Check for dangerous characters
        if re.search(r'[<>"\']', first_name):
            return False
        
        return True
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for web responses"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        }
    
    def log_security_event(self, event_type: str, user_id: Optional[int] = None, details: Optional[str] = None):
        """Log security events"""
        log_message = f"SECURITY_EVENT: {event_type}"
        if user_id:
            log_message += f" | User: {user_id}"
        if details:
            log_message += f" | Details: {details}"
        
        logger.warning(log_message)

# Global security config instance
security_config = SecurityConfig()
