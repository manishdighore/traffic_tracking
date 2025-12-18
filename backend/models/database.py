"""
Database models and configuration
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database URL - Using SQLite for simplicity
DATABASE_URL = "sqlite:///./car_tracking.db"

# Create engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base
Base = declarative_base()


class Vehicle(Base):
    """Vehicle detection model"""
    
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String, index=True)  # car, truck, bus, etc.
    color = Column(String)
    speed = Column(Float, nullable=True)  # in km/h
    direction = Column(String, nullable=True)  # up, down, left, right
    size = Column(String, nullable=True)  # small, medium, large
    confidence = Column(Float)
    bbox_x1 = Column(Integer)
    bbox_y1 = Column(Integer)
    bbox_x2 = Column(Integer)
    bbox_y2 = Column(Integer)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Vehicle {self.id}: {self.vehicle_type} - {self.color}>"
