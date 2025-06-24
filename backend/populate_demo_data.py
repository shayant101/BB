"""
Comprehensive Demo Data Population Script
Creates realistic vendors, restaurants, and orders for testing the Admin Command Center
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
import random
import json

def get_password_hash(password):
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def populate_comprehensive_data():
    """Populate the database with comprehensive demo data"""
    
    # Connect to database
    conn = sqlite3.connect('bistroboard.db')
    cursor = conn.cursor()
    
    print("🚀 Starting comprehensive data population...")
    
    try:
        # VENDORS DATA - Covering all major categories
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
                'category': 'Fresh Produce', 'status': 'pending_approval'
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
                'category': 'Beverages', 'status': 'pending_approval'
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
                'category': 'Equipment & Supplies', 'status': 'pending_approval'
            }
        ]
        
        # RESTAURANTS DATA - Covering major cuisines and types
        restaurants_data = [
            {
                'username': 'bella_italia', 'password': 'demo123', 'name': 'Bella Italia Ristorante',
                'email': 'orders@bellaitalia.com', 'phone': '555-1001',
                'address': '123 Little Italy St, San Francisco, CA 94133',
                'description': 'Authentic Italian cuisine with traditional recipes',
                'cuisine': 'Italian', 'type': 'Fine Dining'
            },
            {
                'username': 'sakura_sushi', 'password': 'demo123', 'name': 'Sakura Sushi Bar',
                'email': 'info@sakurasushi.com', 'phone': '555-1002',
                'address': '456 Japantown Blvd, San Francisco, CA 94115',
                'description': 'Fresh sushi and traditional Japanese dishes',
                'cuisine': 'Japanese', 'type': 'Casual Dining'
            },
            {
                'username': 'le_petit_bistro', 'password': 'demo123', 'name': 'Le Petit Bistro',
                'email': 'reservations@lepetitbistro.com', 'phone': '555-1003',
                'address': '789 French Quarter Ave, San Francisco, CA 94102',
                'description': 'Classic French bistro with seasonal menu',
                'cuisine': 'French', 'type': 'Fine Dining'
            },
            {
                'username': 'spice_route_indian', 'password': 'demo123', 'name': 'Spice Route Indian Kitchen',
                'email': 'orders@spiceroute.com', 'phone': '555-1004',
                'address': '321 Curry Lane, Oakland, CA 94607',
                'description': 'Authentic Indian spices and traditional curries',
                'cuisine': 'Indian', 'type': 'Casual Dining'
            },
            {
                'username': 'dragon_palace', 'password': 'demo123', 'name': 'Dragon Palace Chinese',
                'email': 'info@dragonpalace.com', 'phone': '555-1005',
                'address': '654 Chinatown Way, San Francisco, CA 94108',
                'description': 'Traditional Cantonese cuisine and dim sum',
                'cuisine': 'Chinese', 'type': 'Family Restaurant'
            },
            {
                'username': 'casa_mexico', 'password': 'demo123', 'name': 'Casa Mexico Cantina',
                'email': 'orders@casamexico.com', 'phone': '555-1006',
                'address': '987 Mission District St, San Francisco, CA 94110',
                'description': 'Vibrant Mexican flavors and fresh ingredients',
                'cuisine': 'Mexican', 'type': 'Casual Dining'
            },
            {
                'username': 'athens_taverna', 'password': 'demo123', 'name': 'Athens Taverna',
                'email': 'info@athenstaverna.com', 'phone': '555-1007',
                'address': '147 Greek Town Rd, San Francisco, CA 94134',
                'description': 'Mediterranean cuisine with fresh seafood',
                'cuisine': 'Greek', 'type': 'Casual Dining'
            },
            {
                'username': 'thai_garden', 'password': 'demo123', 'name': 'Thai Garden Restaurant',
                'email': 'orders@thaigarden.com', 'phone': '555-1008',
                'address': '258 Spice Street, Berkeley, CA 94704',
                'description': 'Authentic Thai cuisine with fresh herbs',
                'cuisine': 'Thai', 'type': 'Casual Dining'
            },
            {
                'username': 'steakhouse_prime', 'password': 'demo123', 'name': 'Prime Steakhouse',
                'email': 'reservations@primesteakhouse.com', 'phone': '555-1009',
                'address': '369 Beef Boulevard, San Francisco, CA 94104',
                'description': 'Premium steaks and fine dining experience',
                'cuisine': 'American', 'type': 'Fine Dining'
            },
            {
                'username': 'coastal_seafood', 'password': 'demo123', 'name': 'Coastal Seafood Grill',
                'email': 'info@coastalseafood.com', 'phone': '555-1010',
                'address': '741 Pier View Dr, Monterey, CA 93940',
                'description': 'Fresh seafood with ocean views',
                'cuisine': 'Seafood', 'type': 'Casual Dining'
            },
            {
                'username': 'farm_table', 'password': 'demo123', 'name': 'Farm Table Restaurant',
                'email': 'orders@farmtable.com', 'phone': '555-1011',
                'address': '852 Organic Way, Palo Alto, CA 94301',
                'description': 'Farm-to-table dining with seasonal ingredients',
                'cuisine': 'American', 'type': 'Farm-to-Table'
            },
            {
                'username': 'pizza_corner', 'password': 'demo123', 'name': 'Pizza Corner',
                'email': 'orders@pizzacorner.com', 'phone': '555-1012',
                'address': '963 Slice Street, San Jose, CA 95110',
                'description': 'New York style pizza and Italian classics',
                'cuisine': 'Italian', 'type': 'Casual Dining'
            },
            {
                'username': 'burger_barn', 'password': 'demo123', 'name': 'The Burger Barn',
                'email': 'info@burgerbarn.com', 'phone': '555-1013',
                'address': '159 Grill Avenue, Sacramento, CA 95814',
                'description': 'Gourmet burgers with local ingredients',
                'cuisine': 'American', 'type': 'Fast Casual'
            },
            {
                'username': 'noodle_house', 'password': 'demo123', 'name': 'Golden Noodle House',
                'email': 'orders@noodlehouse.com', 'phone': '555-1014',
                'address': '357 Ramen Row, San Francisco, CA 94103',
                'description': 'Authentic ramen and Asian noodle dishes',
                'cuisine': 'Asian', 'type': 'Fast Casual'
            },
            {
                'username': 'cafe_europa', 'password': 'demo123', 'name': 'Cafe Europa',
                'email': 'info@cafeeuropa.com', 'phone': '555-1015',
                'address': '468 Coffee Lane, San Francisco, CA 94117',
                'description': 'European-style cafe with pastries and light meals',
                'cuisine': 'European', 'type': 'Cafe'
            }
        ]
        
        # Insert vendors
        print("📦 Adding vendors...")
        vendor_ids = []
        for i, vendor in enumerate(vendors_data):
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, name, email, phone, address, description, 
                                 is_active, status, created_at, updated_at)
                VALUES (?, ?, 'vendor', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vendor['username'], get_password_hash(vendor['password']), vendor['name'],
                vendor['email'], vendor['phone'], vendor['address'], vendor['description'],
                vendor['status'] == 'active', vendor['status'],
                datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                datetime.utcnow()
            ))
            vendor_id = cursor.lastrowid
            vendor_ids.append(vendor_id)
            
            # Create vendor profile
            cursor.execute("""
                INSERT INTO vendor_profiles (user_id, business_type, specialties, average_rating, 
                                           review_count, is_active, business_hours, delivery_areas,
                                           minimum_order, payment_terms, business_description,
                                           established_year, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vendor_id, vendor['business_type'], json.dumps(vendor['specialties']),
                round(random.uniform(4.0, 5.0), 1), random.randint(15, 150),
                vendor['status'] == 'active',
                "Monday-Friday: 6:00 AM - 6:00 PM, Saturday: 8:00 AM - 4:00 PM",
                "San Francisco Bay Area, Peninsula, East Bay",
                round(random.uniform(50.0, 200.0), 2),
                "Net 30 days, Credit cards accepted",
                vendor['description'],
                str(random.randint(1990, 2020)),
                datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                datetime.utcnow()
            ))
        
        # Insert restaurants
        print("🍽️ Adding restaurants...")
        restaurant_ids = []
        for restaurant in restaurants_data:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, name, email, phone, address, description,
                                 is_active, status, created_at, updated_at, last_login_at)
                VALUES (?, ?, 'restaurant', ?, ?, ?, ?, ?, 1, 'active', ?, ?, ?)
            """, (
                restaurant['username'], get_password_hash(restaurant['password']), restaurant['name'],
                restaurant['email'], restaurant['phone'], restaurant['address'], restaurant['description'],
                datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                datetime.utcnow(),
                datetime.utcnow() - timedelta(days=random.randint(0, 7))
            ))
            restaurant_ids.append(cursor.lastrowid)
        
        # Create diverse orders in different stages
        print("📋 Creating orders in various stages...")
        order_statuses = ['pending', 'confirmed', 'fulfilled']
        order_items = [
            "10 lbs organic tomatoes, 5 lbs red onions, 3 bunches fresh basil",
            "2 cases premium olive oil, 5 lbs sea salt, 1 case balsamic vinegar",
            "20 lbs fresh salmon fillets, 10 lbs prawns, 5 lbs scallops",
            "50 lbs all-purpose flour, 25 lbs bread flour, 10 lbs semolina",
            "1 case aged cheddar, 2 lbs fresh mozzarella, 1 lb parmesan",
            "5 lbs ground beef, 3 lbs chicken breast, 2 lbs lamb chops",
            "100 eco-friendly takeout containers, 200 compostable utensils",
            "2 cases craft beer, 1 case local wine, 50 specialty cocktail mixers",
            "15 lbs jasmine rice, 10 lbs black beans, 5 lbs quinoa",
            "3 lbs mixed spices, 2 lbs curry powder, 1 lb saffron",
            "20 dozen farm-fresh eggs, 5 lbs organic butter, 2 gallons heavy cream",
            "10 lbs fresh pasta, 5 lbs dried pasta, 3 lbs gnocchi",
            "1 case sparkling water, 2 cases orange juice, 50 coffee beans",
            "25 lbs potatoes, 15 lbs carrots, 10 lbs celery",
            "5 lbs fresh herbs mix, 3 lbs microgreens, 2 lbs edible flowers"
        ]
        
        # Create orders with realistic timing
        for i in range(45):  # Create 45 orders
            restaurant_id = random.choice(restaurant_ids)
            vendor_id = random.choice([vid for vid in vendor_ids if random.random() > 0.1])  # Avoid some vendors
            status = random.choices(order_statuses, weights=[30, 50, 20])[0]  # More confirmed orders
            
            # Create orders with different ages
            if status == 'pending':
                # Some pending orders should be old (stuck orders)
                if random.random() < 0.3:  # 30% chance of stuck order
                    created_time = datetime.utcnow() - timedelta(hours=random.randint(49, 120))
                else:
                    created_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            elif status == 'confirmed':
                created_time = datetime.utcnow() - timedelta(hours=random.randint(6, 72))
            else:  # fulfilled
                created_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            cursor.execute("""
                INSERT INTO orders (restaurant_id, vendor_id, items_text, status, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                restaurant_id, vendor_id, random.choice(order_items), status,
                f"Order for {status} delivery" if random.random() > 0.5 else None,
                created_time, created_time + timedelta(minutes=random.randint(0, 60))
            ))
        
        # Add some user events for realistic activity
        print("📊 Adding user activity events...")
        event_types = ['login', 'profile_updated', 'order_created', 'password_reset']
        for _ in range(100):  # 100 user events
            user_id = random.choice(restaurant_ids + vendor_ids)
            event_type = random.choice(event_types)
            
            cursor.execute("""
                INSERT INTO user_event_logs (user_id, event_type, details, ip_address, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id, event_type, 
                json.dumps({"action": event_type, "success": True}),
                f"192.168.1.{random.randint(1, 254)}",
                datetime.utcnow() - timedelta(days=random.randint(0, 30))
            ))
        
        conn.commit()
        print("✅ Demo data population completed successfully!")
        print(f"📊 Added:")
        print(f"   - {len(vendors_data)} vendors across all categories")
        print(f"   - {len(restaurants_data)} restaurants with diverse cuisines")
        print(f"   - 45 orders in various stages")
        print(f"   - 100 user activity events")
        print(f"   - Realistic timestamps and data relationships")
        
    except Exception as e:
        print(f"❌ Error during data population: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    populate_comprehensive_data()