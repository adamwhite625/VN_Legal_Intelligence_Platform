#!/usr/bin/env python3
"""
Script để tạo các bảng trong database.
Chạy: python scripts/create_tables.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import engine, Base
from app.models import User, ChatSession, Message, SavedLaw, SavedQuestion, MessageSummary

def create_all_tables():
    """Create all tables in database"""
    print("Creating all database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!")
        
        # Print table info
        print("\nCreated tables:")
        print("  - users")
        print("  - sessions (with session_type, law_id fields)")
        print("  - messages (with sources field)")
        print("  - saved_laws")
        print("  - saved_questions")
        print("  - message_summaries")
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_all_tables()
