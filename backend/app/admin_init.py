"""
Admin Command Center Database Initialization
Creates admin users and updates existing data for admin features
"""

from sqlalchemy.orm import Session
from .database import get_db, engine
from .models import User, AdminAuditLog, UserEventLog
from .admin_auth import get_password_hash
from datetime import datetime

def create_admin_user(db: Session, username: str, password: str, name: str, email: str):
    """Create an admin user if it doesn't exist"""
    existing_admin = db.query(User).filter(User.username == username).first()
    if existing_admin:
        print(f"Admin user '{username}' already exists")
        return existing_admin
    
    admin_user = User(
        username=username,
        password_hash=get_password_hash(password),
        role="admin",
        name=name,
        email=email,
        phone="555-0000",
        address="Admin Office",
        description="System Administrator",
        is_active=True,
        status="active"
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"Created admin user: {username}")
    return admin_user

def update_existing_users_for_admin(db: Session):
    """Update existing users to have admin-compatible fields"""
    users = db.query(User).filter(User.role.in_(["restaurant", "vendor"])).all()
    
    updated_count = 0
    for user in users:
        needs_update = False
        
        # Set default values for new admin fields if they're None
        if user.is_active is None:
            user.is_active = True
            needs_update = True
        
        if user.status is None:
            user.status = "active"
            needs_update = True
        
        if needs_update:
            updated_count += 1
    
    if updated_count > 0:
        db.commit()
        print(f"Updated {updated_count} existing users with admin fields")
    else:
        print("All existing users already have admin fields")

def create_sample_vendor_pending_approval(db: Session):
    """Create a sample vendor in pending approval status for demo"""
    existing_pending = db.query(User).filter(
        User.username == "pending_vendor1"
    ).first()
    
    if existing_pending:
        print("Sample pending vendor already exists")
        return
    
    pending_vendor = User(
        username="pending_vendor1",
        password_hash=get_password_hash("demo123"),
        role="vendor",
        name="Fresh Farms Co.",
        email="contact@freshfarms.com",
        phone="555-0123",
        address="123 Farm Road, Valley City",
        description="Organic produce supplier seeking approval",
        is_active=False,
        status="pending_approval"
    )
    
    db.add(pending_vendor)
    db.commit()
    
    print("Created sample pending vendor for demo")

def initialize_admin_system():
    """Initialize the admin system with default data"""
    print("Initializing Admin Command Center...")
    
    # Create database session
    db = next(get_db())
    
    try:
        # Create default admin user
        admin_user = create_admin_user(
            db=db,
            username="admin",
            password="admin123",
            name="System Administrator",
            email="admin@bistroboard.com"
        )
        
        # Update existing users for admin compatibility
        update_existing_users_for_admin(db)
        
        # Create sample pending vendor
        create_sample_vendor_pending_approval(db)
        
        # Log the initialization
        init_log = AdminAuditLog(
            admin_id=admin_user.id,
            action="system_initialized",
            details={
                "message": "Admin Command Center initialized",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        db.add(init_log)
        db.commit()
        
        print("✅ Admin Command Center initialization complete!")
        print(f"Default admin credentials: admin / admin123")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_admin_system()