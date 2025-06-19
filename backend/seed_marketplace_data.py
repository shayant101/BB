"""
Seed data for BistroBoard Marketplace
Populates vendor categories and creates sample vendor profiles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import VendorCategory, VendorProfile, VendorCategoryMapping, User

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_vendor_categories():
    """Seed the vendor categories table with predefined categories"""
    db = SessionLocal()
    
    try:
        # Check if categories already exist
        existing_categories = db.query(VendorCategory).count()
        if existing_categories > 0:
            print(f"Categories already exist ({existing_categories} found). Skipping category seeding.")
            return
        
        # Food Suppliers Categories
        food_categories = [
            {
                "name": "Fresh Produce",
                "description": "Fruits, vegetables, herbs, organic produce",
                "icon": "🥬",
                "parent_category": "Food Suppliers",
                "sort_order": 1
            },
            {
                "name": "Meat & Seafood",
                "description": "Fresh meats, poultry, fish, shellfish",
                "icon": "🥩",
                "parent_category": "Food Suppliers",
                "sort_order": 2
            },
            {
                "name": "Dairy & Eggs",
                "description": "Milk, cheese, yogurt, eggs, butter",
                "icon": "🥛",
                "parent_category": "Food Suppliers",
                "sort_order": 3
            },
            {
                "name": "Bakery & Grains",
                "description": "Bread, pastries, flour, rice, pasta",
                "icon": "🍞",
                "parent_category": "Food Suppliers",
                "sort_order": 4
            },
            {
                "name": "Beverages",
                "description": "Coffee, tea, juices, soft drinks, alcohol",
                "icon": "☕",
                "parent_category": "Food Suppliers",
                "sort_order": 5
            },
            {
                "name": "Specialty Foods",
                "description": "Spices, sauces, condiments, international foods",
                "icon": "🌶️",
                "parent_category": "Food Suppliers",
                "sort_order": 6
            },
            {
                "name": "Organic & Local",
                "description": "Certified organic, local farms, sustainable products",
                "icon": "🌱",
                "parent_category": "Food Suppliers",
                "sort_order": 7
            },
            {
                "name": "Frozen Foods",
                "description": "Frozen vegetables, meats, prepared foods",
                "icon": "🧊",
                "parent_category": "Food Suppliers",
                "sort_order": 8
            }
        ]
        
        # Service Providers Categories
        service_categories = [
            {
                "name": "Equipment & Supplies",
                "description": "Kitchen equipment, smallwares, furniture",
                "icon": "🔧",
                "parent_category": "Service Providers",
                "sort_order": 9
            },
            {
                "name": "Cleaning & Sanitation",
                "description": "Cleaning supplies, sanitizers, chemicals",
                "icon": "🧽",
                "parent_category": "Service Providers",
                "sort_order": 10
            },
            {
                "name": "Packaging & Disposables",
                "description": "Food containers, bags, utensils, napkins",
                "icon": "📦",
                "parent_category": "Service Providers",
                "sort_order": 11
            },
            {
                "name": "Uniforms & Apparel",
                "description": "Chef coats, aprons, hats, work shoes",
                "icon": "👕",
                "parent_category": "Service Providers",
                "sort_order": 12
            },
            {
                "name": "Maintenance Services",
                "description": "Equipment repair, HVAC, plumbing",
                "icon": "🔨",
                "parent_category": "Service Providers",
                "sort_order": 13
            },
            {
                "name": "Technology Solutions",
                "description": "POS systems, software, hardware",
                "icon": "💻",
                "parent_category": "Service Providers",
                "sort_order": 14
            },
            {
                "name": "Marketing & Design",
                "description": "Menu design, signage, promotional materials",
                "icon": "🎨",
                "parent_category": "Service Providers",
                "sort_order": 15
            },
            {
                "name": "Financial Services",
                "description": "Payment processing, accounting, insurance",
                "icon": "💰",
                "parent_category": "Service Providers",
                "sort_order": 16
            }
        ]
        
        # Combine all categories
        all_categories = food_categories + service_categories
        
        # Create category objects
        for cat_data in all_categories:
            category = VendorCategory(**cat_data)
            db.add(category)
        
        db.commit()
        print(f"Successfully seeded {len(all_categories)} vendor categories")
        
        # Print categories for verification
        categories = db.query(VendorCategory).order_by(VendorCategory.sort_order).all()
        print("\nSeeded Categories:")
        for cat in categories:
            print(f"  {cat.icon} {cat.name} ({cat.parent_category})")
            
    except Exception as e:
        print(f"Error seeding categories: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_vendor_profiles():
    """Create enhanced vendor profiles for existing vendors"""
    db = SessionLocal()
    
    try:
        # Get existing vendors
        vendors = db.query(User).filter(User.role == "vendor").all()
        
        for vendor in vendors:
            # Check if vendor profile already exists
            existing_profile = db.query(VendorProfile).filter(VendorProfile.user_id == vendor.id).first()
            if existing_profile:
                print(f"Profile already exists for {vendor.name}")
                continue
            
            # Create sample vendor profile based on vendor name
            if "Fresh Valley" in vendor.name:
                profile_data = {
                    "user_id": vendor.id,
                    "business_type": "Wholesale Produce Supplier",
                    "specialties": ["Organic Vegetables", "Fresh Fruits", "Herbs", "Local Produce"],
                    "average_rating": 4.8,
                    "review_count": 127,
                    "is_active": True,
                    "business_hours": "Monday-Friday: 6:00 AM - 4:00 PM, Saturday: 7:00 AM - 2:00 PM",
                    "delivery_areas": "Downtown, Midtown, Restaurant District",
                    "minimum_order": 150.00,
                    "payment_terms": "Net 30, Credit Cards Accepted",
                    "certifications": ["Organic Certified", "Food Safety Certified", "Local Farm Partnership"],
                    "business_description": "Premium fresh produce supplier serving restaurants with the highest quality organic and locally-sourced fruits and vegetables. Family-owned business with over 20 years of experience.",
                    "website_url": "https://freshvalleyproduce.com",
                    "established_year": "2003"
                }
                categories = ["Fresh Produce", "Organic & Local"]
            else:
                # Default profile for other vendors
                profile_data = {
                    "user_id": vendor.id,
                    "business_type": "Food Service Supplier",
                    "specialties": ["Quality Products", "Reliable Service"],
                    "average_rating": 4.5,
                    "review_count": 89,
                    "is_active": True,
                    "business_hours": "Monday-Friday: 8:00 AM - 5:00 PM",
                    "delivery_areas": "City-wide delivery available",
                    "minimum_order": 100.00,
                    "payment_terms": "Net 15, Credit Cards Accepted",
                    "certifications": ["Food Safety Certified"],
                    "business_description": f"Reliable supplier providing quality products and excellent service to restaurants throughout the area.",
                    "established_year": "2010"
                }
                categories = ["Specialty Foods"]
            
            # Create vendor profile
            vendor_profile = VendorProfile(**profile_data)
            db.add(vendor_profile)
            db.flush()  # Get the ID
            
            # Add category mappings
            for category_name in categories:
                category = db.query(VendorCategory).filter(VendorCategory.name == category_name).first()
                if category:
                    mapping = VendorCategoryMapping(
                        vendor_profile_id=vendor_profile.id,
                        category_id=category.id
                    )
                    db.add(mapping)
            
            print(f"Created profile for {vendor.name}")
        
        db.commit()
        print("Successfully created sample vendor profiles")
        
    except Exception as e:
        print(f"Error creating vendor profiles: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main seeding function"""
    print("Starting BistroBoard Marketplace data seeding...")
    
    # Seed categories first
    seed_vendor_categories()
    
    # Create sample vendor profiles
    create_sample_vendor_profiles()
    
    print("\nMarketplace data seeding completed!")

if __name__ == "__main__":
    main()