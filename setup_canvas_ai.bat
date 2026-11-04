@echo off
setlocal
cd /d "%~dp0"
echo Canvas AI Studio - LOCAL GPU dependency installer
echo Uses Python 3.11 and installs packages in %CD%\.venv-ai
echo It will download libraries; model weights download on first Generate.
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher is required. Install Python 3.11 x64 first.
  pause
  exit /b 1
)
if not exist ".venv-ai\Scripts\python.exe" (
  py -3.11 -m venv .venv-ai
  if errorlevel 1 (
    echo Python 3.11 is required. Try: py -0p
    pause
    exit /b 1
  )
)
set "PY=%CD%\.venv-ai\Scripts\python.exe"
"%PY%" -m pip install --upgrade pip
if errorlevel 1 goto fail
echo Installing NVIDIA CUDA build of PyTorch...
"%PY%" -m pip install torch --index-url https://download.pytorch.org/whl/cu126
if errorlevel 1 goto fail
echo Installing local image generation libraries...
"%PY%" -m pip install -r ai\requirements-local.txt
if errorlevel 1 goto fail
"%PY%" -c "import torch,diffusers,PIL; print('PyTorch',torch.__version__,'CUDA',torch.cuda.is_available()); print('Diffusers',diffusers.__version__)"
if errorlevel 1 goto fail
echo.
echo Setup complete. Start using launch_canvas_ai.bat
pause
exit /b 0
:fail
echo Setup failed. Check the messages above and GPU driver compatibility.
pause
exit /b 1
