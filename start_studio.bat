@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Local Python environment missing. Run setup_studio.bat first.
  pause
  exit /b 1
)
if not exist "frontend\dist\index.html" (
  echo React UI build missing. Run setup_studio.bat first.
  pause
  exit /b 1
)
where ffmpeg >nul 2>nul
if errorlevel 1 echo WARNING: FFmpeg missing. Preview works, but MP4 render will fail.
where ffprobe >nul 2>nul
if errorlevel 1 echo WARNING: ffprobe missing. MP4 verification will fail.
echo AI 2D Animation Studio starting on http://127.0.0.1:8000
echo Open that address manually if it does not appear automatically.
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m studio
if errorlevel 1 (echo Server stopped with an error. & pause)
