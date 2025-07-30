from typing import List, Optional, Dict, Any
from datetime import datetime
from .inventory_models import (
    InventoryCategory, InventoryItem, InventorySKU, InventoryCounter,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ItemCreate, ItemUpdate, ItemResponse,
    SKUCreate, SKUUpdate, SKUResponse
)
from fastapi import HTTPException, status


class InventoryService:
    """Service layer for inventory management operations"""
    
    @staticmethod
    async def get_next_sequence(collection_name: str) -> int:
        """Get next auto-increment ID for a collection"""
        counter = await InventoryCounter.find_one(
            InventoryCounter.collection_name == collection_name
        )
        
        if not counter:
            # Create new counter
            counter = InventoryCounter(
                collection_name=collection_name,
                sequence_value=1
            )
            await counter.save()
            return 1
        else:
            # Increment and save
            counter.sequence_value += 1
            await counter.save()
            return counter.sequence_value

    # Category operations
    @staticmethod
    async def create_category(vendor_id: int, category_data: CategoryCreate) -> CategoryResponse:
        """Create a new inventory category"""
        # Check if category name already exists for this vendor
        existing = await InventoryCategory.find_one(
            InventoryCategory.vendor_id == vendor_id,
            InventoryCategory.name == category_data.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        
        # Validate parent category if specified
        if category_data.parent_category_id:
            parent = await InventoryCategory.find_one(
                InventoryCategory.category_id == category_data.parent_category_id,
                InventoryCategory.vendor_id == vendor_id
            )
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category not found"
                )
        
        category_id = await InventoryService.get_next_sequence("inventory_categories")
        
        category = InventoryCategory(
            category_id=category_id,
            vendor_id=vendor_id,
            **category_data.dict()
        )
        await category.save()
        
        return CategoryResponse(**category.dict())

    @staticmethod
    async def get_categories(vendor_id: int, include_inactive: bool = False) -> List[CategoryResponse]:
        """Get all categories for a vendor"""
        query_conditions = [InventoryCategory.vendor_id == vendor_id]
        if not include_inactive:
            query_conditions.append(InventoryCategory.is_active == True)
        
        categories = await InventoryCategory.find(*query_conditions).sort(+InventoryCategory.sort_order).to_list()
        return [CategoryResponse(**cat.dict()) for cat in categories]

    @staticmethod
    async def get_category(vendor_id: int, category_id: int) -> CategoryResponse:
        """Get a specific category"""
        category = await InventoryCategory.find_one(
            InventoryCategory.category_id == category_id,
            InventoryCategory.vendor_id == vendor_id
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return CategoryResponse(**category.dict())

    @staticmethod
    async def update_category(vendor_id: int, category_id: int, category_data: CategoryUpdate) -> CategoryResponse:
        """Update a category"""
        category = await InventoryCategory.find_one(
            InventoryCategory.category_id == category_id,
            InventoryCategory.vendor_id == vendor_id
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check for name conflicts if name is being updated
        if category_data.name and category_data.name != category.name:
            existing = await InventoryCategory.find_one(
                InventoryCategory.vendor_id == vendor_id,
                InventoryCategory.name == category_data.name,
                InventoryCategory.category_id != category_id
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists"
                )
        
        # Validate parent category if being updated
        if category_data.parent_category_id:
            parent = await InventoryCategory.find_one(
                InventoryCategory.category_id == category_data.parent_category_id,
                InventoryCategory.vendor_id == vendor_id
            )
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category not found"
                )
        
        # Update fields
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        category.updated_at = datetime.utcnow()
        await category.save()
        
        return CategoryResponse(**category.dict())

    @staticmethod
    async def delete_category(vendor_id: int, category_id: int) -> bool:
        """Delete a category (soft delete by setting is_active=False)"""
        category = await InventoryCategory.find_one(
            InventoryCategory.category_id == category_id,
            InventoryCategory.vendor_id == vendor_id
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Check if category has items
        items_count = await InventoryItem.find(
            InventoryItem.category_id == category_id,
            InventoryItem.vendor_id == vendor_id,
            InventoryItem.is_active == True
        ).count()
        
        if items_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with active items"
            )
        
        category.is_active = False
        category.updated_at = datetime.utcnow()
        await category.save()
        return True

    # Item operations
    @staticmethod
    async def create_item(vendor_id: int, item_data: ItemCreate) -> ItemResponse:
        """Create a new inventory item"""
        # Validate category exists
        category = await InventoryCategory.find_one(
            InventoryCategory.category_id == item_data.category_id,
            InventoryCategory.vendor_id == vendor_id,
            InventoryCategory.is_active == True
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or inactive"
            )
        
        item_id = await InventoryService.get_next_sequence("inventory_items")
        
        item = InventoryItem(
            item_id=item_id,
            vendor_id=vendor_id,
            **item_data.dict()
        )
        await item.save()
        
        return ItemResponse(**item.dict())

    @staticmethod
    async def get_items(
        vendor_id: int, 
        category_id: Optional[int] = None,
        include_inactive: bool = False,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ItemResponse]:
        """Get items for a vendor with optional filtering"""
        query_conditions = [InventoryItem.vendor_id == vendor_id]
        
        if category_id:
            query_conditions.append(InventoryItem.category_id == category_id)
        
        if not include_inactive:
            query_conditions.append(InventoryItem.is_active == True)
        
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            query_conditions.append({
                "$or": [
                    {"name": search_regex},
                    {"description": search_regex},
                    {"brand": search_regex},
                    {"tags": search_regex}
                ]
            })
        
        items = await InventoryItem.find(*query_conditions).skip(skip).limit(limit).to_list()
        return [ItemResponse(**item.dict()) for item in items]

    @staticmethod
    async def get_item(vendor_id: int, item_id: int) -> ItemResponse:
        """Get a specific item"""
        item = await InventoryItem.find_one(
            InventoryItem.item_id == item_id,
            InventoryItem.vendor_id == vendor_id
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return ItemResponse(**item.dict())

    @staticmethod
    async def update_item(vendor_id: int, item_id: int, item_data: ItemUpdate) -> ItemResponse:
        """Update an item"""
        item = await InventoryItem.find_one(
            InventoryItem.item_id == item_id,
            InventoryItem.vendor_id == vendor_id
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Validate category if being updated
        if item_data.category_id and item_data.category_id != item.category_id:
            category = await InventoryCategory.find_one(
                InventoryCategory.category_id == item_data.category_id,
                InventoryCategory.vendor_id == vendor_id,
                InventoryCategory.is_active == True
            )
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found or inactive"
                )
        
        # Update fields
        update_data = item_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        item.updated_at = datetime.utcnow()
        await item.save()
        
        return ItemResponse(**item.dict())

    @staticmethod
    async def delete_item(vendor_id: int, item_id: int) -> bool:
        """Delete an item (soft delete by setting is_active=False)"""
        item = await InventoryItem.find_one(
            InventoryItem.item_id == item_id,
            InventoryItem.vendor_id == vendor_id
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Check if item has active SKUs
        skus_count = await InventorySKU.find(
            InventorySKU.item_id == item_id,
            InventorySKU.vendor_id == vendor_id,
            InventorySKU.is_active == True
        ).count()
        
        if skus_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete item with active SKUs"
            )
        
        item.is_active = False
        item.updated_at = datetime.utcnow()
        await item.save()
        return True

    # SKU operations
    @staticmethod
    async def create_sku(vendor_id: int, sku_data: SKUCreate) -> SKUResponse:
        """Create a new SKU"""
        # Validate item exists
        item = await InventoryItem.find_one(
            InventoryItem.item_id == sku_data.item_id,
            InventoryItem.vendor_id == vendor_id,
            InventoryItem.is_active == True
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item not found or inactive"
            )
        
        # Check if SKU code already exists
        existing = await InventorySKU.find_one(
            InventorySKU.sku_code == sku_data.sku_code
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU code already exists"
            )
        
        sku_id = await InventoryService.get_next_sequence("inventory_skus")
        
        sku = InventorySKU(
            sku_id=sku_id,
            vendor_id=vendor_id,
            available_stock=sku_data.current_stock,  # Initially all stock is available
            **sku_data.dict()
        )
        await sku.save()
        
        return SKUResponse(**sku.dict())

    @staticmethod
    async def get_skus(
        vendor_id: int,
        item_id: Optional[int] = None,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[SKUResponse]:
        """Get SKUs for a vendor with optional filtering"""
        query_conditions = [InventorySKU.vendor_id == vendor_id]
        
        if item_id:
            query_conditions.append(InventorySKU.item_id == item_id)
        
        if not include_inactive:
            query_conditions.append(InventorySKU.is_active == True)
        
        skus = await InventorySKU.find(*query_conditions).skip(skip).limit(limit).to_list()
        return [SKUResponse(**sku.dict()) for sku in skus]

    @staticmethod
    async def get_sku(vendor_id: int, sku_id: int) -> SKUResponse:
        """Get a specific SKU"""
        sku = await InventorySKU.find_one(
            InventorySKU.sku_id == sku_id,
            InventorySKU.vendor_id == vendor_id
        )
        if not sku:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SKU not found"
            )
        return SKUResponse(**sku.dict())

    @staticmethod
    async def update_sku(vendor_id: int, sku_id: int, sku_data: SKUUpdate) -> SKUResponse:
        """Update a SKU"""
        sku = await InventorySKU.find_one(
            InventorySKU.sku_id == sku_id,
            InventorySKU.vendor_id == vendor_id
        )
        if not sku:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SKU not found"
            )
        
        # Check for SKU code conflicts if being updated
        if sku_data.sku_code and sku_data.sku_code != sku.sku_code:
            existing = await InventorySKU.find_one(
                InventorySKU.sku_code == sku_data.sku_code,
                InventorySKU.sku_id != sku_id
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU code already exists"
                )
        
        # Update fields
        update_data = sku_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sku, field, value)
        
        # Recalculate available stock if current_stock or reserved_stock changed
        if 'current_stock' in update_data or 'reserved_stock' in update_data:
            sku.available_stock = sku.current_stock - sku.reserved_stock
        
        sku.updated_at = datetime.utcnow()
        await sku.save()
        
        return SKUResponse(**sku.dict())

    @staticmethod
    async def delete_sku(vendor_id: int, sku_id: int) -> bool:
        """Delete a SKU (soft delete by setting is_active=False)"""
        sku = await InventorySKU.find_one(
            InventorySKU.sku_id == sku_id,
            InventorySKU.vendor_id == vendor_id
        )
        if not sku:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SKU not found"
            )
        
        sku.is_active = False
        sku.updated_at = datetime.utcnow()
        await sku.save()
        return True

    @staticmethod
    async def update_stock(vendor_id: int, sku_id: int, quantity_change: int, operation: str = "set") -> SKUResponse:
        """Update SKU stock levels"""
        sku = await InventorySKU.find_one(
            InventorySKU.sku_id == sku_id,
            InventorySKU.vendor_id == vendor_id
        )
        if not sku:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SKU not found"
            )
        
        if operation == "add":
            sku.current_stock += quantity_change
        elif operation == "subtract":
            sku.current_stock = max(0, sku.current_stock - quantity_change)
        elif operation == "set":
            sku.current_stock = max(0, quantity_change)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid operation. Use 'add', 'subtract', or 'set'"
            )
        
        sku.available_stock = sku.current_stock - sku.reserved_stock
        sku.updated_at = datetime.utcnow()
        await sku.save()
        
        return SKUResponse(**sku.dict())