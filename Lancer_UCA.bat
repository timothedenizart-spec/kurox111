@echo off
REM Double-click launcher for Windows. It opens the local UCA interface in a browser.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 Lancer_UCA.py %*
) else (
  python Lancer_UCA.py %*
)
