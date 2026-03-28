# CV Tailor - Intelligent CV Tailoring Application

A full-stack application that helps users tailor their CVs for specific job descriptions. Built with **FastAPI** (Python) backend and **React** (JavaScript) frontend in a unified monorepo structure.

## ✨ Features

- 👤 **User Authentication** - Register, login, and role-based access control
- 📄 **CV Management** - Upload, parse, and manage CV files (PDF/DOCX)
- 🎯 **Job Analysis** - Extract key requirements from job descriptions
- ✂️ **CV Tailoring** - Automatically tailor CVs for specific jobs
- 📊 **Match Scoring** - Calculate compatibility scores
- 📑 **PDF Generation** - Generate tailored resumes in multiple templates
- 🛡️ **Admin Dashboard** - User management and system statistics
- 🔐 **Secure Authentication** - Token-based with refresh tokens

## 📁 Project Structure

```
cv-tailor-app-new/
├── server/                     # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py            # Main FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
│
├── client/                     # React + Vite Frontend
│   ├── src/
│   │   ├── api/               # HTTP client and API calls
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── stores/            # Zustand state management
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/                # Static assets
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   └── .env.example           # Environment template
│
├── README.md                   # This file
├── SETUP.md                    # Detailed setup guide
├── QUICKSTART.md               # Quick start instructions
└── .gitignore                  # Git ignore rules
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (with pip)
- **Node.js 18+** (with npm)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/cv-tailor-app-new.git
cd cv-tailor-app-new
```

### 2. Install Backend Dependencies
```bash
cd server
pip install -r requirements.txt
cd ..
```

### 3. Install Frontend Dependencies
```bash
cd client
npm install
cd ..
```

### 4. Start Backend Server
```bash
cd server
python -m uvicorn app.main:app --reload --port 8001
```

Backend runs at: **http://localhost:8001**

### 5. Start Frontend Server (new terminal)
```bash
cd client
npm run dev
```

Frontend runs at: **http://localhost:5176** (or next available port)

### 2. Run Backend

```bash
cd server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Backend available at: `http://localhost:8001`
API Docs: `http://localhost:8001/docs`

### 3. Run Frontend

In a new terminal:

```bash
cd client
npm run dev
```

Frontend available at: `http://localhost:5175`

---

## 🔐 Demo Credentials

| Username | Password |
|----------|----------|
| admin    | admin123 |
| user     | password123 |

---

## 📚 Features

### Backend (FastAPI)
- User authentication (Login/Register)
- CV tailoring engine
- Job description analysis
- Match scoring algorithm
- Template management
- Analytics dashboard
- REST API with auto-generated docs
- CORS support

### Frontend (React + Vite)
- Beautiful login/register UI
- Dashboard with real-time analytics
- Responsive design
- API integration
- Session management
- Tailwind CSS styling

---

## 🔗 API Endpoints

```
GET    /                              Root endpoint
GET    /health                        Health check
POST   /api/auth/login                User login
POST   /api/auth/register             User registration
POST   /api/cv/tailor                 Tailor CV for job
GET    /api/cv/templates              Get CV templates
GET    /api/jobs/suggestions          Get job suggestions
GET    /api/analytics                 Get analytics data
```

---

## 🛠️ Project Structure Benefits

✅ **Single Git Repository** - Everything in one place
✅ **Easy to Deploy** - Both apps in root level
✅ **Monorepo Pattern** - Industry standard
✅ **Clean Organization** - server/ and client/ clearly separated
✅ **Scalable** - Easy to add more services

---

## 📦 Configuration

### Backend (.env)

Create `server/.env`:

```
FASTAPI_ENV=development
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key-here
STRIPE_API_KEY=your-stripe-key-here
CORS_ORIGINS=http://localhost:5175,http://localhost:3000
```

### Frontend (.env)

Create `client/.env`:

```
VITE_API_URL=http://localhost:8001
VITE_ENV=development
```

---

## 🧪 Running Everything at Once

### Windows PowerShell

```powershell
# Terminal 1
cd server; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2
cd client; npm run dev
```

### macOS/Linux

```bash
# Terminal 1
cd server && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2
cd client && npm run dev
```

---

## 🐛 Troubleshooting

### Backend not starting?
```bash
cd server
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend issues?
```bash
cd client
npm install
npm run dev
```

### Port already in use?
Change the port numbers in the commands above.

---

## 📚 Documentation

- **API Docs**: `http://localhost:8001/docs`
- **Alternative API Docs**: `http://localhost:8001/redoc`
- **Frontend**: `http://localhost:5175`

---

## 🎯 Git Workflow

Since everything is in one folder, pushing to git is straightforward:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

---

## 📄 License

MIT License

---

**Happy CV Tailoring! 🚀**
