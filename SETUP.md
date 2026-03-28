# CV Tailor Application - Setup Guide

## Project Structure

```
cv-tailor-app-new/
├── server/                 # FastAPI Python Backend
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py        # Main FastAPI application with all routes
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
│
├── client/                 # React + Vite Frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js   # API client with axios
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── AdminPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── components/
│   │   ├── stores/         # Zustand state management
│   │   └── App.jsx
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── .env.example        # Environment template
│   └── public/
│
├── README.md               # Project overview
├── SETUP.md                # This file
├── QUICKSTART.md           # Quick start guide
└── .gitignore              # Git ignore rules
```

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** (with npm)
- **Git**

## Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd cv-tailor-app-new
```

### 2. Backend Setup

```bash
cd server

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd client

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

## Running the Application

### Start Backend (Terminal 1)
```bash
cd server
python -m uvicorn app.main:app --reload --port 8001
```

Backend will be available at: **http://localhost:8001**
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

### Start Frontend (Terminal 2)
```bash
cd client
npm run dev
```

Frontend will be available at: **http://localhost:5176** (or next available port)

## Testing Credentials

### Admin Account
- **Username:** admin
- **Password:** admin123
- **Access:** Admin dashboard at `/admin`

### Regular User Account
- **Username:** user
- **Password:** password123
- **Access:** Dashboard at `/dashboard`

## Available API Endpoints

### Authentication
- `POST /api/auth/login` - Login user
- `POST /api/auth/register` - Register new user
- `GET /api/auth/current-user` - Get current user info

### CV Operations
- `POST /api/cv/upload` - Upload CV file
- `GET /api/cv/list` - List uploaded CVs
- `POST /api/cv/parse` - Parse CV content
- `DELETE /api/cv/{file_id}` - Delete CV

### Job Operations
- `POST /api/job/analyze` - Analyze job description
- `GET /api/jobs/suggestions` - Get job suggestions

### Tailor Operations
- `POST /api/tailor/tailor` - Tailor CV for job
- `POST /api/tailor/batch-tailor` - Batch tailor
- `GET /api/tailor/preview` - Preview tailored CV
- `GET /api/tailor/compare` - Compare CVs

### PDF Operations
- `GET /api/pdf/templates` - Get PDF templates
- `POST /api/pdf/generate` - Generate PDF
- `GET /api/pdf/download/{file_name}` - Download PDF
- `POST /api/pdf/preview` - Preview PDF

### Admin Operations
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/{user_id}` - Get specific user
- `DELETE /api/admin/users/{user_id}` - Delete user
- `PUT /api/admin/users/{user_id}/status` - Toggle user status
- `GET /api/admin/stats` - Get system statistics
- `GET /api/admin/activity-log` - Get activity log

## Architecture

### Backend (FastAPI)
- Fast, modern Python web framework
- Automatic API documentation (OpenAPI/Swagger)
- Built-in request validation with Pydantic
- CORS enabled for frontend communication
- In-memory user and CV storage (demo mode)

### Frontend (React + Vite)
- Fast build tool with hot module replacement
- React 18 for UI components
- Zustand for state management
- Axios for API calls
- Tailwind CSS for styling

## Features

✅ **User Authentication**
- Registration and login
- Admin role support
- Token-based authentication

✅ **CV Management**
- Upload CV files (PDF/DOCX)
- List uploaded CVs
- Parse CV content
- Delete CVs

✅ **Job Tailoring**
- Analyze job descriptions
- Tailor CV for specific jobs
- Calculate match scores
- Preview changes

✅ **PDF Generation**
- Generate PDF resumes
- Multiple templates
- Download options

✅ **Admin Dashboard**
- View all users
- Manage user status
- View system statistics
- Activity logging

## Environment Variables

### Server (.env)
```
ENVIRONMENT=development
DATABASE_URL=sqlite:///cv_tailor.db
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:5176,http://localhost:3000
```

### Client (.env)
```
VITE_API_URL=http://localhost:8001/api
VITE_ENV=development
```

## Troubleshooting

### CORS Errors
- Ensure backend is running on port 8001
- Check `CORS_ORIGINS` in backend configuration
- Clear browser cache and restart

### File Upload Not Working
- Verify backend supports file uploads
- Check file size (max 10MB)
- Verify file type (PDF or DOCX)

### Port Conflicts
- Backend can use different ports: change `--port` flag
- Frontend auto-increments if port 5173 is taken
- Check terminal output for actual running port

### Module Not Found Errors
- Backend: Run `pip install -r requirements.txt`
- Frontend: Run `npm install`

## Building for Production

### Backend
```bash
# No build needed, just ensure dependencies are installed
pip install -r requirements.txt
```

### Frontend
```bash
cd client
npm run build
# Output in dist/ folder
```

## Deploying to GitHub

### Initialize Git (if not already done)
```bash
cd cv-tailor-app-new
git init
git add .
git commit -m "Initial commit: CV Tailor application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cv-tailor-app-new.git
git push -u origin main
```

### Push Updates
```bash
git add .
git commit -m "Your commit message here"
git push origin main
```

## Support & Contributing

For issues or feature requests, please create an issue in the GitHub repository.

## License

MIT License - feel free to use this project for learning and personal use.
