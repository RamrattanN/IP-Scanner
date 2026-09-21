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
