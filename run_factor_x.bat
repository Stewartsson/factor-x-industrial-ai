@echo off
color 0A
echo ===================================================
echo     FACTOR-X : INDUSTRIAL AI OPTIMIZATION
echo ===================================================
echo.

echo [1/4] Activating Virtual Environment...
call venv\Scripts\activate

echo [2/4] Running Factory Digital Twin Simulation...
cd scripts
python simulate_factory_data.py
cd ..
echo.

echo [3/4] Training AI Anomaly Detection (Isolation Forest)...
cd scripts
python train_anomaly_detector.py
cd ..
echo.

echo [4/4] Starting FastAPI Live Server...
echo (Press CTRL+C in this window to stop the server when done)
echo.

:: Start the API server in the background
start /B uvicorn api.main:app --reload > nul 2>&1

:: Wait 3 seconds for the server to spin up
timeout /t 3 /nobreak > nul

:: Open the Dashboard in the default browser
echo Opening FACTOR-X Dashboard in your browser...
start dashboard\index.html

echo.
echo FACTOR-X System is Live!
echo API running at http://127.0.0.1:8000
echo.
:: Keep the window open to hold the API server
cmd /k
