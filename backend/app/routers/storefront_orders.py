from fastapi import APIRouter, HTTPException, status, Header, Depends
from fastapi.security import OAuth2PasswordBearer
from ..order_models import OrderCreate, OrderResponse
from ..mongo_models import User, Order, RestaurantInfo, VendorInfo
from ..auth_simple import verify_token
from datetime import datetime
import uuid

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Dependency to get current user from Clerk JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)
    user = await User.find_one(User.username == token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/orders", response_model=OrderResponse)
async def create_storefront_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user)
):
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
    
    # Use the authenticated user as the restaurant
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can create orders"
        )
    
    restaurant_id = current_user.user_id
    restaurant = current_user
    
    print(f"🔍 Creating storefront order for restaurant: {restaurant.name} (ID: {restaurant_id})")
    
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
        f"{item.name}: {item.quantity} x ${item.price:.2f}"
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
    
    print(f"🔍 Storefront order created: Order {next_order_id} for restaurant {restaurant_id} from vendor {order_data.vendor_id}")
    
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