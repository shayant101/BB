from fastapi import APIRouter, HTTPException, status, Header, Depends
from ..order_models import OrderCreate, OrderResponse
from ..mongo_models import User, Order, RestaurantInfo, VendorInfo
from ..auth_simple import verify_clerk_token
from datetime import datetime
import uuid

router = APIRouter()

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
        
        print(f"🔍 Storefront orders auth - Clerk user ID: {clerk_user_id}")
        
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
            print(f"🔍 Created new user for storefront orders: {user.user_id}")
        
        print(f"🔍 Storefront orders - User: {user.name} (ID: {user.user_id}, Role: {user.role})")
        
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
        print(f"❌ Storefront orders authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

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