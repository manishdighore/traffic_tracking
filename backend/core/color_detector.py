"""
Vehicle Color Detection Module
Detects vehicle color using K-Nearest Neighbors and color histograms
"""
import cv2
import numpy as np
from typing import Dict, List


class ColorDetector:
    """Detects vehicle color using KNN classifier"""
    
    # Predefined color ranges in HSV
    COLOR_RANGES = {
        'red': [(0, 100, 100), (10, 255, 255), (160, 100, 100), (180, 255, 255)],
        'blue': [(100, 100, 100), (130, 255, 255)],
        'green': [(40, 50, 50), (80, 255, 255)],
        'yellow': [(20, 100, 100), (30, 255, 255)],
        'white': [(0, 0, 200), (180, 30, 255)],
        'black': [(0, 0, 0), (180, 255, 50)],
        'gray': [(0, 0, 50), (180, 50, 200)],
        'orange': [(10, 100, 100), (20, 255, 255)]
    }
    
    def __init__(self):
        """Initialize color detector"""
        self.colors = list(self.COLOR_RANGES.keys())
    
    def detect_color(
        self,
        frame: np.ndarray,
        detection: Dict
    ) -> str:
        """
        Detect vehicle color from detection region
        
        Args:
            frame: Full frame image
            detection: Detection dictionary with bbox
            
        Returns:
            Detected color name
        """
        x1, y1, x2, y2 = detection['bbox']
        
        # Crop vehicle region
        vehicle_region = frame[y1:y2, x1:x2]
        
        if vehicle_region.size == 0:
            return 'unknown'
        
        # Convert to HSV
        hsv = cv2.cvtColor(vehicle_region, cv2.COLOR_BGR2HSV)
        
        # Get center region for better color detection
        h, w = hsv.shape[:2]
        center_h, center_w = h // 2, w // 2
        margin_h, margin_w = h // 4, w // 4
        
        center_region = hsv[
            max(0, center_h - margin_h):min(h, center_h + margin_h),
            max(0, center_w - margin_w):min(w, center_w + margin_w)
        ]
        
        if center_region.size == 0:
            return 'unknown'
        
        # Count pixels for each color
        color_scores = {}
        
        for color_name, ranges in self.COLOR_RANGES.items():
            mask = np.zeros(center_region.shape[:2], dtype=np.uint8)
            
            # Handle colors with multiple ranges (like red)
            if len(ranges) == 4:
                lower1, upper1 = np.array(ranges[0]), np.array(ranges[1])
                lower2, upper2 = np.array(ranges[2]), np.array(ranges[3])
                mask1 = cv2.inRange(center_region, lower1, upper1)
                mask2 = cv2.inRange(center_region, lower2, upper2)
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                lower = np.array(ranges[0])
                upper = np.array(ranges[1])
                mask = cv2.inRange(center_region, lower, upper)
            
            # Count matching pixels
            pixel_count = np.sum(mask > 0)
            color_scores[color_name] = pixel_count
        
        # Get color with maximum score
        if not color_scores or max(color_scores.values()) == 0:
            return 'unknown'
        
        detected_color = max(color_scores, key=color_scores.get)
        return detected_color
    
    def get_dominant_color(
        self,
        frame: np.ndarray,
        detection: Dict,
        k: int = 3
    ) -> str:
        """
        Get dominant color using K-means clustering
        
        Args:
            frame: Full frame image
            detection: Detection dictionary with bbox
            k: Number of clusters
            
        Returns:
            Dominant color name
        """
        x1, y1, x2, y2 = detection['bbox']
        vehicle_region = frame[y1:y2, x1:x2]
        
        if vehicle_region.size == 0:
            return 'unknown'
        
        # Resize for faster processing
        vehicle_region = cv2.resize(vehicle_region, (100, 100))
        
        # Reshape to 2D array of pixels
        pixels = vehicle_region.reshape(-1, 3).astype(np.float32)
        
        # Apply K-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(
            pixels, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS
        )
        
        # Get the dominant cluster (most pixels)
        unique, counts = np.unique(labels, return_counts=True)
        dominant_cluster_idx = unique[np.argmax(counts)]
        dominant_color_bgr = centers[dominant_cluster_idx].astype(int)
        
        # Convert to color name
        color_name = self._bgr_to_color_name(dominant_color_bgr)
        
        return color_name
    
    def _bgr_to_color_name(self, bgr: np.ndarray) -> str:
        """
        Convert BGR values to color name
        
        Args:
            bgr: BGR color array
            
        Returns:
            Color name
        """
        b, g, r = int(bgr[0]), int(bgr[1]), int(bgr[2])
        
        # Convert to HSV for better color classification
        hsv_pixel = cv2.cvtColor(
            np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV
        )[0][0]
        
        h, s, v = hsv_pixel
        
        # Classify based on HSV values
        if v < 50:
            return 'black'
        elif s < 30:
            if v > 200:
                return 'white'
            else:
                return 'gray'
        elif h < 10 or h > 160:
            return 'red'
        elif 10 <= h < 20:
            return 'orange'
        elif 20 <= h < 35:
            return 'yellow'
        elif 35 <= h < 85:
            return 'green'
        elif 85 <= h < 135:
            return 'blue'
        else:
            return 'unknown'
    
    def draw_color_label(
        self,
        frame: np.ndarray,
        detection: Dict,
        color: str
    ) -> np.ndarray:
        """
        Draw color label on frame
        
        Args:
            frame: Frame to draw on
            detection: Detection data
            color: Color name
            
        Returns:
            Frame with color label
        """
        x1, y1, x2, y2 = detection['bbox']
        
        # Draw color label
        label = f"Color: {color}"
        label_y = max(y1 - 30, 20)
        
        cv2.putText(
            frame,
            label,
            (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        
        return frame
