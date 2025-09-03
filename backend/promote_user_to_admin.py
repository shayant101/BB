#!/usr/bin/env python3
"""
Script to promote an existing user to admin role.

Usage:
    python promote_user_to_admin.py --email user@example.com

This script will:
1. Connect to the MongoDB database
2. Find the user by email address
3. Update their role to 'admin'
4. Print success/error messages
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path so we can import our modules
sys.path.append(str(Path(__file__).parent / "app"))

# Import required modules
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

# Define a minimal User model for this script
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
    user_id: int
    username: str
    password_hash: Optional[str] = None
    role: str  # "restaurant", "vendor", "admin"
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None
    
    # Google OAuth fields
    google_id: Optional[str] = None
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    google_picture: Optional[str] = None
    
    # Clerk OAuth fields
    clerk_user_id: Optional[str] = None
    
    auth_provider: str = "local"
    
    # Admin fields
    is_active: bool = True
    status: str = "active"
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

# MongoDB connection string from environment variables
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
        db.database = db.client.get_database()
        print(f"🔄 MongoDB client created for database: '{db.database.name}'")
        
        # Test the connection
        await db.client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas")
        
        # Initialize Beanie with just the User model for this script
        print("🔄 Initializing Beanie ODM...")
        await init_beanie(
            database=db.database,
            document_models=[User]
        )
        print("✅ Beanie initialized with User model")
        
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


async def promote_user_to_admin(email: str):
    """
    Promote a user to admin role by email address.
    
    Args:
        email (str): Email address of the user to promote
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Connect to MongoDB
        print("🔄 Connecting to MongoDB...")
        await connect_to_mongo()
        print("✅ Connected to MongoDB successfully")
        
        # Find the user by email
        print(f"🔍 Searching for user with email: {email}")
        user = await User.find_one(User.email == email)
        
        if not user:
            print(f"❌ Error: User with email '{email}' not found")
            return False
        
        # Check if user is already an admin
        if user.role == "admin":
            print(f"ℹ️  User '{email}' is already an admin")
            return True
        
        # Store the old role for logging
        old_role = user.role
        
        # Update the user's role to admin
        print(f"🔄 Promoting user '{email}' from '{old_role}' to 'admin'...")
        user.role = "admin"
        await user.save()
        
        print(f"✅ Success: User '{email}' has been promoted to admin role")
        print(f"   Previous role: {old_role}")
        print(f"   New role: admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Error promoting user: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Close the database connection
        print("🔄 Closing database connection...")
        await close_mongo_connection()


def main():
    """Main function to handle command line arguments and run the promotion."""
    parser = argparse.ArgumentParser(
        description="Promote an existing user to admin role",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python promote_user_to_admin.py --email john@restaurant.com
    python promote_user_to_admin.py --email vendor@supplier.com
        """
    )
    
    parser.add_argument(
        "--email",
        required=True,
        help="Email address of the user to promote to admin"
    )
    
    args = parser.parse_args()
    
    # Validate email format (basic validation)
    if "@" not in args.email or "." not in args.email:
        print("❌ Error: Please provide a valid email address")
        sys.exit(1)
    
    print("🚀 Starting user promotion script...")
    print(f"📧 Target email: {args.email}")
    print("-" * 50)
    
    # Run the async promotion function
    success = asyncio.run(promote_user_to_admin(args.email))
    
    print("-" * 50)
    if success:
        print("🎉 User promotion completed successfully!")
        sys.exit(0)
    else:
        print("💥 User promotion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()