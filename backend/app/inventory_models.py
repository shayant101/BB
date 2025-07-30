from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class InventoryCategory(Document):
    """Inventory category document for organizing items"""
    category_id: Indexed(int, unique=True)  # Auto-incrementing ID
    vendor_id: Indexed(int)  # Reference to vendor user_id
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None  # For hierarchical categories
    is_active: bool = True
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "inventory_categories"


class InventoryItem(Document):
    """Inventory item document representing products/services"""
    item_id: Indexed(int, unique=True)  # Auto-incrementing ID
    vendor_id: Indexed(int)  # Reference to vendor user_id
    category_id: Indexed(int)  # Reference to InventoryCategory
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    unit_of_measure: str = "each"  # e.g., "kg", "lbs", "each", "dozen"
    base_price: float = 0.0
    cost_price: Optional[float] = None  # Vendor's cost
    tax_rate: float = 0.0  # Tax percentage
    is_active: bool = True
    is_featured: bool = False
    minimum_order_quantity: int = 1
    maximum_order_quantity: Optional[int] = None
    lead_time_days: int = 0  # Days needed to fulfill order
    
    # Product specifications
    specifications: Dict[str, Any] = {}  # Flexible specs like weight, dimensions, etc.
    tags: List[str] = []  # Searchable tags
    
    # Media
    image_urls: List[str] = []
    document_urls: List[str] = []  # Product sheets, certifications, etc.
    
    # Inventory tracking
    track_inventory: bool = False
    current_stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "inventory_items"


class InventorySKU(Document):
    """SKU (Stock Keeping Unit) document for item variants"""
    sku_id: Indexed(int, unique=True)  # Auto-incrementing ID
    vendor_id: Indexed(int)  # Reference to vendor user_id
    item_id: Indexed(int)  # Reference to InventoryItem
    sku_code: Indexed(str, unique=True)  # Unique SKU identifier
    
    # Variant attributes
    variant_name: Optional[str] = None  # e.g., "Large", "Red", "Pack of 12"
    attributes: Dict[str, str] = {}  # e.g., {"size": "large", "color": "red"}
    
    # Pricing
    price: float
    cost_price: Optional[float] = None
    discount_price: Optional[float] = None
    
    # Inventory
    current_stock: int = 0
    reserved_stock: int = 0  # Stock reserved for pending orders
    available_stock: int = 0  # current_stock - reserved_stock
    low_stock_threshold: int = 0
    
    # Physical attributes
    weight: Optional[float] = None  # in kg
    dimensions: Optional[Dict[str, float]] = None  # {"length": 10, "width": 5, "height": 2}
    
    # Status
    is_active: bool = True
    is_default: bool = False  # Default SKU for the item
    
    # Supplier info
    supplier_sku: Optional[str] = None  # Supplier's SKU code
    supplier_name: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "inventory_skus"


class InventoryCounter(Document):
    """Counter document for auto-incrementing IDs"""
    collection_name: Indexed(str, unique=True)
    sequence_value: int = 0
    
    class Settings:
        name = "inventory_counters"


# Pydantic models for API requests/responses
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    category_id: int
    vendor_id: int
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


class ItemCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    unit_of_measure: str = "each"
    base_price: float
    cost_price: Optional[float] = None
    tax_rate: float = 0.0
    minimum_order_quantity: int = 1
    maximum_order_quantity: Optional[int] = None
    lead_time_days: int = 0
    specifications: Dict[str, Any] = {}
    tags: List[str] = []
    track_inventory: bool = False
    low_stock_threshold: Optional[int] = None


class ItemUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    unit_of_measure: Optional[str] = None
    base_price: Optional[float] = None
    cost_price: Optional[float] = None
    tax_rate: Optional[float] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    minimum_order_quantity: Optional[int] = None
    maximum_order_quantity: Optional[int] = None
    lead_time_days: Optional[int] = None
    specifications: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    track_inventory: Optional[bool] = None
    current_stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None


class ItemResponse(BaseModel):
    item_id: int
    vendor_id: int
    category_id: int
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    unit_of_measure: str
    base_price: float
    cost_price: Optional[float] = None
    tax_rate: float
    is_active: bool
    is_featured: bool
    minimum_order_quantity: int
    maximum_order_quantity: Optional[int] = None
    lead_time_days: int
    specifications: Dict[str, Any]
    tags: List[str]
    image_urls: List[str]
    document_urls: List[str]
    track_inventory: bool
    current_stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class SKUCreate(BaseModel):
    item_id: int
    sku_code: str
    variant_name: Optional[str] = None
    attributes: Dict[str, str] = {}
    price: float
    cost_price: Optional[float] = None
    discount_price: Optional[float] = None
    current_stock: int = 0
    low_stock_threshold: int = 0
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    supplier_sku: Optional[str] = None
    supplier_name: Optional[str] = None
    is_default: bool = False


class SKUUpdate(BaseModel):
    item_id: Optional[int] = None
    sku_code: Optional[str] = None
    variant_name: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    discount_price: Optional[float] = None
    current_stock: Optional[int] = None
    reserved_stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    is_active: Optional[bool] = None
    supplier_sku: Optional[str] = None
    supplier_name: Optional[str] = None
    is_default: Optional[bool] = None


class SKUResponse(BaseModel):
    sku_id: int
    vendor_id: int
    item_id: int
    sku_code: str
    variant_name: Optional[str] = None
    attributes: Dict[str, str]
    price: float
    cost_price: Optional[float] = None
    discount_price: Optional[float] = None
    current_stock: int
    reserved_stock: int
    available_stock: int
    low_stock_threshold: int
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    is_active: bool
    is_default: bool
    supplier_sku: Optional[str] = None
    supplier_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Export all models for easy import
__all__ = [
    "InventoryCategory", 
    "InventoryItem", 
    "InventorySKU",
    "InventoryCounter",
    "CategoryCreate",
    "CategoryUpdate", 
    "CategoryResponse",
    "ItemCreate",
    "ItemUpdate",
    "ItemResponse",
    "SKUCreate",
    "SKUUpdate",
    "SKUResponse"
]