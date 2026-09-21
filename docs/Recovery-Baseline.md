# IP Scanner Recovery Baseline

## Purpose

This record reconciles the repository state inherited from tag `v1.07` at
commit `fc50a2bbde29c63afb2c2fe443f3bc454c641ad9`.  It distinguishes verified
source behavior from historical descriptions so the desktop recovery proceeds
from evidence rather than assumptions.

## Confirmed v1.07 state

- The FastAPI health route and static browser interface launch successfully.
- The repository contains one CIDR test.
- Adapter gateway parsing is implemented only for Windows.
- The reachability command uses Windows-only ping arguments.
- `probe_host` sets a `P` flag but does not return the `reachable` property
  consumed by `Scanner`, so scan results can be discarded.
- The UI can request detected-network and custom-range scans and clear history.
- The UI does not render host details or offer CSV export.
- UPnP, Bonjour, IPv6, and device-name discovery are placeholders in the
  committed probe implementation.
- The README references `scripts/run_and_open.py`, which is absent.
- Package metadata reports version `1.0.0`, while the repository tag and
  changelog report `v1.07`.

## Recovery checkpoint decisions

- Preserve `main` and the `v1.07` tag as the historical baseline.
- Develop on `recovery/cross-platform-desktop` through reviewed pull requests.
- Restore the explicit `reachable` contract before adding discovery features.
- Isolate platform-specific gateway and ping behavior behind shared functions.
- Test the shared core on macOS, Windows, and Linux before installer work.
- Adopt the Speedtest Monitor visual system as the Ramrattan Network Tools
  family standard.
- Keep the three desktop products on one source and UI baseline.
- Treat unimplemented historical claims as roadmap items, not current features.

## Acceptance gates for this checkpoint

- Unit and API tests pass locally and in the operating-system CI matrix.
- Source compilation succeeds.
- The wheel contains the HTML, CSS, JavaScript, and Ramrattan logo.
- The application binds to the loopback address during documented development
  and packaged operation.
- The interface exposes clear actions, status feedback, an empty state, and
  contextual Help using the shared Ramrattan Network Tools design system.
- README and recovery documentation describe only verified behavior.

## Deferred work

- Asynchronous progress and scan cancellation.
- Range-size confirmation and comprehensive request validation.
- UPnP, Bonjour, IPv6, reverse DNS, and NetBIOS discovery.
- Expandable device details and CSV export.
- Desktop controllers and single-instance lifecycle management.
- Intel Mac, Apple silicon Mac, and Windows x64 installers.
- Target-native package smoke tests and production release publishing.
