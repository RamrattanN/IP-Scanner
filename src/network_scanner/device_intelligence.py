from __future__ import annotations

from typing import Any


VENDOR_IDENTITIES = (
    (("nintendo",), "Nintendo"),
    (("ubiquiti",), "Ubiquiti"),
    (("mikrotik",), "MikroTik"),
    (("cisco meraki", "meraki"), "Cisco Meraki"),
    (("aruba networks",), "Aruba"),
    (("ruckus",), "Ruckus"),
    (("valve",), "Valve"),
)


def infer_identity_from_direct_vendor(host: dict[str, Any]) -> None:
    """Add a conservative identity only when the MAC belongs to this host."""
    if host.get("name") or not host.get("mac"):
        return
    vendor = str(host.get("mac_vendor") or "").strip()
    vendor_key = vendor.casefold()
    identity = next(
        (
            label
            for fragments, label in VENDOR_IDENTITIES
            if any(fragment in vendor_key for fragment in fragments)
        ),
        None,
    )
    if not identity:
        return
    host["name"] = identity
    names = host.setdefault("names", [])
    candidate = {"source": "MAC vendor inference", "value": identity}
    if candidate not in names:
        names.append(candidate)
    host.setdefault("notes", {})["identity_inferred"] = True
