from __future__ import annotations

from functools import lru_cache

from mac_vendor_lookup import BaseMacLookup

from .discovery import format_mac_address, is_valid_unicast_mac


@lru_cache(maxsize=1)
def _vendor_prefixes() -> dict[str, str]:
    location = BaseMacLookup().find_vendors_list()
    if not location:
        return {}
    prefixes: dict[str, str] = {}
    try:
        with open(location, "rb") as vendor_file:
            for line in vendor_file.read().splitlines():
                prefix, separator, vendor = line.partition(b":")
                if separator and prefix and vendor:
                    prefixes[prefix.decode("ascii")] = vendor.decode("utf-8", errors="replace")
    except OSError:
        return {}
    return prefixes


def lookup_mac_vendor(mac: str | None) -> str | None:
    """Return a vendor from the bundled local OUI list without a network call."""
    formatted = format_mac_address(mac)
    if not formatted or not is_valid_unicast_mac(formatted):
        return None
    first_octet = int(formatted.split(":", 1)[0], 16)
    if first_octet & 0x02:
        return None
    prefix = formatted.replace(":", "")[:6]
    return (_vendor_prefixes().get(prefix) or "").strip() or None
