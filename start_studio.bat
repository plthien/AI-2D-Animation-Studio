@echo off
setlocal
cd /d "%~dp0"
if not exist frontend\dist\index.html (
  echo Run setup_studio.bat first to install dependencies and build the UI.
  pause
  exit /b 1
)
echo AI 2D Animation Studio starting on http://127.0.0.1:8000
echo Open that address in your browser if it does not appear automatically.
start "" "http://127.0.0.1:8000"
python -m studio
if errorlevel 1 (echo Server stopped with an error. & pause)
