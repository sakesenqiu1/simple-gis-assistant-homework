@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Configure ArcGIS Pro Python

set "HELPER="
where py >nul 2>&1 && set "HELPER=py -3"
if not defined HELPER where python >nul 2>&1 && set "HELPER=python"

if defined HELPER (
  for /f "usebackq delims=" %%i in (`!HELPER! "%~dp0detect_pro_python.py" 2^>nul`) do (
    echo %%i> "%~dp0python_path.txt"
    echo [OK] Auto detected: %%i
    echo Next: install_deps.bat, then launcher.exe
    goto DONE
  )
)

set "RUNNER="
for %%P in (
  "%ProgramFiles%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
  "%ProgramFiles(x86)%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
  "D:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
) do if exist %%~P if not defined RUNNER set "RUNNER=%%~P"
if defined RUNNER (
  for /f "usebackq delims=" %%i in (`"!RUNNER!" "%~dp0detect_pro_python.py" 2^>nul`) do (
    echo %%i> "%~dp0python_path.txt"
    echo [OK] Saved: %%i
    echo Next: install_deps.bat, then launcher.exe
    goto DONE
  )
  echo !RUNNER!> "%~dp0python_path.txt"
  echo [OK] Found Pro Python: !RUNNER!
  echo Next: install_deps.bat, then launcher.exe
  goto DONE
)

echo [INFO] Pro may use a custom install folder.
echo Please pick arcgispro-py3\python.exe in the dialog.
echo.
if defined HELPER (
  "!HELPER!" "%~dp0configure_path.py"
  goto VERIFY
)
for %%P in (
  "%ProgramFiles%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
  "%ProgramFiles(x86)%\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
  "D:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
) do if exist %%~P (
  "%%~P" "%~dp0configure_path.py"
  goto VERIFY
)
echo [ERROR] Cannot run configure_path.py. Need any Python 3 on PATH.
goto DONE

:VERIFY
if exist "%~dp0python_path.txt" (
  echo [OK] python_path.txt saved.
  echo Next: install_deps.bat, then launcher.exe
) else (
  echo [WARN] No path saved. Pick Pro arcgispro-py3\python.exe manually.
)

:DONE
echo.
echo ========================================
echo Press any key to close this window...
echo ========================================
pause >nul
exit /b 0
