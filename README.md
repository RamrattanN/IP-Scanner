# Network Analysis Tool

A simple local network scanner with a FastAPI backend and a minimal HTML front end.  It stores scan history locally, and lets you view device details with service flags.

## Features
- Scan the current subnet or a custom range.  
- Show only discovered devices.  
- Device names via UPnP friendly name, NetBIOS, and reverse DNS.  
- Flags as colored letter badges: G for Gateway, W for Website, U for UPnP, B for Bonjour, P for Pingable, 6 for IPv6.  
- Click a history row to expand details, click it again to collapse.  
- Export results to CSV.  
- One click launcher opens your browser automatically.

## Quick start
```powershell
cd "C:\Users\niles\Dropbox\GitHub\IP Scanner"
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\scripts\run_and_open.py
```
Open http://127.0.0.1:8000  if it is not already open.

## How it finds names
- UPnP device description friendly name when available.  
- NetBIOS Node Status over UDP.  
- Windows nbtstat call as a fallback.  
- Reverse DNS lookup.

If NetBIOS names are not appearing, try allowing File and Printer Sharing on the device or confirm with:
```powershell
nbtstat -A <ip>
```

## Where data is stored
History JSON is saved under your Documents folder in `Network Scanner\history.json`.  Delete it or use Clear History in the UI to reset.

## Development notes
- Backend: FastAPI and Uvicorn.  
- Front end: static HTML, CSS, and vanilla JavaScript.  
- Source layout uses `src`.  Run Uvicorn with `--app-dir src`.
