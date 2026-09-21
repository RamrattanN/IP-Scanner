# Network Analysis Tool - Changelog

> Recovery note, 2026-09-21: The historical entries below describe intended
> behavior as well as implemented behavior.  The audited source at tag `v1.07`
> does not contain several listed features.  See
> `docs/Recovery-Baseline.md` for the verified baseline and recovery decisions.

## Discovery Experience Baseline 2026.09.21
### Baseline
- Established the owner-accepted `Discovery Experience Baseline 2026.09.21` at
  functional commit `9cd37a98525acda67278d9902c6afcc28be638c4`.
- Merged the accepted recovery into `main` at
  `47d0bc66e7af4c979e5a3c281d70148ff5f7cddb`.  Post-merge CI run 38 passed all
  seven jobs.
- Retained the earlier result-usability checkpoint at
  `451ce6704e55c66717c4884a2b3c775f85e37c02` in the draft pull request history.
- Retained `Recovery Baseline 2026.09.21` as the earlier audited checkpoint
  before the result-usability work.
- Added a documentation guide, current-baseline specification, working Kanban
  board, and origin-to-date roadmap.
- Updated in-application Help to explain inclusive coverage, confirmed versus
  observed results, discovery sources, confidence, and expected unknown values.

### Fixed
- Custom IPv4 ranges are enumerated inclusively, with requested and attempted
  address counts retained for verification.
- Device presence no longer depends on an ICMP response alone.  Common TCP
  services and the operating system ARP/neighbor table provide additional
  local evidence.

### Added
- Reverse-DNS names, MAC addresses, discovery evidence, and common open-service
  details when available.
- Selectable history rows and a device-level result table.
- Validation for incomplete, reversed, invalid, and oversized custom ranges.
- Bonjour/mDNS, UPnP, NetBIOS, and safe web-metadata identity enrichment.
- Identity-source attribution plus High, Medium, and Observed confidence.
- Local IEEE OUI vendor enrichment through the bundled `mac-vendor-lookup`
  dataset, with no per-device external requests.
- Evidence-based device-type icons for Router, Computer, Printer, TV, Audio,
  NAS, Mobile, IoT, and Other.
- Sortable columns in Scan History and Device Results.
- Pointer- and keyboard-resizable Device Results columns with browser-local
  width persistence and per-column reset.
- Historical stacked bar and area charts, a latest-scan device-type pie chart,
  hover metrics, and a shared device-type summary with icons, percentages, and
  counts.

### Changed
- Withdrew the standalone Known Devices inventory candidate after owner review.
  The table, label controls, inventory API, and separate inventory persistence
  were removed before acceptance.
- Subnet network and broadcast addresses remain part of requested and attempted
  coverage but are not counted as devices.
- Broadcast and multicast MAC addresses are rejected.
- ARP-only entries sharing a likely proxy MAC are excluded, while actively
  responding IP addresses remain visible with the shared-MAC condition noted.
- MAC addresses use uppercase colon-separated formatting.  Shared or proxy
  responses appear in a separate MAC status column.

## v1.00 - Initial Build (2025-09-19)
### Added
- Home Page with history table and actions: `Scan`, `Scan Custom Range`, `Clear History`.
- Scan Page with auto-detected adapter and derived CIDR, plus Cancel and Scan buttons.
- Scan Custom Range Page with editable start and end, plus Cancel and Scan buttons.
- Clear History with Y/N prompt.
- Scan engine skeleton with flags:
  - **G** Gateway
  - **W** Website available (HTTP/HTTPS)
  - **U** UPnP available (SSDP)
  - **B** Bonjour available (mDNS)
  - **P** Pingable (ICMP or TCP fallback)
  - **6** IPv6 available
  - **S** Scan in progress (transient)
- Results view scaffolding with filters and export endpoints.
- JSON history persistence and rotating logs.

### Defaults
- Python 3.12 with FastAPI and Uvicorn.
- AsyncIO concurrency default 256 workers with gentle rate limiting.
- Timeouts: 800ms reachability, 600ms DNS/mDNS, 800ms SSDP with 1.5s window.
- Confirmation when range exceeds 4096 IPs.


## v1.01 - Adapter detection and basic probe (2025-09-19)
### Changed
- **Adapter detection** improved: now selects the interface with a real default gateway instead of APIPA (169.254.*).
- **Probing** updated: added Windows ping (`ping -n 1 -w 400`) and quick HTTP HEAD checks (port 80 and 443).
- Hosts are now marked as **P** (Pingable) and **W** (Website available) when detected.


## v1.02 - Reachability fallback, gateway marking, details view (2025-09-19)
### Added
- Per scan details view in the UI.  Click a history row to see all hosts and their flags.
### Changed
- Probe logic now treats a host as reachable if ICMP works or a short TCP connect to 80 or 443 succeeds.
- Scanner marks the adapter default gateway with G automatically when present.


## v1.03 - Host flags UI, reverse DNS, auto browser (2025-09-19)
### Added
- Per-host table in details view with colored flag icons (G/W/U/B/P/6).
- Reverse DNS resolution for hostnames.
- Helper script `scripts/run_and_open.py` opens the default browser on startup.
### Changed
- Refactored probe logic to include reverse DNS, stubs for UPnP/Bonjour/IPv6.


## v1.03 - Names, colored flags, and one-click start (2025-09-19)
### Added
- Reverse DNS name resolution for hosts when reachable.
- Colored letter badges in details view for G, W, U, B, P, and 6.
- `scripts/run_and_open.py` opens your default browser to the app after starting the server.
### Notes
- UPnP, Bonjour, and IPv6 flags remain placeholders for now.  We will wire SSDP and mDNS in the next build.


## v1.04 - Device names and service discovery (2025-09-19)
### Added
- NetBIOS Node Status on UDP 137 to capture device names when available.
- UPnP unicast SSDP on UDP 1900 with device description fetch to capture friendlyName and set U.
- Unicast mDNS probe on UDP 5353 to set B when Bonjour is present.
- CSV export endpoint at `/api/scan/{id}/csv` and a link in the details view.
### Changed
- Only reachable hosts are stored and displayed.  Empty addresses are no longer listed.


## v1.05 - Toggle details and better device names (2025-09-19)
### Added
- Click a history row to expand details, click the same row again to collapse.
### Improved
- NetBIOS Node Status encoding and parsing to capture workstation/server names more reliably.
- Reverse DNS timeout increased with a small retry for stubborn resolvers.
- Details view shows '(Gateway)' next to the device name when applicable.


## v1.06 - Windows nbtstat fallback for device names (2025-09-19)
### Added
- Fallback to `nbtstat -A <ip>` for device names when UDP NetBIOS parsing does not return a name.


## v1.07 - Numeric IP sort and docs (2025-09-19)
### Changed
- Hosts in details are now sorted by numeric IPv4 order rather than lexicographic order.
### Docs
- README updated with current features and quick start instructions.
