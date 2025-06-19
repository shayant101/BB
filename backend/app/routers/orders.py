from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import User, Order
from ..auth_simple import verify_token
from datetime import datetime

router = APIRouter()

# Pydantic models for orders
class OrderCreate(BaseModel):
    vendor_id: int
    items_text: str
    notes: str = ""

class OrderResponse(BaseModel):
    id: int
    restaurant: dict
    vendor: dict
    items_text: str
    status: str
    notes: str
    created_at: datetime
    updated_at: datetime

class OrderStatusUpdate(BaseModel):
    status: str

class OrderNotesUpdate(BaseModel):
    notes: str

# Dependency to get current user from JWT token
async def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )
    
    token = authorization.split(" ")[1]
    token_data = verify_token(token)
    user = db.query(User).filter(User.username == token_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only restaurants can create orders
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can create orders"
        )
    
    # Verify vendor exists
    vendor = db.query(User).filter(User.id == order_data.vendor_id, User.role == "vendor").first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    # Create new order
    new_order = Order(
        restaurant_id=current_user.id,
        vendor_id=order_data.vendor_id,
        items_text=order_data.items_text,
        notes=order_data.notes,
        status="pending"
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return format_order_response(new_order)

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "restaurant":
        # Get orders placed by this restaurant
        orders = db.query(Order).filter(Order.restaurant_id == current_user.id).all()
    elif current_user.role == "vendor":
        # Get orders received by this vendor
        orders = db.query(Order).filter(Order.vendor_id == current_user.id).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )
    
    return [format_order_response(order) for order in orders]

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user has access to this order
    if (current_user.role == "restaurant" and order.restaurant_id != current_user.id) or \
       (current_user.role == "vendor" and order.vendor_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return format_order_response(order)

@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only vendors can update order status
    if current_user.role != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can update order status"
        )
    
    order = db.query(Order).filter(Order.id == order_id, Order.vendor_id == current_user.id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate status
    valid_statuses = ["pending", "confirmed", "fulfilled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    order.status = status_update.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    
    return format_order_response(order)

@router.put("/orders/{order_id}/notes", response_model=OrderResponse)
async def update_order_notes(
    order_id: int,
    notes_update: OrderNotesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user has access to this order
    if (current_user.role == "restaurant" and order.restaurant_id != current_user.id) or \
       (current_user.role == "vendor" and order.vendor_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    order.notes = notes_update.notes
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    
    return format_order_response(order)

def format_order_response(order: Order) -> dict:
    return {
        "id": order.id,
        "restaurant": {
            "id": order.restaurant.id,
            "name": order.restaurant.name,
            "phone": order.restaurant.phone,
            "address": order.restaurant.address,
            "email": order.restaurant.email
        },
        "vendor": {
            "id": order.vendor.id,
            "name": order.vendor.name,
            "phone": order.vendor.phone,
            "address": order.vendor.address,
            "email": order.vendor.email
        },
        "items_text": order.items_text,
        "status": order.status,
        "notes": order.notes,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }