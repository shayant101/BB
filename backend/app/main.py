from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .mongodb import connect_to_mongo, close_mongo_connection, check_database_health
from .routers import auth, orders, profiles, marketplace, vendor_profile
from . import admin_routes

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="BistroBoard API",
    description="Restaurant-Supplier Order Management System with MongoDB Atlas",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
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