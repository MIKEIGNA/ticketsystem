# Deployment Guide: Django Backend (Railway) + Frontend (Firebase)

This guide covers deploying the TicketSystem backend to Railway and the frontend to Firebase Hosting.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment to Railway](#backend-deployment-to-railway)
3. [Frontend Deployment to Firebase](#frontend-deployment-to-firebase)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- **Railway Account**: [railway.app](https://railway.app) - For Django backend
- **Firebase Account**: [firebase.google.com](https://firebase.google.com) - For React frontend
- **GitHub Account**: For connecting Railway to your repository

### Required Tools
- Git installed locally
- Node.js 18+ and npm
- Python 3.10+
- Railway CLI (optional): `npm install -g @railway/cli`
- Firebase CLI: `npm install -g firebase-tools`

---

## Backend Deployment to Railway

### Step 1: Prepare Django for Production

The following files have already been created for you:

- `backend/railway.json` - Railway configuration
- `backend/Procfile` - Process configuration
- `backend/production_settings.py` - Production settings
- `backend/.env.example` - Environment variables template

### Step 2: Push Code to GitHub

```bash
cd c:\Users\Jovi\Documents\ticketsystem
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 3: Deploy to Railway

#### Option A: Via Railway Website (Recommended)

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Click **"Deploy from GitHub repo"**
4. Select your `ticketsystem` repository
5. Configure the project:

**Add PostgreSQL Database:**
- Click **"New Service"** → **Database** → **PostgreSQL**
- Railway will automatically create a PostgreSQL database
- Copy the database URL from the database service

**Add Django Backend Service:**
- Click **"New Service"** → **GitHub** → Select your repo
- Set root directory to: `backend`
- Railway will detect Python and create the service

#### Option B: Via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize Railway project
cd backend
railway init

# Add PostgreSQL database
railway add postgresql

# Deploy
railway up
```

### Step 4: Configure Environment Variables

In Railway, go to your Django service → **Variables** tab. Add these:

```bash
# Django Core
DJANGO_SETTINGS_MODULE=ticketsystem.settings
DEBUG=False
SECRET_KEY=<generate-a-secure-random-key>
ALLOWED_HOSTS=<your-railway-app>.railway.app

# Database (Railway provides these automatically via DATABASE_URL)
# But you can also set individual vars:
POSTGRES_DB=<from-railway-database-service>
POSTGRES_USER=<from-railway-database-service>
POSTGRES_PASSWORD=<from-railway-database-service>
POSTGRES_HOST=<from-railway-database-service>
POSTGRES_PORT=5432

# CORS (Important for frontend)
CORS_ALLOWED_ORIGINS=https://your-firebase-app.web.app,https://your-firebase-app.firebaseapp.com
CSRF_TRUSTED_ORIGINS=https://your-firebase-app.web.app,https://your-firebase-app.firebaseapp.com

# M-Pesa (Sandbox for testing, Production for live)
MPESA_CONSUMER_KEY=<your-daraja-key>
MPESA_CONSUMER_SECRET=<your-daraja-secret>
MPESA_PASSKEY=<your-daraja-passkey>
MPESA_SHORTCODE=174379
MPESA_ENVIRONMENT=sandbox
MPESA_CALLBACK_URL=https://your-railway-app.railway.app/api/payments/mpesa/callback/

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Step 5: Run Database Migrations

Railway will automatically run migrations on deploy, but you can also run them manually:

```bash
# Via Railway CLI
railway run python manage.py migrate

# Or via Railway Console
# Go to your Django service → Console tab
python manage.py migrate
```

### Step 6: Create Superuser

```bash
# Via Railway Console
python manage.py createsuperuser
```

### Step 7: Verify Deployment

1. Open your Railway app URL (e.g., `https://ticketsystem-production.up.railway.app`)
2. Check health endpoint: `https://your-app.railway.app/api/health/`
3. Should return: `{"status": "healthy", "service": "ticketsystem"}`

### Step 8: Note Your Backend URL

Copy your Railway backend URL, you'll need it for the frontend:
```
https://your-app-name.railway.app/api
```

---

## Frontend Deployment to Firebase

### Step 1: Prepare Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **"Add project"**
3. Project name: `ticketsystem-web` (or your preferred name)
4. Enable Google Analytics (optional)
5. Click **"Create project"**

### Step 2: Enable Firebase Hosting

1. In Firebase Console, go to **Build** → **Hosting**
2. Click **"Get started"**
3. Select your Firebase project
4. Click **"Next"** through the setup wizard

### Step 3: Install Firebase CLI

```bash
npm install -g firebase-tools
```

### Step 4: Login to Firebase

```bash
cd c:\Users\Jovi\Documents\ticketsystem\frontend
firebase login
```

This will open a browser to authenticate with Firebase.

### Step 5: Initialize Firebase

The following files have already been created:
- `frontend/firebase.json` - Firebase hosting configuration
- `frontend/.firebaserc` - Firebase project configuration

Update `.firebaserc` with your Firebase project ID:

```json
{
  "projects": {
    "default": "your-actual-firebase-project-id"
  }
}
```

### Step 6: Configure Production API URL

Create a production environment file:

```bash
cd frontend
cp .env.example .env.production
```

Edit `.env.production`:

```bash
# Production (Railway)
VITE_API_URL=https://your-railway-app.railway.app/api
```

### Step 7: Build the React App

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` folder with production-ready files.

### Step 8: Deploy to Firebase

```bash
firebase projects:list
firebase deploy
```

Firebase will ask:
- "What do you want to use as your public directory?" → `dist`
- "Configure as a single-page app?" → `Yes`

### Step 9: Verify Deployment

Firebase will provide URLs like:
- Hosting URL: `https://ticketsystem-web.web.app`
- Hosting URL: `https://ticketsystem-web.firebaseapp.com`

Test the deployed site in your browser.

---

## Post-Deployment Configuration

### Update CORS in Railway

After deploying to Firebase, update your Railway environment variables:

1. Go to Railway → Django service → Variables
2. Update `CORS_ALLOWED_ORIGINS` with your Firebase URLs:
```bash
CORS_ALLOWED_ORIGINS=https://ticketsystem-web.web.app,https://ticketsystem-web.firebaseapp.com
CSRF_TRUSTED_ORIGINS=https://ticketsystem-web.web.app,https://ticketsystem-web.firebaseapp.com
```
3. Click **"Deploy"** to restart the Django service

### Update M-Pesa Callback URL

In Railway variables, update:
```bash
MPESA_CALLBACK_URL=https://your-railway-app.railway.app/api/payments/mpesa/callback/
```

### Test the Full Flow

1. Visit your Firebase URL
2. Try to register/login
3. Browse events
4. Test ticket booking (with M-Pesa sandbox)
5. Download a ticket
6. Verify all functionality works

---

## Troubleshooting

### Railway Issues

**Issue: Database connection errors**
- Check that PostgreSQL service is running
- Verify DATABASE_URL is set correctly
- Try redeploying: Click "Redeploy" button in Railway

**Issue: Migrations not running**
- Go to Console tab in Railway
- Run: `python manage.py migrate`
- Check for migration errors

**Issue: Static files not loading**
- Whitenoise should handle static files automatically
- Check that STATIC_URL is set to `/static/`

**Issue: CORS errors**
- Verify CORS_ALLOWED_ORIGINS includes your Firebase URL
- Check that the URL is HTTPS (required for production)

### Firebase Issues

**Issue: Build fails**
- Check that `npm run build` works locally
- Verify all dependencies are in package.json
- Check for any build errors in the console

**Issue: 404 errors on navigation**
- Ensure single-page app routing is configured (firebase.json)
- Check that the `rewrites` section is correct

**Issue: API calls failing**
- Verify VITE_API_URL is set correctly
- Check browser console for CORS errors
- Ensure Railway backend is running and accessible

### Common Issues

**Issue: Environment variables not loading**
- Railway: Check Variables tab, ensure they're set
- Firebase: Environment variables are build-time only, not runtime
- For Firebase, set API URL in `.env.production` before building

**Issue: M-Pesa payment failing**
- Verify sandbox credentials are correct
- Check callback URL is accessible from internet
- Use ngrok for local testing if needed

**Issue: Images not loading**
- Ensure MEDIA_URL is configured correctly
- For production, consider using cloud storage (AWS S3, Cloudinary)

---

## Maintenance

### Updating the Backend

```bash
git push origin main
# Railway auto-deploys on push
```

### Updating the Frontend

```bash
cd frontend
npm run build
firebase deploy
```

### Monitoring

- **Railway**: Built-in logs and metrics
- **Firebase**: Realtime Database (if using), Analytics
- Check logs regularly for errors

### Backup Strategy

- **Database**: Railway provides automatic backups
- **Media Files**: Consider using cloud storage
- **Code**: Git repository

---

## Cost Estimates

### Railway
- PostgreSQL: ~$5-10/month
- Django Service: ~$5-10/month
- **Total**: ~$10-20/month (free tier available for small apps)

### Firebase
- Hosting: Free (up to 10GB/month)
- Database/Storage: Pay as you go
- **Total**: Free for most small apps

---

## Security Checklist

- [ ] SECRET_KEY is set to a strong random value
- [ ] DEBUG is set to False
- [ ] ALLOWED_HOSTS is configured correctly
- [ ] CORS is properly configured
- [ ] HTTPS is enabled (automatic on Railway and Firebase)
- [ ] Database credentials are not hardcoded
- [ ] API keys are in environment variables
- [ ] M-Pesa credentials are secure
- [ ] Static and media files are served correctly

---

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Firebase Hosting Documentation](https://firebase.google.com/docs/hosting)
- [Django Deployment Guide](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)

---

## Quick Reference

### Backend URL
```
https://your-app.railway.app/api
```

### Frontend URL
```
https://your-app.web.app
```

### Admin Panel
```
https://your-app.railway.app/admin
```

### Health Check
```
https://your-app.railway.app/api/health
```

---

**Need help?** Check the logs in Railway Console and Firebase Console for detailed error messages.


Firebase sdk
// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAJEuHFo5kneQ8ZMrBMVfAdupb_ljStvuY",
  authDomain: "brightpassticket.firebaseapp.com",
  projectId: "brightpassticket",
  storageBucket: "brightpassticket.firebasestorage.app",
  messagingSenderId: "76044044725",
  appId: "1:76044044725:web:aba002f2920223ab2171fc",
  measurementId: "G-ZFBMF2BDH1"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);