from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..mongo_models import User
from ..auth_simple import verify_clerk_token

router = APIRouter()

# Pydantic Models
class UserProfileResponse(BaseModel):
    user_id: int
    username: str
    role: str
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None

class UserProfileUpdateRequest(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None

class SetRoleRequest(BaseModel):
    role: str

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
                role=None,
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
        print(f"❌ Profiles authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    return UserProfileResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        address=current_user.address,
        description=current_user.description
    )

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update the profile of the currently authenticated user."""
    current_user.name = profile_data.name
    current_user.email = profile_data.email
    current_user.phone = profile_data.phone
    current_user.address = profile_data.address
    current_user.description = profile_data.description
    
    await current_user.save()
    
    return UserProfileResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        address=current_user.address,
        description=current_user.description
    )

@router.get("/vendors", response_model=List[UserProfileResponse])
async def get_all_vendors(current_user: User = Depends(get_current_user)):
    """Get a list of all vendor profiles (for restaurants)."""
    if current_user.role != "restaurant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurants can view vendor profiles."
        )
    
    vendors = await User.find(User.role == "vendor", User.is_active == True).to_list()
    
    return [
        UserProfileResponse(
            user_id=v.user_id,
            username=v.username,
            role=v.role,
            name=v.name,
            email=v.email,
            phone=v.phone,
            address=v.address,
            description=v.description
        ) for v in vendors
    ]

@router.post("/set-role", response_model=dict)
async def set_user_role(
    request: SetRoleRequest,
    current_user: User = Depends(get_current_user)
):
    """Set the role for the currently authenticated user."""
    # Validate the input role
    if request.role not in ["vendor", "restaurant"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified"
        )
    
    # Update the current user's role
    current_user.role = request.role
    
    # Save the updated user to the database
    await current_user.save()
    
    return {"message": f"User role updated to {request.role}"}