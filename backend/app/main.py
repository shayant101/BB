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
from .routers import auth, orders, profiles, marketplace, vendor_profile, inventory, storefront, storefront_orders, email
from . import admin_routes

# Create FastAPI app
app = FastAPI(
    title="BistroBoard API",
    description="Restaurant-Supplier Order Management System with MongoDB Atlas",
    version="2.0.0"
)

# Configure comprehensive CORS middleware
# Configure a fully permissive CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(marketplace.router, prefix="/api/marketplace", tags=["marketplace"])
app.include_router(vendor_profile.router, prefix="/api/vendor", tags=["vendor-profile"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(storefront.router, prefix="/api", tags=["storefront"])
app.include_router(storefront_orders.router, prefix="/api/storefront", tags=["storefront-orders"])
app.include_router(email.router, prefix="/api/email", tags=["email"])
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