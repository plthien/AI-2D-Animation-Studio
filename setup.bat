@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=py -3.12"
%PYTHON% --version >nul 2>&1
if errorlevel 1 set "PYTHON=python"
%PYTHON% -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)"
if errorlevel 1 (
  echo Python 3.12 is required. Install it or select it with the py launcher.
  exit /b 1
)
node --version | findstr /r "^v22\." >nul
if errorlevel 1 (
  echo Node.js 22 is required.
  exit /b 1
)
call npm.cmd --version >nul 2>&1
if errorlevel 1 (
  echo npm is required.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" %PYTHON% -m venv ".venv"
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
call npm.cmd ci
if errorlevel 1 exit /b 1
call npm.cmd run build
if errorlevel 1 exit /b 1
if not exist ".env" copy /y ".env.example" ".env" >nul
where ffmpeg.exe >nul 2>&1
if errorlevel 1 echo Optional readiness notice: FFmpeg was not found on PATH. Final video export is not part of P0.
echo Setup complete. Run start.bat.
exit /b 0
