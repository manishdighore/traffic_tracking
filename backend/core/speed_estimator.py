"""
Speed Estimation Module
Estimates vehicle speed based on movement between frames
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class SpeedEstimator:
    """Estimates vehicle speed from frame-to-frame movement"""
    
    def __init__(
        self,
        pixels_per_meter: float = 8.0,
        fps: int = 30,
        roi_y: int = 400,
        tracking_threshold: int = 50
    ):
        """
        Initialize speed estimator
        
        Args:
            pixels_per_meter: Calibration - pixels per real-world meter
            fps: Frames per second of video
            roi_y: Y-coordinate of ROI line for speed measurement
            tracking_threshold: Maximum pixel distance to match detections across frames
        """
        self.pixels_per_meter = pixels_per_meter
        self.fps = fps
        self.roi_y = roi_y
        self.tracking_threshold = tracking_threshold
        
        # Tracking data
        self.tracked_vehicles: Dict[int, List[Dict]] = defaultdict(list)
        self.vehicle_id_counter = 0
        self.completed_vehicles: Dict[int, Dict] = {}
    
    def match_detection(
        self,
        detection: Dict,
        previous_detections: List[Dict]
    ) -> Optional[int]:
        """
        Match current detection with previous frame detections
        
        Args:
            detection: Current detection
            previous_detections: List of previous frame detections
            
        Returns:
            Vehicle ID if matched, None otherwise
        """
        center = detection['center']
        min_distance = float('inf')
        matched_id = None
        
        for vehicle_id, history in self.tracked_vehicles.items():
            if len(history) == 0:
                continue
            
            last_detection = history[-1]
            last_center = last_detection['center']
            
            # Calculate Euclidean distance
            distance = np.sqrt(
                (center[0] - last_center[0])**2 +
                (center[1] - last_center[1])**2
            )
            
            if distance < min_distance and distance < self.tracking_threshold:
                min_distance = distance
                matched_id = vehicle_id
        
        return matched_id
    
    def update_tracking(
        self,
        detections: List[Dict],
        frame_number: int
    ) -> Dict[int, Dict]:
        """
        Update vehicle tracking with new detections
        
        Args:
            detections: List of current frame detections
            frame_number: Current frame number
            
        Returns:
            Dictionary of vehicle IDs to their current data
        """
        current_vehicles = {}
        matched_ids = set()
        
        # Match detections to existing tracks
        for detection in detections:
            vehicle_id = self.match_detection(detection, [])
            
            if vehicle_id is None:
                # New vehicle
                vehicle_id = self.vehicle_id_counter
                self.vehicle_id_counter += 1
            
            matched_ids.add(vehicle_id)
            
            # Add detection to history
            detection_with_frame = {
                **detection,
                'frame_number': frame_number
            }
            self.tracked_vehicles[vehicle_id].append(detection_with_frame)
            
            current_vehicles[vehicle_id] = detection
        
        # Remove stale tracks (not seen for 30 frames)
        vehicles_to_remove = []
        for vehicle_id, history in self.tracked_vehicles.items():
            if len(history) > 0:
                last_frame = history[-1]['frame_number']
                if frame_number - last_frame > 30:
                    vehicles_to_remove.append(vehicle_id)
        
        for vehicle_id in vehicles_to_remove:
            del self.tracked_vehicles[vehicle_id]
        
        return current_vehicles
    
    def estimate_speed(
        self,
        vehicle_id: int,
        current_detection: Dict
    ) -> Optional[float]:
        """
        Estimate vehicle speed based on movement history
        
        Args:
            vehicle_id: Vehicle tracking ID
            current_detection: Current detection data
            
        Returns:
            Estimated speed in km/h, or None if not enough data
        """
        history = self.tracked_vehicles.get(vehicle_id, [])
        
        if len(history) < 10:
            return None
        
        # Get detections from last 10 frames
        recent_history = history[-10:]
        
        # Calculate total pixel displacement
        first_center = recent_history[0]['center']
        last_center = recent_history[-1]['center']
        
        pixel_distance = np.sqrt(
            (last_center[0] - first_center[0])**2 +
            (last_center[1] - first_center[1])**2
        )
        
        # Convert to meters
        distance_meters = pixel_distance / self.pixels_per_meter
        
        # Calculate time elapsed
        frame_diff = recent_history[-1]['frame_number'] - recent_history[0]['frame_number']
        time_seconds = frame_diff / self.fps
        
        if time_seconds == 0:
            return None
        
        # Calculate speed in km/h
        speed_mps = distance_meters / time_seconds
        speed_kmh = speed_mps * 3.6
        
        return round(speed_kmh, 2)
    
    def get_direction(
        self,
        vehicle_id: int,
        current_detection: Dict
    ) -> Optional[str]:
        """
        Determine vehicle direction of movement
        
        Args:
            vehicle_id: Vehicle tracking ID
            current_detection: Current detection data
            
        Returns:
            Direction ('up', 'down', 'left', 'right') or None
        """
        history = self.tracked_vehicles.get(vehicle_id, [])
        
        if len(history) < 2:
            return None
        
        # Compare current position with first detection
        first_center = history[0]['center']
        current_center = current_detection['center']
        
        dx = current_center[0] - first_center[0]
        dy = current_center[1] - first_center[1]
        
        # Determine primary direction
        if abs(dy) > abs(dx):
            return 'down' if dy > 0 else 'up'
        else:
            return 'right' if dx > 0 else 'left'
    
    def is_in_roi(self, detection: Dict) -> bool:
        """
        Check if vehicle crossed the ROI line
        
        Args:
            detection: Detection data
            
        Returns:
            True if vehicle is past ROI line
        """
        center_y = detection['center'][1]
        return center_y > self.roi_y
    
    def reset(self):
        """Reset all tracking data"""
        self.tracked_vehicles.clear()
        self.vehicle_id_counter = 0
        self.completed_vehicles.clear()
