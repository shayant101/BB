from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from pydantic import BaseModel
from ..database import get_db
from ..models import User, VendorProfile, VendorCategory, VendorCategoryMapping
from ..auth_simple import verify_token
from datetime import datetime

router = APIRouter()

# Pydantic models for marketplace
class VendorCategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    parent_category: str
    sort_order: int
    vendor_count: int = 0

class VendorListingResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    phone: str
    address: str
    description: str
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
    website_url: str
    established_year: str
    categories: List[str]

class VendorDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    phone: str
    address: str
    description: str
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

class VendorSearchResponse(BaseModel):
    vendors: List[VendorListingResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

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

@router.get("/categories", response_model=List[VendorCategoryResponse])
async def get_vendor_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all vendor categories with vendor counts"""
    # Only restaurants can view marketplace
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can access marketplace"
        )
    
    # Get categories with vendor counts
    categories = db.query(VendorCategory).filter(VendorCategory.is_active == True).order_by(VendorCategory.sort_order).all()
    
    result = []
    for category in categories:
        # Count active vendors in this category
        vendor_count = db.query(VendorCategoryMapping).join(VendorProfile).join(User).filter(
            and_(
                VendorCategoryMapping.category_id == category.id,
                VendorProfile.is_active == True,
                User.role == "vendor"
            )
        ).count()
        
        result.append(VendorCategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description or "",
            icon=category.icon or "",
            parent_category=category.parent_category or "",
            sort_order=category.sort_order,
            vendor_count=vendor_count
        ))
    
    return result

@router.get("/vendors", response_model=VendorSearchResponse)
async def get_marketplace_vendors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filter by category name"),
    search: Optional[str] = Query(None, description="Search vendor names and descriptions"),
    location: Optional[str] = Query(None, description="Filter by delivery area"),
    rating_min: Optional[float] = Query(None, description="Minimum rating filter"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get paginated list of vendors with filtering and search"""
    # Only restaurants can view marketplace
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can access marketplace"
        )
    
    # Base query
    query = db.query(VendorProfile).join(User).filter(User.role == "vendor")
    
    # Apply filters
    if is_active is not None:
        query = query.filter(VendorProfile.is_active == is_active)
    
    if rating_min is not None:
        query = query.filter(VendorProfile.average_rating >= rating_min)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.description.ilike(search_term),
                VendorProfile.business_description.ilike(search_term),
                VendorProfile.business_type.ilike(search_term)
            )
        )
    
    if location:
        location_term = f"%{location}%"
        query = query.filter(VendorProfile.delivery_areas.ilike(location_term))
    
    if category:
        # Filter by category name
        query = query.join(VendorCategoryMapping).join(VendorCategory).filter(
            VendorCategory.name == category
        )
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    vendors = query.options(joinedload(VendorProfile.user), joinedload(VendorProfile.categories)).offset(offset).limit(page_size).all()
    
    # Format response
    vendor_listings = []
    for vendor_profile in vendors:
        # Get category names
        category_names = [mapping.category.name for mapping in vendor_profile.categories]
        
        vendor_listings.append(VendorListingResponse(
            id=vendor_profile.id,
            user_id=vendor_profile.user.id,
            name=vendor_profile.user.name,
            email=vendor_profile.user.email,
            phone=vendor_profile.user.phone,
            address=vendor_profile.user.address,
            description=vendor_profile.user.description or "",
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
            website_url=vendor_profile.website_url or "",
            established_year=vendor_profile.established_year or "",
            categories=category_names
        ))
    
    total_pages = (total_count + page_size - 1) // page_size
    
    return VendorSearchResponse(
        vendors=vendor_listings,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/vendors/{vendor_id}", response_model=VendorDetailResponse)
async def get_vendor_detail(
    vendor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed vendor information"""
    # Only restaurants can view marketplace
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can access marketplace"
        )
    
    # Get vendor profile with relationships
    vendor_profile = db.query(VendorProfile).options(
        joinedload(VendorProfile.user),
        joinedload(VendorProfile.categories).joinedload(VendorCategoryMapping.category)
    ).filter(VendorProfile.id == vendor_id).first()
    
    if not vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    # Format categories with full info
    categories = []
    for mapping in vendor_profile.categories:
        categories.append({
            "id": mapping.category.id,
            "name": mapping.category.name,
            "icon": mapping.category.icon,
            "parent_category": mapping.category.parent_category
        })
    
    return VendorDetailResponse(
        id=vendor_profile.id,
        user_id=vendor_profile.user.id,
        name=vendor_profile.user.name,
        email=vendor_profile.user.email,
        phone=vendor_profile.user.phone,
        address=vendor_profile.user.address,
        description=vendor_profile.user.description or "",
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

@router.get("/search", response_model=VendorSearchResponse)
async def search_vendors(
    q: str = Query(..., description="Search query"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Advanced vendor search with relevance scoring"""
    # Only restaurants can search marketplace
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can access marketplace"
        )
    
    # Use the main vendors endpoint with search parameter
    return await get_marketplace_vendors(
        current_user=current_user,
        db=db,
        search=q,
        category=category,
        location=None,
        rating_min=None,
        is_active=True,
        page=page,
        page_size=page_size
    )