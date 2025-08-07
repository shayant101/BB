from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from pydantic import BaseModel
from ..mongo_models import User, VendorCategory
from beanie import PydanticObjectId
from bson import ObjectId
from ..auth_simple import verify_token, TokenData
from datetime import datetime
import math

router = APIRouter()

# Pydantic models for marketplace
class VendorCategoryResponse(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_category: Optional[str] = None
    sort_order: int
    vendor_count: int = 0

class VendorListingResponse(BaseModel):
    id: PydanticObjectId
    user_id: int
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None
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
    website_url: Optional[str] = None
    established_year: Optional[str] = None
    categories: List[str] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            PydanticObjectId: str
        }

class VendorDetailResponse(VendorListingResponse):
    gallery_images: List[str] = []
    business_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class VendorSearchResponse(BaseModel):
    vendors: List[VendorListingResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

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

@router.get("/categories", response_model=List[VendorCategoryResponse])
async def get_vendor_categories(current_user: User = Depends(get_current_user)):
    """Get all vendor categories with vendor counts"""
    
    categories = await VendorCategory.find(VendorCategory.is_active == True).sort(+VendorCategory.sort_order).to_list()
    
    result = []
    for category in categories:
        vendor_count = await User.find(
            User.role == "vendor",
            User.vendor_profile.is_active == True,
            User.vendor_profile.categories == category.name
        ).count()
        
        result.append(VendorCategoryResponse(
            category_id=category.category_id,
            name=category.name,
            description=category.description,
            icon=category.icon,
            parent_category=category.parent_category,
            sort_order=category.sort_order,
            vendor_count=vendor_count
        ))
    
    return result

@router.get("/vendors", response_model=VendorSearchResponse)
async def get_marketplace_vendors(
    current_user: User = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filter by category name"),
    search: Optional[str] = Query(None, description="Search vendor names and descriptions"),
    rating_min: Optional[float] = Query(None, description="Minimum rating filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(12, ge=1, le=100, description="Items per page")
):
    """Get paginated list of vendors with filtering and search"""

    # Build the query
    query_conditions = [
        User.role == "vendor",
        User.vendor_profile.is_active == True
    ]

    if category:
        query_conditions.append(User.vendor_profile.categories == category)
    
    if rating_min is not None:
        query_conditions.append(User.vendor_profile.average_rating >= rating_min)

    if search:
        search_regex = {"$regex": search, "$options": "i"}
        query_conditions.append(
            {
                "$or": [
                    {"name": search_regex},
                    {"description": search_regex},
                    {"vendor_profile.business_description": search_regex},
                    {"vendor_profile.specialties": search_regex}
                ]
            }
        )

    # Get total count before pagination
    total_count = await User.find(*query_conditions).count()

    # Apply pagination
    skip = (page - 1) * page_size
    vendors = await User.find(*query_conditions).skip(skip).limit(page_size).to_list()

    # Format response
    vendor_listings = [
        VendorListingResponse(
            id=v.id,
            user_id=v.user_id,
            name=v.name,
            email=v.email,
            phone=v.phone,
            address=v.address,
            description=v.description,
            **v.vendor_profile.dict()
        ) for v in vendors
    ]

    total_pages = math.ceil(total_count / page_size)

    return VendorSearchResponse(
        vendors=vendor_listings,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/vendors/{user_id}", response_model=VendorDetailResponse)
async def get_vendor_detail(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get detailed vendor information"""

    vendor = await User.find_one(User.user_id == user_id, User.role == "vendor")

    if not vendor or not vendor.vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )

    return VendorDetailResponse(
        id=vendor.id,
        user_id=vendor.user_id,
        name=vendor.name,
        email=vendor.email,
        phone=vendor.phone,
        address=vendor.address,
        description=vendor.description,
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
        **vendor.vendor_profile.dict()
    )