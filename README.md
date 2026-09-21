# Ramrattan IP Scanner

A local network scanner in the Ramrattan Network Tools family.  The application
uses a FastAPI service and a shared browser interface, stores scan history
locally, and is being recovered as one codebase for Intel Mac, Apple silicon
Mac, and Windows x64 desktop products.

## Accepted recovery baseline

The accepted functional checkpoint is **Recovery Baseline 2026.09.21**, recorded
on the draft recovery pull request at commit `22f2b6e`.  It is a development
baseline, not a production release.  The historical `main` branch and `v1.07`
tag remain unchanged.

The recovery branch provides:

- Active IPv4 adapter and default-gateway detection on macOS, Windows, and Linux.
- Layered device discovery using native ICMP, common TCP services, and the
  operating system ARP/neighbor table.
- Detected-network and custom-range scan requests.
- Inclusive range accounting that reports requested addresses, attempted
  addresses, probe errors, and discovered devices separately.
- Reverse-DNS names, MAC addresses, discovery evidence, common open services,
  and gateway role when those facts can be established locally.
- Bonjour/mDNS, UPnP, NetBIOS, and safe web-metadata identity enrichment.
- High, Medium, and Observed confidence classifications with identity-source
  attribution.
- Broadcast, multicast-MAC, and repeated proxy-ARP artifact suppression.
- Local JSON history and rotating logs.
- Device-level results for every discovered host, with selectable scan history.
- A shared Ramrattan Network Tools header, logo, palette, action system, empty
  state, and right-side Help panel.
- Automated tests for CIDR handling, adapters, probing, scanning, storage, the
  API health route, and packaged visual assets.

IPv6 discovery, offline MAC-vendor identification, CSV export, background
progress, cancellation, and desktop installers remain planned work.  They must
not be represented as available until implemented and accepted.

Start with the [Documentation Guide](docs/README.md).  The guide links the
accepted current baseline, the audited v1.07 recovery record, result
interpretation, UX standard, Kanban board, and origin-to-date roadmap.

## Developer setup

Python 3.11 or newer is required.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[test]"
python -m pytest -q
python -m uvicorn network_scanner.app:app --host 127.0.0.1 --port 8000
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
. .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[test]"
python -m pytest -q
python -m uvicorn network_scanner.app:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>.  Stop the development server with Control-C.

## Data location

The current recovery build preserves the legacy data location:

```text
~/Documents/Network Scanner/history.json
```

Application logs are stored in the `logs` folder beneath the same directory.
The planned desktop applications will preserve user history through upgrades
and routine uninstallation.

## Architecture

```text
src/network_scanner/
├── adapters.py       # Platform-aware adapter and default-route detection
├── api.py            # Local FastAPI routes
├── discovery.py      # mDNS, UPnP, NetBIOS, confidence primitives
├── probe.py          # ICMP, TCP service, and reverse-DNS probes
├── neighbors.py      # Platform-aware ARP/neighbor-table evidence
├── scanner.py        # Concurrent IPv4 range scanning
├── storage.py        # Local JSON persistence
└── ui/               # Shared HTML, CSS, JavaScript, and brand assets
```

The three desktop products will share this application core and UI.  Only the
platform controller, packaging, and installer layers may differ.

## CI and release direction

Baseline CI runs tests and source compilation on Python 3.11 and 3.12 across
Linux, macOS, and Windows.  It also builds and installs the wheel in isolation
to confirm that the UI and logo are packaged.

Target-native installer workflows will follow the proven Speedtest Monitor
pattern after the shared scanner and user experience pass functional acceptance.

The [Kanban board](docs/KANBAN.md) is the working source of truth for delivery
status.  CI success demonstrates source portability, but it does not replace
hands-on acceptance on Intel Mac, Apple silicon Mac, and Windows x64 hardware.

## License

Licensed under the MIT License.
