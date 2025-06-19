from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from ..database import get_db
from ..models import User, VendorProfile, VendorCategory, VendorCategoryMapping
from ..auth_simple import verify_token
from datetime import datetime

router = APIRouter()

# Pydantic models for vendor profile management
class VendorProfileCreate(BaseModel):
    business_type: Optional[str] = None
    specialties: Optional[List[str]] = []
    business_hours: Optional[str] = None
    delivery_areas: Optional[str] = None
    minimum_order: Optional[float] = None
    payment_terms: Optional[str] = None
    certifications: Optional[List[str]] = []
    logo_url: Optional[str] = None
    gallery_images: Optional[List[str]] = []
    business_description: Optional[str] = None
    website_url: Optional[str] = None
    established_year: Optional[str] = None
    category_ids: Optional[List[int]] = []

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
    category_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None

class VendorProfileResponse(BaseModel):
    id: int
    user_id: int
    business_type: str
    specialties: List[str]
    average_rating: float
    review_count: int
    is_active: bool
    business_hours: str
    delivery_areas: str
    minimum_order: float
    payment_terms: str
    certifications: List[str]
    logo_url: str
    gallery_images: List[str]
    business_description: str
    website_url: str
    established_year: str
    categories: List[dict]
    created_at: datetime
    updated_at: datetime

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

@router.get("/profile", response_model=VendorProfileResponse)
async def get_vendor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current vendor's profile"""
    # Only vendors can access this endpoint
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access vendor profiles"
        )
    
    # Get vendor profile with categories
    vendor_profile = db.query(VendorProfile).options(
        joinedload(VendorProfile.categories).joinedload(VendorCategoryMapping.category)
    ).filter(VendorProfile.user_id == current_user.id).first()
    
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Format categories
    categories = []
    for mapping in vendor_profile.categories:
        categories.append({
            "id": mapping.category.id,
            "name": mapping.category.name,
            "icon": mapping.category.icon,
            "parent_category": mapping.category.parent_category
        })
    
    return VendorProfileResponse(
        id=vendor_profile.id,
        user_id=vendor_profile.user_id,
        business_type=vendor_profile.business_type or "",
        specialties=vendor_profile.specialties or [],
        average_rating=float(vendor_profile.average_rating or 0),
        review_count=vendor_profile.review_count or 0,
        is_active=vendor_profile.is_active,
        business_hours=vendor_profile.business_hours or "",
        delivery_areas=vendor_profile.delivery_areas or "",
        minimum_order=float(vendor_profile.minimum_order or 0),
        payment_terms=vendor_profile.payment_terms or "",
        certifications=vendor_profile.certifications or [],
        logo_url=vendor_profile.logo_url or "",
        gallery_images=vendor_profile.gallery_images or [],
        business_description=vendor_profile.business_description or "",
        website_url=vendor_profile.website_url or "",
        established_year=vendor_profile.established_year or "",
        categories=categories,
        created_at=vendor_profile.created_at,
        updated_at=vendor_profile.updated_at
    )

@router.post("/profile", response_model=VendorProfileResponse)
async def create_vendor_profile(
    profile_data: VendorProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create vendor profile"""
    # Only vendors can create vendor profiles
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can create vendor profiles"
        )
    
    # Check if profile already exists
    existing_profile = db.query(VendorProfile).filter(VendorProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor profile already exists"
        )
    
    # Create vendor profile
    vendor_profile = VendorProfile(
        user_id=current_user.id,
        business_type=profile_data.business_type,
        specialties=profile_data.specialties,
        business_hours=profile_data.business_hours,
        delivery_areas=profile_data.delivery_areas,
        minimum_order=profile_data.minimum_order,
        payment_terms=profile_data.payment_terms,
        certifications=profile_data.certifications,
        logo_url=profile_data.logo_url,
        gallery_images=profile_data.gallery_images,
        business_description=profile_data.business_description,
        website_url=profile_data.website_url,
        established_year=profile_data.established_year
    )
    
    db.add(vendor_profile)
    db.flush()  # Get the ID
    
    # Add category mappings
    if profile_data.category_ids:
        for category_id in profile_data.category_ids:
            # Verify category exists
            category = db.query(VendorCategory).filter(VendorCategory.id == category_id).first()
            if category:
                mapping = VendorCategoryMapping(
                    vendor_profile_id=vendor_profile.id,
                    category_id=category_id
                )
                db.add(mapping)
    
    db.commit()
    db.refresh(vendor_profile)
    
    # Return the created profile
    return await get_vendor_profile(current_user, db)

@router.put("/profile", response_model=VendorProfileResponse)
async def update_vendor_profile(
    profile_data: VendorProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update vendor profile"""
    # Only vendors can update vendor profiles
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can update vendor profiles"
        )
    
    # Get existing profile
    vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == current_user.id).first()
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Update fields
    update_data = profile_data.dict(exclude_unset=True)
    category_ids = update_data.pop('category_ids', None)
    
    for field, value in update_data.items():
        setattr(vendor_profile, field, value)
    
    vendor_profile.updated_at = datetime.utcnow()
    
    # Update category mappings if provided
    if category_ids is not None:
        # Remove existing mappings
        db.query(VendorCategoryMapping).filter(
            VendorCategoryMapping.vendor_profile_id == vendor_profile.id
        ).delete()
        
        # Add new mappings
        for category_id in category_ids:
            # Verify category exists
            category = db.query(VendorCategory).filter(VendorCategory.id == category_id).first()
            if category:
                mapping = VendorCategoryMapping(
                    vendor_profile_id=vendor_profile.id,
                    category_id=category_id
                )
                db.add(mapping)
    
    db.commit()
    db.refresh(vendor_profile)
    
    # Return the updated profile
    return await get_vendor_profile(current_user, db)

@router.delete("/profile")
async def delete_vendor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete vendor profile (deactivate)"""
    # Only vendors can delete their profiles
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can delete vendor profiles"
        )
    
    # Get existing profile
    vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == current_user.id).first()
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Deactivate instead of deleting
    vendor_profile.is_active = False
    vendor_profile.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Vendor profile deactivated successfully"}