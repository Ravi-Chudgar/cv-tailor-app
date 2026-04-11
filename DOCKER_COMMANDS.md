# Docker Commands Reference

## Quick Start Commands

### Start All Services
```bash
# From repository root
docker-compose up
```

### Start Services in Background (Detached Mode)
```bash
docker-compose up -d
```

### Stop All Services
```bash
docker-compose down
```

### Rebuild Images and Start
```bash
docker-compose up --build
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

---

## Building Docker Images

### Build Backend Only
```bash
docker build -t cv-tailor-backend:latest ./server
```

### Build Frontend Only
```bash
docker build -t cv-tailor-frontend:latest ./client
```

### Build with Build Args
```bash
docker build --build-arg NODE_ENV=production -t cv-tailor-frontend:latest ./client
```

---

## Running Containers Individually

### Run Backend
```bash
docker run -d \
  -p 8001:8001 \
  -e PYTHONUNBUFFERED=1 \
  -v ./server/app:/app/app \
  --name cv-tailor-backend \
  cv-tailor-backend:latest
```

### Run Frontend
```bash
docker run -d \
  -p 5173:5173 \
  -e VITE_API_BASE_URL=http://localhost:8001 \
  --name cv-tailor-frontend \
  cv-tailor-frontend:latest
```

---

## Container Management

### List Running Containers
```bash
docker ps
```

### List All Containers
```bash
docker ps -a
```

### Stop Container
```bash
docker stop cv-tailor-backend
docker stop cv-tailor-frontend
```

### Start Container
```bash
docker start cv-tailor-backend
docker start cv-tailor-frontend
```

### Remove Container
```bash
docker rm cv-tailor-backend
docker rm cv-tailor-frontend
```

### Remove Image
```bash
docker rmi cv-tailor-backend:latest
docker rmi cv-tailor-frontend:latest
```

---

## Development Commands

### Execute Command in Running Container
```bash
docker exec -it cv-tailor-backend bash
docker exec -it cv-tailor-frontend sh
```

### Install New Python Package
```bash
docker exec cv-tailor-backend pip install new-package
```

### Install New NPM Package
```bash
docker exec cv-tailor-frontend npm install new-package
```

### View Container Resource Usage
```bash
docker stats
```

---

## Debugging

### View Container Details
```bash
docker inspect cv-tailor-backend
docker inspect cv-tailor-frontend
```

### Check Container Network
```bash
docker network ls
docker network inspect cv-tailor-network
```

### Check Logs with Timestamps
```bash
docker-compose logs --timestamps
```

### Follow Specific Container
```bash
docker-compose logs -f backend --tail=50
```

---

## Clean Up

### Remove Stopped Containers
```bash
docker container prune
```

### Remove Unused Images
```bash
docker image prune
```

### Remove Unused Volumes
```bash
docker volume prune
```

### Complete Reset (Warning: Deletes Everything)
```bash
docker-compose down -v
docker system prune -a
```

---

## Docker Compose Specific

### Scale Services
```bash
docker-compose up -d --scale backend=2
```

### Restart Service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Pause Services
```bash
docker-compose pause
```

### Unpause Services
```bash
docker-compose unpause
```

### Check Service Status
```bash
docker-compose ps
```

---

## Environment Variables in Docker

### Pass Env Vars via Command Line
```bash
docker run -e VARIABLE=value -d cv-tailor-backend:latest
```

### Pass Env Vars via File
```bash
docker run --env-file .env -d cv-tailor-backend:latest
```

### Set Env Vars in docker-compose.yml
```yaml
environment:
  - VARIABLE_NAME=value
  - ANOTHER_VAR=${HOST_ENV_VAR}
```

---

## Production Commands

### Tag Image for Registry
```bash
docker tag cv-tailor-backend:latest myregistry.azurecr.io/cv-tailor-backend:latest
```

### Push to Registry
```bash
docker push myregistry.azurecr.io/cv-tailor-backend:latest
```

### Pull from Registry
```bash
docker pull myregistry.azurecr.io/cv-tailor-backend:latest
```

### Run Production Container
```bash
docker run -d \
  -p 8001:8001 \
  --restart=always \
  -e DEBUG=False \
  --name cv-tailor-backend-prod \
  cv-tailor-backend:latest
```

---

## Troubleshooting Commands

### Check If Port is Available
```bash
# Windows
netstat -ano | findstr :8001

# Linux/Mac
lsof -i :8001
```

### Free Up Port
```bash
# Windows
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>
```

### Check Container Health
```bash
docker-compose ps
```

### View Raw Container Config
```bash
docker inspect cv-tailor-backend | grep -A 20 "HealthCheck"
```

### Force Rebuild
```bash
docker-compose build --no-cache
```
