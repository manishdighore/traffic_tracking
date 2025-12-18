#!/bin/bash
# Download sample traffic video for testing

echo "📥 Downloading sample traffic video..."

# Create sample_videos directory
mkdir -p sample_videos

# Download a sample traffic video (using a public domain video)
# You can replace this URL with any traffic video URL

echo "Downloading sample traffic video from Pexels..."
curl -L "https://videos.pexels.com/video-files/2103099/2103099-uhd_2560_1440_30fps.mp4" \
  -o sample_videos/traffic_sample.mp4 \
  --progress-bar

if [ $? -eq 0 ]; then
    echo "✅ Sample video downloaded successfully!"
    echo "📁 Location: sample_videos/traffic_sample.mp4"
    echo ""
    echo "To use:"
    echo "1. Start the backend: cd backend && python main.py"
    echo "2. Start the frontend: cd frontend && npm run dev"
    echo "3. Open http://localhost:3000"
    echo "4. Upload the video: sample_videos/traffic_sample.mp4"
else
    echo "❌ Download failed. Please check your internet connection."
    echo ""
    echo "Alternative: You can use any traffic video you have or:"
    echo "- Search 'traffic video' on Pexels.com"
    echo "- Download from YouTube (with proper rights)"
    echo "- Use your webcam (source: 0)"
fi
