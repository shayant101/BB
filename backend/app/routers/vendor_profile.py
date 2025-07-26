from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from ..mongo_models import User, VendorProfile
from ..auth_simple import verify_token
from datetime import datetime

router = APIRouter()

# Pydantic models
class VendorProfileUpdate(BaseModel):
    business_type: Optional[str] = None
    specialties: Optional[List[str]] = None
    business_hours: Optional[str] = None
    delivery_areas: Optional[str] = None
    minimum_order: Optional[float] = None
    payment_terms: Optional[str] = None
    certifications: Optional[List[str]] = None
    logo_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    business_description: Optional[str] = None
    website_url: Optional[str] = None
    established_year: Optional[str] = None
    categories: Optional[List[str]] = None
    is_active: Optional[bool] = None

class VendorProfileResponse(BaseModel):
    user_id: int
    business_type: Optional[str] = None
    specialties: List[str] = []
    average_rating: float = 0.0
    review_count: int = 0
    is_active: bool = True
    business_hours: Optional[str] = None
    delivery_areas: Optional[str] = None
    minimum_order: float = 0.0
    payment_terms: Optional[str] = None
    certifications: List[str] = []
    logo_url: Optional[str] = None
    gallery_images: List[str] = []
    business_description: Optional[str] = None
    website_url: Optional[str] = None
    established_year: Optional[str] = None
    categories: List[str] = []
    created_at: datetime
    updated_at: datetime

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

@router.get("/profile", response_model=VendorProfileResponse)
async def get_vendor_profile(current_user: User = Depends(get_current_user)):
    """Get current vendor's profile"""
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access their profile"
        )
    
    if not current_user.vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    return VendorProfileResponse(
        user_id=current_user.user_id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        **current_user.vendor_profile.dict()
    )

@router.put("/profile", response_model=VendorProfileResponse)
async def update_vendor_profile(
    profile_data: VendorProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current vendor's profile"""
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can update their profile"
        )
    
    if not current_user.vendor_profile:
        current_user.vendor_profile = VendorProfile()

    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user.vendor_profile, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return VendorProfileResponse(
        user_id=current_user.user_id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        **current_user.vendor_profile.dict()
    )