from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from ..mongo_models import User, VendorProfile
from ..inventory_models import InventoryItem, InventorySKU, InventoryCategory
from ..auth_simple import verify_clerk_token
from datetime import datetime
from beanie import PydanticObjectId

router = APIRouter()

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
async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )
    
    token = authorization.split(" ")[1]
    
    try:
        # Verify Clerk token and get user info
        clerk_user_info = verify_clerk_token(token)
        clerk_user_id = clerk_user_info['clerk_user_id']
        
        print(f"🔍 Storefront auth - Clerk user ID: {clerk_user_id}")
        
        # Find user by Clerk user ID
        user = await User.find_one(User.clerk_user_id == clerk_user_id)
        
        if not user:
            # Also try to find by email for account linking
            if clerk_user_info.get('email'):
                user = await User.find_one(User.email == clerk_user_info['email'])
                
                # Update Clerk user ID if found by email
                if user:
                    user.clerk_user_id = clerk_user_id
                    user.auth_provider = "clerk" if user.auth_provider == "local" else "both"
                    await user.save()
        
        if not user:
            # Create a new user from Clerk information
            # Generate a unique user_id (find the highest existing user_id and add 1)
            last_user = await User.find().sort(-User.user_id).limit(1).to_list()
            next_user_id = (last_user[0].user_id + 1) if last_user else 1
            
            # Handle None email from Clerk token
            email = clerk_user_info.get('email')
            if not email:
                email = f"user_{clerk_user_id[-8:]}@example.com"
            
            user = User(
                user_id=next_user_id,
                username=f"user_{clerk_user_id[-8:]}",
                name=clerk_user_info.get('name', 'New User'),
                email=email,
                phone="",
                address="",
                role="restaurant",
                clerk_user_id=clerk_user_id,
                auth_provider="clerk",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            await user.save()
            print(f"🔍 Created new user for storefront: {user.user_id}")
        
        print(f"🔍 Storefront - User: {user.name} (ID: {user.user_id}, Role: {user.role})")
        
        # Check if user account is active
        if not user.is_active and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated. Please contact support."
            )
        
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid token)
        raise
    except Exception as e:
        print(f"❌ Storefront authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

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