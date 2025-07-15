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

@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_credentials: UserLogin,
    request: Request
):
    # Find user by username
    user = await User.find_one(User.username == user_credentials.username)
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user account is active (except for admins during system issues)
    if not user.is_active and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time with retry logic for revision conflicts
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Refresh user data to get latest revision
            if attempt > 0:
                user = await User.find_one(User.username == user_credentials.username)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found during login update"
                    )
            
            user.last_login_at = datetime.utcnow()
            await user.save()
            break  # Success, exit retry loop
            
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, log but continue with login
                print(f"⚠️  Failed to update last_login_at after {max_retries} attempts: {e}")
                break
            else:
                print(f"⚠️  Attempt {attempt + 1} failed to update last_login_at: {e}")
                if "RevisionIdWasChanged" in str(type(e).__name__):
                    import asyncio
                    await asyncio.sleep(0.1 * (attempt + 1))
    
    # Log user login event (this now has its own retry logic)
    await log_user_event(
        user_id=user.user_id,
        event_type="login",
        details={
            "login_method": "password",
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
        "name": user.name
    }

@router.post("/google", response_model=Token)
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
        
        # Find or create user
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
            "name": user.name
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
    return GoogleConfigResponse(**config)