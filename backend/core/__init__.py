"""
Initialize core modules
"""
from .detector import VehicleDetector
from .speed_estimator import SpeedEstimator
from .color_detector import ColorDetector
from .video_processor import VideoProcessor

__all__ = [
    'VehicleDetector',
    'SpeedEstimator',
    'ColorDetector',
    'VideoProcessor'
]
