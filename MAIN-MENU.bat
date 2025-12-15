@echo off
title Gremlin Launcher
mode con: cols=70 lines=20
setlocal EnableDelayedExpansion

:uvcheck
@echo off

where uv >nul 2>nul
if errorlevel 1 goto uvnotinstalled

echo UV is installed.
timeout /t 1 >nul
goto :loadwarn

:uvnotinstalled
echo UV is NOT installed.
timeout /t 5 >nul
cls
echo installing UV...
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0uvInstall.ps1" %*
cls
echo UV finished installing!
echo please wait...
timeout /t 3 >nul
goto :loadwarn


:loadwarn
cls
echo IF UV HAS NOT MADE A VENV YET, PLEASE WAIT, IT MAY SEEM LIKE IT ISN'T DOING ANYTHING FOR A WHILE
echo BUT IT IS EXTREMELY LIKELY IT IS CREATING AN ENVIRONMENT TO RUN.
echo.
echo the script will load when ready.
echo.
pause
cls
@echo off
type mambo.txt 
echo.
echo loading...
timeout /t 3 >nul
goto menu

:menu
cls
echo.
@echo off
type art.txt
echo.
echo   [1] Start Main Script (starts with default gremlin)
echo   [2] Select Gremlin
echo   [3] End Gremlin Task
echo   [4] Help
echo.
echo   [Conf] Edit The Config Options
echo.
echo   [Q] Quit
echo ======================================================
set /p choice=Select an option: 

if /i "%choice%"=="1" goto start_main
if /i "%choice%"=="2" goto select_gremlin
if /i "%choice%"=="3" goto kill
if /i "%choice%"=="4" goto help
if /i "%choice%"=="Q" goto 
if /i "%choice%"=="conf" goto confedit

echo.
echo Invalid option. Please try again.
timeout /t 2 >nul
goto menu

:confedit
cls
echo.
echo =NOW EDITING CONFIG=
echo.
timeout /t 1 >nul
@echo off
setlocal EnableDelayedExpansion
set /p AvailList=List available characters(Y/N)?:
if /i "%AvailList%"=="Y" (
    dir /b %~d0spritesheet
)

echo.

set /p CHAR=Default character: 

set /p SYSTRAY=Set to sys tray? (Y/N): 
if /I "%SYSTRAY%"=="Y" (
    set SYSTRAY_VAL=true
) else (
    set SYSTRAY_VAL=false
)

set /p EMOTE_ENABLE=Enable emote key? (Y/N): 
if /I "%EMOTE_ENABLE%"=="Y" (
    set EMOTE_ENABLED=true
    set /p EMOTE_KEY=Set emote key:
) else (
    set EMOTE_ENABLED=false
    set EMOTE_KEY=P
)

set /p VOLUME=Volume (0.1 - 1.0): 

(
echo {
echo     "StartingChar": "%CHAR%",
echo     "Systray": %SYSTRAY_VAL%,
echo     "FollowRadius": 150.0,
echo     "EmoteKeyEnabled": %EMOTE_ENABLED%,
echo     "EmoteKey": "%EMOTE_KEY%",
echo     "Volume": %VOLUME%
echo }
) > config.json

echo.
echo config.json written successfully!
goto return_menu

:start_main
cls
echo Starting Main Script...
echo.
call "%~dp0ex.vbs"
goto exit

:select_gremlin
cls
echo Selecting Gremlin...
echo.
call "%~dp0gpr.vbs"
timeout /t 2 >nul
goto menu

:return_menu
echo.
echo ------------------------------------------------------
echo Press any key to return to menu...
pause >nul
goto menu

:help
cls
echo Option one will simply run the default config for the script 
echo    (Makitanetannhauser / Mambo)
echo    You can edit this by going to:
echo %~dp0\config.json
echo.
echo Option two lets you chose between hikari, mambo, and rice-shower
echo    (will open a powershell menu to select which gremlin you want.)
echo.
echo Option three will kill the gremlin :c :
echo    (must be in main screen, and type 3.)
echo.
echo Option 4 displays this help screen.
goto return_menu

:kill
cls
echo #############################################################
echo.
echo.
echo                WARNING : THIS WILL KILL PYTHON
echo                   DO YOU WANT TO CONTINUE?
echo.
echo.
echo #############################################################
echo.
echo.
echo.
set /p choice=Select an option(Y/n): 

if /i "%choice%"=="Y" goto killpy
if /i "%choice%"=="n" goto menu

:killpy
cls
echo YOU MURDERER
echo YOU KILLED HER
echo HOW COULD YOU???
@echo off 
taskkill /f /im Python.exe
pause
goto menu

:exit
exit /b