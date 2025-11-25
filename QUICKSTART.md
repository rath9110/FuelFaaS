# FuelGuard AI - Quick Start Guide

## Starting the Application

### Backend Server

```powershell
cd c:\Users\46700\PycharmProjects\FuelFaaS
py -m uvicorn backend.main:app --reload --port 8001
```

**Access:**
- API Docs: http://localhost:8001/api/docs
- Health Check: http://localhost:8001/health

### Frontend Dashboard

Open a new terminal:

```powershell
cd c:\Users\46700\PycharmProjects\FuelFaaS\frontend
npm install  # Only needed first time
npm run dev
```

**Access:**
- Dashboard: http://localhost:3000

## Sample Credentials

- Username: `admin`
- Password: `admin123`

## Troubleshooting

### Backend won't start

Make sure you're in the project root:
```powershell
cd c:\Users\46700\PycharmProjects\FuelFaaS
```

### Database errors

Reinitialize the database:
```powershell
py init_db.py
py seed_database.py
```

### Port already in use

Change the port:
```powershell
py -m uvicorn backend.main:app --reload --port 8002
```

Then update `NEXT_PUBLIC_API_URL` in frontend to `http://localhost:8002`

## Sample Data Included

- 3 Vehicles (V001, V002, V003)
- 2 Projects (Stockholm, Gothenburg)
- 2 Workers (Erik, Anna)
- 6 Transactions (including fraud cases)
- 4 Detected anomalies
