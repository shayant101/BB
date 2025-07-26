# Load environment variables FIRST
from dotenv import load_dotenv
import os
import logging

# Configure logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables with explicit path before other imports
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    logger.info(f"Loading .env from: {env_path}")
else:
    logger.warning(f".env file not found at {env_path}")

# Debug: Log environment variable loading status
logger.info(f"GOOGLE_CLIENT_ID loaded: {'Yes' if os.getenv('GOOGLE_CLIENT_ID') else 'No'}")
logger.info(f"GOOGLE_CLIENT_SECRET loaded: {'Yes' if os.getenv('GOOGLE_CLIENT_SECRET') else 'No'}")


# Now, import other modules
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .mongodb import connect_to_mongo, close_mongo_connection, check_database_health
from .routers import auth, orders, profiles, marketplace, vendor_profile
from . import admin_routes

# Create FastAPI app
app = FastAPI(
    title="BistroBoard API",
    description="Restaurant-Supplier Order Management System with MongoDB Atlas",
    version="2.0.0"
)

# Configure comprehensive CORS middleware
# Configure robust CORS for production
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = []

if not allowed_origins_str:
    # Default to a permissive policy for local development if not set
    logger.warning("ALLOWED_ORIGINS not set, defaulting to permissive CORS policy for development.")
    allowed_origins.append("*")
else:
    # Handle multiple origins and automatically include www/non-www variants
    base_origins = [origin.strip() for origin in allowed_origins_str.split(',')]
    for origin in base_origins:
        if origin not in allowed_origins:
            allowed_origins.append(origin)
        
        # If it's a root domain, also add the 'www' version
        if origin.startswith("https://") and not origin.startswith("https://www."):
            www_origin = origin.replace("https://", "https://www.")
            if www_origin not in allowed_origins:
                allowed_origins.append(www_origin)

logger.info(f"Final CORS origins configured: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(marketplace.router, prefix="/api/marketplace", tags=["marketplace"])
app.include_router(vendor_profile.router, prefix="/api/vendor", tags=["vendor-profile"])
app.include_router(admin_routes.router, tags=["admin"])

# MongoDB connection management
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to BistroBoard API with MongoDB Atlas",
        "version": "2.0.0",
        "database": "MongoDB Atlas",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    db_healthy = await check_database_health()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "mongodb",
        "database_status": "connected" if db_healthy else "disconnected"
    }