# CV Tailor — AI-Powered Resume Optimization & ATS Scoring

An intelligent full-stack application that **parses, analyzes, and tailors your CV/resume** to match specific job descriptions — boosting your ATS (Applicant Tracking System) score and helping you land more interviews. Built with **React + Vite** frontend and **FastAPI** (Python) backend.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5+-646CFF?logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-06B6D4?logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 What It Does

Upload your CV and a job description — the app automatically:

1. **Parses your CV** (PDF/DOCX) and extracts structured content
2. **Analyzes the job description** to identify required skills, keywords, and qualifications
3. **Performs gap analysis** — highlights what's missing from your CV
4. **Searches the internet** for relevant industry keywords to inject
5. **Tailors your CV** with aggressive keyword optimization for ATS systems
6. **Scores your CV** with a comprehensive 4-component ATS scorer (keyword match, formatting, impact content, ATS compatibility)
7. **Generates a professional one-page PDF** in a clean, ATS-friendly format

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **CV Parsing** | Extracts text from PDF and DOCX files with structured section detection |
| **Job Description Analysis** | Identifies required skills, qualifications, experience levels, and keywords |
| **ATS Score Calculator** | 4-component weighted scoring: Keyword Match (35%), Formatting (25%), Impact Content (20%), ATS Compatibility (20%) |
| **Keyword Optimization** | Internet-powered keyword search + aggressive injection into CV content |
| **Gap Analysis** | Shows missing skills, certifications, and experience vs. job requirements |
| **PDF Generation** | Professional one-page ATS-optimized resume in Rezi.ai-style format |
| **User Authentication** | JWT-based auth with registration, login, and role-based access |
| **Admin Dashboard** | User management, statistics, and system monitoring |
| **Mobile Override** | Edit phone number and location directly before PDF generation |
| **Modern UI** | Indigo-purple gradient theme with frosted glass effects and responsive design |

---

## 🛠️ Tech Stack

**Frontend:** React 18, Vite, Tailwind CSS, Zustand, Lucide React, Axios  
**Backend:** Python, FastAPI, ReportLab (PDF), python-docx, PyPDF2, BeautifulSoup4  
**Auth:** JWT tokens with bcrypt password hashing  
**Storage:** Excel-based user storage (lightweight, no database required)

---

## 📁 Project Structure

```
cv-tailor-app/
├── server/                     # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # API routes & CV tailoring engine
│   │   ├── ats_scorer.py      # 4-component ATS scoring system
│   │   ├── cv_parser.py       # PDF/DOCX parsing & text extraction
│   │   ├── keyword_search.py  # Internet keyword search engine
│   │   └── users_storage.py   # Excel-based user management
│   ├── data/                  # User data storage
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
│
├── client/                     # React + Vite Frontend
│   ├── src/
│   │   ├── components/        # CVUploader, ATSScoreDisplay, TailoringResults, etc.
│   │   ├── pages/             # Dashboard, Login, Register, Admin
│   │   ├── stores/            # Zustand state (auth, cv)
│   │   ├── api/               # Axios HTTP client
│   │   └── index.css          # Tailwind + custom animations
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── README.md
├── SETUP.md
├── QUICKSTART.md
└── .gitignore
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (with pip)
- **Node.js 18+** (with npm)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Ravi-Chudgar/cv-tailor-app.git
cd cv-tailor-app
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

Frontend runs at: **http://localhost:5173** (or next available port)

---

## 🔐 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | ravi.chudgar@gmail.com | *(your password)* |
| User | *(register a new account)* | *(your choice)* |

---

## � API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | User login (returns JWT) |
| `POST` | `/api/upload-cv` | Upload CV file (PDF/DOCX) |
| `POST` | `/api/analyze-job` | Analyze job description |
| `POST` | `/api/tailor` | Tailor CV to job description |
| `POST` | `/api/generate-pdf` | Generate ATS-optimized PDF |
| `GET` | `/api/admin/users` | Admin: list all users |
| `DELETE` | `/api/admin/users/{id}` | Admin: delete user |

Full interactive docs at: `http://localhost:8001/docs`

---

## 📦 Configuration

### Backend — `server/.env`
```env
SECRET_KEY=your-secret-key-here
```

### Frontend — `client/.env`
```env
VITE_API_URL=http://localhost:8001/api
VITE_ENV=development
```

---

## 📸 Screenshots

> Upload your CV → Paste a job description → Get an ATS-optimized, tailored resume in seconds.

---

## 🧪 Running Both Servers

### Windows PowerShell
```powershell
# Terminal 1 — Backend
cd server; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 — Frontend
cd client; npm run dev
```

### macOS / Linux
```bash
# Terminal 1
cd server && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2
cd client && npm run dev
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend not starting | `cd server && pip install -r requirements.txt` |
| Frontend not loading | `cd client && npm install && npm run dev` |
| Port already in use | Change port number in the start command |
| CORS errors | Ensure backend is running on port 8001 |

---

## 📚 Documentation

- **API Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Setup Guide**: [SETUP.md](SETUP.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

---

## 📄 License

MIT License

---

**Built with ❤️ for job seekers — stop submitting generic resumes.**
