from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..storefront_service import StorefrontService
from ..storefront_models import (
    StorefrontUpdate, StorefrontResponse,
    ProductCategoryCreate, ProductCategoryResponse,
    VendorProductCreate, VendorProductResponse,
    ShoppingCartItem, ShoppingCartResponse,
    WishlistCreate, WishlistResponse
)

router = APIRouter()

@router.get("/storefront/{vendor_id}", response_model=StorefrontResponse)
async def get_storefront(vendor_id: str):
    storefront = await StorefrontService.get_storefront_by_vendor_id(vendor_id)
    if not storefront:
        raise HTTPException(status_code=404, detail="Storefront not found")
    return storefront

@router.post("/storefront/{vendor_id}/categories", response_model=ProductCategoryResponse)
async def create_product_category(vendor_id: int, category_create: ProductCategoryCreate):
    return await StorefrontService.create_product_category(vendor_id, category_create)

@router.get("/storefront/{vendor_id}/categories", response_model=List[ProductCategoryResponse])
async def get_product_categories(vendor_id: int):
    return await StorefrontService.get_product_categories_by_vendor(vendor_id)

@router.post("/storefront/{vendor_id}/products", response_model=VendorProductResponse)
async def create_vendor_product(vendor_id: int, product_create: VendorProductCreate):
    return await StorefrontService.create_vendor_product(vendor_id, product_create)

@router.get("/storefront/{vendor_id}/products")
async def get_vendor_products(vendor_id: int):
    return await StorefrontService.get_vendor_products(vendor_id)

@router.get("/storefront/{vendor_id}/cart/{restaurant_id}", response_model=ShoppingCartResponse)
async def get_cart(vendor_id: int, restaurant_id: int):
    cart = await StorefrontService.get_cart(restaurant_id, vendor_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.post("/storefront/{vendor_id}/cart/{restaurant_id}", response_model=ShoppingCartResponse)
async def update_cart(vendor_id: int, restaurant_id: int, items: List[ShoppingCartItem]):
    return await StorefrontService.update_cart(restaurant_id, vendor_id, items)

@router.post("/storefront/{vendor_id}/wishlist/{restaurant_id}", response_model=WishlistResponse)
async def add_to_wishlist(vendor_id: int, restaurant_id: int, wishlist_create: WishlistCreate):
    # A real implementation would get restaurant_id from auth token
    return await StorefrontService.add_to_wishlist(restaurant_id, vendor_id, wishlist_create.product_id)

@router.get("/storefront/{vendor_id}/wishlist/{restaurant_id}", response_model=List[WishlistResponse])
async def get_wishlist(vendor_id: int, restaurant_id: int):
    # A real implementation would get restaurant_id from auth token
    return await StorefrontService.get_wishlist(restaurant_id, vendor_id)

@router.put("/storefront/{vendor_id}", response_model=StorefrontResponse)
async def update_storefront(vendor_id: int, storefront_update: StorefrontUpdate):
    storefront = await StorefrontService.update_storefront(vendor_id, storefront_update)
    if not storefront:
        raise HTTPException(status_code=404, detail="Storefront not found")
    return storefront