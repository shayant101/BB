#!/usr/bin/env python3
"""
Admin User Seeding Script for BistroBoard
Creates the hardcoded admin user in MongoDB if it doesn't already exist.

Usage:
    cd backend && source venv/bin/activate && python seed_admin_user.py

This script ensures that the hardcoded admin user (username: "admin") has a
corresponding record in the MongoDB database, which is required for proper
authorization in the admin authentication system.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.mongodb import MONGODB_URL


async def seed_admin_user():
    """
    Create admin user in MongoDB if it doesn't already exist.
    The hardcoded admin login requires a corresponding database record.
    """
    client = None
    
    try:
        print("🔄 Connecting to MongoDB...")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client.get_database()
        
        # Test connection
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB database: '{db.name}'")
        
        # Check if admin user already exists
        existing_admin = await db.users.find_one({"username": "admin"})
        
        if existing_admin:
            print("Admin user already exists.")
            return
        
        print("🔄 Creating admin user...")
        
        # Create admin user document
        # Note: No password_hash is set since the login is hardcoded
        # The auth system checks for hardcoded credentials, not database password
        admin_user = {
            "user_id": 999999,  # Match the hardcoded admin user ID in auth.py
            "username": "admin",
            "password_hash": None,  # No password needed for hardcoded auth
            "role": "admin",
            "name": "System Administrator",
            "email": "admin@bistroboard.com",
            "phone": "555-ADMIN",
            "address": "BistroBoard System",
            "description": "System administrator with full access",
            "auth_provider": "local",
            "is_active": True,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert admin user
        result = await db.users.insert_one(admin_user)
        print("Admin user created successfully.")
        print(f"✅ Admin user inserted with MongoDB ID: {result.inserted_id}")
        
    except Exception as e:
        print(f"❌ Error seeding admin user: {e}")
        import traceback
        traceback.print_exc()
        raise
        
    finally:
        if client:
            client.close()
            print("✅ MongoDB connection closed")


async def main():
    """Main function to run admin user seeding"""
    print("BistroBoard Admin User Seeding")
    print("=" * 40)
    await seed_admin_user()


if __name__ == "__main__":
    asyncio.run(main())