@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run install_windows.cmd or restore_windows.cmd first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" scripts\run_windows.py %*
set "result=%errorlevel%"
if not "%result%"=="0" echo Failed. Review the output above and README.md.
pause
exit /b %result%
