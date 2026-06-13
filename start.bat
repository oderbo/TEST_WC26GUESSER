@echo off
cd /d "%~dp0"
echo Starte lokalen Firebase-Server auf Port 8000...
start "" "http://localhost:8000/index.html"
python -m http.server 8000