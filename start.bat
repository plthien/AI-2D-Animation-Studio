@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run setup.bat first.
  exit /b 1
)
if not exist ".env" copy /y ".env.example" ".env" >nul
if not exist "dist\index.html" (
  call npm.cmd run build
  if errorlevel 1 exit /b 1
)
start "AI 2D Studio" /D "%~dp0" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000"
