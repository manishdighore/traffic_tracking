"""
Download sample traffic videos for testing the car tracking system
"""
import os
import urllib.request
from pathlib import Path

def download_sample_video():
    """Download a sample traffic video for testing"""
    
    # Create directory
    sample_dir = Path("sample_videos")
    sample_dir.mkdir(exist_ok=True)
    
    print("📥 Downloading sample traffic video...")
    print("This may take a few minutes depending on your connection...")
    
    # Sample video URLs (these are public domain/free videos)
    videos = [
        {
            "name": "traffic_highway.mp4",
            "url": "https://videos.pexels.com/video-files/2103099/2103099-hd_1920_1080_30fps.mp4",
            "description": "Highway traffic video"
        }
    ]
    
    for video in videos:
        output_path = sample_dir / video["name"]
        
        if output_path.exists():
            print(f"✅ {video['name']} already exists, skipping...")
            continue
            
        try:
            print(f"\n📥 Downloading {video['description']}...")
            urllib.request.urlretrieve(
                video["url"],
                output_path,
                reporthook=download_progress
            )
            print(f"\n✅ Downloaded: {output_path}")
            
        except Exception as e:
            print(f"❌ Error downloading {video['name']}: {e}")
            print(f"   You can manually download from: {video['url']}")
    
    print("\n" + "="*50)
    print("📁 Sample videos location: sample_videos/")
    print("\nTo use the videos:")
    print("1. Start backend: cd backend && python main.py")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Open http://localhost:3000")
    print("4. Click 'Upload Video' and select a video from sample_videos/")
    print("="*50)


def download_progress(block_num, block_size, total_size):
    """Show download progress"""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(downloaded * 100 / total_size, 100)
        print(f"\rProgress: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB)", end="")


if __name__ == "__main__":
    print("🚗 Car Tracking System - Sample Video Downloader")
    print("="*50)
    download_sample_video()
