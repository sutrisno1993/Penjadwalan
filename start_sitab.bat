@echo off
cd /d "D:\Jadwal"
echo ===================================================
echo  Memulai Aplikasi Penjadwalan SITAB...
echo ===================================================
echo.
echo 1. Menjalankan Server Backend...
start "SITAB Backend Server" python -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
echo.
echo 2. Menunggu server siap secara dinamis...

:port_check
netstat -ano | findstr "LISTENING" | findstr ":8002" >nul
if errorlevel 1 (
    choice /d y /t 1 >nul 2>&1
    goto port_check
)

echo.
echo 3. Server siap! Membuka browser pada http://localhost:8002...
start http://localhost:8002
echo.
echo SITAB berhasil diluncurkan! Jendela log backend tetap berjalan.
exit
