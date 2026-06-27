@echo off
echo ==========================================
echo  SITAB - Automatic Timetable Generator
echo  Backend: FastAPI + Supabase (PostgreSQL)
echo ==========================================
echo.
echo Pastikan file .env sudah diisi dengan DATABASE_URL Supabase Anda!
echo.
echo Server berjalan di: http://localhost:8002
echo Tekan Ctrl+C untuk berhenti.
echo.
set OPENBLAS_NUM_THREADS=1
py -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
pause
