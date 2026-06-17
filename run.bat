@echo off
echo ==========================================
echo  SITAB - Automatic Timetable Generator
echo  Backend: FastAPI + Supabase (PostgreSQL)
echo ==========================================
echo.
echo Pastikan file .env sudah diisi dengan DATABASE_URL Supabase Anda!
echo.
echo Server berjalan di: http://localhost:8000
echo Tekan Ctrl+C untuk berhenti.
echo.
set OPENBLAS_NUM_THREADS=1
py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
