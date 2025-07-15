from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


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
    password_hash: str
    role: Indexed(str)  # "restaurant", "vendor", "admin"
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None
    
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
    event_id: Optional[Indexed(int, unique=True)] = None  # Original SQLite ID, optional for new logs
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
    "VendorInfo"
]