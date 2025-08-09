from fastapi import APIRouter, HTTPException, status
from ..order_models import OrderCreate, OrderResponse
import uuid

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
async def create_storefront_order(order_data: OrderCreate):
    """
    Create a new order from the vendor storefront.
    
    This endpoint accepts order data from the vendor storefront and processes it.
    For now, it simply returns a success message confirming the order was placed.
    No database interaction is implemented yet.
    """
    
    # Validate that we have items in the order
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )
    
    # Validate quantities and prices
    for item in order_data.items:
        if item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid quantity for product {item.product_id}: must be greater than 0"
            )
        if item.price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid price for product {item.product_id}: must be non-negative"
            )
    
    # For testing purposes, use hardcoded restaurant_id of 1 if not provided
    restaurant_id = order_data.restaurant_id if order_data.restaurant_id else 1
    
    # Generate a unique order ID for the response
    order_id = str(uuid.uuid4())
    
    # Calculate total items
    total_items = sum(item.quantity for item in order_data.items)
    
    # Return success response
    return OrderResponse(
        message="Order placed successfully",
        order_id=order_id,
        vendor_id=order_data.vendor_id,
        restaurant_id=restaurant_id,
        total_items=total_items,
        status="pending"
    )