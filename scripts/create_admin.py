"""
Create an admin account for Legal Chatbot.
Run: python scripts/create_admin.py
"""

import sys
from pathlib import Path

# Allow importing app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app import models
from app.core.security import get_password_hash


def get_input():
    email = input("Admin email: ").strip()
    if "@" not in email:
        raise ValueError("Invalid email.")

    full_name = input("Full name (optional): ").strip() or None

    password = input("Password (>=6 chars): ").strip()
    if len(password) < 6:
        raise ValueError("Password too short.")

    confirm = input("Confirm password: ").strip()
    if password != confirm:
        raise ValueError("Passwords do not match.")

    return email, full_name, password


def create_admin():
    print("\n=== CREATE ADMIN ACCOUNT ===\n")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    try:
        email, full_name, password = get_input()
    except Exception as e:
        print(f"Error: {e}")
        return False

    db: Session = SessionLocal()

    try:
        user = db.query(models.User).filter_by(email=email).first()

        if user:
            choice = input("User exists. Promote to admin? (y/n): ").lower()
            if choice == "y":
                user.role = "admin"
                db.commit()
                print("User promoted to admin.")
                return True
            return False

        admin = models.User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role="admin",
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nAdmin created successfully!")
        print(f"Email: {admin.email}")
        print(f"ID: {admin.id}")

        return True

    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(0 if create_admin() else 1)
