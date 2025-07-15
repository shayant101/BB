import os
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from fastapi import HTTPException, status
from .mongo_models import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_google_credentials():
    """Get Google OAuth credentials from environment variables"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logger.warning("Google OAuth credentials not found in environment variables")
        logger.warning(f"GOOGLE_CLIENT_ID: {'Set' if client_id else 'Not set'}")
        logger.warning(f"GOOGLE_CLIENT_SECRET: {'Set' if client_secret else 'Not set'}")
    
    return client_id, client_secret

# Get credentials dynamically
GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET = get_google_credentials()

class GoogleOAuthService:
    """Service for handling Google OAuth operations"""
    
    @staticmethod
    async def verify_google_token(token: str) -> Dict[str, Any]:
        """
        Verify Google ID token and extract user information
        
        Args:
            token: Google ID token from frontend
            
        Returns:
            Dict containing user information from Google
            
        Raises:
            HTTPException: If token verification fails
        """
        try:
            # Get credentials dynamically to ensure they're loaded after .env
            client_id, _ = get_google_credentials()
            if not client_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Google OAuth not configured properly"
                )
            
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Extract user information
            google_user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }
            
            logger.info(f"Successfully verified Google token for user: {google_user_info['email']}")
            return google_user_info
            
        except ValueError as e:
            logger.error(f"Google token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during Google token verification: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify Google token"
            )
    
    @staticmethod
    async def find_or_create_user(google_user_info: Dict[str, Any], role: str = "restaurant") -> User:
        """
        Find existing user or create new user from Google OAuth information
        
        Args:
            google_user_info: User information from Google
            role: User role (restaurant, vendor, admin)
            
        Returns:
            User document
        """
        google_id = google_user_info['google_id']
        google_email = google_user_info['email']
        
        # First, try to find user by Google ID
        user = await User.find_one(User.google_id == google_id)
        
        if user:
            # Update Google information if user exists
            user.google_email = google_email
            user.google_name = google_user_info['name']
            user.google_picture = google_user_info['picture']
            user.last_login_at = datetime.utcnow()
            
            # Update auth provider if it was previously local-only
            if user.auth_provider == "local":
                user.auth_provider = "both"
            
            await user.save()
            logger.info(f"Updated existing user with Google ID: {google_id}")
            return user
        
        # If not found by Google ID, try to find by email for account linking
        user = await User.find_one(User.email == google_email)
        
        if user:
            # Link existing account with Google OAuth
            user.google_id = google_id
            user.google_email = google_email
            user.google_name = google_user_info['name']
            user.google_picture = google_user_info['picture']
            user.last_login_at = datetime.utcnow()
            
            # Update auth provider
            if user.auth_provider == "local":
                user.auth_provider = "both"
            elif user.auth_provider == "google":
                user.auth_provider = "both"
            
            await user.save()
            logger.info(f"Linked existing account with Google OAuth: {google_email}")
            return user
        
        # Create new user if not found
        # Get the next user_id
        last_user = await User.find().sort(-User.user_id).limit(1).to_list()
        next_user_id = (last_user[0].user_id + 1) if last_user else 1
        
        # Generate username from email
        username = google_email.split('@')[0]
        
        # Ensure username is unique
        existing_username = await User.find_one(User.username == username)
        if existing_username:
            username = f"{username}_{next_user_id}"
        
        # Create new user
        new_user = User(
            user_id=next_user_id,
            username=username,
            password_hash=None,  # No password for Google OAuth users
            role=role,
            name=google_user_info['name'] or google_email.split('@')[0],
            email=google_email,
            phone="",  # Will be filled later by user
            address="",  # Will be filled later by user
            google_id=google_id,
            google_email=google_email,
            google_name=google_user_info['name'],
            google_picture=google_user_info['picture'],
            auth_provider="google",
            is_active=True,
            status="active",
            last_login_at=datetime.utcnow()
        )
        
        await new_user.save()
        logger.info(f"Created new user from Google OAuth: {google_email}")
        return new_user
    
    @staticmethod
    async def can_user_login_with_google(email: str) -> bool:
        """
        Check if a user can login with Google OAuth
        
        Args:
            email: User's email address
            
        Returns:
            True if user can login with Google, False otherwise
        """
        user = await User.find_one(User.email == email)
        if not user:
            return True  # New users can always sign up with Google
        
        return user.auth_provider in ["google", "both"]
    
    @staticmethod
    def get_google_oauth_config() -> Dict[str, str]:
        """
        Get Google OAuth configuration for frontend
        
        Returns:
            Dict containing Google OAuth configuration
        """
        client_id, _ = get_google_credentials()
        return {
            "client_id": client_id,
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000"),
        }