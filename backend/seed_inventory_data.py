"""
Comprehensive Inventory Data Seeding Script for BistroBoard
Populates MongoDB with vendors, categories, inventory items, and storefront products
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
from app.mongodb import connect_to_mongo, close_mongo_connection
from app.mongo_models import User, VendorProfile
from app.inventory_models import InventoryCategory, InventoryItem, InventorySKU, InventoryCounter
from app.storefront_models import VendorStorefront, ProductCategory, VendorProduct

def get_password_hash(password: str) -> str:
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

class InventorySeeder:
    def __init__(self):
        self.vendor_counter = 1
        self.category_counter = 1
        self.item_counter = 1
        self.sku_counter = 1
        self.product_counter = 1
        self.product_category_counter = 1
        
    async def analyze_existing_data(self):
        """Analyze existing data to understand current state and avoid conflicts"""
        print("🔍 Analyzing existing data...")
        
        try:
            # Get existing users
            existing_users = await User.find_all().to_list()
            existing_vendors = [u for u in existing_users if u.role == "vendor"]
            existing_restaurants = [u for u in existing_users if u.role == "restaurant"]
            existing_admins = [u for u in existing_users if u.role == "admin"]
            
            # Get existing inventory data
            existing_categories = await InventoryCategory.find_all().to_list()
            existing_items = await InventoryItem.find_all().to_list()
            existing_skus = await InventorySKU.find_all().to_list()
            existing_counters = await InventoryCounter.find_all().to_list()
            
            # Get existing storefront data
            existing_storefronts = await VendorStorefront.find_all().to_list()
            existing_product_categories = await ProductCategory.find_all().to_list()
            existing_products = await VendorProduct.find_all().to_list()
            
            print(f"📊 Current database state:")
            print(f"   - Total Users: {len(existing_users)} (Vendors: {len(existing_vendors)}, Restaurants: {len(existing_restaurants)}, Admins: {len(existing_admins)})")
            print(f"   - Inventory Categories: {len(existing_categories)}")
            print(f"   - Inventory Items: {len(existing_items)}")
            print(f"   - SKUs: {len(existing_skus)}")
            print(f"   - Storefronts: {len(existing_storefronts)}")
            print(f"   - Product Categories: {len(existing_product_categories)}")
            print(f"   - Storefront Products: {len(existing_products)}")
            
            # Find max IDs to avoid conflicts
            max_user_id = max([u.user_id for u in existing_users], default=0)
            max_category_id = max([c.category_id for c in existing_categories], default=0)
            max_item_id = max([i.item_id for i in existing_items], default=0)
            max_sku_id = max([s.sku_id for s in existing_skus], default=0)
            max_product_category_id = max([pc.category_id for pc in existing_product_categories], default=0)
            max_product_id = max([p.product_id for p in existing_products], default=0)
            
            print(f"📈 Max IDs found:")
            print(f"   - Max User ID: {max_user_id}")
            print(f"   - Max Category ID: {max_category_id}")
            print(f"   - Max Item ID: {max_item_id}")
            print(f"   - Max SKU ID: {max_sku_id}")
            print(f"   - Max Product Category ID: {max_product_category_id}")
            print(f"   - Max Product ID: {max_product_id}")
            
            # Set starting counters to avoid conflicts
            self.vendor_counter = max_user_id + 1
            self.category_counter = max_category_id + 1
            self.item_counter = max_item_id + 1
            self.sku_counter = max_sku_id + 1
            self.product_category_counter = max_product_category_id + 1
            self.product_counter = max_product_id + 1
            
            # Update or create counters in database
            await self.update_counters()
            
            return {
                'existing_vendors': existing_vendors,
                'existing_restaurants': existing_restaurants,
                'existing_admins': existing_admins,
                'max_user_id': max_user_id,
                'max_category_id': max_category_id,
                'max_item_id': max_item_id,
                'max_sku_id': max_sku_id,
                'max_product_category_id': max_product_category_id,
                'max_product_id': max_product_id
            }
            
        except Exception as e:
            print(f"❌ Error analyzing existing data: {e}")
            raise

    async def update_counters(self):
        """Update counter documents with current max values"""
        counter_updates = [
            ("users", self.vendor_counter),
            ("inventory_categories", self.category_counter),
            ("inventory_items", self.item_counter),
            ("inventory_skus", self.sku_counter),
            ("product_categories", self.product_category_counter),
            ("vendor_products", self.product_counter)
        ]
        
        for collection_name, start_value in counter_updates:
            counter = await InventoryCounter.find_one({"collection_name": collection_name})
            if counter:
                counter.sequence_value = start_value - 1  # -1 because get_next_id will increment
                await counter.save()
            else:
                counter = InventoryCounter(collection_name=collection_name, sequence_value=start_value - 1)
                await counter.insert()

    async def get_next_id(self, collection_name: str) -> int:
        """Get next auto-incrementing ID for a collection"""
        counter = await InventoryCounter.find_one({"collection_name": collection_name})
        if not counter:
            counter = InventoryCounter(collection_name=collection_name, sequence_value=1)
            await counter.insert()
            return 1
        else:
            counter.sequence_value += 1
            await counter.save()
            return counter.sequence_value

    async def seed_vendors(self):
        """Seed comprehensive vendor data from populate_demo_data.py"""
        print("👥 Seeding vendors with comprehensive data...")
        
        # Comprehensive vendor data from populate_demo_data.py
        vendors_data = [
            # Fresh Produce
            {
                'username': 'fresh_valley_farms', 'password': 'demo123', 'name': 'Fresh Valley Farms',
                'email': 'orders@freshvalleyfarms.com', 'phone': '555-0101', 
                'address': '1234 Farm Road, Valley Springs, CA 95252',
                'description': 'Premium organic produce supplier with 30+ years of experience',
                'business_type': 'Organic Farm', 'specialties': ['Organic Vegetables', 'Seasonal Fruits', 'Herbs'],
                'category': 'Fresh Produce', 'status': 'active'
            },
            {
                'username': 'golden_harvest_co', 'password': 'demo123', 'name': 'Golden Harvest Co.',
                'email': 'sales@goldenharvest.com', 'phone': '555-0102',
                'address': '5678 Orchard Lane, Fresno, CA 93720',
                'description': 'Year-round fresh produce with same-day delivery',
                'business_type': 'Produce Distributor', 'specialties': ['Citrus Fruits', 'Root Vegetables', 'Leafy Greens'],
                'category': 'Fresh Produce', 'status': 'active'
            },
            {
                'username': 'mountain_greens', 'password': 'demo123', 'name': 'Mountain Greens',
                'email': 'info@mountaingreens.com', 'phone': '555-0103',
                'address': '9012 Highland Ave, Sacramento, CA 95814',
                'description': 'Locally sourced mountain-grown vegetables and herbs',
                'business_type': 'Local Farm', 'specialties': ['Mountain Vegetables', 'Wild Herbs', 'Microgreens'],
                'category': 'Fresh Produce', 'status': 'active'
            },
            
            # Meat & Seafood
            {
                'username': 'prime_cuts_wholesale', 'password': 'demo123', 'name': 'Prime Cuts Wholesale',
                'email': 'orders@primecuts.com', 'phone': '555-0201',
                'address': '3456 Butcher Block Blvd, San Francisco, CA 94102',
                'description': 'Premium aged beef and specialty cuts for fine dining',
                'business_type': 'Meat Processor', 'specialties': ['Aged Beef', 'Wagyu', 'Specialty Cuts'],
                'category': 'Meat & Seafood', 'status': 'active'
            },
            {
                'username': 'ocean_fresh_seafood', 'password': 'demo123', 'name': 'Ocean Fresh Seafood',
                'email': 'sales@oceanfresh.com', 'phone': '555-0202',
                'address': '7890 Fisherman\'s Wharf, Monterey, CA 93940',
                'description': 'Daily fresh catch from local fishing boats',
                'business_type': 'Seafood Distributor', 'specialties': ['Daily Fresh Fish', 'Shellfish', 'Sustainable Seafood'],
                'category': 'Meat & Seafood', 'status': 'active'
            },
            {
                'username': 'heritage_meats', 'password': 'demo123', 'name': 'Heritage Meats',
                'email': 'contact@heritagemeats.com', 'phone': '555-0203',
                'address': '2345 Ranch Road, Paso Robles, CA 93446',
                'description': 'Grass-fed, heritage breed meats and poultry',
                'business_type': 'Ranch', 'specialties': ['Grass-Fed Beef', 'Heritage Pork', 'Free-Range Poultry'],
                'category': 'Meat & Seafood', 'status': 'active'
            },
            
            # Dairy & Eggs
            {
                'username': 'sunrise_dairy', 'password': 'demo123', 'name': 'Sunrise Dairy',
                'email': 'orders@sunrisedairy.com', 'phone': '555-0301',
                'address': '4567 Dairy Lane, Petaluma, CA 94952',
                'description': 'Artisanal cheeses and fresh dairy products',
                'business_type': 'Dairy Farm', 'specialties': ['Artisan Cheese', 'Fresh Milk', 'Organic Butter'],
                'category': 'Dairy & Eggs', 'status': 'active'
            },
            {
                'username': 'farm_fresh_eggs', 'password': 'demo123', 'name': 'Farm Fresh Eggs Co.',
                'email': 'info@farmfresheggs.com', 'phone': '555-0302',
                'address': '6789 Henhouse Road, Sonoma, CA 95476',
                'description': 'Cage-free and pasture-raised eggs from happy hens',
                'business_type': 'Poultry Farm', 'specialties': ['Pasture-Raised Eggs', 'Duck Eggs', 'Quail Eggs'],
                'category': 'Dairy & Eggs', 'status': 'active'
            },
            
            # Pantry & Dry Goods
            {
                'username': 'golden_grain_supply', 'password': 'demo123', 'name': 'Golden Grain Supply',
                'email': 'sales@goldengrain.com', 'phone': '555-0401',
                'address': '8901 Grain Silo Way, Stockton, CA 95202',
                'description': 'Bulk grains, flours, and specialty baking ingredients',
                'business_type': 'Grain Distributor', 'specialties': ['Organic Flours', 'Ancient Grains', 'Specialty Rice'],
                'category': 'Pantry & Dry Goods', 'status': 'active'
            },
            {
                'username': 'spice_world_imports', 'password': 'demo123', 'name': 'Spice World Imports',
                'email': 'orders@spiceworld.com', 'phone': '555-0402',
                'address': '1357 Spice Market St, Oakland, CA 94607',
                'description': 'Global spices, seasonings, and specialty condiments',
                'business_type': 'Spice Importer', 'specialties': ['International Spices', 'Rare Seasonings', 'Specialty Salts'],
                'category': 'Pantry & Dry Goods', 'status': 'active'
            },
            
            # Beverages
            {
                'username': 'craft_beverage_co', 'password': 'demo123', 'name': 'Craft Beverage Co.',
                'email': 'sales@craftbeverage.com', 'phone': '555-0501',
                'address': '2468 Brewery Lane, San Diego, CA 92101',
                'description': 'Craft sodas, specialty waters, and artisanal beverages',
                'business_type': 'Beverage Distributor', 'specialties': ['Craft Sodas', 'Specialty Waters', 'Kombucha'],
                'category': 'Beverages', 'status': 'active'
            },
            {
                'username': 'wine_country_supply', 'password': 'demo123', 'name': 'Wine Country Supply',
                'email': 'info@winecountrysupply.com', 'phone': '555-0502',
                'address': '3579 Vineyard Road, Napa, CA 94558',
                'description': 'Premium wines and specialty beverages for restaurants',
                'business_type': 'Wine Distributor', 'specialties': ['Local Wines', 'Craft Beer', 'Specialty Cocktail Mixers'],
                'category': 'Beverages', 'status': 'active'
            },
            
            # Packaging & Disposables
            {
                'username': 'eco_pack_solutions', 'password': 'demo123', 'name': 'EcoPack Solutions',
                'email': 'orders@ecopack.com', 'phone': '555-0601',
                'address': '4680 Green Way, Berkeley, CA 94710',
                'description': 'Sustainable packaging and eco-friendly disposables',
                'business_type': 'Packaging Supplier', 'specialties': ['Biodegradable Containers', 'Compostable Utensils', 'Recycled Paper Products'],
                'category': 'Packaging & Disposables', 'status': 'active'
            },
            {
                'username': 'restaurant_supply_pro', 'password': 'demo123', 'name': 'Restaurant Supply Pro',
                'email': 'sales@restaurantsupplypro.com', 'phone': '555-0602',
                'address': '5791 Industrial Blvd, Los Angeles, CA 90021',
                'description': 'Complete restaurant packaging and disposable solutions',
                'business_type': 'Restaurant Supplier', 'specialties': ['Take-out Containers', 'Food Service Disposables', 'Cleaning Supplies'],
                'category': 'Packaging & Disposables', 'status': 'active'
            },
            
            # Equipment & Supplies
            {
                'username': 'kitchen_pro_equipment', 'password': 'demo123', 'name': 'Kitchen Pro Equipment',
                'email': 'info@kitchenpro.com', 'phone': '555-0701',
                'address': '6802 Equipment Row, San Jose, CA 95110',
                'description': 'Professional kitchen equipment and maintenance services',
                'business_type': 'Equipment Supplier', 'specialties': ['Commercial Ovens', 'Refrigeration', 'Kitchen Tools'],
                'category': 'Equipment & Supplies', 'status': 'active'
            },
            {
                'username': 'culinary_tools_plus', 'password': 'demo123', 'name': 'Culinary Tools Plus',
                'email': 'orders@culinarytools.com', 'phone': '555-0702',
                'address': '7913 Chef\'s Avenue, Santa Clara, CA 95050',
                'description': 'Professional culinary tools and kitchen accessories',
                'business_type': 'Tool Supplier', 'specialties': ['Chef Knives', 'Cookware', 'Kitchen Gadgets'],
                'category': 'Equipment & Supplies', 'status': 'active'
            }
        ]
        
        created_vendors = []
        for vendor_data in vendors_data:
            user_id = await self.get_next_id("users")
            
            # Create vendor profile
            vendor_profile = VendorProfile(
                business_type=vendor_data['business_type'],
                specialties=vendor_data['specialties'],
                average_rating=round(random.uniform(4.0, 5.0), 1),
                review_count=random.randint(15, 150),
                is_active=vendor_data['status'] == 'active',
                business_hours="Monday-Friday: 6:00 AM - 6:00 PM, Saturday: 8:00 AM - 4:00 PM",
                delivery_areas="San Francisco Bay Area, Peninsula, East Bay",
                minimum_order=round(random.uniform(50.0, 200.0), 2),
                payment_terms="Net 30 days, Credit cards accepted",
                certifications=["Food Safety Certified", "Business License"],
                business_description=vendor_data['description'],
                established_year=str(random.randint(1990, 2020)),
                categories=[vendor_data['category']]
            )
            
            # Create user with embedded vendor profile
            user = User(
                user_id=user_id,
                username=vendor_data['username'],
                password_hash=get_password_hash(vendor_data['password']),
                role="vendor",
                name=vendor_data['name'],
                email=vendor_data['email'],
                phone=vendor_data['phone'],
                address=vendor_data['address'],
                description=vendor_data['description'],
                is_active=vendor_data['status'] == 'active',
                status=vendor_data['status'],
                vendor_profile=vendor_profile,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                updated_at=datetime.utcnow()
            )
            
            await user.insert()
            created_vendors.append(user)
            
        print(f"✅ Created {len(created_vendors)} vendors")
        return created_vendors

    async def seed_inventory_categories(self, vendors: List[User]):
        """Seed inventory categories for each vendor"""
        print("📂 Seeding inventory categories...")
        
        # Standard categories that most vendors will have
        standard_categories = [
            {"name": "Featured Items", "description": "Our most popular products"},
            {"name": "New Arrivals", "description": "Recently added products"},
            {"name": "Seasonal", "description": "Seasonal and limited-time products"},
            {"name": "Bulk Orders", "description": "Products available in bulk quantities"},
        ]
        
        # Category-specific items based on vendor type
        category_specific = {
            "Fresh Produce": [
                {"name": "Organic Vegetables", "description": "Certified organic vegetables"},
                {"name": "Fresh Fruits", "description": "Seasonal fresh fruits"},
                {"name": "Herbs & Spices", "description": "Fresh herbs and dried spices"},
                {"name": "Root Vegetables", "description": "Potatoes, carrots, onions, etc."}
            ],
            "Meat & Seafood": [
                {"name": "Premium Beef", "description": "High-quality beef cuts"},
                {"name": "Fresh Seafood", "description": "Daily fresh fish and shellfish"},
                {"name": "Poultry", "description": "Chicken, duck, and other poultry"},
                {"name": "Specialty Cuts", "description": "Unique and specialty meat cuts"}
            ],
            "Dairy & Eggs": [
                {"name": "Artisan Cheese", "description": "Handcrafted artisanal cheeses"},
                {"name": "Fresh Dairy", "description": "Milk, cream, and butter"},
                {"name": "Farm Eggs", "description": "Fresh eggs from local farms"},
                {"name": "Organic Products", "description": "Certified organic dairy products"}
            ],
            "Pantry & Dry Goods": [
                {"name": "Grains & Flours", "description": "Various grains and specialty flours"},
                {"name": "Spices & Seasonings", "description": "International spices and seasonings"},
                {"name": "Baking Supplies", "description": "Everything for baking needs"},
                {"name": "Specialty Ingredients", "description": "Unique and hard-to-find ingredients"}
            ],
            "Beverages": [
                {"name": "Craft Beverages", "description": "Artisanal and craft drinks"},
                {"name": "Wine & Beer", "description": "Local wines and craft beers"},
                {"name": "Non-Alcoholic", "description": "Sodas, juices, and specialty waters"},
                {"name": "Coffee & Tea", "description": "Premium coffee beans and teas"}
            ],
            "Packaging & Disposables": [
                {"name": "Eco-Friendly", "description": "Sustainable and biodegradable options"},
                {"name": "Food Containers", "description": "Take-out and storage containers"},
                {"name": "Utensils", "description": "Disposable utensils and cutlery"},
                {"name": "Cleaning Supplies", "description": "Restaurant cleaning products"}
            ],
            "Equipment & Supplies": [
                {"name": "Kitchen Equipment", "description": "Commercial kitchen appliances"},
                {"name": "Tools & Utensils", "description": "Professional kitchen tools"},
                {"name": "Maintenance", "description": "Equipment maintenance and repair"},
                {"name": "Small Appliances", "description": "Countertop and small appliances"}
            ]
        }
        
        created_categories = []
        for vendor in vendors:
            vendor_category = vendor.vendor_profile.categories[0] if vendor.vendor_profile.categories else "General"
            
            # Add standard categories for all vendors
            for cat_data in standard_categories:
                category_id = await self.get_next_id("inventory_categories")
                category = InventoryCategory(
                    category_id=category_id,
                    vendor_id=vendor.user_id,
                    name=cat_data["name"],
                    description=cat_data["description"],
                    is_active=True,
                    sort_order=len(created_categories) + 1
                )
                await category.insert()
                created_categories.append(category)
            
            # Add category-specific items
            if vendor_category in category_specific:
                for cat_data in category_specific[vendor_category]:
                    category_id = await self.get_next_id("inventory_categories")
                    category = InventoryCategory(
                        category_id=category_id,
                        vendor_id=vendor.user_id,
                        name=cat_data["name"],
                        description=cat_data["description"],
                        is_active=True,
                        sort_order=len(created_categories) + 1
                    )
                    await category.insert()
                    created_categories.append(category)
        
        print(f"✅ Created {len(created_categories)} inventory categories")
        return created_categories

    async def seed_inventory_items_and_skus(self, vendors: List[User], categories: List[InventoryCategory]):
        """Seed inventory items and SKUs for each vendor"""
        print("📦 Seeding inventory items and SKUs...")
        
        # Product templates based on vendor categories
        product_templates = {
            "Fresh Produce": [
                {"name": "Organic Tomatoes", "unit": "lb", "base_price": 4.50, "description": "Fresh organic vine-ripened tomatoes"},
                {"name": "Baby Spinach", "unit": "lb", "base_price": 6.00, "description": "Tender baby spinach leaves"},
                {"name": "Red Bell Peppers", "unit": "lb", "base_price": 5.25, "description": "Sweet red bell peppers"},
                {"name": "Fresh Basil", "unit": "bunch", "base_price": 3.50, "description": "Aromatic fresh basil"},
                {"name": "Organic Carrots", "unit": "lb", "base_price": 2.75, "description": "Sweet organic carrots"},
                {"name": "Mixed Greens", "unit": "lb", "base_price": 7.50, "description": "Premium mixed salad greens"},
                {"name": "Yellow Onions", "unit": "lb", "base_price": 1.85, "description": "Fresh yellow cooking onions"},
                {"name": "Avocados", "unit": "each", "base_price": 2.25, "description": "Ripe Hass avocados"}
            ],
            "Meat & Seafood": [
                {"name": "Prime Ribeye Steak", "unit": "lb", "base_price": 28.50, "description": "Premium aged ribeye steaks"},
                {"name": "Fresh Salmon Fillet", "unit": "lb", "base_price": 24.00, "description": "Wild-caught salmon fillets"},
                {"name": "Organic Chicken Breast", "unit": "lb", "base_price": 12.50, "description": "Free-range chicken breast"},
                {"name": "Ground Beef 80/20", "unit": "lb", "base_price": 8.75, "description": "Fresh ground beef"},
                {"name": "Jumbo Shrimp", "unit": "lb", "base_price": 18.50, "description": "Large fresh shrimp"},
                {"name": "Pork Tenderloin", "unit": "lb", "base_price": 15.25, "description": "Lean pork tenderloin"},
                {"name": "Lamb Chops", "unit": "lb", "base_price": 22.00, "description": "Premium lamb chops"},
                {"name": "Fresh Scallops", "unit": "lb", "base_price": 32.00, "description": "Diver scallops"}
            ],
            "Dairy & Eggs": [
                {"name": "Aged Cheddar Cheese", "unit": "lb", "base_price": 12.50, "description": "Sharp aged cheddar"},
                {"name": "Fresh Mozzarella", "unit": "lb", "base_price": 8.75, "description": "House-made fresh mozzarella"},
                {"name": "Farm Fresh Eggs", "unit": "dozen", "base_price": 4.50, "description": "Free-range chicken eggs"},
                {"name": "Organic Butter", "unit": "lb", "base_price": 6.25, "description": "Unsalted organic butter"},
                {"name": "Heavy Cream", "unit": "quart", "base_price": 5.50, "description": "Rich heavy cream"},
                {"name": "Goat Cheese", "unit": "lb", "base_price": 14.00, "description": "Creamy goat cheese"},
                {"name": "Greek Yogurt", "unit": "quart", "base_price": 7.25, "description": "Thick Greek yogurt"},
                {"name": "Parmesan Cheese", "unit": "lb", "base_price": 18.50, "description": "Aged Parmigiano-Reggiano"}
            ],
            "Pantry & Dry Goods": [
                {"name": "All-Purpose Flour", "unit": "50lb bag", "base_price": 22.50, "description": "High-quality all-purpose flour"},
                {"name": "Basmati Rice", "unit": "25lb bag", "base_price": 35.00, "description": "Premium basmati rice"},
                {"name": "Sea Salt", "unit": "5lb container", "base_price": 12.00, "description": "Pure sea salt"},
                {"name": "Black Peppercorns", "unit": "lb", "base_price": 18.50, "description": "Whole black peppercorns"},
                {"name": "Extra Virgin Olive Oil", "unit": "gallon", "base_price": 45.00, "description": "Cold-pressed olive oil"},
                {"name": "Vanilla Extract", "unit": "16oz bottle", "base_price": 28.00, "description": "Pure vanilla extract"},
                {"name": "Balsamic Vinegar", "unit": "gallon", "base_price": 32.50, "description": "Aged balsamic vinegar"},
                {"name": "Quinoa", "unit": "25lb bag", "base_price": 85.00, "description": "Organic quinoa"}
            ],
            "Beverages": [
                {"name": "Craft Root Beer", "unit": "case", "base_price": 24.50, "description": "Artisanal root beer"},
                {"name": "Sparkling Water", "unit": "case", "base_price": 18.00, "description": "Premium sparkling water"},
                {"name": "Local IPA", "unit": "case", "base_price": 42.00, "description": "Local craft IPA"},
                {"name": "Organic Coffee Beans", "unit": "5lb bag", "base_price": 65.00, "description": "Single-origin coffee beans"},
                {"name": "Herbal Tea Blend", "unit": "lb", "base_price": 28.50, "description": "Premium herbal tea"},
                {"name": "Fresh Orange Juice", "unit": "gallon", "base_price": 12.50, "description": "Fresh-squeezed orange juice"},
                {"name": "Kombucha", "unit": "case", "base_price": 36.00, "description": "Probiotic kombucha"},
                {"name": "Wine Selection", "unit": "bottle", "base_price": 25.00, "description": "Curated wine selection"}
            ],
            "Packaging & Disposables": [
                {"name": "Eco Food Containers", "unit": "case", "base_price": 45.00, "description": "Biodegradable food containers"},
                {"name": "Compostable Utensils", "unit": "case", "base_price": 32.50, "description": "Compostable cutlery set"},
                {"name": "Paper Napkins", "unit": "case", "base_price": 28.00, "description": "Recycled paper napkins"},
                {"name": "Take-out Bags", "unit": "case", "base_price": 22.50, "description": "Kraft paper take-out bags"},
                {"name": "Food Storage Bags", "unit": "case", "base_price": 35.00, "description": "Food-grade storage bags"},
                {"name": "Cleaning Wipes", "unit": "case", "base_price": 42.00, "description": "Sanitizing cleaning wipes"},
                {"name": "Disposable Gloves", "unit": "case", "base_price": 38.50, "description": "Food-safe disposable gloves"},
                {"name": "Paper Towels", "unit": "case", "base_price": 45.00, "description": "Heavy-duty paper towels"}
            ],
            "Equipment & Supplies": [
                {"name": "Chef's Knife Set", "unit": "set", "base_price": 285.00, "description": "Professional chef knife set"},
                {"name": "Cutting Boards", "unit": "set", "base_price": 125.00, "description": "Commercial cutting boards"},
                {"name": "Mixing Bowls", "unit": "set", "base_price": 85.00, "description": "Stainless steel mixing bowls"},
                {"name": "Kitchen Thermometer", "unit": "each", "base_price": 45.00, "description": "Digital kitchen thermometer"},
                {"name": "Food Processor", "unit": "each", "base_price": 450.00, "description": "Commercial food processor"},
                {"name": "Stand Mixer", "unit": "each", "base_price": 650.00, "description": "Heavy-duty stand mixer"},
                {"name": "Blender", "unit": "each", "base_price": 325.00, "description": "High-performance blender"},
                {"name": "Kitchen Scale", "unit": "each", "base_price": 125.00, "description": "Digital kitchen scale"}
            ]
        }
        
        created_items = []
        created_skus = []
        
        for vendor in vendors:
            vendor_category = vendor.vendor_profile.categories[0] if vendor.vendor_profile.categories else "General"
            vendor_categories = [cat for cat in categories if cat.vendor_id == vendor.user_id]
            
            if vendor_category in product_templates:
                products = product_templates[vendor_category]
                
                for product_data in products:
                    # Create inventory item
                    item_id = await self.get_next_id("inventory_items")
                    category = random.choice(vendor_categories) if vendor_categories else None
                    
                    item = InventoryItem(
                        item_id=item_id,
                        vendor_id=vendor.user_id,
                        category_id=category.category_id if category else None,
                        name=product_data["name"],
                        description=product_data["description"],
                        unit_of_measure=product_data["unit"],
                        base_price=product_data["base_price"],
                        cost_price=product_data["base_price"] * 0.7,  # 30% markup
                        is_active=True,
                        is_featured=random.choice([True, False]),
                        minimum_order_quantity=1,
                        lead_time_days=random.randint(1, 3),
                        tags=[vendor_category.lower().replace(" & ", "_").replace(" ", "_")],
                        track_inventory=True,
                        current_stock=random.randint(50, 500),
                        low_stock_threshold=random.randint(10, 50)
                    )
                    await item.insert()
                    created_items.append(item)
                    
                    # Create 1-3 SKUs per item
                    num_skus = random.randint(1, 3)
                    for i in range(num_skus):
                        sku_id = await self.get_next_id("inventory_skus")
                        
                        # Generate variant attributes
                        variant_name = None
                        attributes = {}
                        price_modifier = 1.0
                        
                        if num_skus > 1:
                            if i == 0:
                                variant_name = "Standard"
                                attributes = {"size": "standard"}
                            elif i == 1:
                                variant_name = "Large"
                                attributes = {"size": "large"}
                                price_modifier = 1.2
                            else:
                                variant_name = "Bulk"
                                attributes = {"size": "bulk"}
                                price_modifier = 0.9
                        
                        sku = InventorySKU(
                            sku_id=sku_id,
                            vendor_id=vendor.user_id,
                            item_id=item.item_id,
                            sku_code=f"{vendor.username.upper()}-{item.item_id:04d}-{i+1:02d}",
                            variant_name=variant_name,
                            attributes=attributes,
                            price=round(product_data["base_price"] * price_modifier, 2),
                            cost_price=round(product_data["base_price"] * 0.7 * price_modifier, 2),
                            current_stock=random.randint(20, 200),
                            low_stock_threshold=random.randint(5, 25),
                            is_active=True,
                            is_default=(i == 0)
                        )
                        await sku.insert()
                        created_skus.append(sku)
        
        print(f"✅ Created {len(created_items)} inventory items and {len(created_skus)} SKUs")
        return created_items, created_skus

    async def seed_storefronts_and_products(self, vendors: List[User], items: List[InventoryItem]):
        """Seed vendor storefronts and products"""
        print("🏪 Seeding vendor storefronts and products...")
        
        created_storefronts = []
        created_product_categories = []
        created_products = []
        
        for vendor in vendors:
            # Create vendor storefront
            storefront = VendorStorefront(
                vendor_id=vendor.user_id,
                logo_url=f"https://example.com/logos/{vendor.username}.png",
                hero_image_url=f"https://example.com/heroes/{vendor.username}.jpg",
                brand_colors={
                    "primary": random.choice(["#2563eb", "#dc2626", "#059669", "#7c3aed", "#ea580c"]),
                    "secondary": "#6b7280"
                },
                layout_template="default",
                tagline=f"Quality {vendor.vendor_profile.categories[0]} since {vendor.vendor_profile.established_year}",
                welcome_message=f"Welcome to {vendor.name}! {vendor.description}",
                is_active=True
            )
            await storefront.insert()
            created_storefronts.append(storefront)
            
            # Create product categories for storefront
            vendor_items = [item for item in items if item.vendor_id == vendor.user_id]
            unique_categories = list(set([item.name.split()[0] for item in vendor_items[:5]]))  # First word as category
            
            for i, cat_name in enumerate(unique_categories):
                category_id = await self.get_next_id("product_categories")
                product_category = ProductCategory(
                    category_id=category_id,
                    vendor_id=vendor.user_id,
                    name=f"{cat_name} Products",
                    description=f"Our selection of {cat_name.lower()} products",
                    sort_order=i + 1,
                    is_active=True
                )
                await product_category.insert()
                created_product_categories.append(product_category)
            
            # Create vendor products from inventory items
            for item in vendor_items:
                product_id = await self.get_next_id("vendor_products")
                
                # Find matching product category
                matching_category = None
                for cat in created_product_categories:
                    if cat.vendor_id == vendor.user_id and item.name.split()[0] in cat.name:
                        matching_category = cat
                        break
                
                product = VendorProduct(
                    product_id=product_id,
                    vendor_id=vendor.user_id,
                    name=item.name,
                    description=item.description,
                    detailed_description=f"{item.description}. {random.choice(['Perfect for restaurants.', 'High quality guaranteed.', 'Fresh daily delivery.', 'Bulk pricing available.'])}",
                    sku=f"STORE-{item.item_id:04d}",
                    category_id=matching_category.category_id if matching_category else None,
                    price=item.base_price,
                    unit=item.unit_of_measure,
                    images=[f"https://example.com/products/{item.item_id}.jpg"],
                    is_featured=item.is_featured,
                    is_active=item.is_active,
                    stock_status="in_stock" if item.current_stock and item.current_stock > 0 else "out_of_stock",
                    minimum_quantity=item.minimum_order_quantity
                )
                await product.insert()
                created_products.append(product)
        
        print(f"✅ Created {len(created_storefronts)} storefronts, {len(created_product_categories)} product categories, and {len(created_products)} products")
        return created_storefronts, created_product_categories, created_products

    async def run_seeding(self):
        """Run the complete seeding process"""
        try:
            print("🚀 Starting comprehensive inventory data seeding...")
            print(f"📅 Seeding started at: {datetime.utcnow()}")
            
            # Connect to MongoDB
            await connect_to_mongo()
            
            # Analyze existing data instead of clearing
            print("\n" + "="*60)
            existing_data = await self.analyze_existing_data()
            
            # Check if we need to add vendors
            existing_vendor_usernames = [v.username for v in existing_data['existing_vendors']]
            vendors_to_create = []
            
            # Comprehensive vendor data from populate_demo_data.py
            vendors_data = [
                # Fresh Produce
                {
                    'username': 'fresh_valley_farms', 'password': 'demo123', 'name': 'Fresh Valley Farms',
                    'email': 'orders@freshvalleyfarms.com', 'phone': '555-0101',
                    'address': '1234 Farm Road, Valley Springs, CA 95252',
                    'description': 'Premium organic produce supplier with 30+ years of experience',
                    'business_type': 'Organic Farm', 'specialties': ['Organic Vegetables', 'Seasonal Fruits', 'Herbs'],
                    'category': 'Fresh Produce', 'status': 'active'
                },
                {
                    'username': 'golden_harvest_co', 'password': 'demo123', 'name': 'Golden Harvest Co.',
                    'email': 'sales@goldenharvest.com', 'phone': '555-0102',
                    'address': '5678 Orchard Lane, Fresno, CA 93720',
                    'description': 'Year-round fresh produce with same-day delivery',
                    'business_type': 'Produce Distributor', 'specialties': ['Citrus Fruits', 'Root Vegetables', 'Leafy Greens'],
                    'category': 'Fresh Produce', 'status': 'active'
                },
                {
                    'username': 'mountain_greens', 'password': 'demo123', 'name': 'Mountain Greens',
                    'email': 'info@mountaingreens.com', 'phone': '555-0103',
                    'address': '9012 Highland Ave, Sacramento, CA 95814',
                    'description': 'Locally sourced mountain-grown vegetables and herbs',
                    'business_type': 'Local Farm', 'specialties': ['Mountain Vegetables', 'Wild Herbs', 'Microgreens'],
                    'category': 'Fresh Produce', 'status': 'active'
                },
                
                # Meat & Seafood
                {
                    'username': 'prime_cuts_wholesale', 'password': 'demo123', 'name': 'Prime Cuts Wholesale',
                    'email': 'orders@primecuts.com', 'phone': '555-0201',
                    'address': '3456 Butcher Block Blvd, San Francisco, CA 94102',
                    'description': 'Premium aged beef and specialty cuts for fine dining',
                    'business_type': 'Meat Processor', 'specialties': ['Aged Beef', 'Wagyu', 'Specialty Cuts'],
                    'category': 'Meat & Seafood', 'status': 'active'
                },
                {
                    'username': 'ocean_fresh_seafood', 'password': 'demo123', 'name': 'Ocean Fresh Seafood',
                    'email': 'sales@oceanfresh.com', 'phone': '555-0202',
                    'address': '7890 Fisherman\'s Wharf, Monterey, CA 93940',
                    'description': 'Daily fresh catch from local fishing boats',
                    'business_type': 'Seafood Distributor', 'specialties': ['Daily Fresh Fish', 'Shellfish', 'Sustainable Seafood'],
                    'category': 'Meat & Seafood', 'status': 'active'
                },
                {
                    'username': 'heritage_meats', 'password': 'demo123', 'name': 'Heritage Meats',
                    'email': 'contact@heritagemeats.com', 'phone': '555-0203',
                    'address': '2345 Ranch Road, Paso Robles, CA 93446',
                    'description': 'Grass-fed, heritage breed meats and poultry',
                    'business_type': 'Ranch', 'specialties': ['Grass-Fed Beef', 'Heritage Pork', 'Free-Range Poultry'],
                    'category': 'Meat & Seafood', 'status': 'active'
                },
                
                # Dairy & Eggs
                {
                    'username': 'sunrise_dairy', 'password': 'demo123', 'name': 'Sunrise Dairy',
                    'email': 'orders@sunrisedairy.com', 'phone': '555-0301',
                    'address': '4567 Dairy Lane, Petaluma, CA 94952',
                    'description': 'Artisanal cheeses and fresh dairy products',
                    'business_type': 'Dairy Farm', 'specialties': ['Artisan Cheese', 'Fresh Milk', 'Organic Butter'],
                    'category': 'Dairy & Eggs', 'status': 'active'
                },
                {
                    'username': 'farm_fresh_eggs', 'password': 'demo123', 'name': 'Farm Fresh Eggs Co.',
                    'email': 'info@farmfresheggs.com', 'phone': '555-0302',
                    'address': '6789 Henhouse Road, Sonoma, CA 95476',
                    'description': 'Cage-free and pasture-raised eggs from happy hens',
                    'business_type': 'Poultry Farm', 'specialties': ['Pasture-Raised Eggs', 'Duck Eggs', 'Quail Eggs'],
                    'category': 'Dairy & Eggs', 'status': 'active'
                },
                
                # Pantry & Dry Goods
                {
                    'username': 'golden_grain_supply', 'password': 'demo123', 'name': 'Golden Grain Supply',
                    'email': 'sales@goldengrain.com', 'phone': '555-0401',
                    'address': '8901 Grain Silo Way, Stockton, CA 95202',
                    'description': 'Bulk grains, flours, and specialty baking ingredients',
                    'business_type': 'Grain Distributor', 'specialties': ['Organic Flours', 'Ancient Grains', 'Specialty Rice'],
                    'category': 'Pantry & Dry Goods', 'status': 'active'
                },
                {
                    'username': 'spice_world_imports', 'password': 'demo123', 'name': 'Spice World Imports',
                    'email': 'orders@spiceworld.com', 'phone': '555-0402',
                    'address': '1357 Spice Market St, Oakland, CA 94607',
                    'description': 'Global spices, seasonings, and specialty condiments',
                    'business_type': 'Spice Importer', 'specialties': ['International Spices', 'Rare Seasonings', 'Specialty Salts'],
                    'category': 'Pantry & Dry Goods', 'status': 'active'
                },
                
                # Beverages
                {
                    'username': 'craft_beverage_co', 'password': 'demo123', 'name': 'Craft Beverage Co.',
                    'email': 'sales@craftbeverage.com', 'phone': '555-0501',
                    'address': '2468 Brewery Lane, San Diego, CA 92101',
                    'description': 'Craft sodas, specialty waters, and artisanal beverages',
                    'business_type': 'Beverage Distributor', 'specialties': ['Craft Sodas', 'Specialty Waters', 'Kombucha'],
                    'category': 'Beverages', 'status': 'active'
                },
                {
                    'username': 'wine_country_supply', 'password': 'demo123', 'name': 'Wine Country Supply',
                    'email': 'info@winecountrysupply.com', 'phone': '555-0502',
                    'address': '3579 Vineyard Road, Napa, CA 94558',
                    'description': 'Premium wines and specialty beverages for restaurants',
                    'business_type': 'Wine Distributor', 'specialties': ['Local Wines', 'Craft Beer', 'Specialty Cocktail Mixers'],
                    'category': 'Beverages', 'status': 'active'
                },
                
                # Packaging & Disposables
                {
                    'username': 'eco_pack_solutions', 'password': 'demo123', 'name': 'EcoPack Solutions',
                    'email': 'orders@ecopack.com', 'phone': '555-0601',
                    'address': '4680 Green Way, Berkeley, CA 94710',
                    'description': 'Sustainable packaging and eco-friendly disposables',
                    'business_type': 'Packaging Supplier', 'specialties': ['Biodegradable Containers', 'Compostable Utensils', 'Recycled Paper Products'],
                    'category': 'Packaging & Disposables', 'status': 'active'
                },
                {
                    'username': 'restaurant_supply_pro', 'password': 'demo123', 'name': 'Restaurant Supply Pro',
                    'email': 'sales@restaurantsupplypro.com', 'phone': '555-0602',
                    'address': '5791 Industrial Blvd, Los Angeles, CA 90021',
                    'description': 'Complete restaurant packaging and disposable solutions',
                    'business_type': 'Restaurant Supplier', 'specialties': ['Take-out Containers', 'Food Service Disposables', 'Cleaning Supplies'],
                    'category': 'Packaging & Disposables', 'status': 'active'
                },
                
                # Equipment & Supplies
                {
                    'username': 'kitchen_pro_equipment', 'password': 'demo123', 'name': 'Kitchen Pro Equipment',
                    'email': 'info@kitchenpro.com', 'phone': '555-0701',
                    'address': '6802 Equipment Row, San Jose, CA 95110',
                    'description': 'Professional kitchen equipment and maintenance services',
                    'business_type': 'Equipment Supplier', 'specialties': ['Commercial Ovens', 'Refrigeration', 'Kitchen Tools'],
                    'category': 'Equipment & Supplies', 'status': 'active'
                },
                {
                    'username': 'culinary_tools_plus', 'password': 'demo123', 'name': 'Culinary Tools Plus',
                    'email': 'orders@culinarytools.com', 'phone': '555-0702',
                    'address': '7913 Chef\'s Avenue, Santa Clara, CA 95050',
                    'description': 'Professional culinary tools and kitchen accessories',
                    'business_type': 'Tool Supplier', 'specialties': ['Chef Knives', 'Cookware', 'Kitchen Gadgets'],
                    'category': 'Equipment & Supplies', 'status': 'active'
                }
            ]
            
            # Filter out vendors that already exist
            for vendor_data in vendors_data:
                if vendor_data['username'] not in existing_vendor_usernames:
                    vendors_to_create.append(vendor_data)
            
            print(f"📋 Found {len(vendors_to_create)} new vendors to create out of {len(vendors_data)} total")
            
            # Create new vendors
            new_vendors = []
            if vendors_to_create:
                print("\n" + "="*60)
                new_vendors = await self.seed_new_vendors(vendors_to_create)
            
            # Get all vendors (existing + new)
            all_vendors = existing_data['existing_vendors'] + new_vendors
            
            # Run seeding for vendors that need inventory data
            vendors_needing_inventory = []
            for vendor in all_vendors:
                # Check if vendor already has inventory items
                existing_items = await InventoryItem.find({"vendor_id": vendor.user_id}).to_list()
                if not existing_items:
                    vendors_needing_inventory.append(vendor)
            
            print(f"📦 Found {len(vendors_needing_inventory)} vendors needing inventory data")
            
            if vendors_needing_inventory:
                print("\n" + "="*60)
                categories = await self.seed_inventory_categories(vendors_needing_inventory)
                
                print("\n" + "="*60)
                items, skus = await self.seed_inventory_items_and_skus(vendors_needing_inventory, categories)
                
                print("\n" + "="*60)
                storefronts, product_categories, products = await self.seed_storefronts_and_products(vendors_needing_inventory, items)
            else:
                categories = []
                items = []
                skus = []
                storefronts = []
                product_categories = []
                products = []
            
            # Final summary
            print("\n" + "="*60)
            print("🎉 INVENTORY SEEDING COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"📊 Final summary:")
            print(f"   - Total Vendors: {len(all_vendors)} (New: {len(new_vendors)})")
            print(f"   - New Inventory Categories: {len(categories)}")
            print(f"   - New Inventory Items: {len(items)}")
            print(f"   - New SKUs: {len(skus)}")
            print(f"   - New Storefronts: {len(storefronts)}")
            print(f"   - New Product Categories: {len(product_categories)}")
            print(f"   - New Storefront Products: {len(products)}")
            print(f"📅 Completed at: {datetime.utcnow()}")
            
            if new_vendors:
                print("\n🔑 New Vendor Login Credentials:")
                for vendor in new_vendors[:5]:  # Show first 5 new vendors
                    print(f"   {vendor.name}: username='{vendor.username}', password='demo123'")
            
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await close_mongo_connection()

    async def seed_new_vendors(self, vendors_to_create):
        """Seed only new vendors that don't already exist"""
        print(f"👥 Seeding {len(vendors_to_create)} new vendors...")
        
        created_vendors = []
        for vendor_data in vendors_to_create:
            user_id = await self.get_next_id("users")
            
            # Create vendor profile
            vendor_profile = VendorProfile(
                business_type=vendor_data['business_type'],
                specialties=vendor_data['specialties'],
                average_rating=round(random.uniform(4.0, 5.0), 1),
                review_count=random.randint(15, 150),
                is_active=vendor_data['status'] == 'active',
                business_hours="Monday-Friday: 6:00 AM - 6:00 PM, Saturday: 8:00 AM - 4:00 PM",
                delivery_areas="San Francisco Bay Area, Peninsula, East Bay",
                minimum_order=round(random.uniform(50.0, 200.0), 2),
                payment_terms="Net 30 days, Credit cards accepted",
                certifications=["Food Safety Certified", "Business License"],
                business_description=vendor_data['description'],
                established_year=str(random.randint(1990, 2020)),
                categories=[vendor_data['category']]
            )
            
            # Create user with embedded vendor profile
            user = User(
                user_id=user_id,
                username=vendor_data['username'],
                password_hash=get_password_hash(vendor_data['password']),
                role="vendor",
                name=vendor_data['name'],
                email=vendor_data['email'],
                phone=vendor_data['phone'],
                address=vendor_data['address'],
                description=vendor_data['description'],
                is_active=vendor_data['status'] == 'active',
                status=vendor_data['status'],
                vendor_profile=vendor_profile,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                updated_at=datetime.utcnow()
            )
            
            await user.insert()
            created_vendors.append(user)
            
        print(f"✅ Created {len(created_vendors)} new vendors")
        return created_vendors

async def main():
    """Main function to run seeding"""
    seeder = InventorySeeder()
    await seeder.run_seeding()

if __name__ == "__main__":
    print("BistroBoard Comprehensive Inventory Data Seeding")
    print("=" * 60)
    asyncio.run(main())