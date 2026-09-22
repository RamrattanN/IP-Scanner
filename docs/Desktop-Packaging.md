# Desktop Packaging

## Release scope

Version 1.1.0 packages the same loopback-only service and browser interface for
three targets:

| Target | Release artifact |
| --- | --- |
| Intel Mac | `IP-Scanner-macOS-Intel-1.1.0.dmg` |
| Apple silicon Mac | `IP-Scanner-macOS-Apple-Silicon-1.1.0.dmg` |
| Windows x64 | `IP-Scanner-Windows-x64-1.1.0.exe` |

These are accepted unsigned release artifacts.  macOS Gatekeeper and Windows
SmartScreen may warn until signing and notarization are completed in a later
release-hardening gate.

## v1.1.1 QA candidate

The current corrective branch produces the following test artifacts.  These
are not release assets until target-native QA and owner approval are complete.

| Target | QA artifact |
| --- | --- |
| Intel Mac | `IP-Scanner-macOS-Intel-1.1.1.dmg` |
| Apple silicon Mac | `IP-Scanner-macOS-Apple-Silicon-1.1.1.dmg` |
| Windows x64 | `IP-Scanner-Windows-x64-1.1.1.exe` |

The candidate keeps TCP work below the Finder-launch descriptor budget, makes
two paced discovery passes, declares local-network and Bonjour use, records
probe error types, keeps the service tied to the desktop controller, and builds
the Ramrattan shield at the same visual scale as Speedtest Monitor.

## Collection lifecycle

- Manual detected-network and custom-range scans remain available.
- Automatic scans use the currently detected network and default to every 60
  minutes.  The user can select 15 minutes through 24 hours or pause them.
- The application must remain running for automatic scans to occur.
- One coordinator serializes both scan types.  A second scan is rejected while
  another is active.
- Freshness is measured against the selected automatic interval.  Results are
  Fresh within one interval, Aging within two, and Stale after two.

## Local builds

Install the project and release tools first:

```bash
python -m pip install -e ".[test,desktop-release]"
```

Build a DMG on its matching Mac architecture:

```bash
bash scripts/build_macos_release.sh
```

Build the Windows x64 installer from PowerShell with Inno Setup 6 installed:

```powershell
.\scripts\build_windows_release.ps1
```

PyInstaller does not cross-compile these packages.  CI uses separate Intel Mac,
Apple silicon Mac, and Windows x64 runners.

## Data continuity and rollback

History, scheduling settings, and logs remain under
`~/Documents/Network Scanner`.  Installing, repairing, upgrading, or
uninstalling the application does not delete that folder.

To roll back the application, quit IP Scanner, uninstall v1.1.0, and reinstall
v1.0.0 or run the v1.0.0 source release.  Existing `history.json` remains
compatible.  The earlier release ignores `settings.json`.

Before destructive manual maintenance, copy the entire `Network Scanner`
folder.  Clearing history from inside the application intentionally removes
the stored scan records but leaves schedule settings intact.
