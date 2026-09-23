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
| 2026-09-21 | Discovery Experience Baseline | Owner accepted the Intel Mac discovery and review experience at functional commit `9cd37a9`. |
| 2026-09-21 | Recovery integrated | PR #1 merged the accepted baseline into `main` at `47d0bc6`.  Post-merge CI run 38 passed all seven Ubuntu, macOS, Windows, and package jobs. |
| 2026-09-21 | v1.0.0 Discovery Experience Release | Named, tagged, and published the accepted Python application as the protected source-release baseline.  Standalone installers are not included. |
| 2026-09-21 | v1.1.0 desktop work opened | Created `develop/v1.1-desktop-apps` from v1.0.0 and implemented configurable scheduled collection, freshness state, shared desktop lifecycle, and three target build definitions. |
| 2026-09-21 | Target-native desktop acceptance | Intel Mac, Apple silicon Mac, and Windows x64 packages passed CI smoke tests and owner QA. |
| 2026-09-21 | v1.1.0 Desktop Application Release | Published the accepted unsigned DMG and EXE packages with data-continuity, rollback, Gatekeeper, and SmartScreen guidance. |
| 2026-09-22 | Packaged discovery investigation | A clean Intel Mac comparison found 236 packaged probe errors versus none in the Terminal source run.  The hotfix candidate bounds socket concurrency, adds retries and diagnostics, preserves shared/proxy observations, corrects service lifecycle and macOS declarations, and restores the full-size application icon. |
| 2026-09-23 | v1.1.1 Desktop Discovery Maintenance Release | Owner accepted the corrected Intel Mac discovery behavior, history-first presentation, fixed-axis chart zoom, and improved application icon.  All source and target-native packaging workflows passed before publication. |

The historical changelog remains part of the record.  The
[Recovery Baseline](Recovery-Baseline.md) identifies which `v1.07` behavior was
actually present, and the [Current Baseline](Current-Baseline.md) defines what is
available now.

## Forward roadmap

### Stage 1 - Standalone desktop applications

Delivered in v1.1.0 using the Speedtest Monitor deployment pattern: Intel Mac,
Apple silicon Mac, and Windows x64 packages share one application core and UI,
with a desktop lifecycle controller, single-instance behavior, local-data
continuity, target build workflows, installer smoke tests, diagnostics, and
rollback guidance.

Exit criteria:

- Each target application installs, launches, scans, retains history, upgrades,
  and uninstalls as documented on its physical target.
- The three products present the same UI, behavior, Help, and data model.
- Artifacts are versioned, checksummed, traceable to CI, and ready for the
  separately gated signing and publishing process.

### Stage 2 - Change awareness and review

Compare scan history directly, identify new or missing devices, show changed
identity or services, and add the device details panel, search, filter, and
export.  Sortable and resizable columns, charts, and offline OUI evidence are
part of the accepted development baseline.  Do not reintroduce a standalone Known Devices
table without a newly approved use case and interaction design.

Exit criteria:

- Operators can explain why every change was reported.
- False changes caused by incomplete evidence are clearly qualified.
- Exported data matches the selected scan or comparison view.

### Stage 3 - Operational scanning

The v1.1 release line establishes safe interval scheduling and prevents scan
overlap.  Continue with non-blocking background jobs, live progress,
cancellation, retention controls, and optional local change notifications.

Exit criteria:

- A long scan never blocks the application interface.
- Cancellation leaves valid, clearly labelled partial results.
- Scheduling and notification defaults are private and non-disruptive.

### Stage 4 - Protocol depth

Add IPv6 discovery and optional expanded service profiles while preserving one
experience and one data model across all three products.

Exit criteria:

- IPv4 and IPv6 evidence remains distinguishable and auditable.
- Existing local history migrates safely.

## Roadmap governance

The [Kanban board](KANBAN.md) controls current delivery status.  This roadmap
controls sequencing and outcomes.  A stage may be refined as evidence changes,
but unavailable work must not be represented as shipped.  Standalone desktop
applications were delivered in v1.1.0 and stabilized in v1.1.1.  Change
awareness is the next governed delivery stage.
