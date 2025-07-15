#!/usr/bin/env python3
"""
Fix MongoDB indexes for user_event_logs collection
- Drop the unique index on event_id field
- This allows multiple documents with event_id=null
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

# MongoDB connection string (same as in mongodb.py)
MONGODB_URL = "mongodb+srv://shayanstoor:ZpzaX5Y4SJmP7e9d@clusterbb.gzjujes.mongodb.net/bistroboard?retryWrites=true&w=majority&appName=ClusterBB"

async def fix_event_log_indexes():
    """Fix the user_event_logs collection indexes"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.bistroboard
    collection = db.user_event_logs
    
    try:
        # List current indexes
        print("Current indexes on user_event_logs:")
        indexes = await collection.list_indexes().to_list(length=None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
        # Try to drop the unique index on event_id
        try:
            await collection.drop_index("event_id_1")
            print("✅ Successfully dropped unique index on event_id")
        except OperationFailure as e:
            if "index not found" in str(e).lower():
                print("ℹ️  Index event_id_1 not found (already dropped or doesn't exist)")
            else:
                print(f"⚠️  Error dropping index: {e}")
        
        # List indexes after cleanup
        print("\nIndexes after cleanup:")
        indexes = await collection.list_indexes().to_list(length=None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
            
        print("\n✅ Index cleanup completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_event_log_indexes())