# Deploying CV Tailor with Docker

Guide to deploy the CV Tailor app to various cloud platforms using Docker containers.

---

## Local Docker Deployment

### Development
```bash
docker-compose up
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Azure Container Instances

### Prerequisites
- Azure CLI installed
- Azure account with active subscription

### Deploy to ACI

#### 1. Create Resource Group
```bash
az group create --name cv-tailor-rg --location eastus
```

#### 2. Create Container Registry
```bash
az acr create --resource-group cv-tailor-rg \
  --name cvtailorregistry --sku Basic
```

#### 3. Build and Push Images
```bash
# Login to registry
az acr login --name cvtailorregistry

# Build backend
az acr build --registry cvtailorregistry \
  --image cv-tailor-backend:latest ./server

# Build frontend
az acr build --registry cvtailorregistry \
  --image cv-tailor-frontend:latest ./client
```

#### 4. Deploy Backend Container
```bash
az container create \
  --resource-group cv-tailor-rg \
  --name cv-tailor-backend \
  --image cvtailorregistry.azurecr.io/cv-tailor-backend:latest \
  --registry-login-server cvtailorregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label cv-tailor-backend \
  --ports 8001 \
  --environment-variables PYTHONUNBUFFERED=1 DEBUG=False
```

#### 5. Deploy Frontend Container
```bash
az container create \
  --resource-group cv-tailor-rg \
  --name cv-tailor-frontend \
  --image cvtailorregistry.azurecr.io/cv-tailor-frontend:latest \
  --registry-login-server cvtailorregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label cv-tailor-frontend \
  --ports 5173 \
  --environment-variables VITE_API_BASE_URL=http://cv-tailor-backend.eastus.azurecontainer.io:8001
```

---

## AWS Elastic Container Service (ECS)

### Prerequisites
- AWS CLI installed
- AWS account with permissions

### Deploy to ECS

#### 1. Create Cluster
```bash
aws ecs create-cluster --cluster-name cv-tailor-cluster
```

#### 2. Create Task Definition
Create `ecs-task-definition.json`:
```json
{
  "family": "cv-tailor",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/cv-tailor-backend:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PYTHONUNBUFFERED",
          "value": "1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cv-tailor",
          "awslogs-region": "<region>",
          "awslogs-stream-prefix": "ecs"
        }
      }
    },
    {
      "name": "frontend",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/cv-tailor-frontend:latest",
      "portMappings": [
        {
          "containerPort": 5173,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

#### 2. Register Task Definition
```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

#### 3. Create Service
```bash
aws ecs create-service \
  --cluster cv-tailor-cluster \
  --service-name cv-tailor-service \
  --task-definition cv-tailor \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

---

## Google Cloud Run

### Prerequisites
- Google Cloud SDK installed
- Google Cloud project

### Deploy to Cloud Run

#### 1. Build and Push to Google Container Registry
```bash
# Build backend
gcloud builds submit \
  --tag gcr.io/PROJECT-ID/cv-tailor-backend ./server

# Build frontend
gcloud builds submit \
  --tag gcr.io/PROJECT-ID/cv-tailor-frontend ./client
```

#### 2. Deploy Backend
```bash
gcloud run deploy cv-tailor-backend \
  --image gcr.io/PROJECT-ID/cv-tailor-backend \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --timeout 3600 \
  --allow-unauthenticated
```

#### 3. Deploy Frontend
```bash
gcloud run deploy cv-tailor-frontend \
  --image gcr.io/PROJECT-ID/cv-tailor-frontend \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --allow-unauthenticated
```

---

## DigitalOcean App Platform

### Prerequisites
- DigitalOcean account
- doctl CLI installed

### Deploy via App Spec

Create `app.yaml`:
```yaml
name: cv-tailor-app
services:
  - name: backend
    github:
      repo: your-username/cv-tailor-app
      branch: main
    build_command: cd server && pip install -r requirements.txt
    source_dir: server
    http_port: 8001
    envs:
      - key: PYTHONUNBUFFERED
        value: "1"
    health_check:
      http_path: /health

  - name: frontend
    github:
      repo: your-username/cv-tailor-app
      branch: main
    build_command: cd client && npm install && npm run build
    source_dir: client
    http_port: 5173
    envs:
      - key: VITE_API_BASE_URL
        scope: RUN_TIME
        value: https://${APP_DOMAIN}/api
```

Deploy:
```bash
doctl apps create --spec app.yaml
```

---

## Heroku

### Prerequisites
- Heroku CLI installed
- Heroku account

### Deploy Backend

#### 1. Create Heroku App
```bash
heroku create cv-tailor-backend
```

#### 2. Set Buildpack
```bash
heroku buildpacks:add heroku/python -a cv-tailor-backend
```

#### 3. Deploy
```bash
git push heroku main
```

#### 4. Set Environment Variables
```bash
heroku config:set PYTHONUNBUFFERED=1 -a cv-tailor-backend
```

### Deploy Frontend

#### 1. Create Heroku App
```bash
heroku create cv-tailor-frontend
```

#### 2. Set Buildpack
```bash
heroku buildpacks:add heroku/nodejs -a cv-tailor-frontend
```

#### 3. Deploy
```bash
git push heroku main
```

---

## Kubernetes Deployment

### Prerequisites
- kubectl installed
- Kubernetes cluster access

### Deploy to Kubernetes

Create `k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cv-tailor-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cv-tailor-backend
  template:
    metadata:
      labels:
        app: cv-tailor-backend
    spec:
      containers:
      - name: backend
        image: cv-tailor-backend:latest
        ports:
        - containerPort: 8001
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: cv-tailor-backend-service
spec:
  selector:
    app: cv-tailor-backend
  ports:
  - protocol: TCP
    port: 8001
    targetPort: 8001
  type: LoadBalancer
```

Apply:
```bash
kubectl apply -f k8s-deployment.yaml
```

---

## Environment Variables for Production

Create `.env` file:
```env
# Backend
SECRET_KEY=use-a-strong-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-key
STRIPE_API_KEY=your-key
DATABASE_URL=postgresql://user:pass@host/db

# Frontend
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## Best Practices for Production

1. **Use Multi-Stage Builds** - Reduces final image size
2. **Non-Root Users** - Run containers as non-root user
3. **Health Checks** - Implement health checks for orchestration
4. **Environment Variables** - Never hard-code secrets
5. **Resource Limits** - Set CPU and memory limits
6. **Auto-Scaling** - Enable auto-scaling for traffic spikes
7. **Logging** - Use centralized logging service
8. **Monitoring** - Set up alerts and dashboards
9. **Backups** - Regularly backup data volumes
10. **SSL/TLS** - Always use HTTPS in production

---

## Monitoring and Logging

### Container Logs
```bash
# Docker
docker logs cv-tailor-backend

# Docker Compose
docker-compose logs -f backend

# Kubernetes
kubectl logs -l app=cv-tailor-backend
```

### Health Checks
```bash
curl http://localhost:8001/health
curl http://localhost:8001/docs
```

---

## Rollback Procedure

### Docker Compose
```bash
docker-compose down
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
kubectl rollout history deployment cv-tailor-backend
kubectl rollout undo deployment cv-tailor-backend
```

---

## Troubleshooting

### Container won't start
```bash
docker logs container-name
docker inspect container-name
```

### Network issues
```bash
docker network inspect cv-tailor-network
```

### Performance issues
```bash
docker stats
docker top container-name
```
