# NPMVector

npm Supply Chain Security Monitoring System

NPMVector monitors npm packages, detects releases, analyzes explainable security signals, and presents relevance and threat information through a React dashboard.

## 1. Problem

npm packages are deeply connected through dependency relationships and installation workflows. A compromised maintainer account, unexpected dependency, install script, ownership change, or unusual release can create supply-chain risk for downstream users. These changes are easy to miss when package updates are reviewed manually.

## 2. Solution

NPMVector continuously checks monitored packages through the npm Registry. It records package and release metadata, calculates an ecosystem relevance score, analyzes release security signals, calculates a separate threat score, and exposes the results through FastAPI and a React dashboard.

Threat scores are investigation signals, not claims that a package is malicious. Relevance answers how important a package is to the ecosystem; threat answers how suspicious the observed release behavior appears.

## 3. Architecture

```mermaid
flowchart TD
    Registry[npm Registry] --> Monitor[Package Monitor]
    Monitor --> Relevance[Relevance Engine]
    Monitor --> Security[Security Analysis]
    Relevance --> Database[(PostgreSQL)]
    Security --> Threat[Threat Score and Signals]
    Threat --> Database
    Database --> API[FastAPI]
    API --> Dashboard[React Dashboard]
```

The pipeline is:

```text
npm Registry
	| 
Monitoring
	| 
Relevance Engine
	| 
Security Analysis
	| 
Threat Score
	| 
PostgreSQL
	| 
FastAPI
	| 
React Dashboard
```

## 4. Technologies

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- APScheduler
- React
- Vite
- Axios
- Recharts

## 5. Features

- npm package monitoring
- Release detection
- Download tracking
- Relevance scoring
- Security signal analysis
- Threat scoring
- Release history
- Dashboard statistics and charts
- Package investigation view
- High-threat release alerts
- Automatic dashboard refresh

## 6. Project Structure

```text
backend/
  app/
    api/
    database/
    models/
    services/
  requirements.txt
frontend/
  src/
  package.json
tests/
docs/
README.md
```

## 7. Installation

### Backend

From the repository root:

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000` and its interactive documentation is at `http://127.0.0.1:8000/docs`.

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The dashboard is available at `http://127.0.0.1:5173`.

## 8. Environment Variables

Copy `backend/.env.example` to `backend/.env` locally. Never commit the local file or expose its password.

```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/npmvector
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

The backend loads these values through `python-dotenv`. For production, set `DATABASE_URL` to the managed PostgreSQL connection string and `CORS_ORIGINS` to the deployed frontend URL. Do not commit either production value.

For the frontend, copy `frontend/.env.example` to `frontend/.env.local` for local development:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Set `VITE_API_URL` to the deployed FastAPI URL in the frontend hosting provider's environment settings.

## 9. API Overview

```text
GET /health
GET /packages/{package_name}
GET /packages/{package_name}/versions
GET /packages/{package_name}/releases
GET /packages/{package_name}/summary
GET /packages/{package_name}/threats
GET /packages/ranking
GET /dashboard/stats
GET /dashboard/releases
GET /threats/high
```

## 10. Testing

Run backend tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Build the frontend:

```powershell
cd frontend
npm run build
```

The test suite covers release detection, relevance scoring, threat scoring, package metadata analysis, dependency comparison, API responses, and failure cases.

## 11. Deployment

A practical production layout is:

```text
React frontend (Vercel)
  |
  v
FastAPI backend (Render or Railway)
  |
  v
Managed PostgreSQL
```

Configure `DATABASE_URL` and `CORS_ORIGINS` on the backend host, and `VITE_API_URL` on the frontend host. Deploy only after the local tests and frontend build pass. Verify `/health`, `/docs`, the dashboard, and a package investigation page after deployment.

## 12. GitHub Safety

Before publishing the repository, confirm that `.env`, `venv/`, `.venv/`, `node_modules/`, and `dist/` are ignored. PostgreSQL credentials must never be committed. Initialize Git and create the first commit only after reviewing the staged file list:

```powershell
git init
git add .
git status
git commit -m "Complete NPMVector MVP"
```
()
