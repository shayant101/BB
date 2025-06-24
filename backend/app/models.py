from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "restaurant", "vendor", or "admin"
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Admin Command Center fields
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String, default="active", nullable=False)  # "active", "inactive", "pending_approval"
    deactivation_reason = Column(Text, nullable=True)
    deactivated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    restaurant_orders = relationship("Order", foreign_keys="Order.restaurant_id", back_populates="restaurant")
    vendor_orders = relationship("Order", foreign_keys="Order.vendor_id", back_populates="vendor")
    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False)
    
    # Admin relationships
    deactivated_by_admin = relationship("User", remote_side=[id])
    audit_logs_performed = relationship("AdminAuditLog", foreign_keys="AdminAuditLog.admin_id", back_populates="admin")
    audit_logs_target = relationship("AdminAuditLog", foreign_keys="AdminAuditLog.target_user_id", back_populates="target_user")
    user_events = relationship("UserEventLog", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    items_text = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)  # "pending", "confirmed", "fulfilled"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    restaurant = relationship("User", foreign_keys=[restaurant_id], back_populates="restaurant_orders")
    vendor = relationship("User", foreign_keys=[vendor_id], back_populates="vendor_orders")


class VendorProfile(Base):
    __tablename__ = "vendor_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    business_type = Column(String(100))
    specialties = Column(JSON)
    average_rating = Column(Numeric(3, 2), default=0.0)
    review_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    business_hours = Column(Text)
    delivery_areas = Column(Text)
    minimum_order = Column(Numeric(10, 2))
    payment_terms = Column(Text)
    certifications = Column(JSON)
    logo_url = Column(String(255))
    gallery_images = Column(JSON)
    business_description = Column(Text)
    website_url = Column(String(255))
    established_year = Column(String(4))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="vendor_profile")
    categories = relationship("VendorCategoryMapping", back_populates="vendor_profile")


class VendorCategory(Base):
    __tablename__ = "vendor_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    parent_category = Column(String(100))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor_mappings = relationship("VendorCategoryMapping", back_populates="category")


class VendorCategoryMapping(Base):
    __tablename__ = "vendor_category_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_profile_id = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("vendor_categories.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor_profile = relationship("VendorProfile", back_populates="categories")
    category = relationship("VendorCategory", back_populates="vendor_mappings")
    
    # Ensure unique combinations
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class AdminAuditLog(Base):
    """Immutable audit trail for all admin actions"""
    __tablename__ = "admin_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # "user_created", "user_deactivated", "user_reactivated", "impersonation_started"
    details = Column(JSON, nullable=True)  # Additional context like reason, previous values, etc.
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    admin = relationship("User", foreign_keys=[admin_id], back_populates="audit_logs_performed")
    target_user = relationship("User", foreign_keys=[target_user_id], back_populates="audit_logs_target")


class UserEventLog(Base):
    """Track key user events for support and analytics"""
    __tablename__ = "user_event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # "login", "logout", "password_reset", "profile_updated", "order_created"
    details = Column(JSON, nullable=True)  # Additional event context
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_events")


class ImpersonationSession(Base):
    """Track active impersonation sessions for security"""
    __tablename__ = "impersonation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])
    target_user = relationship("User", foreign_keys=[target_user_id])