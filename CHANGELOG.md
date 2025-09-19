# Network Analysis Tool - Changelog

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
