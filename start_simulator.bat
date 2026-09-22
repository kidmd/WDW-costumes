@echo off
title MSEP Costume LED Simulator
echo ========================================================
echo   Main Street Electrical Parade - LED Simulator
echo ========================================================
echo.
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed on this computer!
        echo Please download and install Python from https://www.python.org
        echo (IMPORTANT: Check the box "Add python.exe to PATH" during install)
        echo.
        pause
        exit /b 1
    ) else (
        py simulator.py
        pause
        exit /b 0
    )
)

python simulator.py
if %errorlevel% neq 0 (
    echo.
    pause
)
