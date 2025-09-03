from datetime import timedelta, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from ..mongo_models import User
from ..auth_simple import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    UserLogin,
    get_password_hash,
)
from ..admin_auth import log_user_event

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr
    name: str
    phone: str
    address: str
    role: str
    description: Optional[str] = None

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

@router.post("/register", response_model=Token)
async def register_user(user_data: UserRegister):
    # Check if username already exists
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = await User.find_one(User.email == user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Validate role
    if user_data.role not in ["restaurant", "vendor"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'restaurant' or 'vendor'"
        )
    
    # Get next user ID
    last_user = await User.find().sort(-User.user_id).limit(1).first_or_none()
    next_user_id = (last_user.user_id + 1) if last_user else 1
    
    # Hash password using bcrypt (for new users)
    from ..auth_simple import get_password_hash
    password_hash = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        user_id=next_user_id,
        username=user_data.username,
        password_hash=password_hash,
        role=user_data.role,
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        address=user_data.address,
        description=user_data.description,
        auth_provider="local",
        is_active=True,
        status="active"
    )
    
    await new_user.insert()
    
    # Create access token for the new user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": new_user.username,
            "user_id": new_user.user_id,
            "role": new_user.role,
            "name": new_user.name,
            "is_impersonating": False
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.user_id,
        "role": new_user.role,
        "name": new_user.name
    }