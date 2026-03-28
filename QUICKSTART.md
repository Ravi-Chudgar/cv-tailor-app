# CV Tailor - Quick Start (Unified Structure)

## ✅ Your Application is Ready!

Everything is now in a **single unified folder** for clean git management:

```
F:\cv-tailor-app-new\
├── server/      ← FastAPI Backend
├── client/      ← React Frontend
└── Supporting files
```

---

## 🚀 Start the Application

### Step 1: Install Dependencies

```powershell
# Backend dependencies
cd server
pip install -r requirements.txt
cd ..

# Frontend dependencies
cd client
npm install
cd ..
```

### Step 2: Start Backend (Terminal 1)

```powershell
cd server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

✅ Backend running at: **http://localhost:8001**
📚 API Docs: **http://localhost:8001/docs**

### Step 3: Start Frontend (Terminal 2)

```powershell
cd client
npm run dev
```

✅ Frontend running at: **http://localhost:5175**

---

## 🔐 Login Credentials

```
Username: admin
Password: admin123
```

---

## 📁 Clean Structure for Git

No more issues with git push! Everything is organized:

```
cv-tailor-app/
├── server/           (all backend code)
├── client/           (all frontend code)
├── README.md         (documentation)
├── .gitignore        (git config)
└── Other config files
```

---

## 💡 Key Points

✅ **Single Repository** - One git repo for everything
✅ **Monorepo Pattern** - Industry standard approach
✅ **Easy Deployment** - Both apps at root level
✅ **No Duplicate Files** - Organized structure
✅ **Clean Git History** - Clear commit messages

---

## 🧭 Directory Reference

| Folder | Purpose | Port |
|--------|---------|------|
| `server/` | FastAPI backend | 8001 |
| `client/` | React frontend | 5175 |

---

## 📝 Next Steps

1. Change to this folder: `cd F:\cv-tailor-app-new`
2. Install dependencies
3. Run both servers in separate terminals
4. Open http://localhost:5175
5. Start developing!

---

**Everything is set up and ready to push to git! 🎉**
