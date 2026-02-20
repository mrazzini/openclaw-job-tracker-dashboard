# Deployment Guide - Render

## What You Need
- Render account (free tier works)
- GitHub account with access to this repo

## Architecture
- **Backend**: FastAPI API (Python)
- **Frontend**: React + Vite (Node.js)
- **Database**: Managed PostgreSQL (Render)

## Step 1: Create Database
1. Go to [render.com](https://render.com) → Dashboard → New → PostgreSQL
2. Name: `ambros-db`
3. Region: Choose closest to you (Frankfurt for EU)
4. Plan: Free tier
5. Click "Create Database"
6. Copy the **Internal Database URL** (you'll need it in Step 2)

## Step 2: Deploy Backend
1. Dashboard → New → Web Service
2. Connect your GitHub repo: `mrazzini/openclaw-job-tracker-dashboard`
3. Branch: `deploy-render`
4. Settings:
   - **Name**: `ambros-api`
   - **Region**: Same as database
   - **Runtime**: Docker
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Root Directory**: (leave blank)
5. Environment Variables:
   - `DATABASE_URL`: Paste from Step 1
6. Click "Create Web Service"
7. Wait for build (2-3 mins)
8. Copy the backend URL: `https://ambros-api.onrender.com`

## Step 3: Deploy Frontend
1. Dashboard → New → Static Site
2. Same repo, `deploy-render` branch
3. Settings:
   - **Name**: `ambros-dashboard`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Environment Variables:
   - `VITE_API_URL`: Paste backend URL from Step 2
5. Click "Create Static Site"

## Step 4: Verify
- Frontend URL loads dashboard
- Check API: visit `https://your-backend-url/health`
- Skills/Jobs should appear (auto-seeded on first boot)

## Troubleshooting
- **Blank page**: Check browser console for API errors
- **Database errors**: Verify DATABASE_URL in backend env vars
- **CORS errors**: Ensure frontend VITE_API_URL matches backend URL

## Auto-Deploy
Any push to `deploy-render` branch auto-deploys both services.

## Local Development (Optional)
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# API: http://localhost:8000
```
