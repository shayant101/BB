from datetime import datetime, timedelta
from typing import Optional
import hashlib
import json
import base64
from fastapi import HTTPException, status
from pydantic import BaseModel

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    name: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    id: int
    username: str
    role: str
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None

class UserProfileUpdate(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    description: Optional[str] = None

def verify_password(plain_password, hashed_password):
    """Simple password verification using SHA256"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a simple JWT-like token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire.timestamp()})
    
    # Simple encoding (not secure for production)
    token_string = json.dumps(to_encode)
    encoded_token = base64.b64encode(token_string.encode()).decode()
    
    return encoded_token

def verify_token(token: str):
    """Verify a simple token"""
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
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(username=username)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )