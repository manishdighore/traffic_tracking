# Car Tracking Backend

Modern FastAPI backend for real-time car tracking, detection, counting, and speed estimation.

## Features

- 🚗 **Vehicle Detection** - YOLOv8-based detection
- 📊 **Real-time Tracking** - Multi-object tracking across frames
- 🎨 **Color Recognition** - Vehicle color detection
- 💨 **Speed Estimation** - Real-time speed calculation
- 📈 **Analytics** - Statistics and data export
- 🔌 **WebSocket Streaming** - Real-time video feed with detections
- 💾 **Database Storage** - SQLite/PostgreSQL support

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download YOLOv8 model** (automatic on first run):
The system will automatically download the YOLOv8n model on first startup.

## Usage

### Start the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### REST API

- `GET /` - Health check
- `GET /api/stats` - Get overall statistics
- `GET /api/vehicles` - Get all detected vehicles (paginated)
- `GET /api/vehicles/{id}` - Get specific vehicle
- `DELETE /api/vehicles/{id}` - Delete vehicle record
- `POST /api/clear-data` - Clear all data
- `POST /api/upload-video` - Upload video file for processing

### WebSocket

- `WS /ws/video` - Real-time video streaming with detections

Example WebSocket client:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/video');

ws.onopen = () => {
  ws.send(JSON.stringify({
    source: 0  // 0 for webcam, or path to video file
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.frame: Base64 encoded frame
  // data.detections: Array of detected vehicles
  // data.count: Total vehicle count
};
```

## Configuration

### Speed Estimator Settings

Edit in `core/speed_estimator.py`:
```python
SpeedEstimator(
    pixels_per_meter=8.0,  # Calibration factor
    fps=30,                 # Video FPS
    roi_y=400,              # ROI line Y-coordinate
    tracking_threshold=50   # Tracking threshold in pixels
)
```

### Detection Confidence

Edit in `core/detector.py`:
```python
VehicleDetector(
    model_name='yolov8n.pt',  # Model variant (n, s, m, l, x)
    confidence_threshold=0.5   # Minimum confidence
)
```

## Database

The system uses SQLite by default. Database file: `car_tracking.db`

### Database Schema

**vehicles** table:
- `id`: Primary key
- `vehicle_type`: car, truck, bus, motorcycle, bicycle
- `color`: Detected color
- `speed`: Speed in km/h
- `direction`: up, down, left, right
- `size`: small, medium, large
- `confidence`: Detection confidence (0-1)
- `bbox_x1`, `bbox_y1`, `bbox_x2`, `bbox_y2`: Bounding box coordinates
- `detected_at`: Timestamp

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Project Structure
```
backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── core/
│   ├── detector.py         # Vehicle detection (YOLOv8)
│   ├── speed_estimator.py  # Speed estimation
│   ├── color_detector.py   # Color recognition
│   └── video_processor.py  # Video processing pipeline
└── models/
    ├── database.py         # Database models
    └── schemas.py          # Pydantic schemas
```

### Testing

Run the API:
```bash
python main.py
```

Test endpoints with curl:
```bash
# Health check
curl http://localhost:8000/

# Get statistics
curl http://localhost:8000/api/stats

# Get vehicles
curl http://localhost:8000/api/vehicles
```

## Performance Tips

1. **GPU Acceleration**: Install PyTorch with CUDA support for faster inference
2. **Model Selection**: Use YOLOv8n for speed, YOLOv8x for accuracy
3. **Frame Skip**: Process every Nth frame for lower latency
4. **Resolution**: Reduce input resolution for faster processing

## Troubleshooting

### Common Issues

**YOLOv8 model not found**:
- The model will auto-download on first run
- Manual download: `yolo task=detect mode=predict model=yolov8n.pt`

**Database locked error**:
- Close other connections to the database
- Restart the server

**WebSocket connection fails**:
- Check CORS settings in `main.py`
- Verify frontend URL in `allow_origins`

## License

MIT License - See LICENSE file for details
