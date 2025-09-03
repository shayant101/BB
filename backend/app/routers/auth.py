from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from ..mongo_models import User
from ..auth_simple import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    UserLogin,
    verify_clerk_token
)
from ..admin_auth import log_user_event

router = APIRouter()

# Pydantic models for Clerk authentication
class ClerkLoginRequest(BaseModel):
    token: str
    role: str = "restaurant"  # Default role for new users

@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_credentials: UserLogin,
    request: Request
):
    # Check for hardcoded admin credentials first
    if user_credentials.username == "admin" and user_credentials.password == "admin123":
        # Create access token for hardcoded admin
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": "admin",
                "user_id": 999999,  # Special admin user ID
                "role": "admin",
                "name": "System Administrator",
                "is_impersonating": False
            },
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": 999999,
            "role": "admin",
            "name": "System Administrator"
        }

    # Find user by username or email
    user = await User.find_one(
        {"$or": [{"username": user_credentials.username}, {"email": user_credentials.username}]}
    )

    # Verify user and password
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.user_id,
            "role": user.role,
            "name": user.name,
            "is_impersonating": False
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "role": user.role,
        "name": user.name
    }

@router.post("/clerk")
async def clerk_login(
    clerk_request: ClerkLoginRequest,
    request: Request
):
    """
    Authenticate user with Clerk JWT token
    """
    try:
        # Verify Clerk token and get user info
        clerk_user_info = verify_clerk_token(clerk_request.token)
        clerk_user_id = clerk_user_info['clerk_user_id']
        
        # Check if user already exists
        existing_user = await User.find_one(User.clerk_user_id == clerk_user_id)
        if not existing_user:
            # Also check by email for account linking
            if clerk_user_info.get('email'):
                existing_user = await User.find_one(User.email == clerk_user_info['email'])
        
        # If user doesn't exist, they should be created via webhook
        # For now, return an error asking them to complete registration
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please complete registration first."
            )
        
        # Update Clerk user ID if not set
        if not existing_user.clerk_user_id:
            existing_user.clerk_user_id = clerk_user_id
            existing_user.auth_provider = "clerk" if existing_user.auth_provider == "local" else "both"
            await existing_user.save()
        
        # Check if user account is active
        if not existing_user.is_active and existing_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated. Please contact support.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Log user login event
        await log_user_event(
            user_id=existing_user.user_id,
            event_type="login",
            details={
                "login_method": "clerk",
                "clerk_user_id": clerk_user_id,
                "user_agent": request.headers.get("user-agent"),
                "success": True
            },
            request=request
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": existing_user.username,
                "user_id": existing_user.user_id,
                "role": existing_user.role,
                "name": existing_user.name,
                "is_impersonating": False
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": existing_user.user_id,
            "role": existing_user.role,
            "name": existing_user.name
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid token)
        raise
    except Exception as e:
        # Log unexpected errors
        print(f"❌ Clerk authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk authentication failed"
        )