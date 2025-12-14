@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Defaults

set USE_UV=1
set USE_VENV=0
set USER_ARGS=

REM Collect args without destroying them

:collect_args
if "%~1"=="" goto parse_done

if "%~1"=="--no-uv" (
    set USE_UV=0
) else if "%~1"=="--system" (
    set USE_VENV=0
) else if "%~1"=="--venv" (
    set USE_VENV=1
) else if "%~1"=="--help" (
    goto help
) else if "%~1"=="-h" (
    goto help
) else (
    set USER_ARGS=!USER_ARGS! "%~1"
)

shift
goto collect_args

:help
echo Usage: %~nx0 [OPTIONS] [CHARACTER]
echo   --no-uv   Use Python directly
echo   --system  Use system Python
echo   --venv    Force venv
exit /b 0

:parse_done

REM cd to script directory

cd /d "%~dp0"

REM Find Python

where python >nul 2>&1 || (
    echo Python not found
    pause
    exit /b 1
)
set PYTHON=python

REM uv 

if "%USE_UV%"=="1" (
    where uv >nul 2>&1
    if not errorlevel 1 (
        uv run python -m src.launcher %USER_ARGS%
        exit /b
    )
)

REM python

if "%USE_VENV%"=="0" (
    start "" %PYTHON% -m src.launcher %USER_ARGS%
    exit /b
)

REM venv

if "%USE_VENV%"=="1" (
    if not exist venv (
        %PYTHON% -m venv venv
    )
    call venv\Scripts\activate.bat
    %PYTHON% -m pip install pyside6
    start "" %PYTHON% -m src.launcher %USER_ARGS%
    exit /b
)

REM venv if PySide6 missing

%PYTHON% -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    if not exist venv (
        %PYTHON% -m venv venv
    )
    call venv\Scripts\activate.bat
    %PYTHON% -m pip install -q pyside6
)

start "" %PYTHON% -m src.launcher %USER_ARGS%
exit /b
