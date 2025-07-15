from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import json
import base64
import secrets
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from .mongo_models import User, AdminAuditLog, UserEventLog, ImpersonationSession

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
IMPERSONATION_TOKEN_EXPIRE_MINUTES = 5

security = HTTPBearer()

# Pydantic models for admin operations
class AdminToken(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    name: str
    is_impersonating: bool = False
    impersonated_user_id: Optional[int] = None
    impersonator_id: Optional[int] = None

class ImpersonationRequest(BaseModel):
    target_user_id: int
    reason: str

class UserStatusUpdate(BaseModel):
    status: str  # "active", "inactive", "pending_approval"
    reason: Optional[str] = None

class AdminUserCreate(BaseModel):
    username: str
    password: str
    role: str  # "restaurant", "vendor"
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None
    status: str = "active"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simple password verification using SHA256"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a simple JWT-like token with enhanced claims for admin operations"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire.timestamp()})
    
    # Simple encoding (not secure for production)
    token_string = json.dumps(to_encode)
    encoded_token = base64.b64encode(token_string.encode()).decode()
    
    return encoded_token

def create_impersonation_token(admin_id: int, target_user_id: int, target_user_data: dict) -> str:
    """Create a short-lived impersonation token"""
    expire = datetime.utcnow() + timedelta(minutes=IMPERSONATION_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": target_user_data["username"],
        "user_id": target_user_id,
        "role": target_user_data["role"],
        "name": target_user_data["name"],
        "is_impersonating": True,
        "impersonator_id": admin_id,
        "exp": expire.timestamp()
    }
    
    return create_access_token(token_data, timedelta(minutes=IMPERSONATION_TOKEN_EXPIRE_MINUTES))

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode token"""
    try:
        # Decode the token
        token_string = base64.b64decode(token.encode()).decode()
        payload = json.loads(token_string)
        
        # Check expiration
        if datetime.utcnow().timestamp() > payload.get("exp", 0):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current user from token"""
    payload = verify_token(credentials.credentials)
    username = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = await User.find_one(User.username == username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check if user is active (unless it's an impersonation session)
    if not payload.get("is_impersonating", False) and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )
    
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def log_admin_action(
    admin_id: int,
    action: str,
    target_user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
):
    """Log admin action to audit trail"""
    audit_log = AdminAuditLog(
        admin_id=admin_id,
        target_user_id=target_user_id,
        action=action,
        details=details or {},
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        session_id=secrets.token_hex(16)
    )
    await audit_log.save()

async def log_user_event(
    user_id: int,
    event_type: str,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
):
    """Log user event"""
    event_log = UserEventLog(
        user_id=user_id,
        event_type=event_type,
        details=details or {},
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    await event_log.save()

def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get token payload without user validation (for impersonation checks)"""
    return verify_token(credentials.credentials)