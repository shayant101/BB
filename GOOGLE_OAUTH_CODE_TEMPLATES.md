# Google OAuth 2.0 Code Templates for BistroBoard

This document provides ready-to-use code templates for implementing Google OAuth 2.0 in BistroBoard.

## Backend Implementation Templates

### 1. Google OAuth Service (`backend/app/google_oauth.py`)

```python
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """Service for handling Google OAuth 2.0 authentication"""
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing required Google OAuth environment variables")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate Google OAuth authorization URL"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=[
                    'openid',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile'
                ]
            )
            flow.redirect_uri = self.redirect_uri
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state
            )
            
            return authorization_url
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate authorization URL"
            )
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=[
                    'openid',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile'
                ]
            )
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            
            # Get ID token
            id_token_jwt = flow.credentials.id_token
            
            return {
                'id_token': id_token_jwt,
                'access_token': flow.credentials.token,
                'refresh_token': flow.credentials.refresh_token
            }
            
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization code"
            )
    
    def verify_id_token(self, id_token_jwt: str) -> Dict[str, Any]:
        """Verify Google ID token and extract user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_jwt, 
                requests.Request(), 
                self.client_id
            )
            
            # Verify issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Extract user information
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'email_verified': idinfo.get('email_verified', False),
                'name': idinfo.get('name', ''),
                'given_name': idinfo.get('given_name', ''),
                'family_name': idinfo.get('family_name', ''),
                'picture': idinfo.get('picture', ''),
                'locale': idinfo.get('locale', 'en')
            }
            
            return user_info
            
        except ValueError as e:
            logger.error(f"Invalid ID token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid ID token"
            )
        except Exception as e:
            logger.error(f"Error verifying ID token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed"
            )

# Global instance
google_oauth_service = GoogleOAuthService()
```

### 2. Updated User Model (`backend/app/mongo_models.py` additions)

```python
# Add these fields to the existing User class
class User(Document):
    # ... existing fields ...
    
    # Google OAuth fields
    google_id: Optional[str] = None
    google_email: Optional[str] = None
    google_verified_email: bool = False
    google_picture: Optional[str] = None
    google_name: Optional[str] = None
    auth_provider: str = "local"  # "local", "google", "both"
    
    # Make password_hash optional for Google-only users
    password_hash: Optional[str] = None
    
    # OAuth metadata
    oauth_linked_at: Optional[datetime] = None
    last_oauth_login: Optional[datetime] = None
    
    class Settings:
        name = "users"
        indexes = [
            "user_id",
            "username", 
            "role",
            "google_id",  # New index for Google ID
            "google_email",  # New index for Google email
            "vendor_profile.categories"
        ]

# New Pydantic models for OAuth
class GoogleAuthRequest(BaseModel):
    id_token: str
    
class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    name: str
    auth_provider: str
    is_new_user: bool
```

### 3. OAuth Authentication Endpoints (`backend/app/routers/auth.py` additions)

```python
from ..google_oauth import google_oauth_service
from ..mongo_models import GoogleAuthRequest, GoogleAuthResponse

@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    try:
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in session or cache (implement based on your session management)
        # For now, we'll return it to be handled by frontend
        
        authorization_url = google_oauth_service.get_authorization_url(state=state)
        
        return {
            "authorization_url": authorization_url,
            "state": state
        }
        
    except Exception as e:
        logger.error(f"Error initiating Google login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login"
        )

@router.post("/google/callback")
async def google_callback(
    code: str,
    state: Optional[str] = None,
    request: Request = None
):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        tokens = google_oauth_service.exchange_code_for_tokens(code)
        
        # Verify ID token and get user info
        user_info = google_oauth_service.verify_id_token(tokens['id_token'])
        
        # Find or create user
        user, is_new_user = await find_or_create_google_user(user_info)
        
        # Update last login time
        await update_user_login_time(user)
        
        # Log authentication event
        await log_user_event(
            user_id=user.user_id,
            event_type="login",
            details={
                "login_method": "google_oauth",
                "user_agent": request.headers.get("user-agent") if request else None,
                "success": True,
                "is_new_user": is_new_user
            },
            request=request
        )
        
        # Generate BistroBoard JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.user_id,
                "role": user.role,
                "name": user.name,
                "auth_provider": user.auth_provider,
                "is_impersonating": False
            },
            expires_delta=access_token_expires
        )
        
        return GoogleAuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role,
            name=user.name,
            auth_provider=user.auth_provider,
            is_new_user=is_new_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@router.post("/google/verify", response_model=GoogleAuthResponse)
async def google_verify_token(
    auth_request: GoogleAuthRequest,
    request: Request
):
    """Verify Google ID token directly (for frontend integration)"""
    try:
        # Verify ID token and get user info
        user_info = google_oauth_service.verify_id_token(auth_request.id_token)
        
        # Find or create user
        user, is_new_user = await find_or_create_google_user(user_info)
        
        # Update last login time
        await update_user_login_time(user)
        
        # Log authentication event
        await log_user_event(
            user_id=user.user_id,
            event_type="login",
            details={
                "login_method": "google_oauth_direct",
                "user_agent": request.headers.get("user-agent"),
                "success": True,
                "is_new_user": is_new_user
            },
            request=request
        )
        
        # Generate BistroBoard JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.user_id,
                "role": user.role,
                "name": user.name,
                "auth_provider": user.auth_provider,
                "is_impersonating": False
            },
            expires_delta=access_token_expires
        )
        
        return GoogleAuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role,
            name=user.name,
            auth_provider=user.auth_provider,
            is_new_user=is_new_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )

# Helper functions
async def find_or_create_google_user(user_info: Dict[str, Any]) -> tuple[User, bool]:
    """Find existing user or create new one from Google user info"""
    is_new_user = False
    
    # First, try to find user by Google ID
    user = await User.find_one(User.google_id == user_info['google_id'])
    
    if user:
        # Update Google info if needed
        if user.google_email != user_info['email']:
            user.google_email = user_info['email']
            user.google_verified_email = user_info['email_verified']
            user.google_picture = user_info['picture']
            user.google_name = user_info['name']
            await user.save()
        return user, False
    
    # Try to find user by email (for account linking)
    user = await User.find_one(User.email == user_info['email'])
    
    if user:
        # Link Google account to existing user
        user.google_id = user_info['google_id']
        user.google_email = user_info['email']
        user.google_verified_email = user_info['email_verified']
        user.google_picture = user_info['picture']
        user.google_name = user_info['name']
        user.auth_provider = "both"
        user.oauth_linked_at = datetime.utcnow()
        await user.save()
        return user, False
    
    # Create new user
    # Generate unique user_id
    max_user = await User.find().sort(-User.user_id).limit(1).to_list()
    next_user_id = (max_user[0].user_id + 1) if max_user else 1
    
    # Generate username from email
    base_username = user_info['email'].split('@')[0]
    username = base_username
    counter = 1
    while await User.find_one(User.username == username):
        username = f"{base_username}{counter}"
        counter += 1
    
    # Determine role (default to restaurant, can be changed later)
    role = "restaurant"  # or implement role selection logic
    
    user = User(
        user_id=next_user_id,
        username=username,
        password_hash=None,  # No password for Google-only users
        role=role,
        name=user_info['name'] or user_info['email'],
        email=user_info['email'],
        phone="",  # Will be filled later
        address="",  # Will be filled later
        google_id=user_info['google_id'],
        google_email=user_info['email'],
        google_verified_email=user_info['email_verified'],
        google_picture=user_info['picture'],
        google_name=user_info['name'],
        auth_provider="google",
        oauth_linked_at=datetime.utcnow(),
        is_active=True,
        status="active"
    )
    
    await user.save()
    is_new_user = True
    
    return user, is_new_user

async def update_user_login_time(user: User):
    """Update user's last login time with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                # Refresh user data
                user = await User.find_one(User.user_id == user.user_id)
                if not user:
                    break
            
            user.last_login_at = datetime.utcnow()
            user.last_oauth_login = datetime.utcnow()
            await user.save()
            break
            
        except Exception as e:
            if attempt == max_retries - 1:
                logger.warning(f"Failed to update login time after {max_retries} attempts: {e}")
                break
            else:
                if "RevisionIdWasChanged" in str(type(e).__name__):
                    import asyncio
                    await asyncio.sleep(0.1 * (attempt + 1))
```

## Frontend Implementation Templates

### 1. Google Sign-In Component (`frontend/src/components/GoogleSignIn.js`)

```javascript
import { useState } from 'react';
import { authAPI } from '../lib/api';

export default function GoogleSignIn({ onSuccess, onError, className = "" }) {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    
    try {
      // Load Google Identity Services
      if (!window.google) {
        await loadGoogleIdentityServices();
      }

      // Initialize Google Sign-In
      window.google.accounts.id.initialize({
        client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true
      });

      // Prompt for sign-in
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // Fallback to popup
          window.google.accounts.id.renderButton(
            document.getElementById('google-signin-button'),
            {
              theme: 'outline',
              size: 'large',
              width: '100%'
            }
          );
        }
      });

    } catch (error) {
      console.error('Google Sign-In error:', error);
      setIsLoading(false);
      onError?.(error);
    }
  };

  const handleCredentialResponse = async (response) => {
    try {
      // Send ID token to backend for verification
      const result = await authAPI.googleLogin(response.credential);
      
      // Handle successful authentication
      onSuccess?.(result);
      
    } catch (error) {
      console.error('Authentication error:', error);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadGoogleIdentityServices = () => {
    return new Promise((resolve, reject) => {
      if (window.google) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  };

  return (
    <div className={className}>
      <button
        onClick={handleGoogleSignIn}
        disabled={isLoading}
        className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>
        ) : (
          <>
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign in with Google
          </>
        )}
      </button>
      
      {/* Hidden button for fallback rendering */}
      <div id="google-signin-button" style={{ display: 'none' }}></div>
    </div>
  );
}
```

### 2. Updated Login Page (`frontend/src/components/LoginPage.js`)

```javascript
import { useState } from 'react';
import { useRouter } from 'next/router';
import GoogleSignIn from './GoogleSignIn';
import { authAPI, setAuthToken, setUser } from '../lib/api';

export default function LoginPage() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [authMethod, setAuthMethod] = useState('traditional'); // 'traditional' or 'google'
  const router = useRouter();

  const handleTraditionalLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await authAPI.login(credentials.username, credentials.password);
      
      // Store authentication data
      setAuthToken(response.access_token);
      setUser({
        user_id: response.user_id,
        role: response.role,
        name: response.name
      });

      // Redirect based on role
      redirectAfterLogin(response.role);
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = (response) => {
    // Store authentication data
    setAuthToken(response.access_token);
    setUser({
      user_id: response.user_id,
      role: response.role,
      name: response.name,
      auth_provider: response.auth_provider
    });

    // Show welcome message for new users
    if (response.is_new_user) {
      // You might want to show a welcome modal or redirect to profile setup
      console.log('Welcome new user!');
    }

    // Redirect based on role
    redirectAfterLogin(response.role);
  };

  const handleGoogleError = (error) => {
    setError('Google sign-in failed. Please try again.');
    console.error('Google sign-in error:', error);
  };

  const redirectAfterLogin = (role) => {
    switch (role) {
      case 'admin':
        router.push('/admin');
        break;
      case 'restaurant':
      case 'vendor':
        router.push('/dashboard');
        break;
      default:
        router.push('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to BistroBoard
          </h2>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {/* Google Sign-In */}
          <GoogleSignIn
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            className="w-full"
          />

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-50 text-gray-500">Or continue with</span>
            </div>
          </div>

          {/* Traditional Login Form */}
          <form className="space-y-6" onSubmit={handleTraditionalLogin}>
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Username"
                value={credentials.username}
                onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
```

### 3. Updated API Client (`frontend/src/lib/api.js` additions)

```javascript
// Add to existing authAPI object
export const authAPI = {
  // ... existing methods ...
  
  googleLogin: async (idToken) => {
    const response = await api.post('/auth/google/verify', { 
      id_token: idToken 
    });
    return response.data;
  },
  
  linkGoogleAccount: async (idToken) => {
    const response = await api.post('/auth/google/link', { 
      id_token: idToken 
    });
    return response.data;
  },
  
  unlinkGoogleAccount: async () => {
    const response = await api.post('/auth/google/unlink');
    return response.data;
  }
};
```

## Environment Configuration Templates

### Backend Environment (`.env`)

```bash
# Database
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/bistroboard?retryWrites=true&w=majority

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Production URLs (update for production)
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Frontend Environment (`.env.local`)

```bash
# Google OAuth Configuration
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Database Migration Script

### Google OAuth Migration (`backend/google_oauth_migration.py`)

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.mongo_models import User
import os
from dotenv import load_dotenv

load_dotenv()

async def migrate_users_for_google_oauth():
    """Add Google OAuth fields to existing users"""
    
    # Initialize database connection
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    database = client.bistroboard
    
    await init_beanie(database=database, document_models=[User])
    
    print("🔄 Starting Google OAuth migration...")
    
    # Get all users
    users = await User.find_all().to_list()
    
    updated_count = 0
    for user in users:
        # Add Google OAuth fields if they don't exist
        if not hasattr(user, 'google_id'):
            user.google_id = None
            user.google_email = None
            user.google_verified_email = False
            user.google_picture = None
            user.google_name = None
            user.auth_provider = "local"
            user.oauth_linked_at = None
            user.last_oauth_login = None
            
            await user.save()
            updated_count += 1
    
    print(f"✅ Updated {updated_count} users with Google OAuth fields")
    
    # Create indexes
    print("🔄 Creating indexes...")
    
    collection = database.users
    
    # Create index on google_id
    await collection.create_index("google_id", sparse=True)
    print("✅ Created index on google_id")
    
    # Create index on google_email
    await collection.create_index("google_email", sparse=True)
    print("✅ Created index on google_email")
    
    print("🎉 Google OAuth migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate_users_for_google_oauth())
```

## Testing Templates

### Backend Tests (`backend/tests/test_google_oauth.py`)

```python
import pytest
from unittest.mock import Mock, patch
from app.google_oauth import GoogleOAuthService
from app.routers.auth import find_or_create_google_user
from app.mongo_models import User

class TestGoogleOAuthService:
    
    @pytest