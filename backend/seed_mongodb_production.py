"""
MongoDB Production Seed Data Script for BistroBoard
Populates MongoDB Atlas with comprehensive sample data for production environment
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
import random
from typing import List
import hashlib

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.mongodb import MONGODB_URL
from app.mongo_models import User, Order, VendorCategory, VendorProfile, RestaurantInfo, VendorInfo

def get_password_hash(password: str) -> str:
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

class MongoDBSeeder:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            self.client = AsyncIOMotorClient(MONGODB_URL)
            self.db = self.client.get_database()
            
            print(f"✅ Seeding target database: '{self.db.name}'")
            
            # Test connection
            await self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def check_existing_data(self):
        """Check if data already exists"""
        user_count = await self.db.users.count_documents({})
        order_count = await self.db.orders.count_documents({})
        category_count = await self.db.vendor_categories.count_documents({})
        
        print(f"📊 Current database state:")
        print(f"   - Users: {user_count}")
        print(f"   - Orders: {order_count}")
        print(f"   - Categories: {category_count}")
        
        return user_count, order_count, category_count
    
    async def seed_vendor_categories(self):
        """Seed vendor categories"""
        print("📦 Seeding vendor categories...")
        
        # Check if categories already exist
        existing_count = await self.db.vendor_categories.count_documents({})
        if existing_count > 0:
            print(f"ℹ️ Categories already exist ({existing_count} found). Skipping...")
            return
        
        categories_data = [
            {
                "category_id": 1,
                "name": "Fresh Produce",
                "description": "Fruits, vegetables, herbs, organic produce",
                "icon": "🥬",
                "parent_category": "Food Suppliers",
                "sort_order": 1,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "category_id": 2,
                "name": "Meat & Seafood",
                "description": "Fresh meats, poultry, fish, shellfish",
                "icon": "🥩",
                "parent_category": "Food Suppliers",
                "sort_order": 2,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "category_id": 3,
                "name": "Dairy & Eggs",
                "description": "Milk, cheese, yogurt, eggs, butter",
                "icon": "🥛",
                "parent_category": "Food Suppliers",
                "sort_order": 3,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "category_id": 4,
                "name": "Bakery & Grains",
                "description": "Bread, pastries, flour, rice, pasta",
                "icon": "🍞",
                "parent_category": "Food Suppliers",
                "sort_order": 4,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "category_id": 5,
                "name": "Beverages",
                "description": "Coffee, tea, juices, soft drinks, alcohol",
                "icon": "☕",
                "parent_category": "Food Suppliers",
                "sort_order": 5,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "category_id": 6,
                "name": "Specialty Foods",
                "description": "Spices, sauces, condiments, international foods",
                "icon": "🌶️",
                "parent_category": "Food Suppliers",
                "sort_order": 6,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "category_id": 7,
                "name": "Packaging & Disposables",
                "description": "Food containers, bags, utensils, napkins",
                "icon": "📦",
                "parent_category": "Service Providers",
                "sort_order": 7,
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "category_id": 8,
                "name": "Equipment & Supplies",
                "description": "Kitchen equipment, smallwares, furniture",
                "icon": "🔧",
                "parent_category": "Service Providers",
                "sort_order": 8,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        result = await self.db.vendor_categories.insert_many(categories_data)
        print(f"✅ Inserted {len(result.inserted_ids)} vendor categories")
    
    async def seed_users(self):
        """Seed users (restaurants and vendors)"""
        print("👥 Seeding users...")
        
        # Check if users already exist
        existing_count = await self.db.users.count_documents({})
        if existing_count > 0:
            print(f"ℹ️ Users already exist ({existing_count} found). Skipping...")
            return
        
        # Vendor users with embedded profiles
        vendors_data = [
            {
                "user_id": 1,
                "username": "fresh_valley_farms",
                "password_hash": get_password_hash("demo123"),
                "role": "vendor",
                "name": "Fresh Valley Farms",
                "email": "orders@freshvalleyfarms.com",
                "phone": "555-0101",
                "address": "1234 Farm Road, Valley Springs, CA 95252",
                "description": "Premium organic produce supplier with 30+ years of experience",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow(),
                "vendor_profile": {
                    "business_type": "Organic Farm",
                    "specialties": ["Organic Vegetables", "Seasonal Fruits", "Herbs"],
                    "average_rating": 4.8,
                    "review_count": 127,
                    "is_active": True,
                    "business_hours": "Monday-Friday: 6:00 AM - 4:00 PM, Saturday: 7:00 AM - 2:00 PM",
                    "delivery_areas": "San Francisco Bay Area, Peninsula, East Bay",
                    "minimum_order": 150.0,
                    "payment_terms": "Net 30, Credit Cards Accepted",
                    "certifications": ["Organic Certified", "Food Safety Certified"],
                    "business_description": "Premium fresh produce supplier serving restaurants with the highest quality organic and locally-sourced fruits and vegetables.",
                    "website_url": "https://freshvalleyfarms.com",
                    "established_year": "1993",
                    "categories": ["Fresh Produce"]
                }
            },
            {
                "user_id": 2,
                "username": "prime_cuts_wholesale",
                "password_hash": get_password_hash("demo123"),
                "role": "vendor",
                "name": "Prime Cuts Wholesale",
                "email": "orders@primecuts.com",
                "phone": "555-0201",
                "address": "3456 Butcher Block Blvd, San Francisco, CA 94102",
                "description": "Premium aged beef and specialty cuts for fine dining",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=45),
                "updated_at": datetime.utcnow(),
                "vendor_profile": {
                    "business_type": "Meat Processor",
                    "specialties": ["Aged Beef", "Wagyu", "Specialty Cuts"],
                    "average_rating": 4.9,
                    "review_count": 89,
                    "is_active": True,
                    "business_hours": "Monday-Friday: 7:00 AM - 5:00 PM",
                    "delivery_areas": "San Francisco, Peninsula, South Bay",
                    "minimum_order": 200.0,
                    "payment_terms": "Net 15, Credit Cards Accepted",
                    "certifications": ["USDA Certified", "Food Safety Certified"],
                    "business_description": "Premium meat supplier specializing in aged beef and specialty cuts for fine dining establishments.",
                    "website_url": "https://primecuts.com",
                    "established_year": "2005",
                    "categories": ["Meat & Seafood"]
                }
            },
            {
                "user_id": 3,
                "username": "sunrise_dairy",
                "password_hash": get_password_hash("demo123"),
                "role": "vendor",
                "name": "Sunrise Dairy",
                "email": "orders@sunrisedairy.com",
                "phone": "555-0301",
                "address": "4567 Dairy Lane, Petaluma, CA 94952",
                "description": "Artisanal cheeses and fresh dairy products",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=60),
                "updated_at": datetime.utcnow(),
                "vendor_profile": {
                    "business_type": "Dairy Farm",
                    "specialties": ["Artisan Cheese", "Fresh Milk", "Organic Butter"],
                    "average_rating": 4.7,
                    "review_count": 156,
                    "is_active": True,
                    "business_hours": "Monday-Saturday: 6:00 AM - 6:00 PM",
                    "delivery_areas": "North Bay, San Francisco, East Bay",
                    "minimum_order": 100.0,
                    "payment_terms": "Net 30, Credit Cards Accepted",
                    "certifications": ["Organic Certified", "Artisan Guild Member"],
                    "business_description": "Family-owned dairy farm producing artisanal cheeses and fresh dairy products since 1987.",
                    "website_url": "https://sunrisedairy.com",
                    "established_year": "1987",
                    "categories": ["Dairy & Eggs"]
                }
            },
            {
                "user_id": 4,
                "username": "golden_grain_supply",
                "password_hash": get_password_hash("demo123"),
                "role": "vendor",
                "name": "Golden Grain Supply",
                "email": "sales@goldengrain.com",
                "phone": "555-0401",
                "address": "8901 Grain Silo Way, Stockton, CA 95202",
                "description": "Bulk grains, flours, and specialty baking ingredients",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=20),
                "updated_at": datetime.utcnow(),
                "vendor_profile": {
                    "business_type": "Grain Distributor",
                    "specialties": ["Organic Flours", "Ancient Grains", "Specialty Rice"],
                    "average_rating": 4.6,
                    "review_count": 203,
                    "is_active": True,
                    "business_hours": "Monday-Friday: 8:00 AM - 5:00 PM",
                    "delivery_areas": "Central Valley, Bay Area, Sacramento",
                    "minimum_order": 75.0,
                    "payment_terms": "Net 30, Credit Cards Accepted",
                    "certifications": ["Organic Certified", "Non-GMO Verified"],
                    "business_description": "Leading supplier of bulk grains, flours, and specialty baking ingredients to restaurants and bakeries.",
                    "website_url": "https://goldengrain.com",
                    "established_year": "1998",
                    "categories": ["Bakery & Grains"]
                }
            },
            {
                "user_id": 5,
                "username": "eco_pack_solutions",
                "password_hash": get_password_hash("demo123"),
                "role": "vendor",
                "name": "EcoPack Solutions",
                "email": "orders@ecopack.com",
                "phone": "555-0601",
                "address": "4680 Green Way, Berkeley, CA 94710",
                "description": "Sustainable packaging and eco-friendly disposables",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=15),
                "updated_at": datetime.utcnow(),
                "vendor_profile": {
                    "business_type": "Packaging Supplier",
                    "specialties": ["Biodegradable Containers", "Compostable Utensils", "Recycled Paper Products"],
                    "average_rating": 4.5,
                    "review_count": 78,
                    "is_active": True,
                    "business_hours": "Monday-Friday: 9:00 AM - 5:00 PM",
                    "delivery_areas": "Bay Area, Sacramento, Central Valley",
                    "minimum_order": 50.0,
                    "payment_terms": "Net 15, Credit Cards Accepted",
                    "certifications": ["Sustainable Packaging Certified", "Carbon Neutral"],
                    "business_description": "Leading provider of sustainable packaging solutions for environmentally conscious restaurants.",
                    "website_url": "https://ecopack.com",
                    "established_year": "2015",
                    "categories": ["Packaging & Disposables"]
                }
            }
        ]
        
        # Restaurant users
        restaurants_data = [
            {
                "user_id": 101,
                "username": "bella_italia",
                "password_hash": get_password_hash("demo123"),
                "role": "restaurant",
                "name": "Bella Italia Ristorante",
                "email": "orders@bellaitalia.com",
                "phone": "555-1001",
                "address": "123 Little Italy St, San Francisco, CA 94133",
                "description": "Authentic Italian cuisine with traditional recipes",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=90),
                "updated_at": datetime.utcnow(),
                "last_login_at": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "user_id": 102,
                "username": "sakura_sushi",
                "password_hash": get_password_hash("demo123"),
                "role": "restaurant",
                "name": "Sakura Sushi Bar",
                "email": "info@sakurasushi.com",
                "phone": "555-1002",
                "address": "456 Japantown Blvd, San Francisco, CA 94115",
                "description": "Fresh sushi and traditional Japanese dishes",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=75),
                "updated_at": datetime.utcnow(),
                "last_login_at": datetime.utcnow() - timedelta(hours=5)
            },
            {
                "user_id": 103,
                "username": "le_petit_bistro",
                "password_hash": get_password_hash("demo123"),
                "role": "restaurant",
                "name": "Le Petit Bistro",
                "email": "reservations@lepetitbistro.com",
                "phone": "555-1003",
                "address": "789 French Quarter Ave, San Francisco, CA 94102",
                "description": "Classic French bistro with seasonal menu",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=120),
                "updated_at": datetime.utcnow(),
                "last_login_at": datetime.utcnow() - timedelta(hours=1)
            },
            {
                "user_id": 104,
                "username": "farm_table",
                "password_hash": get_password_hash("demo123"),
                "role": "restaurant",
                "name": "Farm Table Restaurant",
                "email": "orders@farmtable.com",
                "phone": "555-1011",
                "address": "852 Organic Way, Palo Alto, CA 94301",
                "description": "Farm-to-table dining with seasonal ingredients",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=50),
                "updated_at": datetime.utcnow(),
                "last_login_at": datetime.utcnow() - timedelta(hours=8)
            },
            {
                "user_id": 105,
                "username": "pizza_corner",
                "password_hash": get_password_hash("demo123"),
                "role": "restaurant",
                "name": "Pizza Corner",
                "email": "orders@pizzacorner.com",
                "phone": "555-1012",
                "address": "963 Slice Street, San Jose, CA 95110",
                "description": "New York style pizza and Italian classics",
                "is_active": True,
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=35),
                "updated_at": datetime.utcnow(),
                "last_login_at": datetime.utcnow() - timedelta(hours=12)
            }
        ]
        
        # Insert all users
        all_users = vendors_data + restaurants_data
        result = await self.db.users.insert_many(all_users)
        print(f"✅ Inserted {len(result.inserted_ids)} users ({len(vendors_data)} vendors, {len(restaurants_data)} restaurants)")
    
    async def seed_orders(self):
        """Seed orders with realistic data"""
        print("📋 Seeding orders...")
        
        # Check if orders already exist
        existing_count = await self.db.orders.count_documents({})
        if existing_count > 0:
            print(f"ℹ️ Orders already exist ({existing_count} found). Skipping...")
            return
        
        # Get users for order creation
        restaurants = await self.db.users.find({"role": "restaurant"}).to_list(length=None)
        vendors = await self.db.users.find({"role": "vendor"}).to_list(length=None)
        
        if not restaurants or not vendors:
            print("⚠️ No restaurants or vendors found. Cannot create orders.")
            return
        
        # Sample order items
        order_items = [
            "10 lbs organic tomatoes, 5 lbs red onions, 3 bunches fresh basil",
            "2 cases premium olive oil, 5 lbs sea salt, 1 case balsamic vinegar",
            "20 lbs fresh salmon fillets, 10 lbs prawns, 5 lbs scallops",
            "50 lbs all-purpose flour, 25 lbs bread flour, 10 lbs semolina",
            "1 case aged cheddar, 2 lbs fresh mozzarella, 1 lb parmesan",
            "5 lbs ground beef, 3 lbs chicken breast, 2 lbs lamb chops",
            "100 eco-friendly takeout containers, 200 compostable utensils",
            "15 lbs jasmine rice, 10 lbs black beans, 5 lbs quinoa",
            "3 lbs mixed spices, 2 lbs curry powder, 1 lb saffron",
            "20 dozen farm-fresh eggs, 5 lbs organic butter, 2 gallons heavy cream"
        ]
        
        orders_data = []
        order_statuses = ['pending', 'confirmed', 'fulfilled']
        
        # Create 30 orders with realistic timing
        for i in range(30):
            restaurant = random.choice(restaurants)
            vendor = random.choice(vendors)
            status = random.choices(order_statuses, weights=[20, 50, 30])[0]
            
            # Create orders with different ages based on status
            if status == 'pending':
                created_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            elif status == 'confirmed':
                created_time = datetime.utcnow() - timedelta(hours=random.randint(6, 72))
            else:  # fulfilled
                created_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            order_data = {
                "order_id": i + 1,
                "restaurant_id": restaurant["user_id"],
                "vendor_id": vendor["user_id"],
                "restaurant": {
                    "name": restaurant["name"],
                    "phone": restaurant["phone"],
                    "address": restaurant["address"],
                    "email": restaurant["email"]
                },
                "vendor": {
                    "name": vendor["name"],
                    "phone": vendor["phone"],
                    "address": vendor["address"],
                    "email": vendor["email"]
                },
                "items_text": random.choice(order_items),
                "status": status,
                "notes": f"Order for {status} delivery" if random.random() > 0.5 else None,
                "created_at": created_time,
                "updated_at": created_time + timedelta(minutes=random.randint(0, 60))
            }
            orders_data.append(order_data)
        
        result = await self.db.orders.insert_many(orders_data)
        print(f"✅ Inserted {len(result.inserted_ids)} orders")
    
    async def create_admin_user(self):
        """Create admin user if it doesn't exist"""
        print("👑 Creating admin user...")
        
        # Check if admin already exists
        admin_exists = await self.db.users.find_one({"role": "admin"})
        if admin_exists:
            print("ℹ️ Admin user already exists. Skipping...")
            return
        
        admin_data = {
            "user_id": 999,
            "username": "admin",
            "password_hash": get_password_hash("admin123"),
            "role": "admin",
            "name": "System Administrator",
            "email": "admin@bistroboard.com",
            "phone": "555-0000",
            "address": "BistroBoard HQ, San Francisco, CA",
            "description": "System administrator with full access",
            "is_active": True,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.db.users.insert_one(admin_data)
        print(f"✅ Created admin user with ID: {result.inserted_id}")
    
    async def run_seeding(self):
        """Run the complete seeding process"""
        try:
            print("🚀 Starting MongoDB production seeding...")
            print(f"📅 Seeding started at: {datetime.utcnow()}")
            
            await self.connect()
            
            # Check current state
            user_count, order_count, category_count = await self.check_existing_data()
            
            # Run seeding in order
            await self.seed_vendor_categories()
            await self.seed_users()
            await self.create_admin_user()
            await self.seed_orders()
            
            # Final verification
            final_user_count = await self.db.users.count_documents({})
            final_order_count = await self.db.orders.count_documents({})
            final_category_count = await self.db.vendor_categories.count_documents({})
            
            print("\n" + "="*60)
            print("🎉 SEEDING COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"📊 Final database state:")
            print(f"   - Users: {final_user_count}")
            print(f"   - Orders: {final_order_count}")
            print(f"   - Categories: {final_category_count}")
            print(f"📅 Completed at: {datetime.utcnow()}")
            
            print("\n🔑 Test Login Credentials:")
            print("   Admin: username='admin', password='admin123'")
            print("   Restaurant: username='bella_italia', password='demo123'")
            print("   Vendor: username='fresh_valley_farms', password='demo123'")
            
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            raise
        finally:
            if self.client:
                self.client.close()
                print("✅ MongoDB connection closed")

async def main():
    """Main function to run seeding"""
    seeder = MongoDBSeeder()
    await seeder.run_seeding()

if __name__ == "__main__":
    print("BistroBoard MongoDB Production Seeding")
    print("=" * 50)
    asyncio.run(main())