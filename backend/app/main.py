from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables
from .routers import auth, orders, profiles, marketplace, vendor_profile

# Create FastAPI app
app = FastAPI(
    title="BistroBoard API",
    description="Restaurant-Supplier Order Management System",
    version="1.0.0"
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
app.include_router(auth.router, tags=["authentication"])
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(profiles.router, prefix="/api", tags=["profiles"])
app.include_router(marketplace.router, prefix="/api/marketplace", tags=["marketplace"])
app.include_router(vendor_profile.router, prefix="/api/vendor", tags=["vendor-profile"])

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to BistroBoard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}