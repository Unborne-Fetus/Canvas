@echo off
setlocal
set "CANVAS_DIR=%~dp0"
set "SOURCE=%~1"
if not defined SOURCE set "SOURCE=C:\ROM Hacks\Pokemon Brisk Emerald"
set "PY=%CANVAS_DIR%.venv-ai\Scripts\python.exe"
if not exist "%PY%" (
  echo The local AI environment is not set up.
  echo Run setup_canvas_ai.bat once to install the GPU dependencies.
  pause
  exit /b 1
)
echo Canvas AI Studio - PC-only image generation
echo Source art stays local: %SOURCE%
"%PY%" "%CANVAS_DIR%ai\local_reference_library.py" scan --source "%SOURCE%"
if errorlevel 1 (
  echo Cannot read the Pokémon and trainer reference library.
  pause
  exit /b 1
)
echo.
echo Opening Canvas on http://127.0.0.1:8765
echo First Generate will download the chosen model into the local Hugging Face cache.
start "" "http://127.0.0.1:8765"
"%PY%" "%CANVAS_DIR%ai\local_reference_library.py" serve --site "%CANVAS_DIR%" --port 8765
if errorlevel 1 pause
endlocal
