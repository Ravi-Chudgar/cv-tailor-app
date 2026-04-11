# Docker Setup Guide for CV Tailor App

## Prerequisites

- **Docker** - [Install Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Docker Compose** - Included with Docker Desktop

Verify installation:
```bash
docker --version
docker-compose --version
```

---

## Quick Start with Docker

### Option 1: Using Docker Compose (Recommended)

The easiest way to run the entire application with one command:

```bash
cd k:\cv-tailor-app-new
docker-compose up
```

This will:
- ✅ Build both backend and frontend images
- ✅ Start the backend service on http://localhost:8001
- ✅ Start the frontend service on http://localhost:5173
- ✅ Set up networking between services
- ✅ Enable hot reload for development

**To stop the services:**
```bash
docker-compose down
```

**To rebuild images (after dependency changes):**
```bash
docker-compose up --build
```

**To view logs:**
```bash
docker-compose logs -f
# or specific service:
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

### Option 2: Building Manually

If you prefer to build and run images separately:

#### Build Backend Image
```bash
cd k:\cv-tailor-app-new\server
docker build -t cv-tailor-backend:latest .
```

#### Build Frontend Image
```bash
cd k:\cv-tailor-app-new\client
docker build -t cv-tailor-frontend:latest .
```

#### Run Backend
```bash
docker run -d -p 8001:8001 \
  -v k:\cv-tailor-app-new\server\app:/app/app \
  -v k:\cv-tailor-app-new\server\uploads:/app/uploads \
  --name cv-tailor-backend \
  cv-tailor-backend:latest
```

#### Run Frontend
```bash
docker run -d -p 5173:5173 \
  -e VITE_API_BASE_URL=http://localhost:8001 \
  --name cv-tailor-frontend \
  cv-tailor-frontend:latest
```

---

## Accessing the Application

Once the services are running:

- **Frontend:** http://localhost:5173/
- **Backend API:** http://localhost:8001/
- **API Documentation:** http://localhost:8001/docs

---

## Development with Docker

### Hot Reload

When using `docker-compose up`, both services have hot reload enabled:

- **Backend:** Changes to `server/app/` will automatically reload
- **Frontend:** Changes to `client/src/` will automatically rebuild

### Making Changes

Simply edit files locally, and the changes will be reflected in the running containers immediately. No need to restart!

---

## Useful Docker Commands

### View Running Containers
```bash
docker ps
```

### View All Containers (including stopped)
```bash
docker ps -a
```

### Remove Containers
```bash
docker rm cv-tailor-backend cv-tailor-frontend
```

### Remove Images
```bash
docker rmi cv-tailor-backend:latest cv-tailor-frontend:latest
```

### Clean Up Everything (Careful!)
```bash
docker-compose down -v  # Removes volumes too
```

### Inspect Container Logs
```bash
docker logs cv-tailor-backend
docker logs cv-tailor-frontend
```

### Execute Commands Inside Container
```bash
docker exec -it cv-tailor-backend bash
docker exec -it cv-tailor-frontend sh
```

---

## Troubleshooting

### Port Already in Use
If ports 5173 or 8001 are already in use:

**Option 1:** Stop the conflicting service
```bash
# Find what's using the port (Windows)
netstat -ano | findstr :8001
# Kill the process
taskkill /PID <PID> /F
```

**Option 2:** Map to different ports in docker-compose.yml
```yaml
ports:
  - "8002:8001"  # Backend on 8002
  - "5174:5173"  # Frontend on 5174
```

### Permission Denied
On Linux/Mac, you might need to add your user to the docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Container Crashes
Check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Rebuild After Major Changes
```bash
docker-compose down
docker-compose up --build
```

---

## Production Deployment

For production, you can use the Dockerfiles to deploy on services like:
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean
- Heroku
- Any Kubernetes cluster

Just push the built images to your container registry!

---

## Environment Variables

Create a `.env` file in the root directory to override settings:

```env
# Backend settings
BACKEND_PORT=8001
DATABASE_URL=sqlite:///./cv_tailor.db

# Frontend settings
VITE_API_BASE_URL=http://localhost:8001
```

These will be picked up by docker-compose.

---

## Notes

- Both Dockerfiles use alpine-based images for smaller file sizes
- The frontend uses a multi-stage build to optimize image size
- Volumes are mapped for development hot reload
- Health checks are configured for both services
- Services are networked together using a custom bridge network
