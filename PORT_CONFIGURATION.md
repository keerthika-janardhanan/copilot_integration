# Port Configuration Reference

## Current Configuration

### Backend
- **Port**: 8001
- **URL**: http://localhost:8001
- **Start Command**: `.venv\Scripts\Activate.ps1; python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8001`

### Frontend
- **Port**: 5178
- **URL**: http://localhost:5178
- **Start Command**: `cd frontend; npm run dev`

## Files Updated

### Backend Files (Port 8001)
1. `app/event_client.py` - Updated BACKEND_BASE_URL default
2. `app/api/main.py` - Updated default API_PORT and ALLOW_ORIGINS for CORS
3. `test_keyword_inspect_api.py` - Already configured for port 8001
4. `playwright-smoke/smoke.spec.ts` - Updated API_BASE to 8001

### Frontend Files (Port 5178)
1. `frontend/vite.config.ts` - Updated server port to 5178
2. `frontend/src/pages/Dashboard.tsx` - Updated API_BASE to 8001
3. `frontend/src/pages/DashboardModern.tsx` - Updated API_BASE to 8001
4. `frontend/src/pages/AnimatedDashboard.tsx` - Updated BACKEND_URL to 8001
5. `frontend/src/components/design-flow/AutomationScriptFlow.tsx` - Updated all API endpoints to 8001
6. `frontend/src/components/design-flow/RecorderSection.tsx` - Updated recorder and ingest endpoints to 8001
7. `frontend/src/components/design-flow/ManualTestCaseFlow.tsx` - Updated generation endpoint to 8001
8. `frontend/src/api/client.ts` - Already configured for 8001
9. `playwright-smoke/smoke.spec.ts` - Updated APP_BASE to 5178

## Environment Variables

### Backend (.env)
Create a `.env` file in the root directory with:
```
API_HOST=0.0.0.0
API_PORT=8001
BACKEND_BASE_URL=http://localhost:8001
ALLOW_ORIGINS=http://localhost:5178
```

### Frontend (frontend/.env)
Create a `.env` file in the frontend directory with:
```
VITE_API_BASE_URL=http://localhost:8001
VITE_BACKEND_URL=http://localhost:8001
```

## How to Start Both Services

### Terminal 1 (Backend)
```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8001
```

### Terminal 2 (Frontend)
```powershell
cd frontend
npm run dev
```

## Testing the Configuration

1. Backend health check: http://localhost:8001/docs
2. Frontend app: http://localhost:5178
3. CORS should allow requests from frontend to backend

## Notes
- The backend is now configured to accept CORS requests from http://localhost:5178
- All frontend API calls now target http://localhost:8001
- Environment files (.env, frontend/.env) are git-ignored for security
- Use .env.example files as templates for configuration
