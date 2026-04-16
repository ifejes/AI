#!/bin/bash

# Cisco Catalyst Center IP Pool Reservation - Bash Script
# Linux/Mac-hez való futtatás

echo ""
echo "======================================================================"
echo "Cisco Catalyst Center IP Pool Reservation Script"
echo "======================================================================"
echo ""

# Python verzió ellenőrzése
if ! command -v python3 &> /dev/null; then
    echo "[✗] Hiba: Python3 nincs telepítve!"
    echo ""
    echo "Kérlek telepítsd a Python 3.6+ verziót:"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo "  macOS: brew install python3"
    echo ""
    exit 1
fi

echo "[✓] Python verzió:"
python3 --version
echo ""

# Szükséges könyvtárak ellenőrzése
echo "[*] Szükséges könyvtárak ellenőrzése..."
python3 -c "import requests" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "[!] A 'requests' könyvtár nincs telepítve."
    echo ""
    echo "[*] Telepítés indul..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        pip3 install requests urllib3
    fi
    
    if [ $? -ne 0 ]; then
        echo "[✗] Hiba a könyvtárak telepítésénél!"
        exit 1
    fi
fi

echo "[✓] Szükséges könyvtárak elérhetők."
echo ""

# Script futtatása
echo "[*] Script indítása..."
echo ""

python3 catalyst_center_ip_pool_reservation.py

# Exit status
EXIT_CODE=$?

echo ""

if [ $EXIT_CODE -ne 0 ]; then
    echo "[✗] A script hibával fejeződött be (Exit code: $EXIT_CODE)"
    exit $EXIT_CODE
fi

echo "[✓] Script sikeresen befejeződött!"
exit 0
