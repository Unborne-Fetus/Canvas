@echo off
setlocal
set "CANVAS_DIR=%~dp0"
set "SOURCE=%~1"
if not defined SOURCE set "SOURCE=C:\ROM Hacks\Pokemon Brisk Emerald"
echo.
echo Canvas local Pokemon + Trainer reference library
echo Source: %SOURCE%
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 is required. Install Python and try again.
  pause
  exit /b 1
)
python "%CANVAS_DIR%ai\local_reference_library.py" scan --source "%SOURCE%"
if errorlevel 1 (
  echo.
  echo Import failed. Check the source folder above.
  pause
  exit /b 1
)
echo.
echo Open: http://127.0.0.1:8765
start "" "http://127.0.0.1:8765"
python "%CANVAS_DIR%ai\local_reference_library.py" serve --site "%CANVAS_DIR%" --port 8765
if errorlevel 1 pause
endlocal
