@echo off
REM ============================================
REM  Scraper Platform v4.8 - Windows Bootstrap
REM  - Creates/uses .venv
REM  - Installs requirements with trusted-host
REM  - Sets env vars for AlfaBeta
REM  - Runs AlfaBeta pipeline
REM ============================================

SETLOCAL ENABLEDELAYEDEXPANSION

REM Go to the folder where this BAT file lives
cd /d "%~dp0"

echo.
echo [INFO] Working directory: %CD%
echo.

REM --------------------------------------------
REM 1) Ensure virtual environment exists
REM --------------------------------------------
IF NOT EXIST ".venv" (
    echo [INFO] .venv not found. Creating virtual environment...
    python -m venv .venv
) ELSE (
    echo [INFO] Using existing .venv
)

REM --------------------------------------------
REM 2) Install / upgrade pip and requirements
REM    (bypass SSL issues via trusted-host)
REM --------------------------------------------
echo.
echo [INFO] Upgrading pip inside venv...
".venv\Scripts\python.exe" -m pip install --upgrade pip ^
    --trusted-host pypi.org ^
    --trusted-host files.pythonhosted.org

echo.
echo [INFO] Installing requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt ^
    --trusted-host pypi.org ^
    --trusted-host files.pythonhosted.org

REM --------------------------------------------
REM 3) Set environment variables for this run
REM    EDIT THESE for real credentials.
REM --------------------------------------------
echo.
echo [INFO] Setting environment for AlfaBeta (session only)...

REM Fake browser so you can run without Chrome at first
set SCRAPER_PLATFORM_FAKE_BROWSER=1

REM TODO: replace these with real site creds
set ALFABETA_USER_1=user
set ALFABETA_PASS_1=pass

REM If you have proxies, uncomment and fill:
REM set ALFABETA_PROXIES=ip1:port,ip2:port

REM --------------------------------------------
REM 4) Run AlfaBeta pipeline
REM --------------------------------------------
echo.
echo [INFO] Running AlfaBeta pipeline...
".venv\Scripts\python.exe" -m src.scrapers.alfabeta.pipeline

echo.
echo [INFO] Done. Check output\alfabeta\daily\ for CSV.
echo.
pause
ENDLOCAL
