"""
Database Migration: Add License Plate Fields
Adds license_plate and plate_confidence columns to existing Vehicle table
"""
from sqlalchemy import create_engine, Column, String, Float, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import DATABASE_URL, Vehicle, Base

def migrate_database():
    """Add license plate columns to existing database"""
    print("=" * 60)
    print("Database Migration: Adding ALPR Fields")
    print("=" * 60)
    print()
    
    # Create engine
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    try:
        # Check if database exists
        with engine.connect() as conn:
            # Check if vehicles table exists
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='vehicles'"
            ))
            
            if result.fetchone() is None:
                print("✓ No existing vehicles table found.")
                print("  Creating new database with ALPR fields...")
                Base.metadata.create_all(bind=engine)
                print("✓ Database created successfully!")
                return
            
            # Check if license_plate column already exists
            result = conn.execute(text("PRAGMA table_info(vehicles)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'license_plate' in columns:
                print("✓ License plate columns already exist in database.")
                print("  No migration needed.")
                return
            
            print("Adding license_plate column...")
            conn.execute(text(
                "ALTER TABLE vehicles ADD COLUMN license_plate VARCHAR"
            ))
            conn.commit()
            print("✓ license_plate column added")
            
            print("Adding plate_confidence column...")
            conn.execute(text(
                "ALTER TABLE vehicles ADD COLUMN plate_confidence FLOAT"
            ))
            conn.commit()
            print("✓ plate_confidence column added")
            
            print()
            print("=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print()
        print("Solution: Delete the existing database and let the system create a new one:")
        print("  rm backend/car_tracking.db")
        print("  # Then restart the backend")
        sys.exit(1)


if __name__ == "__main__":
    migrate_database()
