#!/usr/bin/env python3
"""
Debug script to investigate user creation issues
"""
import asyncio
from app.mongo_models import User
from app.mongodb import connect_to_mongo

async def debug_users():
    """Debug user creation and find problematic users"""
    await connect_to_mongo()
    
    print("🔍 DEBUGGING USER CREATION ISSUES")
    print("=" * 50)
    
    # Get all users
    all_users = await User.find().to_list()
    print(f"📊 Total users in database: {len(all_users)}")
    
    # Analyze users by auth provider
    auth_providers = {}
    example_com_users = []
    clerk_users = []
    missing_gmail_users = []
    
    for user in all_users:
        provider = user.auth_provider
        auth_providers[provider] = auth_providers.get(provider, 0) + 1
        
        # Check for example.com users (test users)
        if user.email.endswith('@example.com'):
            example_com_users.append(user)
        
        # Check for Clerk users
        if user.clerk_user_id:
            clerk_users.append(user)
        
        # Check for missing Gmail users
        if user.email in ['shayan.s.toor@gmail.com', 'shayantoor1@gmail.com']:
            missing_gmail_users.append(user)
    
    print(f"\n📈 Users by auth provider:")
    for provider, count in auth_providers.items():
        print(f"  {provider}: {count}")
    
    print(f"\n🧪 Example.com users (test users): {len(example_com_users)}")
    for user in example_com_users:
        print(f"  - {user.email} (username: {user.username}, clerk_id: {user.clerk_user_id})")
        print(f"    Created: {user.created_at}, Role: {user.role}")
    
    print(f"\n👤 Clerk users: {len(clerk_users)}")
    for user in clerk_users:
        print(f"  - {user.email} (clerk_id: {user.clerk_user_id})")
        print(f"    Username: {user.username}, Role: {user.role}")
    
    print(f"\n📧 Missing Gmail users found: {len(missing_gmail_users)}")
    for user in missing_gmail_users:
        print(f"  - {user.email} (clerk_id: {user.clerk_user_id})")
        print(f"    Username: {user.username}, Role: {user.role}")
    
    # Check for users with no role
    no_role_users = [u for u in all_users if u.role is None]
    print(f"\n❓ Users with no role: {len(no_role_users)}")
    for user in no_role_users:
        print(f"  - {user.email} (username: {user.username})")
    
    # Check for duplicate emails
    emails = {}
    for user in all_users:
        if user.email in emails:
            emails[user.email].append(user)
        else:
            emails[user.email] = [user]
    
    duplicates = {email: users for email, users in emails.items() if len(users) > 1}
    print(f"\n🔄 Duplicate emails: {len(duplicates)}")
    for email, users in duplicates.items():
        print(f"  - {email}: {len(users)} users")
        for user in users:
            print(f"    * ID: {user.user_id}, Username: {user.username}, Clerk ID: {user.clerk_user_id}")

if __name__ == "__main__":
    asyncio.run(debug_users())