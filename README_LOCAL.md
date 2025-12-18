# 🚀 Running Car Tracking System Locally

Step-by-step guide to run the project on your local machine using `uv` for Python dependency management.

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn
- Webcam (optional, for live tracking)

## 🔧 Installation

### Step 1: Install uv (Python Package Manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

**Verify installation:**
```bash
uv --version
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/manishdighore/traffic_tracking.git
cd traffic_tracking
```

## 🐍 Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Install Python Dependencies with uv

```bash
uv pip install -r requirements.txt
```

**Or create a virtual environment first (recommended):**
```bash
# Create virtual environment
uv venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### Step 3: Create Uploads Directory

```bash
mkdir -p uploads
```

### Step 4: Run the Backend Server

```bash
uv run python main.py
```

**Or if you activated the virtual environment:**
```bash
python main.py
```

The backend will start at: **http://localhost:8000**

API documentation available at: **http://localhost:8000/docs**

## 🎨 Frontend Setup

### Step 1: Open New Terminal and Navigate to Frontend

```bash
cd frontend
```

### Step 2: Install Node.js Dependencies

```bash
npm install
```

**Or using yarn:**
```bash
yarn install
```

### Step 3: Run the Frontend Development Server

```bash
npm run dev
```

**Or using yarn:**
```bash
yarn dev
```

The frontend will start at: **http://localhost:3000**

## ✅ Verify Everything is Running

1. **Backend**: http://localhost:8000 should show "Car Tracking API"
2. **API Docs**: http://localhost:8000/docs should show Swagger UI
3. **Frontend**: http://localhost:3000 should show the car tracking dashboard

## 🎥 Using the Application

### Option 1: Use Webcam

1. Open http://localhost:3000
2. Click on "Live Feed" tab
3. Select "Camera" as source
4. Adjust ROI line position if needed (100-800px)
5. Click "Start Tracking"

### Option 2: Upload Video File

1. Open http://localhost:3000
2. Click on "Live Feed" tab
3. Select "Video File" as source
4. Click "Choose File" and select your video
5. Click "Upload" and wait for processing
6. Adjust ROI line position if needed
7. Click "Start Tracking"

### Option 3: Use Sample Video

**Download sample video:**
```bash
# From project root directory
python download_sample_video.py
```

**Or using bash script:**
```bash
chmod +x download_sample_video.sh
./download_sample_video.sh
```

The sample video will be saved in `sample_videos/traffic_sample.mp4`

## 🛠️ Development Commands

### Backend

```bash
cd backend

# Run with uv
uv run python main.py

# Test video processing
uv run python test_video.py

# Install new package
uv pip install package-name

# Update requirements
uv pip freeze > requirements.txt
```

### Frontend

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill process on port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**uv command not found:**
```bash
# Make sure uv is in your PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Missing system dependencies (OpenCV):**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

**macOS:**
```bash
brew install opencv
```

**YOLO model download issues:**
```bash
# Models download automatically on first run
# If issues occur, manually download:
cd backend
mkdir -p models
# Download yolov8n.pt from https://github.com/ultralytics/assets/releases
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Find and kill process on port 3000
# macOS/Linux:
lsof -ti:3000 | xargs kill -9

# Or change port in package.json
# Edit "dev" script: "next dev -p 3001"
```

**Module not found errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Build errors:**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## 📊 Project Structure

```
car_tracking/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── requirements.txt        # Python dependencies
│   ├── core/
│   │   ├── detector.py        # YOLOv8 vehicle detection
│   │   ├── speed_estimator.py # Speed calculation
│   │   ├── color_detector.py  # Color recognition
│   │   └── video_processor.py # Video processing pipeline
│   ├── models/
│   │   ├── database.py        # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   └── uploads/               # Video uploads directory
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js 14 app router
│   │   └── components/       # React components
│   ├── package.json          # Node.js dependencies
│   └── next.config.js        # Next.js configuration
├── sample_videos/            # Sample traffic videos
└── README_LOCAL.md          # This file
```

## 🚀 Quick Start (TL;DR)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repo
git clone https://github.com/manishdighore/traffic_tracking.git
cd traffic_tracking

# Backend
cd backend
uv pip install -r requirements.txt
uv run python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Open http://localhost:3000
```

## 🐳 Alternative: Using Docker

If you prefer Docker, see [DOCKER.md](DOCKER.md) for instructions:

```bash
docker-compose up --build
```

## 📚 Additional Resources

- [Full Documentation](README.md)
- [Docker Setup](DOCKER.md)
- [Quick Start Guide](QUICKSTART.md)
- [Sample Videos Guide](SAMPLE_VIDEOS.md)
- [GitHub Push Instructions](GITHUB_PUSH_INSTRUCTIONS.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Need Help?

- Check [Issues](https://github.com/manishdighore/traffic_tracking/issues)
- Create a new issue with detailed information
- Include error messages and screenshots

---

**Happy Tracking! 🚗💨**
