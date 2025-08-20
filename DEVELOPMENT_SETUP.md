# BistroBoard Development Setup Guide

## Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- MongoDB Atlas account (or local MongoDB)

### 1. Backend Setup
```bash
cd "bistroboard 2/backend"
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd "bistroboard 2/frontend"
npm install
npm run dev
```

## Environment Configuration

### Frontend Environment Variables
Create `.env.local` in the frontend directory:
```env
# Required: API endpoint (must include /api suffix)
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Optional: Development settings
NODE_ENV=development
```

### Backend Environment Variables
Create `.env` in the backend directory:
```env
# MongoDB Configuration
MONGODB_URL=your_mongodb_atlas_connection_string

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# JWT Configuration
SECRET_KEY=your_secret_key
```

## Common Issues & Solutions

### Issue 1: "404 Not Found" on API calls
**Symptoms:** Login fails, API endpoints return 404
**Cause:** Frontend API URL doesn't match backend route structure
**Solution:** Ensure `NEXT_PUBLIC_API_URL` ends with `/api`

### Issue 2: Frontend compilation hanging
**Symptoms:** Next.js build process gets stuck
**Cause:** Usually complex components with circular dependencies or SSR issues
**Solution:** Check components for:
- Circular imports
- Improper use of `useEffect` with external scripts
- localStorage access during SSR

### Issue 3: CORS errors
**Symptoms:** Browser blocks API requests
**Cause:** Backend CORS configuration
**Solution:** Backend is configured for permissive CORS in development

## Architecture Overview

### API Structure
- Backend routes are prefixed with `/api`
- Frontend must call `/api/auth/login`, not `/auth/login`
- Health check endpoint: `/health` (no /api prefix)

### Key Components
- **AuthInitializer**: Handles token restoration on page load
- **CartContext**: Manages shopping cart state with localStorage
- **GoogleSignIn**: Handles OAuth authentication

## Development Workflow

### Starting Development
1. Start backend server first: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
2. Start frontend server: `cd frontend && npm run dev`
3. Check health: Visit `http://localhost:8000/health`
4. Access app: Visit `http://localhost:3000`

### Testing API Connectivity
The frontend automatically runs a health check in development mode. Check browser console for:
- ✅ API Health Check Passed
- ❌ API Health Check Failed (indicates backend issues)

### Demo Accounts
- **Restaurant**: username: `restaurant1`, password: `demo123`
- **Vendor**: username: `fresh_valley_farms`, password: `demo123`  
- **Admin**: username: `admin`, password: `admin123`

## Troubleshooting

### Backend Not Starting
1. Check MongoDB connection string
2. Verify Python dependencies: `pip install -r requirements.txt`
3. Check port 8000 availability: `lsof -i :8000`

### Frontend Not Starting
1. Clear Next.js cache: `rm -rf .next`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Check Node.js version: `node --version` (should be 18+)

### API Connection Issues
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check frontend environment: Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000/api`
3. Check browser network tab for actual request URLs

## Production Deployment

### Environment Variables Required
- Frontend: `NEXT_PUBLIC_API_URL` (must be set, no fallback in production)
- Backend: `MONGODB_URL`, `SECRET_KEY`, Google OAuth credentials

### Build Process
```bash
# Frontend
npm run build
npm start

# Backend  
# Deploy with proper environment variables
```

## Preventive Measures Implemented

1. **Robust API URL validation** - Automatically normalizes URLs and validates format
2. **Environment variable validation** - Fails fast in production if required vars missing
3. **API health checks** - Automatic connectivity verification in development
4. **Enhanced error logging** - Detailed error messages for debugging
5. **Proper fallback handling** - Safe defaults for development environment

This setup guide should prevent configuration mismatches and provide clear debugging steps for future development.