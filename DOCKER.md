# 🐳 Docker Setup for Car Tracking System

Complete Docker and Docker Compose configuration for easy deployment.

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended for GPU support)

## 🚀 Quick Start

### 1. Build and Start All Services

```bash
docker-compose up --build
```

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Stop Services

```bash
docker-compose down
```

## 📦 What's Included

### Services

1. **Backend** (Port 8000)
   - Python 3.11 with FastAPI
   - YOLOv8 for vehicle detection
   - OpenCV for video processing
   - Persistent data storage

2. **Frontend** (Port 3000)
   - Next.js 14 with React 18
   - TypeScript
   - Tailwind CSS
   - Optimized production build

### Volumes

- `backend_data`: Persistent SQLite database
- `./backend/uploads`: Video file uploads (mounted)
- `./sample_videos`: Sample videos (mounted)

### Networks

- `car-tracking-network`: Bridge network for service communication

## 🛠️ Docker Commands

### Build Services

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Start Services

```bash
# Start in foreground
docker-compose up

# Start in background (detached)
docker-compose up -d

# Start specific service
docker-compose up backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### View Logs

```bash
# All services
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs backend
docker-compose logs frontend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Execute Commands in Container

```bash
# Backend shell
docker-compose exec backend bash

# Run Python script
docker-compose exec backend python test_video.py

# Frontend shell
docker-compose exec frontend sh
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend
BACKEND_PORT=8000
PYTHONUNBUFFERED=1

# Frontend
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Custom Ports

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # Change 8080 to your desired port
  
  frontend:
    ports:
      - "3001:3000"  # Change 3001 to your desired port
```

## 🎯 Development vs Production

### Development Mode

```bash
# Use docker-compose with live reload
docker-compose up
```

### Production Mode

```bash
# Build optimized images
docker-compose build --no-cache

# Run in background
docker-compose up -d

# View status
docker-compose ps
```

## 📊 Resource Management

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Clean Up

```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove all unused resources
docker system prune -a
```

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Rebuild without cache
docker-compose build --no-cache backend
docker-compose up backend
```

### Frontend Build Fails

```bash
# Check Node.js version
docker-compose exec frontend node --version

# Rebuild
docker-compose build --no-cache frontend
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Change ports in docker-compose.yml
```

### Cannot Connect to Backend from Frontend

- Ensure both services are on the same network
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify CORS settings in backend

### Database Issues

```bash
# Remove volume and restart
docker-compose down -v
docker-compose up --build
```

## 🚀 Deployment

### AWS EC2

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and run
git clone <your-repo>
cd car_tracking
docker-compose up -d
```

### DigitalOcean

```bash
# Use Docker Droplet
# SSH into server
docker-compose up -d
```

### Google Cloud Run

```bash
# Build and push images
docker build -t gcr.io/PROJECT_ID/car-tracking-backend ./backend
docker build -t gcr.io/PROJECT_ID/car-tracking-frontend ./frontend

# Deploy
gcloud run deploy backend --image gcr.io/PROJECT_ID/car-tracking-backend
gcloud run deploy frontend --image gcr.io/PROJECT_ID/car-tracking-frontend
```

## 🔐 Security

### Production Checklist

- [ ] Change default ports
- [ ] Set strong database passwords
- [ ] Use HTTPS (add Nginx reverse proxy)
- [ ] Implement rate limiting
- [ ] Set up firewall rules
- [ ] Use secrets management
- [ ] Enable container security scanning

### Add Nginx Reverse Proxy

Create `nginx/nginx.conf` and update `docker-compose.yml`:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

## 📈 Performance Optimization

### GPU Support (NVIDIA)

Update `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Limit Resources

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 🔍 Health Checks

Add to `docker-compose.yml`:

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  frontend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 📝 Best Practices

1. **Use multi-stage builds** ✅ (Already implemented)
2. **Minimize image size** ✅ (Using alpine and slim images)
3. **Don't run as root** ✅ (Frontend uses non-root user)
4. **Use .dockerignore** ✅ (Implemented)
5. **Keep secrets out of images** ✅ (Use environment variables)
6. **Tag your images** (Add version tags for production)
7. **Health checks** (Add for production)
8. **Resource limits** (Set for production)

## 🎉 Success!

Your car tracking system should now be running in Docker containers! 🚗💨

Visit http://localhost:3000 and start tracking vehicles!
