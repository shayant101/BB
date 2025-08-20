import os
from typing import Dict, Any

# Email configuration
EMAIL_CONFIG: Dict[str, Any] = {
    "resend_api_key": os.getenv("RESEND_API_KEY"),
    "from_address": os.getenv("EMAIL_FROM_ADDRESS", "noreply@bistroboard.com"),
    "from_name": os.getenv("EMAIL_FROM_NAME", "BistroBoard"),
    "enabled": os.getenv("EMAIL_ENABLED", "true").lower() == "true",
    "templates": {
        "welcome_vendor": "welcome-vendor",
        "welcome_restaurant": "welcome-restaurant", 
        "new_order": "new-order-notification",
        "order_confirmation": "order-confirmation"
    }
}

# Validate required configuration
def validate_email_config():
    """Validate email configuration on startup"""
    if EMAIL_CONFIG["enabled"] and not EMAIL_CONFIG["resend_api_key"]:
        raise ValueError("RESEND_API_KEY environment variable is required when EMAIL_ENABLED=true")
    
    return EMAIL_CONFIG["enabled"]