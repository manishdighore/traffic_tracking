# ALPR Quick Testing Guide

## Testing Without YOLOv4 Weights

The system is designed to work even without ALPR weights. Here's how to test:

### 1. Start the Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

**Expected Console Output:**
```
🚀 Initializing models...
Loading YOLOv8 model: yolov8n.pt
YOLOv8 model loaded successfully!
🔍 Initializing License Plate Detection...
⚠️  Warning: YOLOv4 weights not found at yolo_weights/yolov4-tiny-license-plate.weights
   License plate detection will be disabled.
   Run download_yolo_weights.py to download the weights.
⚠️  ALPR initialization warning: ...
   License plate detection will be disabled.
✅ Models initialized successfully!
```

✅ This is normal! The system works without ALPR.

### 2. Test Vehicle Detection Only

Navigate to `http://localhost:3000` and you should see:
- Vehicle detection working ✅
- Color detection working ✅
- Speed estimation working ✅
- No license plates (expected without weights) ⚠️

## Testing With YOLOv4 Weights

### 1. Obtain Weights

#### Option A: Quick Test with Generic Weights
```bash
python download_yolo_weights.py
# Choose 'y' to download generic YOLOv4-tiny
```

⚠️ **Note**: Generic weights won't detect license plates, but will test the pipeline.

#### Option B: Train Custom Weights (Recommended)
1. Open: https://colab.research.google.com/drive/1zi0m3pE3KcWyKATRhqo4wTCSqglzLG3u
2. Follow the training notebook
3. Download your `.weights` and `.cfg` files
4. Place them in `backend/yolo_weights/`:
   ```
   backend/yolo_weights/
   ├── yolov4-tiny-license-plate.weights
   └── yolov4-tiny-license-plate.cfg
   ```

### 2. Restart Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

**Expected Console Output:**
```
🚀 Initializing models...
Loading YOLOv8 model: yolov8n.pt
YOLOv8 model loaded successfully!
🔍 Initializing License Plate Detection...
Initializing License Plate Detector...
Using weights: yolo_weights/yolov4-tiny-license-plate.weights
Using config: yolo_weights/yolov4-tiny-license-plate.cfg
Using dims: (256, 160)
License Plate Detector initialized successfully!
Initializing EasyOCR...
EasyOCR initialized.
Initializing super resolution...
Super resolution initialized (ESPCN x2).
✅ ALPR components initialized!
✅ Models initialized successfully!
```

### 3. Test ALPR

Now you should see:
- Vehicle detection ✅
- Color detection ✅
- Speed estimation ✅
- License plate detection ✅
- OCR text recognition ✅
- Plates displayed in UI ✅

## Database Migration

If you have an existing database:

```bash
python migrate_database.py
```

**Expected Output:**
```
============================================================
Database Migration: Adding ALPR Fields
============================================================

Adding license_plate column...
✓ license_plate column added
Adding plate_confidence column...
✓ plate_confidence column added

============================================================
✅ Migration completed successfully!
============================================================
```

## Verifying ALPR Works

### 1. Check Video Feed

In the browser at `http://localhost:3000`:
- Look for yellow "Plate:" badges on detected vehicles
- Check if plate numbers are being recognized
- Verify confidence percentages appear

### 2. Check Vehicle History

In the "Vehicle History" tab:
- Recent vehicles should show license plates
- Yellow badge with monospace font
- Confidence percentage in gray

### 3. Check Database

```bash
cd backend
python

>>> from models.database import SessionLocal, Vehicle
>>> db = SessionLocal()
>>> vehicles = db.query(Vehicle).all()
>>> for v in vehicles[:5]:
...     print(f"{v.vehicle_type}: {v.license_plate} ({v.plate_confidence})")
```

**Expected Output:**
```
car: AB123CD (0.87)
truck: None (None)
car: EF456GH (0.92)
```

### 4. Check API Response

```bash
curl http://localhost:8000/api/vehicles?limit=5
```

Look for:
```json
{
  "license_plate": "AB123CD",
  "plate_confidence": 0.87
}
```

## Common Test Scenarios

### Scenario 1: No Weights Installed
✅ **Expected**: System works, no plates detected
- Vehicle detection: ✅
- ALPR: ⚠️ Disabled

### Scenario 2: Generic Weights Installed
✅ **Expected**: ALPR initialized but won't detect plates
- Vehicle detection: ✅
- ALPR: ✅ Initialized
- Plates detected: ❌ (wrong model)

### Scenario 3: Trained Weights Installed
✅ **Expected**: Full ALPR functionality
- Vehicle detection: ✅
- ALPR: ✅ Working
- Plates detected: ✅
- OCR: ✅ Working

## Performance Testing

### Test ALPR Performance

```bash
cd backend
python

>>> from core.license_plate_detector import LicensePlateDetector
>>> from core.plate_ocr import PlateOCR
>>> import cv2
>>> import time

# Load test image
>>> img = cv2.imread("path/to/test/image.jpg")

# Test detection
>>> detector = LicensePlateDetector()
>>> start = time.time()
>>> plates = detector.detect(img)
>>> print(f"Detection: {(time.time() - start) * 1000:.1f}ms")

# Test OCR
>>> ocr = PlateOCR()
>>> start = time.time()
>>> text = ocr.read(plate_img)
>>> print(f"OCR: {(time.time() - start) * 1000:.1f}ms")
```

**Expected Performance:**
- Detection: 5-10ms per vehicle
- OCR: 50-80ms per plate
- Total: ~60-90ms per vehicle with plate

## Test Video Files

Use sample videos with European license plates:

```bash
# Download sample video
python download_sample_video.py

# Or use your own video
# Place in: sample_videos/your_video.mp4
```

## Troubleshooting Tests

### Problem: "EasyOCR not available"

**Solution:**
```bash
pip install easyocr==1.7.0
```

### Problem: "opencv-contrib-python" not found

**Solution:**
```bash
pip install opencv-contrib-python==4.8.1.78
```

### Problem: Database errors

**Solution:**
```bash
# Delete old database
rm backend/car_tracking.db

# Or run migration
python migrate_database.py
```

### Problem: Plates detected but no text

**Possible causes:**
1. OCR not initialized (check console)
2. Plate images too small (check super resolution)
3. Wrong OCR backend (try switching)

**Test:**
```bash
cd backend
python

>>> from core.plate_ocr import PlateOCR
>>> ocr = PlateOCR(use_tesseract=False)  # Try EasyOCR
>>> # or
>>> ocr = PlateOCR(use_tesseract=True)   # Try Tesseract
```

## Visual Testing Checklist

When the system is running:

- [ ] Video feed displays in browser
- [ ] Vehicles are detected with bounding boxes
- [ ] Vehicle IDs appear above boxes
- [ ] Colors are detected correctly
- [ ] Speed is calculated (when crossing ROI)
- [ ] License plates appear (if weights available)
- [ ] Plates show confidence scores
- [ ] Vehicle history shows all detections
- [ ] Database stores plate numbers
- [ ] Dashboard shows statistics

## Next Steps

Once ALPR is working:

1. **Fine-tune detection**:
   - Adjust confidence thresholds
   - Modify network input size
   - Test with different lighting

2. **Improve OCR accuracy**:
   - Add preprocessing steps
   - Use super resolution models
   - Validate plate formats

3. **Add features**:
   - Plate matching against watchlist
   - Alert system for specific plates
   - Export detected plates to CSV
   - Search by plate number

4. **Optimize performance**:
   - Skip frames for OCR
   - Use GPU acceleration
   - Batch processing

## Success Indicators

Your ALPR integration is working correctly if:

✅ Backend starts without errors
✅ Console shows "ALPR components initialized"
✅ Vehicles are detected in video feed
✅ License plates appear in frontend (with weights)
✅ Plates are stored in database
✅ Confidence scores are displayed
✅ System works even without ALPR weights

---

**Happy Testing! 🧪🚗🔍**
