from pydantic import BaseModel
from typing import List


class OrderItemCreate(BaseModel):
    """Pydantic model for individual order items in storefront orders"""
    product_id: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    """Pydantic model for creating orders from vendor storefront"""
    vendor_id: int
    restaurant_id: int
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    """Response model for order creation"""
    message: str
    order_id: str
    vendor_id: int
    restaurant_id: int
    total_items: int
    status: str