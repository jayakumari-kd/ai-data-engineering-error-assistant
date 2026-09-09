@echo off
title AI Data Engineering Assistant

echo.
echo ==========================================
echo   AI Data Engineering Assistant
echo ==========================================
echo.

echo Starting Docker container...
docker start jaya-error-library

echo.
echo Starting Streamlit...

docker exec -d jaya-error-library bash -c "cd '/home/jovyan/work/Data Engineering Error Library' && nohup streamlit run app.py --server.address 0.0.0.0 --server.port 8501 > /tmp/streamlit.log 2>&1"

echo.
echo Waiting for Streamlit...
timeout /t 5 /nobreak >nul

echo Opening browser...
start "" "http://localhost:8501"

echo.
echo ==========================================
echo   AI Assistant started
echo ==========================================
echo.
echo   http://localhost:8501
echo.