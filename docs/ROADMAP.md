# IP Scanner Roadmap

## Origin to current baseline

| Date | Milestone | Verified record |
| --- | --- | --- |
| 2025-09-19 | Project origination | Initial Network Analysis Tool commits established a FastAPI service, browser UI, local history, and early IPv4 scan structure. |
| 2025-09-19 | Historical `v1.07` checkpoint | Tag `v1.07` at `fc50a2b` documented numeric IP sorting and a broader intended feature set.  The later source audit found that several changelog claims were not present in committed code. |
| 2026-09-20 | Recovery initiated | Repository added to the Ramrattan Projects VS Code workspace.  `recovery/cross-platform-desktop` was created so `main` and `v1.07` remained untouched. |
| 2026-09-20 | Runnable baseline restored | Python 3.11 environment, existing test, API health route, and local browser interface were verified. |
| 2026-09-20 | Cross-platform and UX baseline | Platform-specific adapter and ping behavior were isolated.  The Speedtest Monitor visual system became the shared Ramrattan Network Tools standard. |
| 2026-09-21 | Discovery phase 1 | Inclusive range accounting, ICMP, common TCP, ARP, reverse DNS, device results, and portable CI were established. |
| 2026-09-21 | Discovery phase 2 | Bonjour/mDNS, UPnP, NetBIOS, safe web metadata, confidence, identity sources, and artifact controls were added. |
| 2026-09-21 | Recovery Baseline 2026.09.21 | Functional commit `22f2b6e` passed seven CI jobs.  Current behavior, Help, Kanban, and roadmap were reconciled on draft pull request #1. |
| 2026-09-21 | Inventory candidate withdrawn | A standalone Known Devices table and label workflow were evaluated, then removed before acceptance after owner review.  Scan history and device results remain the current source of truth. |
| 2026-09-21 | Result usability and visualization | Added local OUI enrichment, device-type intelligence, sortable and resizable result columns, historical stacked bar and area charts, a latest-scan mix chart, hover metrics, and a shared icon summary. |
| 2026-09-21 | Discovery Experience Baseline | Owner accepted the Intel Mac discovery and review experience at functional commit `9cd37a9`.  The draft pull request remains unmerged while Apple silicon Mac and Windows x64 hands-on gates remain open. |

The historical changelog remains part of the record.  The
[Recovery Baseline](Recovery-Baseline.md) identifies which `v1.07` behavior was
actually present, and the [Current Baseline](Current-Baseline.md) defines what is
available now.

## Forward roadmap

### Stage 1 - Change awareness and review

Compare scan history directly, identify new or missing devices, show changed
identity or services, and add the device details panel, search, filter, and
export.  Sortable and resizable columns, charts, and offline OUI evidence are
part of the accepted development baseline.  Do not reintroduce a standalone Known Devices
table without a newly approved use case and interaction design.

Exit criteria:

- Operators can explain why every change was reported.
- False changes caused by incomplete evidence are clearly qualified.
- Exported data matches the selected scan or comparison view.

### Stage 2 - Operational scanning

Move scans to background jobs with live progress and cancellation.  Add safe
scheduling, retention controls, and optional local change notifications.

Exit criteria:

- A long scan never blocks the application interface.
- Cancellation leaves valid, clearly labelled partial results.
- Scheduling and notification defaults are private and non-disruptive.

### Stage 3 - Protocol and platform completion

Add IPv6 discovery and validate the shared core on physical Intel Mac, Apple
silicon Mac, and Windows x64 systems.  Preserve one experience and one data
model across all three products.

Exit criteria:

- Target-specific behavior has automated coverage and hands-on acceptance.
- IPv4 and IPv6 evidence remains distinguishable and auditable.
- Existing local history migrates safely.

### Stage 4 - Desktop distribution

Apply the Speedtest Monitor deployment pattern to the IP Scanner lifecycle and
build three deliverables: Intel Mac, Apple silicon Mac, and Windows x64.  Add
single-instance operation, signing, notarization where applicable, installer
smoke tests, rollback guidance, and release publishing.

Exit criteria:

- Each installer launches, scans, retains history, upgrades, and uninstalls as
  documented on its target hardware.
- Release artifacts are signed, checksummed, versioned, and traceable to CI.
- User documentation and support diagnostics match the released build.

## Roadmap governance

The [Kanban board](KANBAN.md) controls current delivery status.  This roadmap
controls sequencing and outcomes.  A stage may be refined as evidence changes,
but unavailable work must not be represented as shipped.  Moving to installer
work requires acceptance of the shared core on all three target platforms.
