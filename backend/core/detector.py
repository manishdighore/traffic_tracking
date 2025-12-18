"""
Vehicle Detection Module using YOLOv8
Detects and classifies vehicles in video frames
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional


class VehicleDetector:
    """Vehicle detector using YOLOv8 model"""
    
    # Vehicle class IDs from COCO dataset
    VEHICLE_CLASSES = {
        2: 'car',
        3: 'motorcycle',
        5: 'bus',
        7: 'truck',
        1: 'bicycle'
    }
    
    def __init__(self, model_name: str = 'yolov8n.pt', confidence_threshold: float = 0.5):
        """
        Initialize vehicle detector
        
        Args:
            model_name: YOLOv8 model variant (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
            confidence_threshold: Minimum confidence for detection
        """
        print(f"Loading YOLOv8 model: {model_name}")
        self.model = YOLO(model_name)
        self.confidence_threshold = confidence_threshold
        print("YOLOv8 model loaded successfully!")
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect vehicles in a frame
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            List of detected vehicles with bounding boxes and metadata
        """
        # Run inference
        results = self.model(frame, verbose=False)[0]
        
        detections = []
        
        # Process each detection
        for box in results.boxes:
            # Get class ID
            class_id = int(box.cls[0])
            
            # Check if it's a vehicle class
            if class_id not in self.VEHICLE_CLASSES:
                continue
            
            # Get confidence
            confidence = float(box.conf[0])
            
            # Filter by confidence
            if confidence < self.confidence_threshold:
                continue
            
            # Get bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            # Calculate center point
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            
            # Calculate width and height
            width = int(x2 - x1)
            height = int(y2 - y1)
            
            detection = {
                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                'center': [center_x, center_y],
                'width': width,
                'height': height,
                'confidence': round(confidence, 2),
                'class_id': class_id,
                'class_name': self.VEHICLE_CLASSES[class_id],
                'area': width * height
            }
            
            detections.append(detection)
        
        return detections
    
    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            color: Bounding box color (BGR)
            thickness: Line thickness
            
        Returns:
            Frame with drawn detections
        """
        annotated_frame = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
            
            # Prepare label
            label = f"{detection['class_name']}: {detection['confidence']:.2f}"
            
            # Draw label background
            label_size, baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            y_label = max(y1, label_size[1] + 10)
            
            cv2.rectangle(
                annotated_frame,
                (x1, y_label - label_size[1] - 10),
                (x1 + label_size[0], y_label + baseline - 10),
                color,
                cv2.FILLED
            )
            
            # Draw label text
            cv2.putText(
                annotated_frame,
                label,
                (x1, y_label - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1
            )
        
        return annotated_frame
    
    def get_vehicle_size(self, detection: Dict) -> str:
        """
        Classify vehicle size based on bounding box area
        
        Args:
            detection: Detection dictionary
            
        Returns:
            Size classification (small, medium, large)
        """
        area = detection['area']
        
        if area < 10000:
            return 'small'
        elif area < 30000:
            return 'medium'
        else:
            return 'large'
