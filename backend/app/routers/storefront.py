from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..mongo_models import User, VendorProfile
from ..inventory_models import InventoryItem, InventorySKU, InventoryCategory
from ..auth_simple import verify_token
from datetime import datetime
from beanie import PydanticObjectId

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Pydantic models for storefront
class StorefrontItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: float
    unit: Optional[str] = None
    image_url: Optional[str] = None
    in_stock: bool = True
    quantity_available: int = 0
    lead_time_days: int = 0

class StorefrontResponse(BaseModel):
    vendor_id: int
    vendor_name: str
    business_name: Optional[str] = None  # Add this field for frontend compatibility
    vendor_description: Optional[str] = None
    business_hours: Optional[str] = None
    minimum_order: float = 0.0
    items: List[StorefrontItem] = []
    categories: List[str] = []
    # Additional fields that frontend expects
    tagline: Optional[str] = None
    average_rating: Optional[float] = None
    review_count: Optional[int] = None
    logo_url: Optional[str] = None
    welcome_message: Optional[str] = None
    location: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

# Dependency to get current user from Clerk JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)
    user = await User.find_one(User.username == token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.get("/storefront/{vendor_id}", response_model=StorefrontResponse)
async def get_vendor_storefront(
    vendor_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get vendor storefront with available items"""
    
    # Find the vendor
    vendor = await User.find_one(User.user_id == vendor_id, User.role == "vendor")
    
    if not vendor or not vendor.vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found or inactive"
        )
    
    if not vendor.vendor_profile.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor storefront is not active"
        )
    
    # Get vendor's inventory items
    items = await InventoryItem.find(
        InventoryItem.vendor_id == vendor_id,
        InventoryItem.is_active == True
    ).to_list()
    
    # Convert items to storefront format
    storefront_items = []
    categories = set()
    
    for item in items:
        # Get category name
        category = await InventoryCategory.find_one(InventoryCategory.category_id == item.category_id)
        category_name = category.name if category else "Other"
        categories.add(category_name)
        
        # Get default SKU for pricing and stock info
        default_sku = await InventorySKU.find_one(
            InventorySKU.item_id == item.item_id,
            InventorySKU.vendor_id == vendor_id,
            InventorySKU.is_default == True,
            InventorySKU.is_active == True
        )
        
        if not default_sku:
            # Fallback to any active SKU
            default_sku = await InventorySKU.find_one(
                InventorySKU.item_id == item.item_id,
                InventorySKU.vendor_id == vendor_id,
                InventorySKU.is_active == True
            )
        
        price = default_sku.price if default_sku else item.base_price
        quantity_available = default_sku.current_stock if default_sku else 0
        in_stock = quantity_available > 0
        
        storefront_items.append(StorefrontItem(
            id=item.item_id,
            name=item.name,
            description=item.description,
            brand=item.brand,
            category=category_name,
            price=float(price),
            unit=item.unit_of_measure,
            image_url=item.image_urls[0] if item.image_urls else None,
            in_stock=in_stock,
            quantity_available=quantity_available,
            lead_time_days=item.lead_time_days
        ))
    
    return StorefrontResponse(
        vendor_id=vendor.user_id,
        vendor_name=vendor.name,
        business_name=vendor.name,  # Use vendor name as business name
        vendor_description=vendor.vendor_profile.business_description,
        business_hours=vendor.vendor_profile.business_hours,
        minimum_order=vendor.vendor_profile.minimum_order,
        items=storefront_items,
        categories=sorted(list(categories)),
        # Additional fields for frontend compatibility - only use fields that exist in VendorProfile
        tagline=None,  # Not in VendorProfile model
        average_rating=vendor.vendor_profile.average_rating,
        review_count=vendor.vendor_profile.review_count,
        logo_url=vendor.vendor_profile.logo_url,
        welcome_message=None,  # Not in VendorProfile model
        location=None,  # Not in VendorProfile model
        contact_phone=vendor.phone,  # Use vendor's phone from User model
        contact_email=vendor.email   # Use vendor's email from User model
    )

@router.get("/vendors", response_model=List[dict])
async def get_active_vendors(current_user: User = Depends(get_current_user)):
    """Get list of active vendors for storefront selection"""
    
    vendors = await User.find(
        User.role == "vendor",
        User.is_active == True,
        User.vendor_profile.is_active == True
    ).to_list()
    
    vendor_list = []
    for vendor in vendors:
        # Count available items
        item_count = await InventoryItem.find(
            InventoryItem.vendor_id == vendor.user_id,
            InventoryItem.is_active == True
        ).count()
        
        vendor_list.append({
            "vendor_id": vendor.user_id,
            "name": vendor.name,
            "description": vendor.vendor_profile.business_description,
            "categories": vendor.vendor_profile.categories,
            "minimum_order": vendor.vendor_profile.minimum_order,
            "average_rating": vendor.vendor_profile.average_rating,
            "item_count": item_count,
            "logo_url": vendor.vendor_profile.logo_url
        })
    
    return vendor_list

@router.get("/storefront/{vendor_id}/products", response_model=List[StorefrontItem])
async def get_vendor_products(
    vendor_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get vendor products for storefront"""
    
    # Find the vendor
    vendor = await User.find_one(User.user_id == vendor_id, User.role == "vendor")
    
    if not vendor or not vendor.vendor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found or inactive"
        )
    
    if not vendor.vendor_profile.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor storefront is not active"
        )
    
    # Get vendor's inventory items
    items = await InventoryItem.find(
        InventoryItem.vendor_id == vendor_id,
        InventoryItem.is_active == True
    ).to_list()
    
    # Convert items to storefront format
    storefront_items = []
    
    for item in items:
        # Get category name
        category = await InventoryCategory.find_one(InventoryCategory.category_id == item.category_id)
        category_name = category.name if category else "Other"
        
        # Get default SKU for pricing and stock info
        default_sku = await InventorySKU.find_one(
            InventorySKU.item_id == item.item_id,
            InventorySKU.vendor_id == vendor_id,
            InventorySKU.is_default == True,
            InventorySKU.is_active == True
        )
        
        if not default_sku:
            # Fallback to any active SKU
            default_sku = await InventorySKU.find_one(
                InventorySKU.item_id == item.item_id,
                InventorySKU.vendor_id == vendor_id,
                InventorySKU.is_active == True
            )
        
        price = default_sku.price if default_sku else item.base_price
        quantity_available = default_sku.current_stock if default_sku else 0
        in_stock = quantity_available > 0
        
        storefront_items.append(StorefrontItem(
            id=item.item_id,
            name=item.name,
            description=item.description,
            brand=item.brand,
            category=category_name,
            price=float(price),
            unit=item.unit_of_measure,
            image_url=item.image_urls[0] if item.image_urls else None,
            in_stock=in_stock,
            quantity_available=quantity_available,
            lead_time_days=item.lead_time_days
        ))
    
    return storefront_items