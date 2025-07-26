from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from ..mongo_models import User
from ..auth_simple import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    UserLogin
)
from ..admin_auth import log_user_event
from ..google_oauth import GoogleOAuthService

router = APIRouter()

# Pydantic models for Google OAuth
class GoogleLoginRequest(BaseModel):
    token: str
    role: str = "restaurant"  # Default role for new users

class GoogleConfigResponse(BaseModel):
    client_id: str
    redirect_uri: str

class GoogleRoleSelectionResponse(BaseModel):
    access_token: str = ""
    token_type: str = "bearer"
    user_id: int = 0
    role: str = ""
    name: str
    needs_role_selection: bool = True
    google_token: str

@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_credentials: UserLogin,
    request: Request
):
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

@router.post("/google")
async def google_login(
    google_request: GoogleLoginRequest,
    request: Request
):
    """
    Authenticate user with Google OAuth token
    """
    try:
        # Verify Google token and get user info
        google_user_info = await GoogleOAuthService.verify_google_token(google_request.token)
        
        # Check if user already exists
        existing_user = await User.find_one(User.google_id == google_user_info['google_id'])
        if not existing_user:
            # Also check by email for account linking
            existing_user = await User.find_one(User.email == google_user_info['email'])
        
        # If user exists and has no role or default role, they need role selection
        needs_role_selection = False
        if existing_user and (not existing_user.role or existing_user.role == 'restaurant'):
            # Check if this is a newly created user (created in last 5 minutes) or has default role
            if (existing_user.created_at and
                datetime.utcnow() - existing_user.created_at < timedelta(minutes=5)) or \
               existing_user.role == 'restaurant':
                needs_role_selection = True
        
        # If new user and no role specified, they need role selection
        if not existing_user and google_request.role == 'restaurant':
            needs_role_selection = True
        
        # If user needs role selection, return special response
        if needs_role_selection and google_request.role == 'restaurant':
            return {
                "access_token": "",
                "token_type": "bearer",
                "user_id": 0,
                "role": "",
                "name": google_user_info['name'],
                "needs_role_selection": True,
                "google_token": google_request.token
            }
        
        # Find or create user with specified role
        user = await GoogleOAuthService.find_or_create_user(
            google_user_info,
            role=google_request.role
        )
        
        # Check if user account is active
        if not user.is_active and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated. Please contact support.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Log user login event
        await log_user_event(
            user_id=user.user_id,
            event_type="login",
            details={
                "login_method": "google_oauth",
                "google_id": user.google_id,
                "user_agent": request.headers.get("user-agent"),
                "success": True
            },
            request=request
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
            "name": user.name,
            "needs_role_selection": False
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid token)
        raise
    except Exception as e:
        # Log unexpected errors
        print(f"❌ Google OAuth login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed"
        )

@router.get("/google/config", response_model=GoogleConfigResponse)
async def get_google_config():
    """
    Get Google OAuth configuration for frontend
    """
    config = GoogleOAuthService.get_google_oauth_config()
    return GoogleConfigResponse(
        client_id=config.get("client_id"),
        redirect_uri=config.get("redirect_uri")
    )

@router.put("/google/role")
async def update_google_user_role(
    google_request: GoogleLoginRequest,
    request: Request
):
    """
    Update role for Google OAuth user
    """
    try:
        # Verify Google token and get user info
        google_user_info = await GoogleOAuthService.verify_google_token(google_request.token)
        
        # Find user by Google ID
        user = await User.find_one(User.google_id == google_user_info['google_id'])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user role
        user.role = google_request.role
        await user.save()
        
        # Log role update event
        await log_user_event(
            user_id=user.user_id,
            event_type="role_update",
            details={
                "new_role": google_request.role,
                "update_method": "google_oauth",
                "user_agent": request.headers.get("user-agent")
            },
            request=request
        )
        
        # Create new access token with updated role
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
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Google OAuth role update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )