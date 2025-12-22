"""
FastAPI Backend for Car Tracking System
Handles video processing, object detection, and real-time streaming
"""
import asyncio
import cv2
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional
import json
from datetime import datetime
import base64

from models.database import engine, Base, SessionLocal
from models.schemas import VehicleDetection, VehicleCreate, VehicleResponse
from core.detector import VehicleDetector
from core.speed_estimator import SpeedEstimator
from core.color_detector import ColorDetector
from core.license_plate_detector_v8 import LicensePlateDetector
from core.plate_ocr_v8 import PlateOCR
from core.video_processor import VideoProcessor

# Create database tables
Base.metadata.create_all(bind=engine)

# Global instances
vehicle_detector = None
speed_estimator = None
color_detector = None
plate_detector = None
plate_ocr = None
video_processor = None
active_connections: List[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    global vehicle_detector, speed_estimator, color_detector, plate_detector, plate_ocr, video_processor
    
    print("🚀 Initializing models...")
    vehicle_detector = VehicleDetector()
    speed_estimator = SpeedEstimator()
    color_detector = ColorDetector()
    
    # Initialize ALPR components (optional, will work without weights)
    print("🔍 Initializing License Plate Detection...")
    try:
        plate_detector = LicensePlateDetector()
        plate_ocr = PlateOCR(use_gpu=False)  # Use EasyOCR with CPU
        print("✅ ALPR components initialized!")
    except Exception as e:
        print(f"⚠️  ALPR initialization warning: {e}")
        print("   License plate detection will be disabled.")
        plate_detector = None
        plate_ocr = None
    
    video_processor = VideoProcessor(
        detector=vehicle_detector,
        speed_estimator=speed_estimator,
        color_detector=color_detector,
        plate_detector=plate_detector,
        plate_ocr=plate_ocr
    )
    print("✅ Models initialized successfully!")
    
    yield
    
    # Shutdown (cleanup if needed)
    print("👋 Shutting down...")


app = FastAPI(
    title="Car Tracking API",
    description="Real-time vehicle detection, tracking, counting, and speed estimation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js ports
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Car Tracking Backend API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    db = SessionLocal()
    try:
        from models.database import Vehicle
        total_vehicles = db.query(Vehicle).count()
        
        # Get vehicle type distribution
        from sqlalchemy import func
        type_distribution = db.query(
            Vehicle.vehicle_type,
            func.count(Vehicle.id)
        ).group_by(Vehicle.vehicle_type).all()
        
        # Get color distribution
        color_distribution = db.query(
            Vehicle.color,
            func.count(Vehicle.id)
        ).group_by(Vehicle.color).all()
        
        # Get average speed
        avg_speed = db.query(func.avg(Vehicle.speed)).scalar() or 0
        
        return {
            "total_vehicles": total_vehicles,
            "vehicle_types": {vtype: count for vtype, count in type_distribution},
            "vehicle_colors": {color: count for color, count in color_distribution},
            "average_speed": round(avg_speed, 2)
        }
    finally:
        db.close()


@app.get("/api/vehicles", response_model=List[VehicleResponse])
async def get_vehicles(skip: int = 0, limit: int = 100):
    """Get all detected vehicles"""
    db = SessionLocal()
    try:
        from models.database import Vehicle
        vehicles = db.query(Vehicle).offset(skip).limit(limit).all()
        return vehicles
    finally:
        db.close()


@app.get("/api/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: int):
    """Get specific vehicle by ID"""
    db = SessionLocal()
    try:
        from models.database import Vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return vehicle
    finally:
        db.close()


@app.websocket("/ws/video")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time video streaming with detections"""
    await websocket.accept()
    active_connections.append(websocket)
    
    cap = None
    is_paused = False
    frame_skip = 0
    
    try:
        # Receive initial configuration from client
        data = await websocket.receive_text()
        config = json.loads(data)
        
        video_source = config.get("source", 0)  # 0 for webcam, or video path
        roi_position = config.get("roi_y", None)  # ROI line Y position
        
        # Set ROI position if provided
        if roi_position is not None:
            video_processor.set_roi_position(int(roi_position))
            print(f"ROI position set to: {roi_position}")
        
        # Convert to integer if it's a string number (for webcam)
        if isinstance(video_source, str) and video_source.isdigit():
            video_source = int(video_source)
        
        print(f"Opening video source: {video_source}")
        
        # Start video processing
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            error_msg = f"Could not open video source: {video_source}"
            print(error_msg)
            await websocket.send_json({
                "type": "error",
                "message": error_msg
            })
            return
        
        print(f"Video source opened successfully. Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        
        frame_count = 0
        
        # Main processing loop
        while True:
            # Check for commands from client (non-blocking)
            try:
                command_data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.001
                )
                command = json.loads(command_data)
                
                if command.get("action") == "pause":
                    is_paused = not is_paused
                    print(f"Playback {'paused' if is_paused else 'resumed'}")
                    continue
                    
                elif command.get("action") == "skip":
                    frame_skip = command.get("frames", 0)
                    print(f"Skipping {frame_skip} frames")
                    
            except asyncio.TimeoutError:
                pass  # No command received, continue processing
            except json.JSONDecodeError:
                pass  # Invalid command, ignore
            
            # Handle pause
            if is_paused:
                await asyncio.sleep(0.1)
                continue
            
            # Handle frame skipping
            if frame_skip != 0:
                if frame_skip > 0:
                    # Skip forward
                    for _ in range(frame_skip):
                        ret = cap.grab()
                        if not ret:
                            break
                        frame_count += 1
                else:
                    # Skip backward (seek to earlier position)
                    current_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    new_pos = max(0, current_pos + frame_skip)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
                    frame_count = int(new_pos)
                
                frame_skip = 0
            
            # Read and process frame
            ret, frame = cap.read()
            if not ret:
                # End of video
                await websocket.send_json({
                    "type": "end",
                    "message": "Video ended"
                })
                break
            
            frame_count += 1
            
            # Process frame
            result = video_processor.process_frame(frame, frame_count)
            
            # Encode frame as base64
            _, buffer = cv2.imencode('.jpg', result['frame'])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send detection data
            await websocket.send_json({
                "type": "frame",
                "frame": frame_base64,
                "detections": result['detections'],
                "count": result['total_count'],
                "frame_number": frame_count,
                "timestamp": datetime.now().isoformat()
            })
            
            # Control frame rate
            await asyncio.sleep(0.033)  # ~30 FPS
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {str(e)}")
    finally:
        if cap is not None:
            cap.release()
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file for processing"""
    try:
        # Create uploads directory if it doesn't exist
        import os
        os.makedirs("uploads", exist_ok=True)
        
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "status": "success",
            "message": "Video uploaded successfully",
            "filename": file.filename,
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: int):
    """Delete a vehicle record"""
    db = SessionLocal()
    try:
        from models.database import Vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        db.delete(vehicle)
        db.commit()
        return {"status": "success", "message": "Vehicle deleted"}
    finally:
        db.close()


@app.post("/api/clear-data")
async def clear_all_data():
    """Clear all vehicle detection data"""
    db = SessionLocal()
    try:
        from models.database import Vehicle
        db.query(Vehicle).delete()
        db.commit()
        return {"status": "success", "message": "All data cleared"}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
