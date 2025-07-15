# 🚀 BistroBoard Production Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying BistroBoard to production using:
- **Frontend**: Vercel (Next.js)
- **Backend**: Render (FastAPI)
- **Database**: MongoDB Atlas (already configured)

## 🔧 Prerequisites

Before starting deployment, ensure you have:

1. **GitHub Repository**: Code pushed to `https://github.com/shayant101/BB.git`
2. **MongoDB Atlas**: Cluster already configured and running
3. **Google Cloud Console**: Access to create OAuth 2.0 credentials
4. **Vercel Account**: For frontend deployment
5. **Render Account**: For backend deployment

## 🎯 Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Render        │    │ MongoDB Atlas   │
│   (Frontend)    │───▶│   (Backend)     │───▶│   (Database)    │
│   Next.js       │    │   FastAPI       │    │   ClusterBB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
              Google OAuth 2.0
```

## 📝 Step-by-Step Deployment

### Phase 1: Backend Deployment (Render)

#### 1.1 Create Render Account and Service

1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `https://github.com/shayant101/BB.git`
4. Configure the service:
   - **Name**: `bistroboard-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: Leave empty (uses project root)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 1.2 Configure Environment Variables

In Render dashboard, go to Environment tab and add:

```bash
# Required Environment Variables
MONGODB_URL=mongodb+srv://username:password@clusterbb.gzjujes.mongodb.net/bistroboard?retryWrites=true&w=majority&appName=ClusterBB
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret
GOOGLE_REDIRECT_URI=https://your-frontend-domain.vercel.app
JWT_SECRET_KEY=your_secure_jwt_secret_key
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

**🔐 Security Notes:**
- Generate JWT_SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Use the same MongoDB URL from your current `.env` file
- Google OAuth credentials will be created in next steps

#### 1.3 Deploy Backend

1. Click "Create Web Service"
2. Wait for deployment to complete (5-10 minutes)
3. Note your backend URL: `https://bistroboard-api.onrender.com`
4. Test health endpoint: `https://bistroboard-api.onrender.com/health`

### Phase 2: Google OAuth Production Setup

#### 2.1 Create Production OAuth Client

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "APIs & Services" → "Credentials"
3. Click "Create Credentials" → "OAuth 2.0 Client ID"
4. Configure:
   - **Application type**: Web application
   - **Name**: BistroBoard Production
   - **Authorized JavaScript origins**:
     - `https://your-frontend-domain.vercel.app`
   - **Authorized redirect URIs**:
     - `https://your-frontend-domain.vercel.app`

#### 2.2 Update Backend Environment Variables

1. Copy the Client ID and Client Secret
2. Update Render environment variables:
   - `GOOGLE_CLIENT_ID`: Your new production client ID
   - `GOOGLE_CLIENT_SECRET`: Your new production client secret

### Phase 3: Frontend Deployment (Vercel)

#### 3.1 Create Vercel Account and Project

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "New Project"
3. Import from GitHub: `https://github.com/shayant101/BB.git`
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

#### 3.2 Configure Environment Variables

In Vercel dashboard, go to Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=https://bistroboard-api.onrender.com/api
```

#### 3.3 Deploy Frontend

1. Click "Deploy"
2. Wait for deployment (3-5 minutes)
3. Note your frontend URL: `https://bistroboard-frontend.vercel.app`

### Phase 4: Final Configuration Updates

#### 4.1 Update Backend CORS

1. Go back to Render dashboard
2. Update environment variable:
   ```bash
   ALLOWED_ORIGINS=https://bistroboard-frontend.vercel.app
   ```

#### 4.2 Update Google OAuth Redirect URI

1. Go back to Google Cloud Console
2. Edit your OAuth 2.0 Client
3. Update authorized origins and redirect URIs to use your actual Vercel domain

#### 4.3 Update Backend Google Redirect URI

1. In Render dashboard, update:
   ```bash
   GOOGLE_REDIRECT_URI=https://bistroboard-frontend.vercel.app
   ```

## ✅ Verification Steps

### 1. Backend Health Check
```bash
curl https://bistroboard-api.onrender.com/health
```
Expected response:
```json
{
  "status": "healthy",
  "database": "mongodb",
  "database_status": "connected"
}
```

### 2. Frontend Access
- Visit: `https://bistroboard-frontend.vercel.app`
- Should load the login page
- Google Sign-In should work without errors

### 3. API Integration Test
- Login via frontend
- Navigate to dashboard
- Verify data loads correctly

## 🔒 Security Checklist

- [ ] MongoDB connection string uses environment variables
- [ ] CORS restricted to production domains only
- [ ] Google OAuth configured for production domains
- [ ] JWT secret key is secure and unique
- [ ] HTTPS enabled on all services
- [ ] Security headers configured in Next.js

## 🚨 Troubleshooting

### Common Issues:

#### 1. "Origin not allowed" CORS Error
**Solution**: Update `ALLOWED_ORIGINS` in Render to match your Vercel domain

#### 2. Google OAuth "redirect_uri_mismatch"
**Solution**: Ensure Google Cloud Console redirect URIs match your Vercel domain

#### 3. Database connection failed
**Solution**: Verify `MONGODB_URL` environment variable is correct

#### 4. API calls failing from frontend
**Solution**: Check `NEXT_PUBLIC_API_URL` points to your Render backend

## 📊 Monitoring & Maintenance

### Render Monitoring
- Check logs in Render dashboard
- Monitor service health at `/health` endpoint
- Set up alerts for service downtime

### Vercel Monitoring
- Monitor build logs in Vercel dashboard
- Check function execution logs
- Monitor Core Web Vitals

### MongoDB Atlas Monitoring
- Monitor cluster performance
- Set up alerts for high CPU/memory usage
- Review slow query logs

## 🔄 CI/CD Pipeline

Both Render and Vercel are configured for automatic deployments:

- **Trigger**: Push to `main` branch
- **Backend**: Render automatically rebuilds and deploys
- **Frontend**: Vercel automatically rebuilds and deploys

## 📈 Scaling Considerations

### Render Scaling
- Upgrade to higher tier plans for more resources
- Enable auto-scaling for traffic spikes

### Vercel Scaling
- Automatic scaling included
- Monitor function execution limits

### MongoDB Atlas Scaling
- Already configured for horizontal scaling
- Monitor and upgrade cluster tier as needed

## 🎉 Deployment Complete!

Your BistroBoard application is now live in production:

- **Frontend**: `https://bistroboard-frontend.vercel.app`
- **Backend**: `https://bistroboard-api.onrender.com`
- **Database**: MongoDB Atlas (ClusterBB)

## 📞 Support

If you encounter issues during deployment:

1. Check the troubleshooting section above
2. Review service logs in respective dashboards
3. Verify all environment variables are correctly set
4. Test each component individually

---

**Last Updated**: January 2025
**Version**: 1.0.0