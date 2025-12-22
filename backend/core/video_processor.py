"""
Video Processing Pipeline
Integrates detection, tracking, color recognition, and speed estimation
"""
import cv2
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

from core.detector import VehicleDetector
from core.speed_estimator import SpeedEstimator
from core.color_detector import ColorDetector
from core.license_plate_detector import LicensePlateDetector
from core.plate_ocr import PlateOCR
from models.database import SessionLocal, Vehicle


class VideoProcessor:
    """Main video processing pipeline"""
    
    def __init__(
        self,
        detector: VehicleDetector,
        speed_estimator: SpeedEstimator,
        color_detector: ColorDetector,
        plate_detector: Optional[LicensePlateDetector] = None,
        plate_ocr: Optional[PlateOCR] = None,
        save_to_db: bool = True
    ):
        """
        Initialize video processor
        
        Args:
            detector: Vehicle detector instance
            speed_estimator: Speed estimator instance
            color_detector: Color detector instance
            plate_detector: License plate detector instance (optional)
            plate_ocr: License plate OCR instance (optional)
            save_to_db: Whether to save detections to database
        """
        self.detector = detector
        self.speed_estimator = speed_estimator
        self.color_detector = color_detector
        self.plate_detector = plate_detector
        self.plate_ocr = plate_ocr
        self.save_to_db = save_to_db
        
        self.total_vehicle_count = 0
        self.frame_detections = []
        self.counted_vehicles = set()  # Track which vehicles have been counted
        
    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int
    ) -> Dict:
        """
        Process a single frame
        
        Args:
            frame: Input frame
            frame_number: Frame number in sequence
            
        Returns:
            Dictionary containing processed frame and detection data
        """
        # Detect vehicles
        detections = self.detector.detect(frame)
        
        # Update tracking
        tracked_vehicles = self.speed_estimator.update_tracking(
            detections,
            frame_number
        )
        
        # Process each detection
        enriched_detections = []
        
        for detection in detections:
            # Find vehicle ID
            vehicle_id = None
            for vid, vdata in tracked_vehicles.items():
                if vdata == detection:
                    vehicle_id = vid
                    break
            
            if vehicle_id is None:
                continue
            
            # Detect color
            color = self.color_detector.detect_color(frame, detection)
            
            # Estimate speed
            speed = self.speed_estimator.estimate_speed(vehicle_id, detection)
            
            # Get direction
            direction = self.speed_estimator.get_direction(vehicle_id, detection)
            
            # Check if in ROI
            in_roi = self.speed_estimator.is_in_roi(detection)
            
            # Get vehicle size
            size = self.detector.get_vehicle_size(detection)
            
            # Detect license plate
            license_plate = None
            plate_confidence = None
            if self.plate_detector is not None and self.plate_ocr is not None:
                plate_detections = self.plate_detector.detect(frame, detection['bbox'])
                if plate_detections:
                    # Get the first (most confident) plate
                    plate = plate_detections[0]
                    plate_img = self.plate_detector.extract_plate_image(frame, plate['bbox'])
                    if plate_img is not None:
                        # Try Indian format first, then UK, then auto
                        license_plate, plate_confidence = self.plate_ocr.read_with_confidence(plate_img, format_type='auto')
            
            # Enrich detection data
            enriched_detection = {
                **detection,
                'vehicle_id': vehicle_id,
                'color': color,
                'speed': speed,
                'direction': direction,
                'in_roi': in_roi,
                'size': size,
                'license_plate': license_plate,
                'plate_confidence': plate_confidence,
                'timestamp': datetime.now().isoformat()
            }
            
            enriched_detections.append(enriched_detection)
            
            # Save to database if vehicle crossed ROI for the first time
            if (self.save_to_db and in_roi and speed is not None and
                not self._is_vehicle_saved(vehicle_id)):
                self._save_to_database(enriched_detection)
                self.counted_vehicles.add(vehicle_id)  # Mark as counted
                self.total_vehicle_count += 1
        
        # Draw detections on frame
        annotated_frame = self._draw_annotations(
            frame.copy(),
            enriched_detections
        )
        
        return {
            'frame': annotated_frame,
            'detections': enriched_detections,
            'total_count': self.total_vehicle_count,
            'frame_number': frame_number
        }
    
    def _draw_annotations(
        self,
        frame: np.ndarray,
        detections: List[Dict]
    ) -> np.ndarray:
        """
        Draw all annotations on frame
        
        Args:
            frame: Input frame
            detections: List of enriched detections
            
        Returns:
            Annotated frame
        """
        # Draw ROI line
        roi_y = self.speed_estimator.roi_y
        cv2.line(frame, (0, roi_y), (frame.shape[1], roi_y), (0, 255, 255), 3)
        cv2.putText(
            frame,
            'ROI Line',
            (10, roi_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )
        
        # Draw detections
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            
            # Choose color based on vehicle type
            color_map = {
                'car': (0, 255, 0),
                'truck': (255, 0, 0),
                'bus': (0, 0, 255),
                'motorcycle': (255, 255, 0),
                'bicycle': (255, 0, 255)
            }
            bbox_color = color_map.get(detection['class_name'], (0, 255, 0))
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), bbox_color, 2)
            
            # Prepare info text
            info_lines = [
                f"ID: {detection['vehicle_id']}",
                f"{detection['class_name']} ({detection['confidence']})",
                f"Color: {detection['color']}",
            ]
            
            if detection.get('license_plate'):
                info_lines.append(f"Plate: {detection['license_plate']}")
            
            if detection['speed'] is not None:
                info_lines.append(f"Speed: {detection['speed']} km/h")
            
            if detection['direction']:
                info_lines.append(f"Dir: {detection['direction']}")
            
            # Draw info text
            y_offset = y1 - 10
            for line in reversed(info_lines):
                cv2.putText(
                    frame,
                    line,
                    (x1, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )
                y_offset -= 20
        
        # Draw counter
        cv2.rectangle(frame, (10, 10), (300, 100), (0, 0, 0), -1)
        cv2.putText(
            frame,
            f"Total Vehicles: {self.total_vehicle_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        cv2.putText(
            frame,
            f"Current Frame: {len(detections)} vehicles",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        
        return frame
    
    def _save_to_database(self, detection: Dict):
        """
        Save vehicle detection to database
        
        Args:
            detection: Enriched detection dictionary
        """
        db = SessionLocal()
        try:
            vehicle = Vehicle(
                vehicle_type=detection['class_name'],
                color=detection['color'],
                speed=detection['speed'],
                direction=detection['direction'],
                size=detection['size'],
                confidence=detection['confidence'],
                bbox_x1=detection['bbox'][0],
                bbox_y1=detection['bbox'][1],
                bbox_x2=detection['bbox'][2],
                bbox_y2=detection['bbox'][3],
                license_plate=detection.get('license_plate'),
                plate_confidence=detection.get('plate_confidence')
            )
            db.add(vehicle)
            db.commit()
        except Exception as e:
            print(f"Error saving to database: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _is_vehicle_saved(self, vehicle_id: int) -> bool:
        """
        Check if vehicle was already saved to database
        
        Args:
            vehicle_id: Vehicle tracking ID
            
        Returns:
            True if already saved
        """
        return vehicle_id in self.counted_vehicles
    
    def reset(self):
        """Reset processor state"""
        self.total_vehicle_count = 0
        self.frame_detections = []
        self.counted_vehicles.clear()
        self.speed_estimator.reset()
    
    def set_roi_position(self, y_position: int):
        """
        Set ROI line Y position
        
        Args:
            y_position: Y coordinate for ROI line
        """
        self.speed_estimator.roi_y = y_position
