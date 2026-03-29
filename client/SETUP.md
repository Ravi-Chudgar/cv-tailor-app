# Frontend Setup Instructions

Complete React frontend for CV Tailor application has been created!

## Quick Start

### 1. Navigate to frontend directory
```bash
cd F:\cv-tailor-app\frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Create environment file
```bash
copy .env.example .env
```

### 4. Start development server
```bash
npm run dev
```

The frontend will be available at: **http://localhost:3000**

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js              # API client with axios
│   ├── components/
│   │   ├── Header.jsx             # App header
│   │   ├── CVUploader.jsx         # File upload
│   │   ├── JobDescriptionForm.jsx # Job analysis
│   │   ├── TailoringResults.jsx   # Results display
│   │   ├── ATSScoreDisplay.jsx    # Score visualization
│   │   └── ProtectedRoute.jsx     # Auth protection
│   ├── pages/
│   │   ├── LoginPage.jsx          # Login
│   │   ├── RegisterPage.jsx       # Register
│   │   └── DashboardPage.jsx      # Main dashboard
│   ├── stores/
│   │   ├── authStore.js           # Auth state
│   │   └── cvStore.js             # CV state
│   ├── App.jsx                    # Main app
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Tailwind CSS
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Features

✨ **Authentication**
- Register new users
- Login with username/password
- JWT token management
- Auto token refresh

📄 **CV Management**
- Upload PDF/DOCX files
- Parse CV content
- List uploaded CVs

🎯 **CV Tailoring**
- Analyze job descriptions
- Tailor CV to match jobs
- View ATS scores
- Copy/download tailored CV

📊 **ATS Optimization**
- Component scores breakdown
- Keyword analysis
- Recommendations
- Visual score display

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool (super fast!)
- **React Router** - Navigation
- **Zustand** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Environment Variables

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api
```

## Backend Requirements

Make sure your backend is running:

1. Backend running at `http://localhost:8000`
2. API endpoints available at `http://localhost:8000/api`

## Development Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Port Configuration

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

If ports conflict, update `vite.config.js`:
```javascript
server: {
  port: 3001  // change to different port
}
```

## Common Issues

### "Cannot GET /" at http://localhost:3000

- Make sure `npm run dev` is running
- Check that you're accessing it in browser

### API Connection Errors

- Verify backend is running: `http://localhost:8000/docs`
- Check `VITE_API_URL` in `.env`
- Look for CORS errors in browser console

### Module Not Found Errors

- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

## Next Steps

1. **Install dependencies**: `npm install`
2. **Start frontend**: `npm run dev`
3. **Open browser**: http://localhost:3000
4. **Register/Login**: Create a test account
5. **Upload CV**: Test with a sample CV
6. **Test Tailoring**: Input a job description
7. **Download PDF**: Generate and download tailored CV

## Deployment

After testing locally, deploy to:
- **Vercel** (recommended, free tier)
- **Netlify** (free tier)
- **GitHub Pages** (static, limited features)
- **AWS S3 + CloudFront**

See README.md for deployment instructions.

## Support

For issues:
1. Check browser console for errors
2. Check backend logs
3. Verify API connectivity
4. See README.md in frontend directory

---

**Ready to go!** Run `npm install && npm run dev` to start. 🚀
