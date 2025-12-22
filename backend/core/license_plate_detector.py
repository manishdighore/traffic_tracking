"""
License Plate Detection Module using YOLOv4-tiny
Detects license plates in vehicle bounding boxes
Based on: https://github.com/BarthPaleologue/ALPR
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import os


class LicensePlateDetector:
    """License plate detector using YOLOv4-tiny model trained on European plates"""
    
    def __init__(
        self,
        weights_path: str = "yolo_weights/yolov4-tiny-license-plate.weights",
        config_path: str = "yolo_weights/yolov4-tiny-license-plate.cfg",
        dims: Tuple[int, int] = (256, 160),
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.4
    ):
        """
        Initialize license plate detector
        
        Args:
            weights_path: Path to YOLOv4 weights file
            config_path: Path to YOLOv4 config file
            dims: Input dimensions for the network (width, height)
            confidence_threshold: Minimum confidence for detection
            nms_threshold: Non-maximum suppression threshold
        """
        self.dims = dims
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        
        # Check if weights and config exist
        if not os.path.exists(weights_path):
            print(f"⚠️  Warning: YOLOv4 weights not found at {weights_path}")
            print("   License plate detection will be disabled.")
            print("   Run download_yolo_weights.py to download the weights.")
            self.net = None
            return
        
        if not os.path.exists(config_path):
            print(f"⚠️  Warning: YOLOv4 config not found at {config_path}")
            print("   License plate detection will be disabled.")
            self.net = None
            return
        
        print(f"Initializing License Plate Detector...")
        print(f"Using weights: {weights_path}")
        print(f"Using config: {config_path}")
        print(f"Using dims: {self.dims}")
        
        # Load YOLOv4 network
        self.net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        
        # Get output layer names
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        print("License Plate Detector initialized successfully!")
    
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
            List of detected plates with bounding boxes
        """
        if self.net is None:
            return []
        
        # If vehicle bbox is provided, crop to that region
        if vehicle_bbox is not None:
            x1, y1, x2, y2 = vehicle_bbox
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
        
        if roi.size == 0:
            return []
        
        # Prepare blob
        blob = cv2.dnn.blobFromImage(
            roi,
            1/255.0,
            self.dims,
            swapRB=True,
            crop=False
        )
        
        # Set input
        self.net.setInput(blob)
        
        # Forward pass
        outputs = self.net.forward(self.output_layers)
        
        # Process detections
        boxes = []
        confidences = []
        h, w = roi.shape[:2]
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                confidence = scores[0]  # Only one class: license plate
                
                if confidence < self.confidence_threshold:
                    continue
                
                # Get bounding box
                box = detection[:4] * np.array([w, h, w, h])
                center_x, center_y, width, height = box.astype("int")
                
                x = int(center_x - (width / 2))
                y = int(center_y - (height / 2))
                
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
        
        # Apply non-maximum suppression
        if len(boxes) == 0:
            return []
        
        indices = cv2.dnn.NMSBoxes(
            boxes,
            confidences,
            self.confidence_threshold,
            self.nms_threshold
        )
        
        detections = []
        
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w_box, h_box = boxes[i]
                
                # Convert back to original frame coordinates
                x1 = offset_x + x
                y1 = offset_y + y
                x2 = offset_x + x + w_box
                y2 = offset_y + y + h_box
                
                detection = {
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': [int(x1 + w_box/2), int(y1 + h_box/2)],
                    'width': int(w_box),
                    'height': int(h_box),
                    'confidence': round(confidences[i], 2)
                }
                
                detections.append(detection)
        
        return detections
    
    def extract_plate_image(
        self,
        frame: np.ndarray,
        plate_bbox: List[int]
    ) -> Optional[np.ndarray]:
        """
        Extract and return the license plate region from frame
        
        Args:
            frame: Input frame
            plate_bbox: Plate bounding box [x1, y1, x2, y2]
            
        Returns:
            Cropped plate image or None
        """
        x1, y1, x2, y2 = plate_bbox
        
        # Validate coordinates
        if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
            return None
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        # Crop plate region
        plate_img = frame[y1:y2, x1:x2]
        
        return plate_img if plate_img.size > 0 else None
    
    def draw_plates(
        self,
        frame: np.ndarray,
        detections: List[Dict],
        color: Tuple[int, int, int] = (0, 255, 255),  # Yellow
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw detected license plates on frame
        
        Args:
            frame: Input frame
            detections: List of plate detections
            color: BGR color for drawing
            thickness: Line thickness
            
        Returns:
            Frame with drawn plates
        """
        output = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            conf = detection['confidence']
            
            # Draw rectangle
            cv2.rectangle(output, (x1, y1), (x2, y2), color, thickness)
            
            # Draw confidence
            label = f"Plate: {conf:.2f}"
            label_size, baseline = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                1
            )
            
            # Draw label background
            cv2.rectangle(
                output,
                (x1, y1 - label_size[1] - baseline),
                (x1 + label_size[0], y1),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                output,
                label,
                (x1, y1 - baseline),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1
            )
        
        return output
