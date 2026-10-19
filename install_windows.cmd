@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Install official Python 3.14 x64 with the Python launcher, then reopen terminal.
  pause
  exit /b 1
)
py -3.14 scripts\setup_windows.py %*
set "result=%errorlevel%"
if not "%result%"=="0" echo Failed. Review the output above and README.md.
pause
exit /b %result%
