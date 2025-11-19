from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash


def init_database():
    """Initialize database with default admin user"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            # Create default admin user
            admin_user = models.User(
                username="admin",
                email="admin@translator-qa.com",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created: username='admin', password='admin123'")
        else:
            print("Admin user already exists")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
