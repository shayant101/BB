"""
BistroBoard SQLite to MongoDB Atlas Migration Script
Preserves all existing data while transforming to MongoDB document structure
"""

import asyncio
import sqlite3
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import InsertOne
import json
import sys
import os

# Add the app directory to the path so we can import our models
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.mongodb import MONGODB_URL
from app.mongo_models import (
    User, Order, VendorCategory, AdminAuditLog, 
    UserEventLog, ImpersonationSession, VendorProfile,
    RestaurantInfo, VendorInfo
)

class BistroboardMigration:
    def __init__(self):
        self.sqlite_conn = None
        self.mongo_client = None
        self.mongo_db = None
        self.migration_log = []
        self.errors = []
    
    async def setup_connections(self):
        """Initialize database connections"""
        try:
            # SQLite connection
            self.sqlite_conn = sqlite3.connect('bistroboard.db')
            self.sqlite_conn.row_factory = sqlite3.Row
            print("✅ Connected to SQLite database")
            
            # MongoDB connection
            self.mongo_client = AsyncIOMotorClient(MONGODB_URL)
            self.mongo_db = self.mongo_client.bistroboard
            
            # Test MongoDB connection
            await self.mongo_client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas")
            
        except Exception as e:
            print(f"❌ Failed to setup connections: {e}")
            raise
    
    def parse_datetime(self, dt_string):
        """Parse datetime string from SQLite"""
        if not dt_string:
            return None
        try:
            # Handle different datetime formats
            if '.' in dt_string:
                return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            else:
                return datetime.fromisoformat(dt_string)
        except Exception as e:
            print(f"Warning: Could not parse datetime '{dt_string}': {e}")
            return datetime.utcnow()
    
    def parse_json_field(self, json_string):
        """Parse JSON field from SQLite"""
        if not json_string:
            return []
        try:
            return json.loads(json_string)
        except Exception as e:
            print(f"Warning: Could not parse JSON '{json_string}': {e}")
            return []
    
    async def migrate_vendor_categories(self):
        """Migrate vendor categories first (referenced by users)"""
        print("📦 Migrating vendor categories...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT * FROM vendor_categories")
        categories = cursor.fetchall()
        
        if not categories:
            print("ℹ️ No vendor categories found to migrate")
            return
        
        mongo_categories = []
        for cat in categories:
            mongo_doc = {
                "category_id": cat["id"],
                "name": cat["name"],
                "description": cat["description"],
                "icon": cat["icon"],
                "parent_category": cat["parent_category"],
                "sort_order": cat["sort_order"] or 0,
                "is_active": bool(cat["is_active"]),
                "created_at": self.parse_datetime(cat["created_at"])
            }
            mongo_categories.append(InsertOne(mongo_doc))
        
        if mongo_categories:
            result = await self.mongo_db.vendor_categories.bulk_write(mongo_categories)
            self.log_migration("vendor_categories", result.inserted_count)
    
    async def migrate_users_with_profiles(self):
        """Migrate users with embedded vendor profiles"""
        print("👥 Migrating users with vendor profiles...")
        
        cursor = self.sqlite_conn.cursor()
        
        # Get all users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("ℹ️ No users found to migrate")
            return
        
        # Get vendor profiles
        cursor.execute("SELECT * FROM vendor_profiles")
        vendor_profiles = {vp["user_id"]: vp for vp in cursor.fetchall()}
        
        # Get vendor category mappings
        cursor.execute("""
            SELECT vcm.vendor_profile_id, vc.name 
            FROM vendor_category_mappings vcm
            JOIN vendor_categories vc ON vcm.category_id = vc.id
        """)
        category_mappings = {}
        for mapping in cursor.fetchall():
            if mapping["vendor_profile_id"] not in category_mappings:
                category_mappings[mapping["vendor_profile_id"]] = []
            category_mappings[mapping["vendor_profile_id"]].append(mapping["name"])
        
        mongo_users = []
        for user in users:
            try:
                mongo_doc = {
                    "user_id": user["id"],
                    "username": user["username"],
                    "password_hash": user["password_hash"],
                    "role": user["role"],
                    "name": user["name"],
                    "email": user["email"],
                    "phone": user["phone"],
                    "address": user["address"],
                    "description": user["description"],
                    "is_active": bool(user["is_active"]),
                    "status": user["status"] or "active",
                    "deactivation_reason": user["deactivation_reason"],
                    "deactivated_by": user["deactivated_by"],
                    "deactivated_at": self.parse_datetime(user["deactivated_at"]),
                    "last_login_at": self.parse_datetime(user["last_login_at"]),
                    "created_at": self.parse_datetime(user["created_at"]),
                    "updated_at": self.parse_datetime(user["updated_at"])
                }
                
                # Embed vendor profile if user is a vendor
                if user["role"] == "vendor" and user["id"] in vendor_profiles:
                    vp = vendor_profiles[user["id"]]
                    mongo_doc["vendor_profile"] = {
                        "business_type": vp["business_type"],
                        "specialties": self.parse_json_field(vp["specialties"]),
                        "average_rating": float(vp["average_rating"]) if vp["average_rating"] else 0.0,
                        "review_count": vp["review_count"] or 0,
                        "is_active": bool(vp["is_active"]),
                        "business_hours": vp["business_hours"],
                        "delivery_areas": vp["delivery_areas"],
                        "minimum_order": float(vp["minimum_order"]) if vp["minimum_order"] else 0.0,
                        "payment_terms": vp["payment_terms"],
                        "certifications": self.parse_json_field(vp["certifications"]),
                        "logo_url": vp["logo_url"],
                        "gallery_images": self.parse_json_field(vp["gallery_images"]),
                        "business_description": vp["business_description"],
                        "website_url": vp["website_url"],
                        "established_year": vp["established_year"],
                        "categories": category_mappings.get(vp["id"], [])
                    }
                
                mongo_users.append(InsertOne(mongo_doc))
                
            except Exception as e:
                error_msg = f"Error processing user {user['id']}: {e}"
                print(f"⚠️ {error_msg}")
                self.errors.append(error_msg)
        
        if mongo_users:
            result = await self.mongo_db.users.bulk_write(mongo_users)
            self.log_migration("users", result.inserted_count)
    
    async def migrate_orders_with_denormalization(self):
        """Migrate orders with denormalized user data"""
        print("📋 Migrating orders with denormalized data...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT o.*, 
                   r.name as restaurant_name, r.phone as restaurant_phone, 
                   r.address as restaurant_address, r.email as restaurant_email,
                   v.name as vendor_name, v.phone as vendor_phone,
                   v.address as vendor_address, v.email as vendor_email
            FROM orders o
            JOIN users r ON o.restaurant_id = r.id
            JOIN users v ON o.vendor_id = v.id
        """)
        orders = cursor.fetchall()
        
        if not orders:
            print("ℹ️ No orders found to migrate")
            return
        
        mongo_orders = []
        for order in orders:
            try:
                mongo_doc = {
                    "order_id": order["id"],
                    "restaurant_id": order["restaurant_id"],
                    "vendor_id": order["vendor_id"],
                    "restaurant": {
                        "name": order["restaurant_name"],
                        "phone": order["restaurant_phone"],
                        "address": order["restaurant_address"],
                        "email": order["restaurant_email"]
                    },
                    "vendor": {
                        "name": order["vendor_name"],
                        "phone": order["vendor_phone"],
                        "address": order["vendor_address"],
                        "email": order["vendor_email"]
                    },
                    "items_text": order["items_text"],
                    "status": order["status"] or "pending",
                    "notes": order["notes"],
                    "created_at": self.parse_datetime(order["created_at"]),
                    "updated_at": self.parse_datetime(order["updated_at"])
                }
                mongo_orders.append(InsertOne(mongo_doc))
                
            except Exception as e:
                error_msg = f"Error processing order {order['id']}: {e}"
                print(f"⚠️ {error_msg}")
                self.errors.append(error_msg)
        
        if mongo_orders:
            result = await self.mongo_db.orders.bulk_write(mongo_orders)
            self.log_migration("orders", result.inserted_count)
    
    async def migrate_audit_logs(self):
        """Migrate admin audit logs"""
        print("📊 Migrating admin audit logs...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT * FROM admin_audit_logs")
        logs = cursor.fetchall()
        
        if not logs:
            print("ℹ️ No audit logs found to migrate")
            return
        
        mongo_logs = []
        for log in logs:
            try:
                mongo_doc = {
                    "log_id": log["id"],
                    "admin_id": log["admin_id"],
                    "target_user_id": log["target_user_id"],
                    "action": log["action"],
                    "details": self.parse_json_field(log["details"]) if log["details"] else {},
                    "ip_address": log["ip_address"],
                    "user_agent": log["user_agent"],
                    "session_id": log["session_id"],
                    "created_at": self.parse_datetime(log["created_at"])
                }
                mongo_logs.append(InsertOne(mongo_doc))
                
            except Exception as e:
                error_msg = f"Error processing audit log {log['id']}: {e}"
                print(f"⚠️ {error_msg}")
                self.errors.append(error_msg)
        
        if mongo_logs:
            result = await self.mongo_db.admin_audit_logs.bulk_write(mongo_logs)
            self.log_migration("admin_audit_logs", result.inserted_count)
    
    async def migrate_user_events(self):
        """Migrate user event logs"""
        print("📈 Migrating user event logs...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_event_logs")
        events = cursor.fetchall()
        
        if not events:
            print("ℹ️ No user events found to migrate")
            return
        
        mongo_events = []
        for event in events:
            try:
                mongo_doc = {
                    "event_id": event["id"],
                    "user_id": event["user_id"],
                    "event_type": event["event_type"],
                    "details": self.parse_json_field(event["details"]) if event["details"] else {},
                    "ip_address": event["ip_address"],
                    "user_agent": event["user_agent"],
                    "created_at": self.parse_datetime(event["created_at"])
                }
                mongo_events.append(InsertOne(mongo_doc))
                
            except Exception as e:
                error_msg = f"Error processing user event {event['id']}: {e}"
                print(f"⚠️ {error_msg}")
                self.errors.append(error_msg)
        
        if mongo_events:
            result = await self.mongo_db.user_event_logs.bulk_write(mongo_events)
            self.log_migration("user_event_logs", result.inserted_count)
    
    async def migrate_impersonation_sessions(self):
        """Migrate impersonation sessions"""
        print("🎭 Migrating impersonation sessions...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT * FROM impersonation_sessions")
        sessions = cursor.fetchall()
        
        if not sessions:
            print("ℹ️ No impersonation sessions found to migrate")
            return
        
        mongo_sessions = []
        for session in sessions:
            try:
                mongo_doc = {
                    "session_id_num": session["id"],
                    "admin_id": session["admin_id"],
                    "target_user_id": session["target_user_id"],
                    "session_token": session["session_token"],
                    "expires_at": self.parse_datetime(session["expires_at"]),
                    "is_active": bool(session["is_active"]),
                    "ended_at": self.parse_datetime(session["ended_at"]),
                    "created_at": self.parse_datetime(session["created_at"])
                }
                mongo_sessions.append(InsertOne(mongo_doc))
                
            except Exception as e:
                error_msg = f"Error processing impersonation session {session['id']}: {e}"
                print(f"⚠️ {error_msg}")
                self.errors.append(error_msg)
        
        if mongo_sessions:
            result = await self.mongo_db.impersonation_sessions.bulk_write(mongo_sessions)
            self.log_migration("impersonation_sessions", result.inserted_count)
    
    async def create_indexes(self):
        """Create performance indexes"""
        print("🔍 Creating performance indexes...")
        
        try:
            # Users collection indexes
            await self.mongo_db.users.create_index([("user_id", 1)], unique=True)
            await self.mongo_db.users.create_index([("username", 1)], unique=True)
            await self.mongo_db.users.create_index([("role", 1)])
            await self.mongo_db.users.create_index([("vendor_profile.categories", 1)])
            
            # Orders collection indexes
            await self.mongo_db.orders.create_index([("order_id", 1)], unique=True)
            await self.mongo_db.orders.create_index([("restaurant_id", 1)])
            await self.mongo_db.orders.create_index([("vendor_id", 1)])
            await self.mongo_db.orders.create_index([("status", 1)])
            await self.mongo_db.orders.create_index([("created_at", -1)])
            
            # Vendor categories indexes
            await self.mongo_db.vendor_categories.create_index([("category_id", 1)], unique=True)
            await self.mongo_db.vendor_categories.create_index([("name", 1)])
            
            # Audit logs indexes
            await self.mongo_db.admin_audit_logs.create_index([("log_id", 1)], unique=True)
            await self.mongo_db.admin_audit_logs.create_index([("admin_id", 1)])
            await self.mongo_db.admin_audit_logs.create_index([("created_at", -1)])
            
            # Event logs indexes
            await self.mongo_db.user_event_logs.create_index([("event_id", 1)], unique=True)
            await self.mongo_db.user_event_logs.create_index([("user_id", 1)])
            await self.mongo_db.user_event_logs.create_index([("created_at", -1)])
            
            # Impersonation sessions indexes
            await self.mongo_db.impersonation_sessions.create_index([("session_id_num", 1)], unique=True)
            await self.mongo_db.impersonation_sessions.create_index([("session_token", 1)], unique=True)
            await self.mongo_db.impersonation_sessions.create_index([("admin_id", 1)])
            
            self.log_migration("indexes", "created successfully")
            
        except Exception as e:
            error_msg = f"Error creating indexes: {e}"
            print(f"⚠️ {error_msg}")
            self.errors.append(error_msg)
    
    def log_migration(self, collection, count):
        """Log migration progress"""
        message = f"Migrated {count} documents to {collection}"
        self.migration_log.append(message)
        print(f"✅ {message}")
    
    async def validate_migration(self):
        """Validate data integrity after migration"""
        print("🔍 Validating migration...")
        
        validation_results = {}
        
        # Count documents in each collection
        collections = ["users", "orders", "vendor_categories", "admin_audit_logs", "user_event_logs", "impersonation_sessions"]
        
        for collection in collections:
            try:
                mongo_count = await self.mongo_db[collection].count_documents({})
                validation_results[collection] = mongo_count
            except Exception as e:
                print(f"⚠️ Error counting {collection}: {e}")
                validation_results[collection] = "Error"
        
        # Validate specific data integrity
        try:
            sample_user = await self.mongo_db.users.find_one({"role": "vendor"})
            if sample_user and "vendor_profile" in sample_user:
                print("✅ Vendor profile embedding successful")
            
            sample_order = await self.mongo_db.orders.find_one({})
            if sample_order and "restaurant" in sample_order and "vendor" in sample_order:
                print("✅ Order denormalization successful")
                
        except Exception as e:
            print(f"⚠️ Error during validation: {e}")
        
        return validation_results
    
    async def run_migration(self):
        """Execute complete migration process"""
        start_time = datetime.utcnow()
        
        try:
            print("🚀 Starting BistroBoard MongoDB migration...")
            print(f"📅 Migration started at: {start_time}")
            
            await self.setup_connections()
            
            # Migration sequence (order matters due to dependencies)
            await self.migrate_vendor_categories()
            await self.migrate_users_with_profiles()
            await self.migrate_orders_with_denormalization()
            await self.migrate_audit_logs()
            await self.migrate_user_events()
            await self.migrate_impersonation_sessions()
            
            await self.create_indexes()
            
            validation_results = await self.validate_migration()
            
            end_time = datetime.utcnow()
            duration = end_time - start_time
            
            print("\n" + "="*60)
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"📅 Started: {start_time}")
            print(f"📅 Completed: {end_time}")
            print(f"⏱️ Duration: {duration}")
            print(f"📊 Final document counts:")
            for collection, count in validation_results.items():
                print(f"   - {collection}: {count}")
            
            if self.errors:
                print(f"\n⚠️ {len(self.errors)} warnings/errors occurred:")
                for error in self.errors[:10]:  # Show first 10 errors
                    print(f"   - {error}")
                if len(self.errors) > 10:
                    print(f"   ... and {len(self.errors) - 10} more")
            else:
                print("\n✅ No errors occurred during migration")
            
            print("\n🔄 Next steps:")
            print("1. Update FastAPI application to use MongoDB")
            print("2. Test all API endpoints")
            print("3. Update authentication and session management")
            print("4. Perform comprehensive testing")
            
        except Exception as e:
            print(f"\n❌ MIGRATION FAILED: {e}")
            print("🔄 Please check the error and try again")
            raise
        finally:
            if self.sqlite_conn:
                self.sqlite_conn.close()
                print("✅ SQLite connection closed")
            if self.mongo_client:
                self.mongo_client.close()
                print("✅ MongoDB connection closed")

# Run migration
if __name__ == "__main__":
    print("BistroBoard SQLite to MongoDB Atlas Migration")
    print("=" * 50)
    
    migration = BistroboardMigration()
    asyncio.run(migration.run_migration())