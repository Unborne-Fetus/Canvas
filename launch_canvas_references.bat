@echo off
setlocal
set "CANVAS_DIR=%~dp0"
set "SOURCE=%~1"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 and Pillow are required for the local reference browser.
  echo Or launch the complete AI version with launch_canvas_ai.bat.
  pause
  exit /b 1
)
if not "%SOURCE%"=="" (
  python "%CANVAS_DIR%ai\local_reference_library.py" scan --source "%SOURCE%"
  if errorlevel 1 (
    echo Cannot index that source. Try another folder.
    pause
    exit /b 1
  )
)
echo Canvas reference browser on this computer: http://127.0.0.1:8765
echo You can connect your own Expansion folder using References in the browser.
start "" "http://127.0.0.1:8765"
python "%CANVAS_DIR%ai\local_reference_library.py" serve --site "%CANVAS_DIR%" --port 8765
if errorlevel 1 pause
endlocal
