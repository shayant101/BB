from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from pydantic import BaseModel
from ..mongo_models import User, VendorCategory
from ..inventory_models import InventoryItem, InventorySKU, InventoryCategory
from ..comparison_models import (
    ComparisonRequest,
    ComparisonResponse,
    ProductComparisonResult,
    VendorResult,
    PricingDetails,
    Availability,
    PerformanceMetrics,
    Recommendation,
    ComparisonSummary,
    SmartSuggestion
)
from beanie import PydanticObjectId
from bson import ObjectId
from ..auth_simple import verify_token, TokenData, verify_clerk_token
from datetime import datetime
import math
import uuid
import time

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

# Dependency to get current user from Clerk JWT token
async def get_current_user(authorization: str = Header(None)):
    print(f"🔍 Marketplace auth check - Authorization header: {authorization[:50] if authorization else 'None'}...")
    
    if not authorization or not authorization.startswith("Bearer "):
        print("❌ Authorization header missing or invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )
    
    token = authorization.split(" ")[1]
    print(f"🔍 Extracted token: {token[:20]}...")
    
    try:
        # Verify Clerk token and get user info
        print("🔍 Attempting to verify Clerk token...")
        clerk_user_info = verify_clerk_token(token)
        print(f"✅ Clerk token verified: {clerk_user_info}")
        
        clerk_user_id = clerk_user_info['clerk_user_id']
        print(f"🔍 Looking for user with Clerk ID: {clerk_user_id}")
        
        # Find user by Clerk user ID
        user = await User.find_one(User.clerk_user_id == clerk_user_id)
        print(f"🔍 User found by Clerk ID: {user is not None}")
        
        if not user:
            # Also try to find by email for account linking
            if clerk_user_info.get('email'):
                print(f"🔍 Trying to find user by email: {clerk_user_info['email']}")
                user = await User.find_one(User.email == clerk_user_info['email'])
                print(f"🔍 User found by email: {user is not None}")
                
                # Update Clerk user ID if found by email
                if user:
                    print(f"🔧 Linking user account with Clerk ID")
                    user.clerk_user_id = clerk_user_id
                    user.auth_provider = "clerk" if user.auth_provider == "local" else "both"
                    await user.save()
                    print(f"✅ User account linked successfully")
        
        if not user:
            print("🔧 User not found in database, creating new user from Clerk data...")
            
            # Generate a unique user_id (find the highest existing user_id and add 1)
            last_user = await User.find().sort(-User.user_id).limit(1).to_list()
            next_user_id = (last_user[0].user_id + 1) if last_user else 1
            
            # Create new user with Clerk data
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
            print(f"✅ New user created successfully: {user.name} (ID: {user.user_id})")
        
        # Check if user account is active
        if not user.is_active and user.role != "admin":
            print("❌ User account is deactivated")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated. Please contact support."
            )
        
        print(f"✅ Authentication successful for user: {user.name} ({user.role})")
        return user
        
    except HTTPException as e:
        print(f"❌ HTTP Exception during auth: {e.detail}")
        # Re-raise HTTP exceptions (like invalid token)
        raise
    except Exception as e:
        print(f"❌ Marketplace authentication error: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

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

# Helper functions for price comparison
async def search_products_by_query(query: str, category: str = None, brand: str = None) -> List[InventoryItem]:
    """Search for products matching the query parameters"""
    query_conditions = [InventoryItem.is_active == True]
    
    # Filter by name (case-insensitive partial match)
    if query:
        search_regex = {"$regex": query, "$options": "i"}
        query_conditions.append(
            {
                "$or": [
                    {"name": search_regex},
                    {"description": search_regex},
                    {"tags": search_regex}
                ]
            }
        )
    
    # Filter by category if provided
    if category:
        # First find matching categories
        categories = await InventoryCategory.find(
            InventoryCategory.name.regex(category, "i"),
            InventoryCategory.is_active == True
        ).to_list()
        
        if categories:
            category_ids = [cat.category_id for cat in categories]
            query_conditions.append(InventoryItem.category_id.in_(category_ids))
    
    # Filter by brand if provided
    if brand:
        query_conditions.append(InventoryItem.brand.regex(brand, "i"))
    
    return await InventoryItem.find(*query_conditions).to_list()

async def create_vendor_result(item: InventoryItem, vendor: User) -> VendorResult:
    """Create a VendorResult from database models"""
    # Get category name
    category = await InventoryCategory.find_one(InventoryCategory.category_id == item.category_id)
    category_name = category.name if category else "Unknown"
    
    # Get SKUs for this item to find pricing
    skus = await InventorySKU.find(
        InventorySKU.item_id == item.item_id,
        InventorySKU.vendor_id == item.vendor_id,
        InventorySKU.is_active == True
    ).to_list()
    
    # Use the default SKU or first available SKU for pricing
    default_sku = next((sku for sku in skus if sku.is_default), skus[0] if skus else None)
    unit_price = default_sku.price if default_sku else item.base_price
    
    # Mock pricing details
    pricing = PricingDetails(
        unit_price=float(unit_price),
        total_cost=float(unit_price),
        delivery_fee=5.99,
        tax_rate=0.08
    )
    
    # Mock availability based on SKU data
    availability = Availability(
        in_stock=default_sku.current_stock > 0 if default_sku else True,
        quantity_available=default_sku.current_stock if default_sku else 100,
        lead_time_days=item.lead_time_days
    )
    
    return VendorResult(
        vendor_id=str(vendor.user_id),
        vendor_name=vendor.name,
        product_id=str(item.item_id),
        product_name=item.name,
        brand=item.brand,
        category=category_name,
        pricing=pricing,
        availability=availability,
        vendor_rating=vendor.vendor_profile.average_rating if vendor.vendor_profile else 4.5,
        delivery_time="1-2 business days",
        minimum_order=vendor.vendor_profile.minimum_order if vendor.vendor_profile else 50.0,
        certifications=["Organic", "FDA Approved"]  # Mocked certifications
    )

def generate_mock_recommendations(vendors: List[VendorResult]) -> List[Recommendation]:
    """Generate mock recommendations based on vendor results"""
    recommendations = []
    
    if vendors:
        # Find the vendor with the best price
        best_price_vendor = min(vendors, key=lambda v: v.pricing.unit_price)
        recommendations.append(Recommendation(
            vendor_id=best_price_vendor.vendor_id,
            reason="Best price available with good rating",
            confidence_score=0.85,
            potential_savings=10.50
        ))
        
        # Find highly rated vendor
        best_rated_vendor = max(vendors, key=lambda v: v.vendor_rating or 0)
        if best_rated_vendor.vendor_id != best_price_vendor.vendor_id:
            recommendations.append(Recommendation(
                vendor_id=best_rated_vendor.vendor_id,
                reason="Highest rated vendor with reliable service",
                confidence_score=0.78,
                potential_savings=5.25
            ))
    
    return recommendations

def generate_smart_suggestions(results: List[ProductComparisonResult]) -> List[SmartSuggestion]:
    """Generate smart suggestions based on comparison results"""
    suggestions = []
    
    # Bundle suggestion
    if len(results) > 1:
        suggestions.append(SmartSuggestion(
            type="bundle",
            title="Bundle Discount Available",
            description="Order all items from the same vendor to save on delivery fees",
            potential_savings=15.99,
            confidence_score=0.72
        ))
    
    # Alternative product suggestion
    suggestions.append(SmartSuggestion(
        type="alternative",
        title="Similar Product Available",
        description="Consider this similar product with better pricing",
        potential_savings=8.50,
        confidence_score=0.65
    ))
    
    return suggestions

@router.post("/compare-prices", response_model=ComparisonResponse)
async def compare_prices(request: ComparisonRequest, current_user: User = Depends(get_current_user)):
    """
    Compare prices across vendors for the requested products
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        results = []
        all_vendors = set()
        total_products_found = 0
        
        # Process each product query
        for product_query in request.products:
            # Search for matching products
            products = await search_products_by_query(
                product_query.name,
                product_query.category,
                product_query.brand
            )
            
            vendor_results = []
            
            # Create vendor results for each matching product
            for product in products:
                # Get vendor information
                vendor = await User.find_one(
                    User.user_id == product.vendor_id,
                    User.role == "vendor",
                    User.is_active == True
                )
                
                if vendor and vendor.vendor_profile and vendor.vendor_profile.is_active:
                    vendor_result = await create_vendor_result(product, vendor)
                    
                    # Apply filters if provided
                    if request.filters:
                        # Price filters
                        if request.filters.max_price and vendor_result.pricing.unit_price > request.filters.max_price:
                            continue
                        if request.filters.min_price and vendor_result.pricing.unit_price < request.filters.min_price:
                            continue
                        
                        # Vendor filter
                        if request.filters.vendors and vendor_result.vendor_id not in request.filters.vendors:
                            continue
                        
                        # Rating filter
                        if request.filters.min_rating and (vendor_result.vendor_rating or 0) < request.filters.min_rating:
                            continue
                    
                    vendor_results.append(vendor_result)
                    all_vendors.add(vendor_result.vendor_id)
                    total_products_found += 1
            
            # Sort results based on filters
            if request.filters and request.filters.sort_by:
                if request.filters.sort_by == "price_low_to_high":
                    vendor_results.sort(key=lambda v: v.pricing.unit_price)
                elif request.filters.sort_by == "price_high_to_low":
                    vendor_results.sort(key=lambda v: v.pricing.unit_price, reverse=True)
                elif request.filters.sort_by == "rating":
                    vendor_results.sort(key=lambda v: v.vendor_rating or 0, reverse=True)
            
            # Calculate comparison metrics
            best_price_vendor = None
            average_price = None
            price_range = None
            
            if vendor_results:
                prices = [v.pricing.unit_price for v in vendor_results]
                best_price_vendor = min(vendor_results, key=lambda v: v.pricing.unit_price).vendor_id
                average_price = sum(prices) / len(prices)
                price_range = {"min": min(prices), "max": max(prices)}
            
            # Create product comparison result
            product_result = ProductComparisonResult(
                query=product_query,
                vendors=vendor_results,
                best_price_vendor=best_price_vendor,
                average_price=average_price,
                price_range=price_range
            )
            
            results.append(product_result)
        
        # Calculate performance metrics
        end_time = time.time()
        performance_metrics = PerformanceMetrics(
            search_time_ms=int((end_time - start_time) * 1000),
            vendors_searched=len(all_vendors),
            products_found=total_products_found,
            cache_hit_rate=0.0  # No caching implemented yet
        )
        
        # Generate recommendations if requested
        recommendations = []
        if request.include_recommendations:
            all_vendor_results = []
            for result in results:
                all_vendor_results.extend(result.vendors)
            recommendations = generate_mock_recommendations(all_vendor_results)
        
        # Create comparison summary
        summary = ComparisonSummary(
            total_products_compared=len(request.products),
            total_vendors=len(all_vendors),
            average_savings_potential=12.75,  # Mocked value
            best_overall_vendor=recommendations[0].vendor_id if recommendations else None
        )
        
        # Generate smart suggestions
        smart_suggestions = generate_smart_suggestions(results) if request.include_recommendations else []
        
        # Create response
        response = ComparisonResponse(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            results=results,
            performance_metrics=performance_metrics,
            recommendations=recommendations,
            summary=summary,
            smart_suggestions=smart_suggestions
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing comparison request: {str(e)}")