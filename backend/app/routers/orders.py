from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, BackgroundTasks
from pydantic import BaseModel
from ..mongo_models import User, Order, RestaurantInfo, VendorInfo
from ..auth_simple import verify_clerk_token
from datetime import datetime
import asyncio

router = APIRouter()

# Pydantic models for orders
class OrderCreate(BaseModel):
    vendor_id: int
    items_text: str
    notes: Optional[str] = ""

class OrderResponse(BaseModel):
    order_id: int
    restaurant: RestaurantInfo
    vendor: VendorInfo
    items_text: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class OrderStatusUpdate(BaseModel):
    status: str

class OrderNotesUpdate(BaseModel):
    notes: str

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
        print(f"❌ Orders authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can create orders"
        )
    
    vendor = await User.find_one(User.user_id == order_data.vendor_id, User.role == "vendor")
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    last_order = await Order.find().sort(-Order.order_id).limit(1).first_or_none()
    next_order_id = (last_order.order_id + 1) if last_order else 1

    new_order = Order(
        order_id=next_order_id,
        restaurant_id=current_user.user_id,
        vendor_id=order_data.vendor_id,
        restaurant=RestaurantInfo(**current_user.dict()),
        vendor=VendorInfo(**vendor.dict()),
        items_text=order_data.items_text,
        notes=order_data.notes,
        status="pending"
    )
    
    await new_order.insert()
    
    # Send email notifications in background
    try:
        from ..email_service import EmailService
        email_service = EmailService()
        
        # Send new order notification to vendor
        background_tasks.add_task(
            email_service.send_new_order_notification,
            {
                "order": new_order.dict(),
                "vendor_email": vendor.email,
                "vendor_name": vendor.name,
                "restaurant_name": current_user.name
            }
        )
        
        # Send order confirmation to restaurant
        background_tasks.add_task(
            email_service.send_order_confirmation,
            {
                "order": new_order.dict(),
                "restaurant_email": current_user.email,
                "restaurant_name": current_user.name,
                "vendor_name": vendor.name
            }
        )
        
    except Exception as e:
        # Log error but don't fail the order creation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to queue order notification emails: {str(e)}")
    
    return OrderResponse(**new_order.dict())

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(current_user: User = Depends(get_current_user)):
    print(f"🔍 Orders API - User: {current_user.name} (ID: {current_user.user_id}, Role: {current_user.role})")
    
    if current_user.role == "restaurant":
        print(f"🔍 Searching for orders with restaurant_id: {current_user.user_id}")
        orders = await Order.find(Order.restaurant_id == current_user.user_id).to_list()
        print(f"🔍 Found {len(orders)} orders for restaurant")
    elif current_user.role == "vendor":
        print(f"🔍 Searching for orders with vendor_id: {current_user.user_id}")
        orders = await Order.find(Order.vendor_id == current_user.user_id).to_list()
        print(f"🔍 Found {len(orders)} orders for vendor")
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )
    
    # Debug: Show order details
    for order in orders:
        print(f"🔍 Order {order.order_id}: restaurant_id={order.restaurant_id}, vendor_id={order.vendor_id}, status={order.status}")
    
    return [OrderResponse(**order.dict()) for order in orders]

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    order = await Order.find_one(Order.order_id == order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if (current_user.role == "restaurant" and order.restaurant_id != current_user.user_id) or \
       (current_user.role == "vendor" and order.vendor_id != current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return OrderResponse(**order.dict())

@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can update order status"
        )
    
    order = await Order.find_one(Order.order_id == order_id, Order.vendor_id == current_user.user_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    valid_statuses = ["pending", "confirmed", "fulfilled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    order.status = status_update.status
    order.updated_at = datetime.utcnow()
    await order.save()
    
    return OrderResponse(**order.dict())

@router.put("/orders/{order_id}/notes", response_model=OrderResponse)
async def update_order_notes(
    order_id: int,
    notes_update: OrderNotesUpdate,
    current_user: User = Depends(get_current_user)
):
    order = await Order.find_one(Order.order_id == order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if (current_user.role == "restaurant" and order.restaurant_id != current_user.user_id) or \
       (current_user.role == "vendor" and order.vendor_id != current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    order.notes = notes_update.notes
    order.updated_at = datetime.utcnow()
    await order.save()
    
    return OrderResponse(**order.dict())