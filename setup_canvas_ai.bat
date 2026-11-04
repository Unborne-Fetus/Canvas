@echo off
setlocal
cd /d "%~dp0"
echo.
echo Installing Canvas AI Studio on this computer.
echo Model weights and user sprite references remain on this computer.
echo Python 3.11 x64 is needed.
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher missing. Install Python 3.11 and retry.
  pause
  exit /b 1
)
if not exist ".venv-ai\Scripts\python.exe" (
  py -3.11 -m venv ".venv-ai"
  if errorlevel 1 goto fail
)
set "PY=%CD%\.venv-ai\Scripts\python.exe"
"%PY%" -m pip install --upgrade pip
if errorlevel 1 goto fail
where nvidia-smi >nul 2>nul
if errorlevel 1 goto cpu
nvidia-smi >nul 2>nul
if errorlevel 1 goto cpu
echo NVIDIA GPU found. Installing Windows CUDA PyTorch...
"%PY%" -m pip install torch --index-url https://download.pytorch.org/whl/cu126
if errorlevel 1 goto fail
goto other
:cpu
echo No supported NVIDIA GPU found. Installing CPU PyTorch.
echo CPU generation is experimental and can require substantial RAM.
"%PY%" -m pip install torch --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto fail
:other
"%PY%" -m pip install -r "ai\requirements-local.txt"
if errorlevel 1 goto fail
"%PY%" -c "import torch,diffusers,PIL; print('Torch',torch.__version__,'CUDA',torch.cuda.is_available(),'Diffusers',diffusers.__version__)"
if errorlevel 1 goto fail
echo.
echo Setup finished. Run launch_canvas_ai.bat.
exit /b 0
:fail
echo Installation failed. See error above and check Python, network and device compatibility.
pause
exit /b 1
