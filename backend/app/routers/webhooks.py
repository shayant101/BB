import hashlib
import hmac
import json
import os
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from ..mongo_models import User
from ..admin_auth import log_user_event

router = APIRouter()

# Clerk webhook configuration
CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET", "whsec_your_webhook_secret_here")

class ClerkWebhookEvent(BaseModel):
    """Clerk webhook event model"""
    data: Dict[str, Any]
    object: str
    type: str

def verify_clerk_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Clerk webhook signature"""
    try:
        # Clerk uses HMAC-SHA256 for webhook signatures
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Clerk sends signature in format "v1,{signature}"
        if signature.startswith('v1,'):
            signature = signature[3:]
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        return False

@router.post("/clerk")
async def handle_clerk_webhook(request: Request):
    """Handle Clerk webhook events for user sync"""
    try:
        # Get the raw payload and signature
        payload = await request.body()
        signature = request.headers.get('svix-signature') or request.headers.get('clerk-signature')
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing webhook signature"
            )
        
        # Verify the webhook signature
        if not verify_clerk_webhook_signature(payload, signature, CLERK_WEBHOOK_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse the webhook payload
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        event_type = event_data.get('type')
        user_data = event_data.get('data', {})
        
        # Handle different event types
        if event_type == 'user.created':
            await handle_user_created(user_data, request)
        elif event_type == 'user.updated':
            await handle_user_updated(user_data, request)
        elif event_type == 'user.deleted':
            await handle_user_deleted(user_data, request)
        else:
            print(f"Unhandled Clerk webhook event type: {event_type}")
        
        return {"status": "success", "message": f"Processed {event_type} event"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Clerk webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )

async def handle_user_created(user_data: Dict[str, Any], request: Request):
    """Handle user.created webhook event"""
    try:
        clerk_user_id = user_data.get('id')
        if not clerk_user_id:
            print("❌ Missing Clerk user ID in webhook data")
            return
        
        # Check if user already exists
        existing_user = await User.find_one(User.clerk_user_id == clerk_user_id)
        if existing_user:
            print(f"User with Clerk ID {clerk_user_id} already exists")
            return
        
        # Extract user information from Clerk data
        email_addresses = user_data.get('email_addresses', [])
        primary_email = None
        for email in email_addresses:
            if email.get('id') == user_data.get('primary_email_address_id'):
                primary_email = email.get('email_address')
                break
        
        if not primary_email and email_addresses:
            primary_email = email_addresses[0].get('email_address')
        
        # Get user's name
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip() or primary_email.split('@')[0] if primary_email else 'Unknown User'
        
        # Get the next user_id
        last_user = await User.find().sort(-User.user_id).limit(1).to_list()
        next_user_id = (last_user[0].user_id + 1) if last_user else 1
        
        # Generate username from email
        username = primary_email.split('@')[0] if primary_email else f"user_{next_user_id}"
        
        # Ensure username is unique
        existing_username = await User.find_one(User.username == username)
        if existing_username:
            username = f"{username}_{next_user_id}"
        
        # Create new user
        new_user = User(
            user_id=next_user_id,
            username=username,
            password_hash=None,  # No password for Clerk users
            role=None,  # No default role, user must select one
            name=full_name,
            email=primary_email or "",
            phone="",  # Will be filled later by user
            address="",  # Will be filled later by user
            clerk_user_id=clerk_user_id,
            auth_provider="clerk",
            is_active=True,
            status="active",
            last_login_at=datetime.utcnow()
        )
        
        await new_user.save()
        print(f"✅ Created new user from Clerk webhook: {primary_email}")
        
        # Log user creation event
        await log_user_event(
            user_id=new_user.user_id,
            event_type="user_created",
            details={
                "creation_method": "clerk_webhook",
                "clerk_user_id": clerk_user_id,
                "email": primary_email,
                "user_agent": request.headers.get("user-agent")
            },
            request=request
        )
        
    except Exception as e:
        print(f"❌ Error handling user.created webhook: {str(e)}")
        raise

async def handle_user_updated(user_data: Dict[str, Any], request: Request):
    """Handle user.updated webhook event"""
    try:
        clerk_user_id = user_data.get('id')
        if not clerk_user_id:
            print("❌ Missing Clerk user ID in webhook data")
            return
        
        # Find existing user
        user = await User.find_one(User.clerk_user_id == clerk_user_id)
        if not user:
            print(f"User with Clerk ID {clerk_user_id} not found for update")
            return
        
        # Update user information
        email_addresses = user_data.get('email_addresses', [])
        primary_email = None
        for email in email_addresses:
            if email.get('id') == user_data.get('primary_email_address_id'):
                primary_email = email.get('email_address')
                break
        
        if not primary_email and email_addresses:
            primary_email = email_addresses[0].get('email_address')
        
        # Update user fields
        if primary_email and primary_email != user.email:
            user.email = primary_email
        
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip()
        if full_name and full_name != user.name:
            user.name = full_name
        
        user.updated_at = datetime.utcnow()
        await user.save()
        
        print(f"✅ Updated user from Clerk webhook: {primary_email}")
        
        # Log user update event
        await log_user_event(
            user_id=user.user_id,
            event_type="user_updated",
            details={
                "update_method": "clerk_webhook",
                "clerk_user_id": clerk_user_id,
                "email": primary_email,
                "user_agent": request.headers.get("user-agent")
            },
            request=request
        )
        
    except Exception as e:
        print(f"❌ Error handling user.updated webhook: {str(e)}")
        raise

async def handle_user_deleted(user_data: Dict[str, Any], request: Request):
    """Handle user.deleted webhook event"""
    try:
        clerk_user_id = user_data.get('id')
        if not clerk_user_id:
            print("❌ Missing Clerk user ID in webhook data")
            return
        
        # Find existing user
        user = await User.find_one(User.clerk_user_id == clerk_user_id)
        if not user:
            print(f"User with Clerk ID {clerk_user_id} not found for deletion")
            return
        
        # Deactivate user instead of deleting (to preserve data integrity)
        user.is_active = False
        user.status = "deleted"
        user.deactivated_at = datetime.utcnow()
        user.deactivation_reason = "User deleted from Clerk"
        user.updated_at = datetime.utcnow()
        
        await user.save()
        
        print(f"✅ Deactivated user from Clerk webhook: {user.email}")
        
        # Log user deletion event
        await log_user_event(
            user_id=user.user_id,
            event_type="user_deleted",
            details={
                "deletion_method": "clerk_webhook",
                "clerk_user_id": clerk_user_id,
                "email": user.email,
                "user_agent": request.headers.get("user-agent")
            },
            request=request
        )
        
    except Exception as e:
        print(f"❌ Error handling user.deleted webhook: {str(e)}")
        raise