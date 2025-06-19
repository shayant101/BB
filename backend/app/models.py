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
    role = Column(String, nullable=False)  # "restaurant" or "vendor"
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    restaurant_orders = relationship("Order", foreign_keys="Order.restaurant_id", back_populates="restaurant")
    vendor_orders = relationship("Order", foreign_keys="Order.vendor_id", back_populates="vendor")
    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False)

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