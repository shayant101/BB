from beanie import Document, Indexed
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import uuid


class VendorProfile(BaseModel):
    """Embedded vendor profile within User document"""
    business_type: Optional[str] = None
    specialties: List[str] = []
    average_rating: float = 0.0
    review_count: int = 0
    is_active: bool = True
    business_hours: Optional[str] = None
    delivery_areas: Optional[str] = None
    minimum_order: float = 0.0
    payment_terms: Optional[str] = None
    certifications: List[str] = []
    logo_url: Optional[str] = None
    gallery_images: List[str] = []
    business_description: Optional[str] = None
    website_url: Optional[str] = None
    established_year: Optional[str] = None
    categories: List[str] = []


class User(Document):
    """User document for restaurants, vendors, and admins"""
    user_id: Indexed(int, unique=True)  # Original SQLite ID
    username: Indexed(str, unique=True)
    password_hash: Optional[str] = None  # Optional for Google OAuth users
    role: Indexed(str)  # "restaurant", "vendor", "admin"
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None
    
    # Google OAuth fields
    google_id: Optional[str] = None  # Google user ID
    google_email: Optional[str] = None  # Google email (may differ from primary email)
    google_name: Optional[str] = None  # Google display name
    google_picture: Optional[str] = None  # Google profile picture URL
    
    # Clerk OAuth fields
    clerk_user_id: Optional[str] = None  # Clerk user ID
    
    auth_provider: str = "local"  # "local", "google", "clerk", or "both"
    
    # Admin fields
    is_active: bool = True
    status: str = "active"  # "active", "inactive", "pending_approval"
    deactivation_reason: Optional[str] = None
    deactivated_by: Optional[int] = None
    deactivated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    # Embedded vendor profile (only for vendors)
    vendor_profile: Optional[VendorProfile] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        # Indexes are already created by migration script
        # indexes = [
        #     "user_id",
        #     "username",
        #     "role",
        #     "vendor_profile.categories"
        # ]


class RestaurantInfo(BaseModel):
    """Embedded restaurant info in orders"""
    name: str
    phone: str
    address: str
    email: str


class VendorInfo(BaseModel):
    """Embedded vendor info in orders"""
    name: str
    phone: str
    address: str
    email: str


class Order(Document):
    """Order document with denormalized user data"""
    order_id: Indexed(int, unique=True)  # Original SQLite ID
    restaurant_id: Indexed(int)
    vendor_id: Indexed(int)
    
    # Denormalized user data for performance
    restaurant: RestaurantInfo
    vendor: VendorInfo
    
    items_text: str
    status: Indexed(str) = "pending"  # "pending", "confirmed", "fulfilled"
    notes: Optional[str] = None
    
    created_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "orders"
        # Indexes are already created by migration script


class VendorCategory(Document):
    """Vendor category document"""
    category_id: Indexed(int, unique=True)  # Original SQLite ID
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_category: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "vendor_categories"
        # Indexes are already created by migration script


class AdminAuditLog(Document):
    """Admin audit log document"""
    log_id: Indexed(int, unique=True)  # Original SQLite ID
    admin_id: Indexed(int)
    target_user_id: Optional[int] = None
    action: str  # "user_created", "user_deactivated", etc.
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    created_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "admin_audit_logs"
        # Indexes are already created by migration script


class UserEventLog(Document):
    """User event log document"""
    event_id: Optional[int] = None  # Original SQLite ID, optional for new logs (removed unique constraint)
    user_id: Indexed(int)
    event_type: str  # "login", "logout", "password_reset", etc.
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_event_logs"
        # Indexes are already created by migration script


class ImpersonationSession(Document):
    """Impersonation session document"""
    session_id_num: Indexed(int, unique=True)  # Original SQLite ID
    admin_id: int
    target_user_id: int
    session_token: Indexed(str, unique=True)
    expires_at: datetime
    is_active: bool = True
    ended_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "impersonation_sessions"
        # Indexes are already created by migration script


class EmailTemplate(Document):
    """Email template document"""
    template_id: Indexed(str, unique=True)  # "welcome_vendor", "welcome_restaurant", etc.
    name: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    variables: List[str] = []  # List of template variables like {{user_name}}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "email_templates"


class EmailLog(Document):
    """Email send log document"""
    log_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid.uuid4()))  # UUID
    user_id: Optional[int] = None  # Recipient user ID if applicable
    to_email: EmailStr
    template_type: str  # "welcome", "new_order", "order_confirmation"
    template_id: str  # Specific template used
    subject: str
    status: Indexed(str)  # "sent", "failed", "delivered", "bounced"
    external_id: Optional[str] = None  # Resend message ID
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}  # Additional context (order_id, etc.)
    sent_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    
    class Settings:
        name = "email_logs"


# Export all models for easy import
__all__ = [
    "User",
    "Order",
    "VendorCategory",
    "AdminAuditLog",
    "UserEventLog",
    "ImpersonationSession",
    "VendorProfile",
    "RestaurantInfo",
    "VendorInfo",
    "EmailTemplate",
    "EmailLog"
]