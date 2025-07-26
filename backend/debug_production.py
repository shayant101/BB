"""
Production Environment Debugging Script
This script is designed to be run on the production server to diagnose environment and connection issues.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load production environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env.production')
if os.path.exists(env_path):
    print(f"✅ Loading production environment from: {env_path}")
    load_dotenv(env_path)
else:
    print(f"⚠️ Production environment file not found at: {env_path}")

async def debug_production():
    """Run a series of checks to debug the production environment."""
    print("\n" + "="*50)
    print("🕵️  STARTING PRODUCTION DEBUGGING")
    print("="*50)

    # --- 1. Check Environment Variables ---
    print("\n--- 1. Checking Environment Variables ---")
    mongodb_url = os.getenv("MONGODB_URL")
    allowed_origins = os.getenv("ALLOWED_ORIGINS")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")

    print(f"  - MONGODB_URL: {'Set' if mongodb_url else 'Not Set'}")
    if mongodb_url:
        # Mask credentials for security
        parts = mongodb_url.split('@')
        if len(parts) > 1:
            print(f"    - Value (masked): {parts[0].split('//')[0]}//...@{parts[1]}")
        else:
            print(f"    - Value: {mongodb_url}")

    print(f"  - ALLOWED_ORIGINS: {'Set' if allowed_origins else 'Not Set'}")
    if allowed_origins:
        print(f"    - Value: {allowed_origins}")

    print(f"  - GOOGLE_CLIENT_ID: {'Set' if google_client_id else 'Not Set'}")
    if google_client_id:
        print(f"    - Value: {google_client_id}")

    # --- 2. Test Database Connection ---
    print("\n--- 2. Testing Database Connection ---")
    if not mongodb_url:
        print("  - ❌ SKIPPED: MONGODB_URL is not set.")
    else:
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
            await client.admin.command('ping')
            print("  - ✅ Successfully connected to MongoDB Atlas.")
            
            # Try to fetch some data
            db = client.get_database() # Get the default database from the connection string
            user_count = await db.users.count_documents({})
            print(f"  - 📊 Found {user_count} users in the database.")
            
            client.close()
        except Exception as e:
            print(f"  - ❌ FAILED to connect to MongoDB: {e}")

    # --- 3. Verify CORS Configuration ---
    print("\n--- 3. Verifying CORS Configuration ---")
    if not allowed_origins:
        print("  - ⚠️ ALLOWED_ORIGINS is not set. CORS will be permissive ('*').")
    else:
        origins = [origin.strip() for origin in allowed_origins.split(',')]
        final_origins = []
        for origin in origins:
            if origin not in final_origins:
                final_origins.append(origin)
            if origin.startswith("https://") and not origin.startswith("https://www."):
                www_origin = origin.replace("https://", "https://www.")
                if www_origin not in final_origins:
                    final_origins.append(www_origin)
        print(f"  - 🛠️  Final CORS origins that will be used: {final_origins}")

    print("\n" + "="*50)
    print("✅ DEBUGGING COMPLETE")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(debug_production())