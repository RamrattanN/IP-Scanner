# IP Scanner Kanban

Last re-baselined: 2026-09-21

This repository-tracked board is the working delivery source of truth.  Cards
move from Ready to In Progress to In Review to Done.  Later holds sequenced work
that has not yet met the Ready criteria.  Blocked records an explicit dependency
or approval gate.

## In Progress

No card is actively being implemented at this checkpoint.

## In Review

| Card | Outcome | Acceptance evidence still needed |
| --- | --- | --- |
| Cross-platform shared core | One source and UI behave consistently across targets | Hands-on Apple silicon Mac and Windows x64 acceptance |

## Ready

| Priority | Card | Outcome | Done when |
| --- | --- | --- | --- |
| 1 | Scan comparison | Show new, missing, changed, and returning devices between scans | Changes are reproducible and false positives are controlled |
| 2 | Device details panel | Present all names, sources, services, notes, and first/last seen without widening the main table | Keyboard and responsive behavior are accepted |
| 3 | Search and filter | Find devices by IP, identity, vendor, service, confidence, or change state | Controls work with keyboard and preserve numeric IP sorting |
| 4 | Export | Export the selected scan or comparison to documented local formats | CSV schema, escaping, tests, and Help are accepted |

## Later

| Stage | Cards |
| --- | --- |
| Scan operation | Background jobs, live progress, cancellation, configurable safe concurrency |
| Monitoring | Scheduled scans, change notifications, retention controls, scan reports |
| Protocol depth | IPv6 discovery, optional expanded service profiles, additional safe identity sources |
| Productization | Desktop lifecycle controller, single-instance behavior, data migration, diagnostics bundle |
| Distribution | Intel Mac, Apple silicon Mac, and Windows x64 installers, signing, notarization, release publishing |

## Done

| Completed | Card | Evidence |
| --- | --- | --- |
| 2026-09-20 | Preserve historical baseline | `main` and `v1.07` retained; recovery branch created |
| 2026-09-20 | Restore runnable shared application | Python 3.11 environment, baseline test, health route, and local UI verified |
| 2026-09-20 | Establish family UX | Speedtest Monitor header, logo, palette, actions, Help, and responsive shell adopted |
| 2026-09-20 | Cross-platform primitives | Platform-aware adapter, gateway, and ping behavior implemented |
| 2026-09-21 | Auditable inclusive scanning | Requested and attempted counts plus inclusive range tests added |
| 2026-09-21 | Layered presence discovery | ICMP, common TCP services, ARP, and reverse DNS combined |
| 2026-09-21 | Device-level history | Selectable scans and numerically sorted device results added |
| 2026-09-21 | Identity enrichment | mDNS, UPnP, NetBIOS, and safe web metadata added |
| 2026-09-21 | Confidence and artifact controls | Source attribution, confidence, reserved-address filtering, invalid-MAC rejection, and proxy-ARP suppression added |
| 2026-09-21 | Portable CI baseline | Seven Linux, macOS, Windows, and package jobs passed on functional commit `22f2b6e` |
| 2026-09-21 | Intel Mac functional acceptance | Owner accepted the refreshed interface and discovery results on the recovery host |
| 2026-09-21 | Result usability and intelligence | Owner accepted device-type icons, sortable and resizable columns, normalized MAC values, proxy status, and local vendor enrichment |
| 2026-09-21 | Discovery visualization | Owner accepted stacked device history, bar and area modes, latest-scan mix, hover metrics, and the shared icon summary |
| 2026-09-21 | Discovery Experience Baseline | Functional checkpoint `9cd37a9` recorded with synchronized Help, README, Changelog, roadmap, and baseline documentation |

## Blocked

| Card | Blocker | Unblock condition |
| --- | --- | --- |
| Merge recovery to `main` | Recovery pull request remains intentionally draft | Apple silicon Mac and Windows x64 acceptance plan is approved |
| Production installers | Shared core is not yet accepted on all physical target platforms | Intel Mac, Apple silicon Mac, and Windows x64 acceptance complete |
| Signed public release | Signing identities and release policy are outside the current recovery checkpoint | Packaging, signing, notarization, and release checklist approved |

## Withdrawn

| Card | Decision | Reason |
| --- | --- | --- |
| Standalone Known Devices inventory | Removed before acceptance | Owner determined the table did not provide sufficient value and its rename or label interaction was not usable |

## Board rules

- A card is Done only when its code or documentation is committed, its relevant
  tests pass, Help is current, and the acceptance evidence is recorded.
- CI success is not a substitute for physical target acceptance.
- Planned features must remain labelled Planned in product and project text.
- Update this board in the same pull request as any material status change.
