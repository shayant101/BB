from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..auth_simple import verify_token, UserProfile, UserProfileUpdate

router = APIRouter()

# Dependency to get current user from JWT token
async def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )
    
    token = authorization.split(" ")[1]
    token_data = verify_token(token)
    user = db.query(User).filter(User.username == token_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.get("/profile", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        address=current_user.address,
        description=current_user.description
    )

@router.put("/profile", response_model=UserProfile)
async def update_current_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update user profile
    current_user.name = profile_update.name
    current_user.email = profile_update.email
    current_user.phone = profile_update.phone
    current_user.address = profile_update.address
    current_user.description = profile_update.description
    
    db.commit()
    db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        address=current_user.address,
        description=current_user.description
    )

@router.get("/vendors", response_model=List[UserProfile])
async def get_vendors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only restaurants can view vendor list
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can view vendor list"
        )
    
    vendors = db.query(User).filter(User.role == "vendor").all()
    
    return [
        UserProfile(
            id=vendor.id,
            username=vendor.username,
            role=vendor.role,
            name=vendor.name,
            email=vendor.email,
            phone=vendor.phone,
            address=vendor.address,
            description=vendor.description
        )
        for vendor in vendors
    ]

@router.get("/restaurants", response_model=List[UserProfile])
async def get_restaurants(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only vendors can view restaurant list
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can view restaurant list"
        )
    
    restaurants = db.query(User).filter(User.role == "restaurant").all()
    
    return [
        UserProfile(
            id=restaurant.id,
            username=restaurant.username,
            role=restaurant.role,
            name=restaurant.name,
            email=restaurant.email,
            phone=restaurant.phone,
            address=restaurant.address,
            description=restaurant.description
        )
        for restaurant in restaurants
    ]