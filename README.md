# Network Analysis Tool

A Windows desktop friendly tool built with Python FastAPI and a lightweight front end.  
Scans the local network and records results to a JSON history file.  Supports quick scan, custom range, and clear history.

## Features
- Home page with history table and actions: Scan, Scan Custom Range, Clear History.
- Live scan results with device flags: G, W, U, B, P, 6, and transient S while pending.
- JSON and CSV export for each scan.
- Rotating logs for troubleshooting.

## Getting started

### Prerequisites
- Python 3.12
- Windows recommended.  Works on other platforms for development.
- Optional: virtual environment

### Setup
```bash
python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run the app
```bash
uvicorn network_scanner.app:app --reload
```

Then open http://127.0.0.1:8000 in your browser.

### Project layout
```
network-analysis-tool/
├─ CHANGELOG.md
├─ LICENSE
├─ README.md
├─ requirements.txt
├─ pyproject.toml
├─ .gitignore
├─ src/
│  └─ network_scanner/
│     ├─ __init__.py
│     ├─ app.py
│     ├─ api.py
│     ├─ adapters.py
│     ├─ cidr.py
│     ├─ probe.py
│     ├─ scanner.py
│     ├─ storage.py
│     ├─ logging_config.py
│     └─ ui/
│        ├─ index.html
│        ├─ styles.css
│        └─ app.js
├─ tests/
│  └─ test_cidr.py
└─ scripts/
   ├─ run_dev.ps1
   └─ run_dev.bat
```

## License
MIT.  See `LICENSE`.

## Notes
- History is saved to `Documents/Network Scanner/history.json` on Windows.  
- The initial implementation includes scaffolding for probes and storage.  Extend `probe.py` and `scanner.py` for full functionality.
