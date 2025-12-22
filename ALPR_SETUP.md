# Automatic License Plate Recognition (ALPR) Setup

This document describes the ALPR integration based on [BarthPaleologue/ALPR](https://github.com/BarthPaleologue/ALPR).

## Overview

The traffic tracking system now includes automatic license plate detection and OCR capabilities for European license plates. The system uses:

1. **YOLOv4-tiny** for license plate detection
2. **EasyOCR or Tesseract** for optical character recognition
3. **Super Resolution** for enhancing small license plates

## Features

- ✅ Real-time license plate detection in vehicle bounding boxes
- ✅ OCR with multiple backend support (EasyOCR, Tesseract)
- ✅ Super resolution for upscaling small plates
- ✅ European plate format support (French, Romanian, etc.)
- ✅ Database storage with confidence scores
- ✅ Fuzzy matching with Levenshtein distance for known plates
- ✅ Graceful degradation (works without ALPR if weights unavailable)

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `easyocr==1.7.0` - OCR engine
- `pytesseract==0.3.10` - Alternative OCR engine
- `opencv-contrib-python==4.8.1.78` - Super resolution models

### 2. Install Tesseract (Optional)

If you want to use Tesseract OCR:

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install and add to PATH
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 3. Get YOLOv4 Weights for License Plates

You have several options:

#### Option A: Train Your Own Model (Recommended)

Use the ALPR repository training notebook:
- https://colab.research.google.com/drive/1zi0m3pE3KcWyKATRhqo4wTCSqglzLG3u

#### Option B: Use Pre-trained Weights

1. Download or train weights for European license plates
2. Place the files in `backend/yolo_weights/`:
   - `yolov4-tiny-license-plate.weights`
   - `yolov4-tiny-license-plate.cfg`

#### Option C: Use Example Script

```bash
python download_yolo_weights.py
```

This will guide you through the download process and create example config files.

### 4. Download Super Resolution Models (Optional)

For better OCR on small plates, download super resolution models:

```bash
cd backend
mkdir -p super_resolution

# Download ESPCN x2 model (recommended - fast and small)
wget https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/ESPCN_x2.pb -O super_resolution/ESPCN_x2.pb

# Or download EDSR x4 model (slower but higher quality)
wget https://github.com/Saafke/EDSR_Tensorflow/raw/master/models/EDSR_x4.pb -O super_resolution/EDSR_x4.pb
```

## Usage

### Basic Usage

The ALPR system is automatically integrated into the video processing pipeline. When properly configured:

1. Vehicles are detected using YOLOv8
2. License plates are detected within vehicle bounding boxes
3. Plate images are extracted and enhanced
4. OCR reads the plate text
5. Results are stored in the database with confidence scores

### API Response

Vehicle detections now include license plate information:

```json
{
  "vehicle_id": 1,
  "class_name": "car",
  "color": "blue",
  "speed": 45.2,
  "license_plate": "AB123CD",
  "plate_confidence": 0.87
}
```

### Configuration

#### Change OCR Backend

In `main.py`, modify:

```python
# Use EasyOCR (default)
plate_ocr = PlateOCR(use_tesseract=False)

# Use Tesseract
plate_ocr = PlateOCR(use_tesseract=True)
```

#### Adjust Detection Parameters

In `core/license_plate_detector.py`:

```python
plate_detector = LicensePlateDetector(
    weights_path="yolo_weights/yolov4-tiny-license-plate.weights",
    config_path="yolo_weights/yolov4-tiny-license-plate.cfg",
    dims=(256, 160),  # Network input size
    confidence_threshold=0.5,  # Minimum detection confidence
    nms_threshold=0.4  # Non-maximum suppression threshold
)
```

## Architecture

### Components

1. **LicensePlateDetector** (`core/license_plate_detector.py`)
   - Detects license plates using YOLOv4-tiny
   - Searches within vehicle bounding boxes
   - Returns plate coordinates and confidence

2. **PlateOCR** (`core/plate_ocr.py`)
   - Reads text from plate images
   - Supports EasyOCR and Tesseract
   - Preprocesses images for better accuracy
   - Includes super resolution for small plates

3. **VideoProcessor** Integration
   - Automatically detects plates for each vehicle
   - Passes plate images to OCR
   - Stores results in database

### Database Schema

The `Vehicle` model now includes:

```python
license_plate = Column(String, nullable=True, index=True)
plate_confidence = Column(Float, nullable=True)
```

## Advanced Features

### Fuzzy Matching

Match detected plates against a known list:

```python
from core.plate_ocr import match_plate_to_database

detected = "AB123CD"
known_plates = ["AB123CD", "EF456GH", "IJ789KL"]

best_match, distance = match_plate_to_database(detected, known_plates, threshold=2)
# Returns: ("AB123CD", 0)
```

### Plate Validation

Validate plate format:

```python
from core.plate_ocr import PlateOCR

ocr = PlateOCR()
is_valid = ocr.validate_plate_format("AB123CD", country="FR")
```

### OCR Confidence Scores

Get confidence scores with OCR results:

```python
plate_text, confidence = plate_ocr.read_with_confidence(plate_img)
```

## Training Data

The ALPR repository uses these datasets:

1. **Romanian License Plates**: https://github.com/RobertLucian/license-plate-dataset
2. **French License Plates**: https://github.com/qanastek/FrenchLicencePlateDataset
3. **PP4AV (Paris + Strasbourg)**: https://huggingface.co/datasets/khaclinh/pp4av

## Performance

Based on the ALPR repository benchmarks:

- **YOLOv4-tiny (256x160)**: ~5-10ms per detection
- **EasyOCR**: ~50ms per plate (18 FPS)
- **Tesseract**: ~80ms per plate (11 FPS)
- **Super Resolution (ESPCN x2)**: ~10ms per plate

## Troubleshooting

### ALPR Not Working

If license plate detection is not working:

1. **Check weights exist**:
   ```bash
   ls backend/yolo_weights/yolov4-tiny-license-plate.*
   ```

2. **Check console output**:
   ```
   ⚠️  Warning: YOLOv4 weights not found
   ```

3. **System continues working**: The system gracefully degrades - vehicle detection still works without ALPR.

### Poor OCR Accuracy

1. **Use super resolution**: Download ESPCN or EDSR models
2. **Increase plate size**: Adjust detection to capture more context
3. **Try different OCR backend**: Switch between EasyOCR and Tesseract
4. **Improve lighting**: Better video quality improves results

### Performance Issues

1. **Use smaller super resolution model**: ESPCN x2 instead of EDSR x4
2. **Skip OCR for some frames**: Process every Nth vehicle
3. **Use GPU acceleration**: EasyOCR supports CUDA if available
4. **Reduce detection frequency**: Only detect plates in ROI

## Example Output

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

## References

- Original ALPR Repository: https://github.com/BarthPaleologue/ALPR
- YOLOv4 Paper: https://arxiv.org/abs/2004.10934
- EasyOCR: https://github.com/JaidedAI/EasyOCR
- Tesseract: https://github.com/tesseract-ocr/tesseract

## License

The ALPR integration follows the same license as the original ALPR repository. Please refer to their repository for licensing information.

## Credits

This ALPR integration is based on the work by:
- BarthPaleologue: https://github.com/BarthPaleologue/ALPR
- École Polytechnique X-INF573 course project
