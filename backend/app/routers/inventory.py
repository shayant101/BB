from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from ..mongo_models import User
from ..auth_simple import verify_token
from ..inventory_service import InventoryService
from ..inventory_models import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ItemCreate, ItemUpdate, ItemResponse,
    SKUCreate, SKUUpdate, SKUResponse
)

router = APIRouter()

# Dependency to get current vendor user from JWT token
async def get_current_vendor(authorization: str = Header(None)):
    """Get current authenticated vendor user"""
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
    
    if user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access inventory management"
        )
    
    return user

# Category endpoints
@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_vendor)
):
    """Create a new inventory category"""
    return await InventoryService.create_category(current_user.user_id, category_data)

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    include_inactive: bool = Query(False, description="Include inactive categories"),
    current_user: User = Depends(get_current_vendor)
):
    """Get all categories for the current vendor"""
    return await InventoryService.get_categories(current_user.user_id, include_inactive)

@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_vendor)
):
    """Get a specific category"""
    return await InventoryService.get_category(current_user.user_id, category_id)

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_vendor)
):
    """Update a category"""
    return await InventoryService.update_category(current_user.user_id, category_id, category_data)

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_vendor)
):
    """Delete a category (soft delete)"""
    await InventoryService.delete_category(current_user.user_id, category_id)

# Item endpoints
@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(get_current_vendor)
):
    """Create a new inventory item"""
    return await InventoryService.create_item(current_user.user_id, item_data)

@router.get("/items", response_model=List[ItemResponse])
async def get_items(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    include_inactive: bool = Query(False, description="Include inactive items"),
    search: Optional[str] = Query(None, description="Search items by name, description, brand, or tags"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    current_user: User = Depends(get_current_vendor)
):
    """Get items for the current vendor with optional filtering"""
    return await InventoryService.get_items(
        current_user.user_id, category_id, include_inactive, search, skip, limit
    )

@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    current_user: User = Depends(get_current_vendor)
):
    """Get a specific item"""
    return await InventoryService.get_item(current_user.user_id, item_id)

@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user: User = Depends(get_current_vendor)
):
    """Update an item"""
    return await InventoryService.update_item(current_user.user_id, item_id, item_data)

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_vendor)
):
    """Delete an item (soft delete)"""
    await InventoryService.delete_item(current_user.user_id, item_id)

# SKU endpoints
@router.post("/skus", response_model=SKUResponse, status_code=status.HTTP_201_CREATED)
async def create_sku(
    sku_data: SKUCreate,
    current_user: User = Depends(get_current_vendor)
):
    """Create a new SKU"""
    return await InventoryService.create_sku(current_user.user_id, sku_data)

@router.get("/skus", response_model=List[SKUResponse])
async def get_skus(
    item_id: Optional[int] = Query(None, description="Filter by item ID"),
    include_inactive: bool = Query(False, description="Include inactive SKUs"),
    skip: int = Query(0, ge=0, description="Number of SKUs to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of SKUs to return"),
    current_user: User = Depends(get_current_vendor)
):
    """Get SKUs for the current vendor with optional filtering"""
    return await InventoryService.get_skus(
        current_user.user_id, item_id, include_inactive, skip, limit
    )

@router.get("/skus/{sku_id}", response_model=SKUResponse)
async def get_sku(
    sku_id: int,
    current_user: User = Depends(get_current_vendor)
):
    """Get a specific SKU"""
    return await InventoryService.get_sku(current_user.user_id, sku_id)

@router.put("/skus/{sku_id}", response_model=SKUResponse)
async def update_sku(
    sku_id: int,
    sku_data: SKUUpdate,
    current_user: User = Depends(get_current_vendor)
):
    """Update a SKU"""
    return await InventoryService.update_sku(current_user.user_id, sku_id, sku_data)

@router.delete("/skus/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sku(
    sku_id: int,
    current_user: User = Depends(get_current_vendor)
):
    """Delete a SKU (soft delete)"""
    await InventoryService.delete_sku(current_user.user_id, sku_id)

# Stock management endpoints
@router.patch("/skus/{sku_id}/stock", response_model=SKUResponse)
async def update_stock(
    sku_id: int,
    quantity_change: int = Query(..., description="Quantity to change (positive or negative)"),
    operation: str = Query("set", regex="^(add|subtract|set)$", description="Operation: add, subtract, or set"),
    current_user: User = Depends(get_current_vendor)
):
    """Update SKU stock levels"""
    return await InventoryService.update_stock(current_user.user_id, sku_id, quantity_change, operation)

# Bulk operations
@router.get("/items/{item_id}/skus", response_model=List[SKUResponse])
async def get_item_skus(
    item_id: int,
    include_inactive: bool = Query(False, description="Include inactive SKUs"),
    current_user: User = Depends(get_current_vendor)
):
    """Get all SKUs for a specific item"""
    return await InventoryService.get_skus(
        current_user.user_id, item_id, include_inactive
    )

@router.get("/categories/{category_id}/items", response_model=List[ItemResponse])
async def get_category_items(
    category_id: int,
    include_inactive: bool = Query(False, description="Include inactive items"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    current_user: User = Depends(get_current_vendor)
):
    """Get all items for a specific category"""
    return await InventoryService.get_items(
        current_user.user_id, category_id, include_inactive, None, skip, limit
    )

# Dashboard/summary endpoints
@router.get("/summary")
async def get_inventory_summary(
    current_user: User = Depends(get_current_vendor)
):
    """Get inventory summary statistics"""
    from ..inventory_models import InventoryCategory, InventoryItem, InventorySKU
    
    # Get counts
    categories_count = await InventoryCategory.find(
        InventoryCategory.vendor_id == current_user.user_id,
        InventoryCategory.is_active == True
    ).count()
    
    items_count = await InventoryItem.find(
        InventoryItem.vendor_id == current_user.user_id,
        InventoryItem.is_active == True
    ).count()
    
    skus_count = await InventorySKU.find(
        InventorySKU.vendor_id == current_user.user_id,
        InventorySKU.is_active == True
    ).count()
    
    # Get low stock SKUs
    low_stock_skus = await InventorySKU.find(
        InventorySKU.vendor_id == current_user.user_id,
        InventorySKU.is_active == True,
        InventorySKU.current_stock <= InventorySKU.low_stock_threshold
    ).count()
    
    # Get total inventory value (based on cost price)
    skus = await InventorySKU.find(
        InventorySKU.vendor_id == current_user.user_id,
        InventorySKU.is_active == True
    ).to_list()
    
    total_inventory_value = sum(
        (sku.cost_price or sku.price) * sku.current_stock 
        for sku in skus
    )
    
    return {
        "categories_count": categories_count,
        "items_count": items_count,
        "skus_count": skus_count,
        "low_stock_alerts": low_stock_skus,
        "total_inventory_value": round(total_inventory_value, 2)
    }