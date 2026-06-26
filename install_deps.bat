@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Install Python Dependencies

set "PY="
if exist "python_path.txt" set /p PY=<python_path.txt
if not defined PY (
  for %%P in (
    "%ProgramFiles%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
    "%ProgramFiles(x86)%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
    "D:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
  ) do if exist %%~P set "PY=%%~P"
)

if not defined PY (
  echo [ERROR] Run configure_path.bat first.
  goto DONE
)

set "DEPS=%~dp0pydeps"
if not exist "!DEPS!" mkdir "!DEPS!"

set "HTTP_PROXY="
set "HTTPS_PROXY="
set "http_proxy="
set "https_proxy="
set "ALL_PROXY="
set "PIP_NO_CACHE_DIR=1"

echo Installing into pydeps folder (no admin needed) ...
echo Using Python: !PY!
"!PY!" "%~dp0install_pydeps.py" "!DEPS!"
set "PIP_ERR=!ERRORLEVEL!"
if not "!PIP_ERR!"=="0" (
  echo [ERROR] Dependency install or verify failed.
  goto DONE
)
echo [OK] Dependencies ready. Double-click launcher.exe

:DONE
echo.
echo ========================================
echo Press any key to close this window...
echo ========================================
pause >nul
exit /b 0
