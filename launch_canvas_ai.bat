@echo off
setlocal
cd /d "%~dp0"
set "PY=%CD%\.venv-ai\Scripts\python.exe"
if not exist "%PY%" (
  echo Canvas AI needs a one-time local installation on THIS computer.
  call "%CD%\setup_canvas_ai.bat"
  if errorlevel 1 exit /b 1
)
echo.
echo Launching Canvas AI Studio on this device, not a remote PC.
if not "%~1"=="" (
  "%PY%" "%CD%\run_canvas_ai.py" --source "%~1"
) else (
  "%PY%" "%CD%\run_canvas_ai.py"
)
if errorlevel 1 (
  echo Could not start Canvas. Check whether port 8765 is already in use.
  pause
  exit /b 1
)
endlocal
