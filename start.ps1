# Launches backend (FastAPI) and frontend (Vite) each in their own window.
$root = $PSScriptRoot

Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$root\backend\run.ps1'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$root\frontend\run.ps1'"

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
