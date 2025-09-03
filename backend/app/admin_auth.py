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

# Pydantic models
class ImpersonationRequest(BaseModel):
    reason: str

class UserStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None

class AdminUserCreate(BaseModel):
    username: str
    password: str
    role: str
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None
    status: str = "active"

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire.timestamp()})
    token_string = json.dumps(to_encode)
    return base64.b64encode(token_string.encode()).decode()

def create_impersonation_token(admin_id: int, target_user_id: int, target_user_data: dict) -> str:
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
    try:
        token_string = base64.b64decode(token.encode()).decode()
        payload = json.loads(token_string)
        if datetime.utcnow().timestamp() > payload.get("exp", 0):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    print(f"🔍 AUTH DEBUG - get_current_user called")
    print(f"🔍 Token received: {credentials.credentials[:50]}..." if credentials.credentials else "No token")
    
    try:
        payload = verify_token(credentials.credentials)
        print(f"🔍 Token payload: {payload}")
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        raise
    
    username = payload.get("sub")
    print(f"🔍 Username from token: {username}")
    
    if not username:
        print(f"❌ No username in token payload")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    # Special case for hardcoded admin - bypass database lookup
    if username == "admin" and payload.get("user_id") == 999999:
        print(f"✅ Using hardcoded admin user")
        # This is the special hardcoded admin.
        # Return a User object directly without a database lookup.
        return User(
            user_id=999999,
            username="admin",
            role="admin",
            email="admin@bistroboard.com",
            name="System Administrator",
            phone="555-0000",
            address="Admin Office"
        )
    
    print(f"🔍 Looking up user in database: {username}")
    user = await User.find_one(User.username == username)
    if not user:
        print(f"❌ User not found in database: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    print(f"✅ User found: {user.username}, role: {user.role}")
    
    if not payload.get("is_impersonating", False) and not user.is_active:
        print(f"❌ User account is deactivated")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is deactivated")
    
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    print(f"🔍 ADMIN AUTH DEBUG - get_current_admin called")
    print(f"🔍 Current user: {current_user}")
    print(f"🔍 User role: {current_user.role if current_user else 'No user'}")
    print(f"🔍 User ID: {current_user.user_id if current_user else 'No user'}")
    
    if current_user.role != "admin":
        print(f"❌ ADMIN AUTH FAILED - User role '{current_user.role}' is not 'admin'")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    print(f"✅ ADMIN AUTH SUCCESS - User {current_user.username} is admin")
    return current_user

async def log_admin_action(admin_id: int, action: str, target_user_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None, request: Optional[Request] = None):
    last_log = await AdminAuditLog.find().sort(-AdminAuditLog.log_id).limit(1).first_or_none()
    next_log_id = (last_log.log_id + 1) if last_log else 1
    
    audit_log = AdminAuditLog(
        log_id=next_log_id,
        admin_id=admin_id,
        target_user_id=target_user_id,
        action=action,
        details=details or {},
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    await audit_log.insert()

async def log_user_event(user_id: int, event_type: str, details: Optional[Dict[str, Any]] = None, request: Optional[Request] = None):
    event_log = UserEventLog(
        user_id=user_id,
        event_type=event_type,
        details=details or {},
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    await event_log.insert()

def get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    return verify_token(credentials.credentials)