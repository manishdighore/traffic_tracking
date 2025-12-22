"""
License Plate Detection Module using YOLOv8
Detects license plates using YOLOv8 model from Video-ANPR
Based on: https://github.com/sveyek/Video-ANPR
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import os
from ultralytics import YOLO


class LicensePlateDetector:
    """License plate detector using fine-tuned YOLOv8 model"""
    
    def __init__(
        self,
        model_path: str = "license_plate_detector.pt",
        confidence_threshold: float = 0.5
    ):
        """
        Initialize license plate detector
        
        Args:
            model_path: Path to YOLOv8 weights file (.pt)
            confidence_threshold: Minimum confidence for detection
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"⚠️  Warning: YOLOv8 license plate model not found at {model_path}")
            print("   License plate detection will be disabled.")
            print("   Download from: https://github.com/sveyek/Video-ANPR/raw/main/models/license_plate_detector.pt")
            return
        
        print(f"Initializing License Plate Detector (YOLOv8)...")
        print(f"Using model: {model_path}")
        print(f"Confidence threshold: {self.confidence_threshold}")
        
        try:
            # Load YOLOv8 model
            self.model = YOLO(model_path)
            print("✅ License Plate Detector (YOLOv8) initialized successfully!")
        except Exception as e:
            print(f"❌ Error loading YOLOv8 model: {e}")
            self.model = None
    
    def detect(
        self,
        frame: np.ndarray,
        vehicle_bbox: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Detect license plates in a frame or vehicle region
        
        Args:
            frame: Input frame (numpy array)
            vehicle_bbox: Optional vehicle bounding box [x1, y1, x2, y2] to search within
            
        Returns:
            List of detected plates with bounding boxes and confidence
        """
        if self.model is None:
            return []
        
        # If vehicle bbox is provided, crop to that region
        if vehicle_bbox is not None:
            x1, y1, x2, y2 = map(int, vehicle_bbox)
            # Add some padding to ensure we don't crop the plate
            padding = 10
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(frame.shape[1], x2 + padding)
            y2 = min(frame.shape[0], y2 + padding)
            
            roi = frame[y1:y2, x1:x2]
            offset_x = x1
            offset_y = y1
        else:
            roi = frame
            offset_x = 0
            offset_y = 0
        
        # Run YOLOv8 detection
        results = self.model(roi, conf=self.confidence_threshold, verbose=False)
        
        plates = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates
                x1_box, y1_box, x2_box, y2_box = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                
                # Adjust coordinates if we cropped
                x1_abs = int(x1_box + offset_x)
                y1_abs = int(y1_box + offset_y)
                x2_abs = int(x2_box + offset_x)
                y2_abs = int(y2_box + offset_y)
                
                plates.append({
                    'bbox': [x1_abs, y1_abs, x2_abs, y2_abs],
                    'confidence': confidence
                })
        
        return plates
    
    def extract_plate_image(
        self,
        frame: np.ndarray,
        plate_bbox: List[int],
        padding: int = 2
    ) -> np.ndarray:
        """
        Extract license plate region from frame
        
        Args:
            frame: Input frame
            plate_bbox: Plate bounding box [x1, y1, x2, y2]
            padding: Padding pixels around plate
            
        Returns:
            Cropped plate image
        """
        x1, y1, x2, y2 = map(int, plate_bbox)
        
        # Add padding
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(frame.shape[1], x2 + padding)
        y2 = min(frame.shape[0], y2 + padding)
        
        return frame[y1:y2, x1:x2]
    
    def draw_plates(
        self,
        frame: np.ndarray,
        plates: List[Dict],
        color: Tuple[int, int, int] = (0, 255, 255),  # Yellow
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw detected plates on frame
        
        Args:
            frame: Input frame
            plates: List of detected plates
            color: BGR color for bounding box
            thickness: Line thickness
            
        Returns:
            Frame with drawn plates
        """
        frame_copy = frame.copy()
        
        for plate in plates:
            x1, y1, x2, y2 = map(int, plate['bbox'])
            confidence = plate['confidence']
            
            # Draw bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, thickness)
            
            # Draw confidence label
            label = f"Plate {confidence:.2f}"
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(
                frame_copy,
                (x1, y1 - label_h - baseline - 5),
                (x1 + label_w, y1),
                color,
                -1
            )
            cv2.putText(
                frame_copy,
                label,
                (x1, y1 - baseline - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1
            )
        
        return frame_copy
    
    def map_plate_to_vehicle(
        self,
        plate_bbox: List[int],
        vehicle_bboxes: List[Tuple[List[int], int]]
    ) -> Optional[int]:
        """
        Map detected plate to a vehicle
        
        Args:
            plate_bbox: Plate bounding box [x1, y1, x2, y2]
            vehicle_bboxes: List of (vehicle_bbox, vehicle_id) tuples
            
        Returns:
            Vehicle ID that contains this plate, or None
        """
        x1, y1, x2, y2 = plate_bbox
        
        for vehicle_bbox, vehicle_id in vehicle_bboxes:
            x1_car, y1_car, x2_car, y2_car = vehicle_bbox
            
            # Check if plate is inside vehicle bounding box
            if (x1 > x1_car and y1 > y1_car and 
                x2 < x2_car and y2 < y2_car):
                return vehicle_id
        
        return None
