"""
Pydantic schemas for API validation
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VehicleBase(BaseModel):
    """Base vehicle schema"""
    vehicle_type: str
    color: str
    speed: Optional[float] = None
    direction: Optional[str] = None
    size: Optional[str] = None
    confidence: float


class VehicleCreate(VehicleBase):
    """Schema for creating vehicle"""
    bbox_x1: int
    bbox_y1: int
    bbox_x2: int
    bbox_y2: int


class VehicleResponse(VehicleBase):
    """Schema for vehicle response"""
    id: int
    bbox_x1: int
    bbox_y1: int
    bbox_x2: int
    bbox_y2: int
    detected_at: datetime
    
    class Config:
        from_attributes = True


class VehicleDetection(BaseModel):
    """Schema for real-time detection"""
    bbox: list[int]
    center: list[int]
    width: int
    height: int
    confidence: float
    class_name: str
    color: Optional[str] = None
    speed: Optional[float] = None
    direction: Optional[str] = None
    vehicle_id: Optional[int] = None


class StatsResponse(BaseModel):
    """Schema for statistics response"""
    total_vehicles: int
    vehicle_types: dict
    vehicle_colors: dict
    average_speed: float
