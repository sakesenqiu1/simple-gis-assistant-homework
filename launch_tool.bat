@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title GIS Tool

set "TOKEN="
if not "%~1"=="" set "TOKEN=%~1"
if not defined TOKEN if exist ".launcher.key" set /p TOKEN=<.launcher.key
if defined TOKEN set "TOKEN=!TOKEN: =!"
if not defined TOKEN (
  echo [ERROR] Please start with launcher.exe only. Do not double-click launch_tool.bat.
  echo.
  pause
  exit /b 1
)

set "PY="
if exist "python_path.txt" set /p PY=<python_path.txt
if defined PY set "PY=!PY: =!"
if defined PY if not exist "!PY!" set "PY="
if defined PY (
  "!PY!" "%~dp0verify_pro_python.py" "!PY!" >nul 2>&1
  if errorlevel 1 (
    echo !PY! | findstr /i "arcgispro-py3" >nul
    if errorlevel 1 (set "PY=") else echo [WARN] arcpy pre-check failed, trying launch anyway...
  )
)
if not defined PY (
  set "RUNNER="
  for %%P in (
    "D:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
    "%ProgramFiles%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
    "%ProgramFiles(x86)%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
  ) do if exist %%~P if not defined RUNNER set "RUNNER=%%~P"
  if defined RUNNER (
    for /f "usebackq delims=" %%i in (`"!RUNNER!" "%~dp0detect_pro_python.py" 2^>nul`) do set "PY=%%i"
  )
)
if not defined PY (
  for %%P in (
    "D:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
    "%ProgramFiles%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
    "%ProgramFiles(x86)%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
  ) do if exist %%~P if not defined PY (
    "%%~P" "%~dp0verify_pro_python.py" "%%~P" >nul 2>&1
    if not errorlevel 1 set "PY=%%~P"
  )
)
if not defined PY (
  echo [ERROR] Cannot find Pro Python path.
  echo Pro may be installed - run configure_path.bat and pick arcgispro-py3\python.exe
  echo.
  pause
  exit /b 1
)

set "DEPS=%~dp0pydeps"
rem pydeps is configured in bootstrap.py (do not set PYTHONPATH)

echo Starting GIS tool...
"!PY!" "%~dp0bootstrap.py" --token=!TOKEN!
set "ERR=!ERRORLEVEL!"
if not "!ERR!"=="0" (
  echo.
  echo [ERROR] GIS tool failed to start. Exit code=!ERR!
  echo Try: install_deps.bat, configure_path.bat, or read launcher.log
  echo.
  pause
  exit /b !ERR!
)
exit /b 0
