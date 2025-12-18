# Sample Videos for Testing

## Quick Start

### Option 1: Download Sample Video (Recommended)

Run the Python script to download a free sample traffic video:

```bash
python download_sample_video.py
```

This will download a sample traffic video to `sample_videos/traffic_highway.mp4`.

### Option 2: Use Your Webcam

No download needed! Just click "Start Camera" in the UI.

### Option 3: Use Your Own Video

You can use any video file (MP4, AVI, MOV, etc.) with traffic or vehicles.

## How to Use

1. **Start the Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start the Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**: Go to http://localhost:3000

4. **Choose Your Source**:

   **For Webcam**:
   - Click "Start Camera" button
   - Allow camera access when prompted
   
   **For Video File**:
   - Click "Select Video File" button
   - Choose a video from your computer or `sample_videos/` folder
   - Click "Process Video" to start detection

## Sample Video Sources

If you want to test with different videos, here are some free sources:

1. **Pexels** (Free, No Attribution Required):
   - https://www.pexels.com/search/videos/traffic/
   - https://www.pexels.com/search/videos/highway/
   - https://www.pexels.com/search/videos/cars/

2. **Pixabay** (Free):
   - https://pixabay.com/videos/search/traffic/
   - https://pixabay.com/videos/search/highway/

3. **Videvo** (Free with Attribution):
   - https://www.videvo.net/royalty-free-stock-video-footage/traffic/

## Tips for Best Results

1. **Video Quality**: Use 720p or 1080p videos for best detection
2. **Frame Rate**: 30 FPS works well
3. **Angle**: Top-down or angled views work better than side views
4. **Lighting**: Daylight videos give better results than nighttime
5. **Motion**: Videos with cars moving across the frame work best

## Troubleshooting

**Video upload fails?**
- Check video size (< 100MB recommended)
- Try converting to MP4 format
- Ensure backend is running

**Detection not working?**
- Check if video has clear vehicle views
- Try adjusting ROI line position in backend settings
- Ensure good lighting in video

**Slow performance?**
- Use smaller video resolution
- Close other applications
- Use YOLOv8n (fastest model)

## Video Format Support

Supported formats:
- ✅ MP4 (recommended)
- ✅ AVI
- ✅ MOV
- ✅ MKV
- ✅ WebM

## Example Videos in Repository

After running `download_sample_video.py`, you'll have:

```
sample_videos/
└── traffic_highway.mp4    # Highway traffic video (~20MB)
```

You can add more videos to this folder for quick testing.
