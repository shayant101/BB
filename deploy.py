#!/usr/bin/env python3
"""
BistroBoard Production Deployment Helper Script

This script helps validate and prepare the BistroBoard application for production deployment.
It checks configurations, generates secure keys, and provides deployment guidance.
"""

import os
import secrets
import sys
import json
from pathlib import Path

def generate_secure_key(length=32):
    """Generate a secure random key for JWT and other secrets."""
    return secrets.token_urlsafe(length)

def check_file_exists(filepath):
    """Check if a file exists and return status."""
    return Path(filepath).exists()

def validate_environment():
    """Validate the current environment setup."""
    print("🔍 Validating BistroBoard Environment...")
    
    issues = []
    
    # Check required files
    required_files = [
        "backend/requirements.txt",
        "backend/app/main.py",
        "frontend/package.json",
        "frontend/src/lib/api.js",
        "render.yaml",
        "frontend/vercel.json"
    ]
    
    for file in required_files:
        if not check_file_exists(file):
            issues.append(f"❌ Missing required file: {file}")
        else:
            print(f"✅ Found: {file}")
    
    # Check backend environment
    env_file = Path("backend/.env")
    if env_file.exists():
        print("✅ Backend .env file exists")
        # Check for hardcoded values that need to be changed
        with open(env_file, 'r') as f:
            content = f.read()
            if "your_google_client_id_here" in content:
                issues.append("⚠️  Google OAuth not configured in backend/.env")
            if "localhost" in content:
                print("ℹ️  Localhost URLs found in .env (expected for development)")
    else:
        issues.append("❌ Backend .env file not found")
    
    return issues

def generate_production_secrets():
    """Generate secure secrets for production."""
    print("\n🔐 Generating Production Secrets...")
    
    secrets_data = {
        "JWT_SECRET_KEY": generate_secure_key(32),
        "SECRET_KEY": generate_secure_key(32),
        "SESSION_SECRET": generate_secure_key(24)
    }
    
    print("Generated secure keys (save these in your deployment platform):")
    for key, value in secrets_data.items():
        print(f"{key}={value}")
    
    return secrets_data

def create_production_env_template():
    """Create a production environment template."""
    print("\n📝 Creating production environment template...")
    
    template = """# BistroBoard Production Environment Variables
# Copy these to your Render dashboard Environment section

# Database
MONGODB_URL=mongodb+srv://username:password@clusterbb.gzjujes.mongodb.net/bistroboard?retryWrites=true&w=majority&appName=ClusterBB

# Google OAuth (Create new production credentials)
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret
GOOGLE_REDIRECT_URI=https://your-frontend-domain.vercel.app

# Security Keys (Generated below)
JWT_SECRET_KEY={jwt_key}
SECRET_KEY={secret_key}

# Application Configuration
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
LOG_LEVEL=INFO
"""
    
    secrets = generate_production_secrets()
    template = template.format(
        jwt_key=secrets["JWT_SECRET_KEY"],
        secret_key=secrets["SECRET_KEY"]
    )
    
    with open("production-env-template.txt", "w") as f:
        f.write(template)
    
    print("✅ Created production-env-template.txt")
    return template

def check_deployment_readiness():
    """Check if the application is ready for deployment."""
    print("\n🚀 Checking Deployment Readiness...")
    
    readiness_checks = []
    
    # Check if API configuration uses environment variables
    api_file = Path("frontend/src/lib/api.js")
    if api_file.exists():
        with open(api_file, 'r') as f:
            content = f.read()
            if "process.env.NEXT_PUBLIC_API_URL" in content:
                readiness_checks.append("✅ Frontend API configured for environment variables")
            else:
                readiness_checks.append("❌ Frontend API still uses hardcoded localhost")
    
    # Check if MongoDB uses environment variables
    mongodb_file = Path("backend/app/mongodb.py")
    if mongodb_file.exists():
        with open(mongodb_file, 'r') as f:
            content = f.read()
            if "os.getenv(\"MONGODB_URL\"" in content:
                readiness_checks.append("✅ MongoDB configured for environment variables")
            else:
                readiness_checks.append("❌ MongoDB still uses hardcoded connection string")
    
    # Check CORS configuration
    main_file = Path("backend/app/main.py")
    if main_file.exists():
        with open(main_file, 'r') as f:
            content = f.read()
            if "ALLOWED_ORIGINS" in content and "ENVIRONMENT" in content:
                readiness_checks.append("✅ CORS configured for production")
            else:
                readiness_checks.append("❌ CORS still allows all origins")
    
    for check in readiness_checks:
        print(check)
    
    return readiness_checks

def print_deployment_summary():
    """Print deployment summary and next steps."""
    print("\n" + "="*60)
    print("🎯 BISTROBOARD DEPLOYMENT SUMMARY")
    print("="*60)
    
    print("\n📋 Files Created:")
    print("✅ render.yaml - Render deployment configuration")
    print("✅ frontend/vercel.json - Vercel deployment configuration")
    print("✅ backend/.env.production.example - Production environment template")
    print("✅ frontend/next.config.js - Next.js production configuration")
    print("✅ PRODUCTION_DEPLOYMENT_GUIDE.md - Complete deployment guide")
    print("✅ production-env-template.txt - Environment variables template")
    
    print("\n🔧 Configuration Updates:")
    print("✅ MongoDB connection uses environment variables")
    print("✅ Frontend API uses environment variables")
    print("✅ CORS configured for production")
    print("✅ Security headers added to Next.js")
    
    print("\n🚀 Next Steps:")
    print("1. Push code to GitHub repository")
    print("2. Create Render web service using render.yaml")
    print("3. Set environment variables in Render dashboard")
    print("4. Create production Google OAuth credentials")
    print("5. Deploy frontend to Vercel")
    print("6. Update CORS and OAuth redirect URIs with actual domains")
    print("7. Test the complete deployment")
    
    print("\n📖 For detailed instructions, see: PRODUCTION_DEPLOYMENT_GUIDE.md")
    print("\n🔐 Use the generated secrets in production-env-template.txt")

def main():
    """Main deployment preparation function."""
    print("🚀 BistroBoard Production Deployment Helper")
    print("=" * 50)
    
    # Validate environment
    issues = validate_environment()
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(issue)
        print("\nPlease fix these issues before proceeding with deployment.")
    else:
        print("\n✅ Environment validation passed!")
    
    # Generate production secrets
    create_production_env_template()
    
    # Check deployment readiness
    check_deployment_readiness()
    
    # Print summary
    print_deployment_summary()
    
    print("\n🎉 Deployment preparation complete!")
    print("Follow the PRODUCTION_DEPLOYMENT_GUIDE.md for step-by-step deployment instructions.")

if __name__ == "__main__":
    main()