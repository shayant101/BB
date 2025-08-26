from datetime import datetime, timedelta
from typing import Optional
import hashlib
import json
import base64
import jwt
import requests
import os
from fastapi import HTTPException, status
from pydantic import BaseModel

# Clerk configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "sk_test_z4rcEfLKZQhDvVQL1rf0VMArdIhBW89ULi9MPwBPWO")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "https://relaxed-primate-77.clerk.accounts.dev/.well-known/jwks.json")
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "https://relaxed-primate-77.clerk.accounts.dev")

# Legacy configuration (kept for backward compatibility during transition)
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

def get_clerk_jwks():
    """Fetch JWKS from Clerk"""
    try:
        response = requests.get(CLERK_JWKS_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch JWKS: {str(e)}"
        )

def verify_clerk_token(token: str):
    """Verify Clerk JWT token"""
    try:
        # Get the token header to find the key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get JWKS and find the matching key
        jwks = get_clerk_jwks()
        key = None
        for jwk in jwks.get('keys', []):
            if jwk.get('kid') == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find matching key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            issuer=CLERK_ISSUER,
            options={"verify_aud": False}  # Clerk doesn't always include audience
        )
        
        # Extract user information from Clerk token
        user_id = payload.get('sub')  # Clerk user ID
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            'clerk_user_id': user_id,
            'email': payload.get('email'),
            'name': payload.get('name', ''),
            'payload': payload
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_token(token: str):
    """Verify token - supports both legacy and Clerk tokens"""
    # First try to verify as Clerk token
    try:
        clerk_data = verify_clerk_token(token)
        # Return in legacy format for compatibility
        return TokenData(username=clerk_data['clerk_user_id'])
    except HTTPException:
        # If Clerk verification fails, try legacy verification
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