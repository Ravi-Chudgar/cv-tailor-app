# 🌍 Deploy CV Tailor App Live

Complete guide to make your CV Tailor app live for everyone to use.

---

## 📊 Deployment Options Comparison

| Platform | Cost | Setup Time | Difficulty | Uptime | Auto Deploy |
|----------|------|-----------|-----------|--------|------------|
| **Render** (Recommended) | Free / $7/month | 5 mins | ⭐ Easy | 99.9% | ✅ Yes |
| **Railway** | Free tier / $5/month | 5 mins | ⭐ Easy | 99.9% | ✅ Yes |
| **DigitalOcean** | $12/month | 10 mins | ⭐⭐ Medium | 99.9% | ✅ Yes |
| **Vercel + Render** | Free / $20/month | 10 mins | ⭐⭐ Medium | 99.9% | ✅ Yes |
| **AWS** | Free tier / $10/month | 20 mins | ⭐⭐⭐ Hard | 99.99% | ✅ Yes |
| **Heroku** | $7/month | 5 mins | ⭐ Easy | 99.95% | ✅ Yes |

---

## 🚀 **OPTION 1: Render.com (EASIEST - Recommended)**

### Why Render?
- ✅ FREE tier available
- ✅ 5-minute setup
- ✅ Auto-deploys on GitHub push
- ✅ Includes database persistence
- ✅ No credit card needed initially

### Step-by-Step Setup:

#### **Step 1: Sign Up**
1. Go to [render.com](https://render.com)
2. Click "Get Started" 
3. Select "GitHub" to sign up
4. Authorize access to your GitHub account

#### **Step 2: Create Blueprint Deployment**
1. Click "Dashboard" → "New +"
2. Select **"Blueprint"** (not Web Service)
3. Select your `cv-tailor-app` repository
4. Configure:
   - Branch: `main`
   - Root Directory: (leave empty)
   - Auto-deploy: Toggle **ON**

#### **Step 3: Configure Services**
Render will auto-detect the `render.yaml` file and deploy:
- **Backend:** `cv-tailor-backend` on port 10000
- **Frontend:** `cv-tailor-frontend` on port 10001

#### **Step 4: Add Environment Variables** (Optional)
For backend OpenAI/Stripe integration:
1. Go to Backend service → "Environment"
2. Add:
   ```
   OPENAI_API_KEY=your-key
   STRIPE_API_KEY=your-key
   ```

#### **Step 5: Get Your Live URLs**
After deployment completes (3-5 mins), you'll get:
- 🔗 Frontend: `https://cv-tailor-frontend.onrender.com`
- 🔗 Backend: `https://cv-tailor-backend.onrender.com`
- 📚 API Docs: `https://cv-tailor-backend.onrender.com/docs`

**Share these URLs with everyone!**

#### **Step 6: Enable Auto-Deploy on GitHub Push**
- Already enabled! Every time you push to `main`, Render auto-deploys

---

## 🚀 **OPTION 2: Railway.app**

### Setup:

#### **Step 1: Sign Up**
1. Go to [railway.app](https://railway.app)
2. Click "Dashboard"
3. Authorize with GitHub

#### **Step 2: Deploy**
1. Click "New Project"
2. Select "Deploy from GitHub Repo"
3. Choose `cv-tailor-app`
4. Click "Deploy"

#### **Step 3: Configure Services**
Railway auto-detects and deploys both backend and frontend.

1. Click on `backend` service:
   - In Variables tab, set:
   ```
   PORT=10000
   PYTHONUNBUFFERED=1
   ```

2. Click on `frontend` service:
   - In Variables tab, set:
   ```
   VITE_API_BASE_URL=https://backend-production-xxxxx.up.railway.app
   ```

#### **Step 4: Get URLs**
- Frontend: `https://frontend-production-xxxxx.up.railway.app`
- Backend: `https://backend-production-xxxxx.up.railway.app`

**Cost:** $5 credit/month free, then $5/month per service

---

## 🚀 **OPTION 3: DigitalOcean (Affordable)**

### Setup:

#### **Step 1: Create Account**
1. Go to [digitalocean.com](https://digitalocean.com)
2. Sign up with GitHub

#### **Step 2: Create App**
1. Click "Create" → "Apps"
2. Connect GitHub repository
3. Select `cv-tailor-app`
4. Choose: "Automatically detect and deploy"

#### **Step 3: Configure Environment**
DigitalOcean reads your `render.yaml` file automatically!

Set environment variables:
- `VITE_API_BASE_URL` to your backend URL

#### **Step 4: Deploy**
Click "Create Resources" and wait 5-10 minutes

**Cost:** $12/month for both services ($6 each)

---

## 🚀 **OPTION 4: Vercel + Render (Frontend + Backend)**

### Setup Frontend on Vercel:

#### **Step 1: Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "Add New..." → "Project"
4. Select `cv-tailor-app` repository

#### **Step 2: Configure**
1. Framework: React
2. Root Directory: `client`
3. Build Command: `npm run build`
4. Environment Variables:
   ```
   VITE_API_BASE_URL=https://cv-tailor-backend-production.up.railway.app
   ```
5. Deploy!

#### **Step 3: Deploy Backend on Render**
Follow **OPTION 1** above

**URLs:**
- Frontend: `https://cv-tailor-app.vercel.app`
- Backend: `https://cv-tailor-backend.onrender.com`

---

## 🔑 Environment Variables for Production

Create these in your deployment platform:

### Backend Variables:
```
PYTHONUNBUFFERED=1
SECRET_KEY=generate-a-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=sk-xxxx...
STRIPE_API_KEY=sk_test_xxxx...
DATABASE_URL=sqlite:///./cv_tailor.db
```

### Frontend Variables:
```
VITE_API_BASE_URL=https://your-backend-url.com
```

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] Frontend loads without errors
- [ ] Can register a new account
- [ ] Can login with credentials
- [ ] Can upload a CV
- [ ] Can upload a job description
- [ ] Can see ATS score
- [ ] Can generate PDF
- [ ] API docs page loads at `/docs`

### Test URLs:
```
# Frontend
https://your-frontend-url

# Backend Health
https://your-backend-url/health

# API Documentation
https://your-backend-url/docs

# Swagger UI
https://your-backend-url/redoc
```

---

## 🚨 Common Issues & Solutions

### **Issue: Frontend can't connect to backend**
**Solution:** Update `VITE_API_BASE_URL` environment variable to match your backend URL exactly

### **Issue: Slow on first load**
**Solution:** Free tier services spin down after 15 mins. Wait for cold start (30-60 seconds)

### **Issue: "Port already in use"**
**Solution:** Platform assigns ports automatically. Check dashboard for assigned port

### **Issue: Large file upload fails**
**Solution:** Increase upload limit in backend `main.py`:
```python
# Add to FastAPI app
app = FastAPI(
    # ... existing config
    max_upload_size=100_000_000  # 100MB
)
```

### **Issue: Database not persisting**
**Solution:** Free tier doesn't persist data. Upgrade to paid plan or use external database

---

## 💡 Tips for Production

1. **HTTPS:** All deployed URLs are HTTPS by default ✅

2. **Custom Domain:** 
   - Render: $5/month, set CNAME in DNS
   - Railway: $10/month
   - DigitalOcean: $6/month
   - Vercel: Free

3. **SSL Certificate:** Auto-generated (no extra setup needed)

4. **Backup Data:**
   - Download data from `/data` folder regularly
   - Or set up database backup service

5. **Monitor Performance:**
   - Render: Dashboard shows CPU/RAM usage
   - Railway: Real-time metrics
   - DigitalOcean: Usage dashboard

6. **Scale Up if Needed:**
   - All platforms allow easy upgrades
   - Increase CPU/RAM in dashboard

---

## 🔗 Share Your App

Once live, share these URLs:

```
📱 Frontend: https://your-frontend-url
📚 API Docs: https://your-backend-url/docs
🐙 GitHub: https://github.com/Ravi-Chudgar/cv-tailor-app
```

---

## 📱 Next Steps

1. **Monitor Performance** → Check dashboard regularly
2. **Gather Feedback** → Share with friends/colleagues
3. **Add Features** → Push to GitHub, auto-deploys
4. **Scale Up** → Upgrade plan as needed
5. **Set Up Analytics** → Track usage

---

## 🎯 My Recommendation

**For beginners:** Use **Render** (easiest, free)  
**For production:** Use **DigitalOcean** (affordable, reliable)  
**For rapid growth:** Use **AWS** (scales infinitely)

---

## 📞 Support Links

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- DigitalOcean Docs: https://docs.digitalocean.com
- Vercel Docs: https://vercel.com/docs

Good luck! 🚀
