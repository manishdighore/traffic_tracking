"""
Test script to verify video file can be opened
"""
import cv2
import os

# Check if uploads directory exists
if not os.path.exists('uploads'):
    print("❌ 'uploads' directory does not exist")
    print("Creating it now...")
    os.makedirs('uploads')
    print("✅ Created 'uploads' directory")

# Check if sample video exists
sample_video = '../sample_videos/traffic_sample.mp4'
if os.path.exists(sample_video):
    print(f"✅ Sample video found: {sample_video}")
    print(f"   Size: {os.path.getsize(sample_video) / 1024 / 1024:.2f} MB")
else:
    print(f"❌ Sample video not found: {sample_video}")

# Test opening the video
print("\nTesting video file...")
test_path = 'uploads/traffic_sample.mp4'

if os.path.exists(test_path):
    cap = cv2.VideoCapture(test_path)
    
    if cap.isOpened():
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"✅ Video opened successfully!")
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps}")
        print(f"   Total frames: {frame_count}")
        print(f"   Duration: {frame_count / fps:.2f} seconds")
        
        cap.release()
    else:
        print(f"❌ Could not open video: {test_path}")
else:
    print(f"❌ Video file not found: {test_path}")
    print("\nTo use the video upload feature:")
    print("1. Upload a video through the UI")
    print("2. Or copy sample video: cp ../sample_videos/traffic_sample.mp4 uploads/")
