@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo ================================================
echo   AI 2D Animation Studio - first-time setup
echo ================================================

where python >nul 2>nul
if errorlevel 1 (echo ERROR: Python 3.12 is required & pause & exit /b 1)
where npm >nul 2>nul
if errorlevel 1 (echo ERROR: Node.js 22 and npm are required & pause & exit /b 1)

python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)"
if errorlevel 1 (echo ERROR: Python 3.12.x required. Check python --version & pause & exit /b 1)
node -e "process.exit(parseInt(process.versions.node,10)===22?0:1)"
if errorlevel 1 (echo ERROR: Node.js 22.x required. Check node --version & pause & exit /b 1)

if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto error
)
set "PYTHON=%CD%\.venv\Scripts\python.exe"
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto error
"%PYTHON%" -m pip install -e ".[rig,test]"
if errorlevel 1 goto error

call npm --prefix frontend install --no-audit --no-fund
if errorlevel 1 goto error
call npm --prefix frontend run build
if errorlevel 1 goto error
call npm --prefix runtime install --no-audit --no-fund
if errorlevel 1 goto error
pushd runtime
call npx playwright install chromium
set "INSTALL_RESULT=%ERRORLEVEL%"
popd
if not "%INSTALL_RESULT%"=="0" goto error

if not exist vendor\genielabs\scripts\split_character.py (
  echo Downloading pinned Genielabs open-source builder scripts ...
  "%PYTHON%" -c "from pathlib import Path; import urllib.request; sha='702b71689cac826efee942ee4564fef9560d6ef8'; dst=Path('vendor/genielabs/scripts'); dst.mkdir(parents=True,exist_ok=True); [(urllib.request.urlretrieve('https://raw.githubusercontent.com/GenielabsOpenSource/spine-animation-ai/'+sha+'/scripts/'+n, str(dst/n))) for n in ('split_character.py','position_parts.py','build_spine_json.py','make_atlas.py')]"
  if errorlevel 1 goto error
)
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo WARNING: FFmpeg not on PATH. Install FFmpeg and ffprobe before rendering.
) else (
  where ffprobe >nul 2>nul
  if errorlevel 1 echo WARNING: ffprobe not on PATH.
)
echo.
echo Setup complete with isolated local .venv. Start with start_studio.bat.
pause
exit /b 0
:error
echo Setup failed. Read the error above and retry setup_studio.bat.
pause
exit /b 1
