from fastapi import APIRouter, HTTPException, status
from ..order_models import OrderCreate, OrderResponse
from ..mongo_models import User, Order, RestaurantInfo, VendorInfo
import uuid

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
async def create_storefront_order(order_data: OrderCreate):
    """
    Create a new order from the vendor storefront and save it to the database.
    
    This endpoint accepts order data from the vendor storefront, processes it,
    and saves it to MongoDB so it appears in the restaurant dashboard.
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
    
    # Get restaurant and vendor information from database
    restaurant = await User.find_one(User.user_id == restaurant_id, User.role == "restaurant")
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    vendor = await User.find_one(User.user_id == order_data.vendor_id, User.role == "vendor")
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    # Generate next order ID
    last_order = await Order.find().sort(-Order.order_id).limit(1).first_or_none()
    next_order_id = (last_order.order_id + 1) if last_order else 1
    
    # Convert items to text format for compatibility with existing Order model
    items_text = "\n".join([
        f"{item.product_id}: {item.quantity} x ${item.price:.2f}"
        for item in order_data.items
    ])
    
    # Create and save the order to database
    new_order = Order(
        order_id=next_order_id,
        restaurant_id=restaurant_id,
        vendor_id=order_data.vendor_id,
        restaurant=RestaurantInfo(
            name=restaurant.name,
            phone=restaurant.phone,
            address=restaurant.address,
            email=restaurant.email
        ),
        vendor=VendorInfo(
            name=vendor.name,
            phone=vendor.phone,
            address=vendor.address,
            email=vendor.email
        ),
        items_text=items_text,
        status="pending"
    )
    
    await new_order.insert()
    
    # Calculate total items
    total_items = sum(item.quantity for item in order_data.items)
    
    # Return success response
    return OrderResponse(
        message="Order placed successfully",
        order_id=str(next_order_id),
        vendor_id=order_data.vendor_id,
        restaurant_id=restaurant_id,
        total_items=total_items,
        status="pending"
    )