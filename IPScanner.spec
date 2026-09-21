import os

from PyInstaller.utils.hooks import collect_all
from mac_vendor_lookup import BaseMacLookup

vendor_datas, vendor_binaries, vendor_hiddenimports = collect_all("mac_vendor_lookup")
vendor_list = BaseMacLookup().find_vendors_list()
if not vendor_list:
    raise RuntimeError("The mac-vendor-lookup OUI database was not installed.")
target_arch = os.environ.get("IP_SCANNER_MACOS_TARGET_ARCH", "x86_64")

a = Analysis(
    ["src/network_scanner/desktop.py"],
    pathex=["src"],
    binaries=vendor_binaries,
    datas=vendor_datas + [
        ("src/network_scanner/ui", "network_scanner/ui"),
        (vendor_list, "cache"),
    ],
    hiddenimports=vendor_hiddenimports + [
        "network_scanner.app",
        "network_scanner.api",
        "network_scanner.scanner",
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan.on",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name="IP Scanner", debug=False,
    bootloader_ignore_signals=False, strip=False, upx=False, console=False,
    argv_emulation=False, icon="build/macos-icon/IPScanner.icns", target_arch=target_arch,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="IP Scanner")
app = BUNDLE(
    coll,
    name="IP Scanner.app",
    icon="build/macos-icon/IPScanner.icns",
    bundle_identifier="com.ramrattan.ip-scanner",
    info_plist={
        "CFBundleDisplayName": "IP Scanner",
        "CFBundleShortVersionString": "1.1.0",
        "CFBundleVersion": "1.1.0",
        "LSMinimumSystemVersion": "13.0",
        "NSHighResolutionCapable": True,
    },
)
