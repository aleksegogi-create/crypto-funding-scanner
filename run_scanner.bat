@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

title Crypto Funding Scanner

echo ============================================================
echo   CRYPTO FUNDING SCANNER
echo ============================================================
echo.

set "MIN_MAJOR=3"
set "MIN_MINOR=10"
set "PY_CMD="
set "PY_VERSION="

goto FIND_PYTHON

:FIND_PYTHON
set "PY_CMD="
set "PY_VERSION="

REM First try normal python command.
python --version >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=python"
    goto CHECK_VERSION
)

REM Then try explicit Python Launcher versions.
for %%V in (3.13 3.12 3.11 3.10) do (
    py -%%V --version >nul 2>nul
    if not errorlevel 1 (
        set "PY_CMD=py -%%V"
        goto CHECK_VERSION
    )
)

goto NO_WORKING_PYTHON

:CHECK_VERSION
for /f "tokens=2 delims= " %%A in ('!PY_CMD! --version 2^>^&1') do (
    set "PY_VERSION=%%A"
)

if not defined PY_VERSION (
    goto NO_WORKING_PYTHON
)

for /f "tokens=1,2 delims=." %%A in ("!PY_VERSION!") do (
    set "PY_MAJOR=%%A"
    set "PY_MINOR=%%B"
)

echo [INFO] Python candidate: !PY_CMD!
echo [INFO] Python version:   !PY_VERSION!

if !PY_MAJOR! LSS %MIN_MAJOR% (
    goto OLD_PYTHON
)

if !PY_MAJOR! EQU %MIN_MAJOR% (
    if !PY_MINOR! LSS %MIN_MINOR% (
        goto OLD_PYTHON
    )
)

echo [OK] Suitable Python found.
goto START_PROJECT

:OLD_PYTHON
echo.
echo [WARNING] Python !PY_VERSION! is too old.
echo [INFO] Python %MIN_MAJOR%.%MIN_MINOR%+ is required.
echo [INFO] The launcher will try to install Python 3.12 side-by-side.
goto INSTALL_PYTHON

:NO_WORKING_PYTHON
echo.
echo [WARNING] Working Python 3.10+ was not found.
echo [INFO] The launcher will try to install Python 3.12.
goto INSTALL_PYTHON

:INSTALL_PYTHON
echo.
where winget >nul 2>nul
if errorlevel 1 (
    echo [ERROR] winget was not found on this Windows system.
    echo.
    echo Install Python manually:
    echo https://www.python.org/downloads/
    echo.
    echo During installation enable:
    echo Add python.exe to PATH
    echo.
    pause
    exit /b 1
)

echo [INFO] Installing Python 3.12 via winget...
echo [INFO] This may require confirmation in Windows.
echo.

winget install --id Python.Python.3.12 -e --source winget --scope user --accept-package-agreements --accept-source-agreements

echo.
echo [INFO] Re-checking Python after installation...
echo.
goto FIND_PYTHON

:START_PROJECT
echo.

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" --version >nul 2>nul
    if errorlevel 1 (
        echo [WARNING] Existing venv is broken. Recreating it...
        rmdir /s /q venv
    )
)

if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    !PY_CMD! -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

set "VENV_PY=venv\Scripts\python.exe"

echo.
echo [INFO] Virtual environment Python:
"%VENV_PY%" --version

echo.
echo [INFO] Checking and installing dependencies...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b 1
)

"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        echo.
        echo [INFO] .env not found. Creating .env from .env.example...
        copy ".env.example" ".env" >nul
    )
)

echo.
echo ============================================================
echo Starting Crypto Funding Scanner...
echo Press CTRL+C to stop.
echo ============================================================
echo.

"%VENV_PY%" main.py

echo.
echo ============================================================
echo Scanner stopped.
echo ============================================================
pause
endlocal
