import resend
import logging
from typing import Dict, Any, Optional
from jinja2 import Template
from .mongo_models import EmailLog, EmailTemplate, User
from .config import EMAIL_CONFIG

# Set up logging
logger = logging.getLogger("bistroboard.email")

class EmailService:
    def __init__(self):
        if EMAIL_CONFIG["enabled"] and EMAIL_CONFIG["resend_api_key"]:
            resend.api_key = EMAIL_CONFIG["resend_api_key"]
        else:
            logger.warning("Email service disabled or API key not configured")
    
    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new user"""
        try:
            template_type = f"welcome_{user.role}"  # "welcome_vendor" or "welcome_restaurant"
            template_data = {
                "user_name": user.name,
                "user_email": user.email,
                "role": user.role,
                "login_url": "https://bistroboard.com/login"  # Update with actual URL
            }
            
            return await self._send_email(
                to_email=user.email,
                template_type=template_type,
                template_data=template_data,
                user_id=user.user_id
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return False
    
    async def send_new_order_notification(self, order_data: Dict[str, Any]) -> bool:
        """Send new order notification to vendor"""
        try:
            template_data = {
                "vendor_name": order_data.get("vendor_name", ""),
                "restaurant_name": order_data.get("restaurant_name", ""),
                "order_id": order_data.get("order", {}).get("order_id", ""),
                "items_text": order_data.get("order", {}).get("items_text", ""),
                "notes": order_data.get("order", {}).get("notes", ""),
                "order_date": order_data.get("order", {}).get("created_at", ""),
                "dashboard_url": "https://bistroboard.com/dashboard"  # Update with actual URL
            }
            
            return await self._send_email(
                to_email=order_data.get("vendor_email", ""),
                template_type="new_order",
                template_data=template_data,
                metadata={"order_id": order_data.get("order", {}).get("order_id")}
            )
        except Exception as e:
            logger.error(f"Failed to send new order notification: {str(e)}")
            return False
    
    async def send_order_confirmation(self, order_data: Dict[str, Any]) -> bool:
        """Send order confirmation to restaurant"""
        try:
            template_data = {
                "restaurant_name": order_data.get("restaurant_name", ""),
                "vendor_name": order_data.get("vendor_name", ""),
                "order_id": order_data.get("order", {}).get("order_id", ""),
                "items_text": order_data.get("order", {}).get("items_text", ""),
                "notes": order_data.get("order", {}).get("notes", ""),
                "order_date": order_data.get("order", {}).get("created_at", ""),
                "dashboard_url": "https://bistroboard.com/dashboard"  # Update with actual URL
            }
            
            return await self._send_email(
                to_email=order_data.get("restaurant_email", ""),
                template_type="order_confirmation",
                template_data=template_data,
                metadata={"order_id": order_data.get("order", {}).get("order_id")}
            )
        except Exception as e:
            logger.error(f"Failed to send order confirmation: {str(e)}")
            return False
    
    async def _send_email(
        self, 
        to_email: str, 
        template_type: str, 
        template_data: Dict[str, Any],
        user_id: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Internal method to send email via Resend"""
        if not EMAIL_CONFIG["enabled"]:
            logger.info(f"Email sending disabled, would send {template_type} to {to_email}")
            return True
        
        if not EMAIL_CONFIG["resend_api_key"]:
            logger.error("Resend API key not configured")
            return False
        
        try:
            # Get email template
            template = await self._get_template(template_type)
            if not template:
                logger.error(f"Template not found for type: {template_type}")
                return False
            
            # Render template with data
            subject = self._render_template(template["subject"], template_data)
            html_content = self._render_template(template["html_content"], template_data)
            text_content = self._render_template(template.get("text_content", ""), template_data) if template.get("text_content") else None
            
            # Send email via Resend
            email_data = {
                "from": f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_address']}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            if text_content:
                email_data["text"] = text_content
            
            response = resend.Emails.send(email_data)
            
            # Log successful send
            await self._log_email(
                to_email=to_email,
                template_type=template_type,
                template_id=template["template_id"],
                subject=subject,
                status="sent",
                external_id=response.get("id"),
                user_id=user_id,
                metadata=metadata or {}
            )
            
            logger.info(f"Email sent successfully to {to_email}, message ID: {response.get('id')}")
            return True
            
        except Exception as e:
            # Log failed send
            await self._log_email(
                to_email=to_email,
                template_type=template_type,
                template_id=template_type,
                subject=f"Failed to render subject for {template_type}",
                status="failed",
                error_message=str(e),
                user_id=user_id,
                metadata=metadata or {}
            )
            
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def _get_template(self, template_type: str) -> Optional[Dict[str, Any]]:
        """Get email template from database or use default"""
        try:
            # Try to get template from database
            template = await EmailTemplate.find_one(
                EmailTemplate.template_id == template_type,
                EmailTemplate.is_active == True
            )
            
            if template:
                return template.dict()
            
            # Fall back to default templates
            return self._get_default_template(template_type)
            
        except Exception as e:
            logger.error(f"Error getting template {template_type}: {str(e)}")
            return self._get_default_template(template_type)
    
    def _get_default_template(self, template_type: str) -> Optional[Dict[str, Any]]:
        """Get default email templates"""
        templates = {
            "welcome_vendor": {
                "template_id": "welcome_vendor",
                "name": "Welcome Vendor",
                "subject": "Welcome to BistroBoard, {{user_name}}!",
                "html_content": """
                <html>
                <body>
                    <h1>Welcome to BistroBoard!</h1>
                    <p>Hi {{user_name}},</p>
                    <p>Welcome to BistroBoard! We're excited to have you as a vendor on our platform.</p>
                    <p>You can now start managing your inventory and receiving orders from restaurants.</p>
                    <p><a href="{{login_url}}">Login to your dashboard</a></p>
                    <p>Best regards,<br>The BistroBoard Team</p>
                </body>
                </html>
                """,
                "text_content": "Welcome to BistroBoard, {{user_name}}! You can login at {{login_url}}",
                "variables": ["user_name", "login_url"]
            },
            "welcome_restaurant": {
                "template_id": "welcome_restaurant",
                "name": "Welcome Restaurant",
                "subject": "Welcome to BistroBoard, {{user_name}}!",
                "html_content": """
                <html>
                <body>
                    <h1>Welcome to BistroBoard!</h1>
                    <p>Hi {{user_name}},</p>
                    <p>Welcome to BistroBoard! We're excited to have you as a restaurant on our platform.</p>
                    <p>You can now browse vendors and place orders for your restaurant.</p>
                    <p><a href="{{login_url}}">Login to your dashboard</a></p>
                    <p>Best regards,<br>The BistroBoard Team</p>
                </body>
                </html>
                """,
                "text_content": "Welcome to BistroBoard, {{user_name}}! You can login at {{login_url}}",
                "variables": ["user_name", "login_url"]
            },
            "new_order": {
                "template_id": "new_order",
                "name": "New Order Notification",
                "subject": "New Order #{{order_id}} from {{restaurant_name}}",
                "html_content": """
                <html>
                <body>
                    <h1>New Order Received!</h1>
                    <p>Hi {{vendor_name}},</p>
                    <p>You have received a new order from {{restaurant_name}}.</p>
                    <h3>Order Details:</h3>
                    <p><strong>Order ID:</strong> #{{order_id}}</p>
                    <p><strong>Items:</strong></p>
                    <p>{{items_text}}</p>
                    {% if notes %}
                    <p><strong>Notes:</strong> {{notes}}</p>
                    {% endif %}
                    <p><strong>Order Date:</strong> {{order_date}}</p>
                    <p><a href="{{dashboard_url}}">View in Dashboard</a></p>
                    <p>Best regards,<br>The BistroBoard Team</p>
                </body>
                </html>
                """,
                "text_content": "New order #{{order_id}} from {{restaurant_name}}. Items: {{items_text}}",
                "variables": ["vendor_name", "restaurant_name", "order_id", "items_text", "notes", "order_date", "dashboard_url"]
            },
            "order_confirmation": {
                "template_id": "order_confirmation",
                "name": "Order Confirmation",
                "subject": "Order Confirmation #{{order_id}} - {{vendor_name}}",
                "html_content": """
                <html>
                <body>
                    <h1>Order Confirmation</h1>
                    <p>Hi {{restaurant_name}},</p>
                    <p>Your order has been successfully placed with {{vendor_name}}.</p>
                    <h3>Order Details:</h3>
                    <p><strong>Order ID:</strong> #{{order_id}}</p>
                    <p><strong>Items:</strong></p>
                    <p>{{items_text}}</p>
                    {% if notes %}
                    <p><strong>Notes:</strong> {{notes}}</p>
                    {% endif %}
                    <p><strong>Order Date:</strong> {{order_date}}</p>
                    <p>The vendor will process your order and update you on the status.</p>
                    <p><a href="{{dashboard_url}}">View in Dashboard</a></p>
                    <p>Best regards,<br>The BistroBoard Team</p>
                </body>
                </html>
                """,
                "text_content": "Order confirmation #{{order_id}} with {{vendor_name}}. Items: {{items_text}}",
                "variables": ["restaurant_name", "vendor_name", "order_id", "items_text", "notes", "order_date", "dashboard_url"]
            }
        }
        
        return templates.get(template_type)
    
    def _render_template(self, template_string: str, data: Dict[str, Any]) -> str:
        """Render Jinja2 template with data"""
        try:
            template = Template(template_string)
            return template.render(**data)
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            return template_string
    
    async def _log_email(
        self, 
        to_email: str, 
        template_type: str, 
        template_id: str,
        subject: str,
        status: str, 
        external_id: Optional[str] = None,
        error_message: Optional[str] = None,
        user_id: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ):
        """Log email send attempt"""
        try:
            email_log = EmailLog(
                to_email=to_email,
                template_type=template_type,
                template_id=template_id,
                subject=subject,
                status=status,
                external_id=external_id,
                error_message=error_message,
                user_id=user_id,
                metadata=metadata or {}
            )
            await email_log.insert()
        except Exception as e:
            logger.error(f"Failed to log email: {str(e)}")