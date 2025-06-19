from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import User
from app.auth_simple import get_password_hash

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_database():
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already seeded. Skipping...")
            return
        
        # Create restaurant user
        restaurant_user = User(
            username="restaurant1",
            password_hash=get_password_hash("demo123"),
            role="restaurant",
            name="Mario's Pizzeria",
            email="mario@mariospizza.com",
            phone="(555) 123-4567",
            address="123 Main St, Downtown, CA 90210",
            description="Family-owned Italian restaurant serving authentic pizzas and pasta since 1985. We pride ourselves on using fresh, locally-sourced ingredients and traditional recipes passed down through generations."
        )
        
        # Create vendor user
        vendor_user = User(
            username="vendor1",
            password_hash=get_password_hash("demo123"),
            role="vendor",
            name="Fresh Valley Produce",
            email="orders@freshvalley.com",
            phone="(555) 987-6543",
            address="456 Farm Road, Valley, CA 90211",
            description="Premium organic produce supplier serving restaurants across the region. We specialize in farm-fresh vegetables, herbs, and specialty ingredients with same-day delivery available."
        )
        
        # Add users to database
        db.add(restaurant_user)
        db.add(vendor_user)
        db.commit()
        
        print("Database seeded successfully!")
        print("\nTest Users Created:")
        print("Restaurant: username='restaurant1', password='demo123'")
        print("Vendor: username='vendor1', password='demo123'")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()