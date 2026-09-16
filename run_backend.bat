@echo off
echo Starting Noor's Attire Backend...
cd /d "%~dp0"
if exist ".\venv\Scripts\python.exe" (
    ".\venv\Scripts\python.exe" main.py
) else (
    python main.py
)
pause
