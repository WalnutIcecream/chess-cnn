@echo off
setlocal
rem moveexp - one-command demo launcher.
rem Double-click this file (no typing needed) or run it from a terminal.
rem It runs the live showcase, then opens the demo pages in the browser.
rem Set MOVEXP_NO_BROWSER=1 to skip opening the browser (used for smoke tests).

cd /d "%~dp0"

set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo === moveexp live demo ===
"%PY%" "%~dp0scripts\demo_run.py"
if errorlevel 1 (
  echo.
  echo Demo failed - see the output above.
  pause
  exit /b 1
)

if /i "%MOVEXP_NO_BROWSER%"=="1" (
  echo Browser launch skipped.
) else (
  echo Opening demo\index.html in your browser...
  start "" "%~dp0demo\index.html"
)

echo.
echo Demo pages : demo\index.html   demo\process.html   demo\gallery.html
echo Live output: demo\live\showcase.json   demo\live\showcase.png
pause
exit /b 0
