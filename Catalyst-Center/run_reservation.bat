@echo off
REM Cisco Catalyst Center IP Pool Reservation - Windows Batch Fájl
REM Ez a fájl könnyebbé teszi a script futtatását Windows-on

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo Cisco Catalyst Center IP Pool Reservation Script
echo ======================================================================
echo.

REM Ellenőrizd, hogy Python telepítve van-e
python --version >/dev/null 2>&1
if %errorlevel% neq 0 (
    echo [x] Hiba: Python nincs telepítve!
    echo.
    echo Kérlek telepítsd a Python 3.6+ verziót a Python.org-ról
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python verzió:
python --version
echo.

REM Ellenőrizd a szükséges könyvtárakat
echo [*] Szükséges könyvtárak ellenőrzése...
python -c "import requests" >/dev/null 2>&1
if %errorlevel% neq 0 (
    echo [!] A 'requests' könyvtár nincs telepítve.
    echo.
    echo [*] Telepítés indul...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [x] Hiba a könyvtárak telepítésénél!
        pause
        exit /b 1
    )
)

echo [OK] Szükséges könyvtárak elérhetők.
echo.

REM Script futtatása
echo [*] Script indítása...
echo.
python catalyst_center_ip_pool_reservation.py

REM Pausolj, ha hiba van
if %errorlevel% neq 0 (
    echo.
    echo [x] A script hibával fejeződött be!
    pause
    exit /b %errorlevel%
)

echo.
pause
