"""
Force MongoDB Production Seed Data Script
This script is designed to be run manually to seed the production database.
It explicitly loads the .env.production file to ensure the correct database is targeted.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load production environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env.production')
if os.path.exists(env_path):
    print(f"✅ Loading production environment from: {env_path}")
    load_dotenv(env_path)
else:
    print(f"❌ Production environment file not found at: {env_path}")
    print("Please create a .env.production file with the necessary variables.")
    sys.exit(1)

# Now that the environment is loaded, import the seeder
from seed_mongodb_production import MongoDBSeeder

async def main():
    """Main function to run seeding"""
    print("🚀 Starting MongoDB production seeding (FORCED)...")
    
    seeder = MongoDBSeeder()
    
    # The seeder will now use the MONGODB_URL from the loaded .env.production
    await seeder.run_seeding()

if __name__ == "__main__":
    print("BistroBoard MongoDB Production Seeding (Forced)")
    print("=" * 50)
    # Confirm with the user before proceeding
    confirm = input("⚠️ This will seed the PRODUCTION database. Are you sure you want to continue? (yes/no): ")
    if confirm.lower() == 'yes':
        asyncio.run(main())
    else:
        print("🚫 Seeding cancelled by user.")