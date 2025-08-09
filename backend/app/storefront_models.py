from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class VendorStorefront(Document):
    """Vendor storefront configuration and branding"""
    vendor_id: Indexed(int, unique=True)
    logo_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    brand_colors: Dict[str, str] = {}  # e.g., {"primary": "#FFFFFF", "secondary": "#000000"}
    layout_template: str = "default"
    custom_css: Optional[str] = None
    tagline: Optional[str] = None
    welcome_message: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "vendor_storefronts"

class StorefrontUpdate(BaseModel):
    logo_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    brand_colors: Optional[Dict[str, str]] = None
    layout_template: Optional[str] = None
    custom_css: Optional[str] = None
    tagline: Optional[str] = None
    welcome_message: Optional[str] = None
    is_active: Optional[bool] = None

class StorefrontResponse(BaseModel):
    vendor_id: int
    business_name: Optional[str] = None
    logo_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    brand_colors: Dict[str, str]
    layout_template: str
    tagline: Optional[str] = None
    welcome_message: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ProductCategory(Document):
    """Product categories for vendor storefronts"""
    category_id: Indexed(int, unique=True)
    vendor_id: Indexed(int)
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "product_categories"

class VendorProduct(Document):
    """Products listed on a vendor's storefront"""
    product_id: Indexed(int, unique=True)
    vendor_id: Indexed(int)
    name: str
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[Indexed(int)] = None
    price: float
    unit: str = "each"
    images: List[str] = []
    is_featured: bool = False
    is_active: bool = True
    stock_status: str = "in_stock"  # in_stock, out_of_stock, limited_quantity
    minimum_quantity: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "vendor_products"

class ProductCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    sort_order: int = 0

class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class ProductCategoryResponse(BaseModel):
    category_id: int
    vendor_id: int
    name: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    sort_order: int
    is_active: bool

class VendorProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    price: float
    unit: str = "each"
    is_featured: bool = False
    stock_status: str = "in_stock"
    minimum_quantity: int = 1

class VendorProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    stock_status: Optional[str] = None
    minimum_quantity: Optional[int] = None

class VendorProductResponse(BaseModel):
    product_id: int
    vendor_id: int
    name: str
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    price: float
    unit: str
    images: List[str]
    is_featured: bool
    is_active: bool
    stock_status: str
    minimum_quantity: int

class ShoppingCartItem(BaseModel):
    product_id: int
    quantity: int
    notes: Optional[str] = None

class ShoppingCart(Document):
    """Shopping cart for a restaurant and vendor pair"""
    restaurant_id: Indexed(int)
    vendor_id: Indexed(int)
    items: List[ShoppingCartItem] = []
    session_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "shopping_carts"
        indexes = [
            [("restaurant_id", 1), ("vendor_id", 1)],
        ]

class CustomerWishlist(Document):
    """Customer wishlist for a specific vendor"""
    restaurant_id: Indexed(int)
    vendor_id: Indexed(int)
    product_id: Indexed(int)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "customer_wishlists"
        indexes = [
            [("restaurant_id", 1), ("vendor_id", 1), ("product_id", 1)],
        ]

class WishlistCreate(BaseModel):
    product_id: int

class WishlistResponse(BaseModel):
    restaurant_id: int
    vendor_id: int
    product_id: int

class ShoppingCartResponse(BaseModel):
    restaurant_id: int
    vendor_id: int
    items: List[ShoppingCartItem]
    updated_at: datetime

__all__ = [
    "VendorStorefront",
    "StorefrontUpdate",
    "StorefrontResponse",
    "ProductCategory",
    "VendorProduct",
    "ProductCategoryCreate",
    "ProductCategoryUpdate",
    "ProductCategoryResponse",
    "VendorProductCreate",
    "VendorProductUpdate",
    "VendorProductResponse",
    "ShoppingCart",
    "ShoppingCartItem",
    "ShoppingCartResponse",
    "CustomerWishlist",
    "WishlistCreate",
    "WishlistResponse",
]