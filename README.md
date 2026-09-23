# Ramrattan IP Scanner

A local network scanner in the Ramrattan Network Tools family.  The application
uses a FastAPI service and a shared browser interface, stores scan history
locally, and now provides the accepted shared baseline for Intel Mac, Apple
silicon Mac, and Windows x64 desktop products.

## Current release

The current release is **Ramrattan IP Scanner v1.1.1 - Desktop Discovery
Maintenance Release**.  Its functional checkpoint is `7ee0d65`, approved after
native QA of the Intel Mac discovery fix and successful Intel Mac, Apple silicon
Mac, and Windows x64 packaging workflows.  Version 1.1.0 remains the immediate
desktop rollback release, v1.0.0 remains the protected source-release rollback
baseline, and the historical `v1.07` tag remains unchanged as the audited
pre-recovery checkpoint.

The accepted baseline provides:

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
- Local IEEE OUI vendor enrichment for valid globally administered MAC
  addresses, without sending scanned addresses to an external service.
- Consistent uppercase MAC formatting, a separate shared/proxy status column,
  evidence-based device-type icons, sortable table columns, and persistent
  user-resizable Device Results columns.
- Broadcast, multicast-MAC, and repeated proxy-ARP artifact suppression.
- Local JSON history and rotating logs.
- Device-level results for every discovered host, with selectable scan history.
- Historical device totals and type composition in stacked bar or area charts,
  a latest-scan device-type pie chart, hover metrics, and a shared icon key.
- A shared Ramrattan Network Tools header, logo, palette, action system, empty
  state, and right-side Help panel.
- Automated tests for CIDR handling, adapters, probing, scanning, storage, the
  API health route, and packaged visual assets.
- Configurable automatic detected-network scans, serialized with manual scans,
  with explicit freshness and next-run information.
- A shared desktop controller with single-instance behavior and local-service
  lifecycle management.
- Native Intel Mac DMG, Apple silicon Mac DMG, and Windows x64 EXE installer
  packages.

The v1.1.1 desktop packages are published unsigned.  macOS Gatekeeper and
Windows SmartScreen may therefore display a warning.  Signing and notarization
remain a separately governed release-hardening activity.

## Maintenance release

Version 1.1.1 bounds packaged-app resource use, retries unanswered addresses,
improves response evidence and diagnostics, prevents orphaned services, adds
the macOS local-network declarations, corrects the application icon scale,
places scan analytics before device results, and supports horizontal timeline
zoom while preserving the chart's device-count axis.

Start with the [Wiki Home](docs/WIKI.md) or the
[Documentation Guide](docs/README.md).  They link the accepted current
baseline, the audited v1.07 recovery record, result interpretation, UX
standard, Kanban board, and origin-to-date roadmap.

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

To exercise the desktop controller from source, run:

```bash
python -m network_scanner.desktop
```

## Data location

The current baseline preserves the legacy data location:

```text
~/Documents/Network Scanner/history.json
```

Automatic scan settings are stored in `settings.json`.  Application logs are
stored in the `logs` folder beneath the same directory.  Desktop upgrades and
routine uninstallation preserve this directory.

## Architecture

```text
src/network_scanner/
├── adapters.py       # Platform-aware adapter and default-route detection
├── api.py            # Local FastAPI routes
├── discovery.py      # mDNS, UPnP, NetBIOS, confidence primitives
├── device_types.py   # Evidence-based device type classification
├── probe.py          # ICMP, TCP service, and reverse-DNS probes
├── neighbors.py      # Platform-aware ARP/neighbor-table evidence
├── scanner.py        # Concurrent IPv4 range scanning
├── scan_coordinator.py # Manual and scheduled scan serialization and status
├── desktop.py        # Shared desktop controller and local service lifecycle
├── storage.py        # Local JSON persistence
├── vendors.py        # Local bundled IEEE OUI lookup
└── ui/               # Shared HTML, CSS, JavaScript, and brand assets
```

The three desktop products share this application core and UI.  Only the
platform controller, packaging, and installer layers differ.

## CI and release direction

Baseline CI runs tests and source compilation on Python 3.11 and 3.12 across
Linux, macOS, and Windows.  It also builds and installs the wheel in isolation
to confirm that the UI and logo are packaged.

Target-native workflows build two macOS disk images and one Windows x64
installer using the proven Speedtest Monitor pattern.  See
[Desktop Packaging](docs/Desktop-Packaging.md) for artifact names, local build
commands, installation, data continuity, and rollback.

The [Kanban board](docs/KANBAN.md) is the working source of truth for delivery
status.  CI success demonstrates source portability, but it does not replace
hands-on acceptance on Intel Mac, Apple silicon Mac, and Windows x64 hardware.

## License

Licensed under the MIT License.
