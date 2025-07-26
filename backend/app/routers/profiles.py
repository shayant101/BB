from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional

from ..mongo_models import User
from ..auth_simple import verify_token

router = APIRouter()

# Pydantic Models
class UserProfileResponse(BaseModel):
    user_id: int
    username: str
    role: str
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None

class UserProfileUpdateRequest(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None

# Dependency to get current user from JWT token
async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )
    
    token = authorization.split(" ")[1]
    token_data = verify_token(token)
    user = await User.find_one(User.username == token_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    return UserProfileResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        address=current_user.address,
        description=current_user.description
    )

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update the profile of the currently authenticated user."""
    current_user.name = profile_data.name
    current_user.email = profile_data.email
    current_user.phone = profile_data.phone
    current_user.address = profile_data.address
    current_user.description = profile_data.description
    
    await current_user.save()
    
    return UserProfileResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        address=current_user.address,
        description=current_user.description
    )

@router.get("/vendors", response_model=List[UserProfileResponse])
async def get_all_vendors(current_user: User = Depends(get_current_user)):
    """Get a list of all vendor profiles (for restaurants)."""
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can view vendor profiles."
        )
    
    vendors = await User.find(User.role == "vendor", User.is_active == True).to_list()
    
    return [
        UserProfileResponse(
            user_id=v.user_id,
            username=v.username,
            role=v.role,
            name=v.name,
            email=v.email,
            phone=v.phone,
            address=v.address,
            description=v.description
        ) for v in vendors
    ]