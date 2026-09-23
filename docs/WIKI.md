# Ramrattan IP Scanner Wiki

Ramrattan IP Scanner provides local visibility into devices and services on an
IPv4 network.  It combines active probes with the operating system neighbor
table, keeps history on the local computer, and presents results through the
same interface on Intel Mac, Apple silicon Mac, and Windows x64.

## Current release

The current release is **v1.1.1 - Desktop Discovery Maintenance Release**.
It includes the corrected packaged-discovery behavior, improved diagnostics,
shared/proxy observation handling, the full-size application icon, the
history-first results layout, and horizontal chart zoom with a fixed
device-count axis.

- [Download v1.1.1](https://github.com/RamrattanN/IP-Scanner/releases/tag/v1.1.1)
- [Read the changelog](https://github.com/RamrattanN/IP-Scanner/blob/main/CHANGELOG.md)
- [Review the accepted baseline](https://github.com/RamrattanN/IP-Scanner/blob/main/docs/Current-Baseline.md)

The published desktop packages are unsigned.  macOS Gatekeeper or Windows
SmartScreen may display a warning.  Version v1.1.0 remains the immediate
desktop rollback release.

## Start here

| Guide | Purpose |
| --- | --- |
| [Desktop Packaging](https://github.com/RamrattanN/IP-Scanner/blob/main/docs/Desktop-Packaging.md) | Release artifacts, collection lifecycle, local builds, data continuity, and rollback |
| [Discovery Confidence](https://github.com/RamrattanN/IP-Scanner/blob/main/docs/Discovery-Confidence.md) | Confirmed and observed devices, evidence sources, unknown values, and artifact controls |
| [UX Guidelines](https://github.com/RamrattanN/IP-Scanner/blob/main/docs/UX-Guidelines.md) | Shared Ramrattan Network Tools visual and interaction standard |
| [Kanban](https://github.com/RamrattanN/IP-Scanner/blob/main/docs/KANBAN.md) | Current delivery priorities, later work, completed work, and blockers |
| [Roadmap](https://github.com/RamrattanN/IP-Scanner/blob/main/docs/ROADMAP.md) | Project origination, delivered milestones, and planned stages |
| [Third-Party Notices](https://github.com/RamrattanN/IP-Scanner/blob/main/docs/Third-Party-Notices.md) | Local OUI lookup source and license record |

The repository documents are the canonical, version-controlled project record.
This page is the public navigation entry point.

## Reading scan results

- **Confirmed** devices answered an active probe such as ICMP or a selected TCP
  connection.
- **Observed** devices were present in the operating system neighbor table but
  did not answer the selected active probes.
- **Shared/proxy response** means more than one address returned the same MAC
  address.  The address remains visible when other evidence supports it, but
  the shared response is not treated as a unique hardware identity.
- **Not advertised** means a device was found but did not publish that identity
  through the discovery sources used by the application.
- **Not available** means the application could not establish the value from
  valid local evidence.

Manufacturer and device-type values are evidence-based hints.  They do not
assert ownership, security, or a guaranteed product model.

## Collection and privacy

- Manual detected-network and custom-range scans are available.
- Automatic detected-network scans can run every 15 minutes through 24 hours,
  or be paused.
- The application must remain running for automatic scans to occur.
- History, settings, and logs remain under `~/Documents/Network Scanner`.
- Vendor enrichment uses a bundled local IEEE OUI list.  Scanned addresses are
  not sent to an external MAC lookup service.
- The application service binds to the local loopback address.

## Current direction

The next delivery stage is change awareness and review: scan comparison, a
device details panel, search and filtering, and export.  Background progress,
cancellation, retention controls, notifications, IPv6 discovery, deeper
optional service profiles, signing, and notarization remain later or blocked
work.  The [Kanban](https://github.com/RamrattanN/IP-Scanner/blob/main/docs/KANBAN.md)
is the delivery source of truth.

## Help and troubleshooting

Use the **Help** button inside the application for operating guidance,
interpretation details, chart controls, and troubleshooting.  For source-based
development, follow the setup commands in the
[repository README](https://github.com/RamrattanN/IP-Scanner/blob/main/README.md).
