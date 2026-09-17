# SmartBio Documentation

Refer to the main [Root Project README](../README.md) for full technical documentation, setup steps, and API specifications.

### Quick Start Reference

#### Backend
```bash
cd backend
backend\venv\Scripts\Activate.ps1
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm run dev
```

#### Interactive API Docs
Visit: `http://127.0.0.1:8000/docs`
