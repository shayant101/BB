from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from .mongo_models import (
    User, Order, VendorCategory, AdminAuditLog,
    UserEventLog, ImpersonationSession
)
from .inventory_models import (
    InventoryCategory, InventoryItem, InventorySKU, InventoryCounter
)

# MongoDB Atlas connection string from environment variables
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://shayanstoor:ZpzaX5Y4SJmP7e9d@clusterbb.gzjujes.mongodb.net/bistroboard?retryWrites=true&w=majority&appName=ClusterBB")

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection and initialize Beanie"""
    try:
        print("🔄 Starting MongoDB connection...")
        
        # Create MongoDB client
        db.client = AsyncIOMotorClient(MONGODB_URL)
        # Get the database from the client. If the database is specified in the
        # connection string, that database will be used. Otherwise, it will default
        # to the 'bistroboard' database.
        db.database = db.client.get_database()
        print(f"🔄 MongoDB client created for database: '{db.database.name}'")
        
        # Test the connection
        await db.client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas")
        
        # Initialize Beanie with document models
        print("🔄 Initializing Beanie ODM...")
        await init_beanie(
            database=db.database,
            document_models=[
                User, Order, VendorCategory,
                AdminAuditLog, UserEventLog, ImpersonationSession,
                InventoryCategory, InventoryItem, InventorySKU, InventoryCounter
            ]
        )
        print("✅ Beanie initialized with document models")
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        import traceback
        traceback.print_exc()
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("✅ MongoDB connection closed")

async def get_database():
    """Get database instance"""
    return db.database

# Health check function
async def check_database_health():
    """Check if database connection is healthy"""
    try:
        if db.client:
            await db.client.admin.command('ping')
            return True
        return False
    except Exception:
        return False