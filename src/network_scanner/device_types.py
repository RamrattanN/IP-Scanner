from __future__ import annotations

from typing import Any


def classify_device_type(host: dict[str, Any]) -> str:
    """Classify from observed metadata and return Other when evidence is weak."""
    flags = host.get("flags") or {}
    if flags.get("G"):
        return "Router"

    services = {str(value).casefold() for value in host.get("services") or []}
    names = [host.get("name") or ""]
    names.extend(item.get("value", "") for item in host.get("names") or [])
    text = " ".join(
        [
            *names,
            host.get("manufacturer") or "",
            host.get("model") or "",
            host.get("mac_vendor") or "",
            *services,
        ]
    ).casefold()

    def contains(*terms: str) -> bool:
        return any(term in text for term in terms)

    if contains(
        "router", "gateway", "access point", "extender", "mesh", "amplifi",
        "orbi", "nighthawk", "ex3700", "ex7000"
    ):
        return "Router"
    if contains("nintendo", "playstation", "xbox", "steam deck", "game console"):
        return "Game Console"
    if contains(
        "ubiquiti", "mikrotik", "cisco meraki", "aruba networks", "ruckus",
        "juniper networks", "network switch", "wireless bridge"
    ):
        return "Network Device"
    if services.intersection({"ipp", "lpd", "printer"}) or contains("printer", "officejet", "laserjet"):
        return "Printer"
    if contains("synology", "qnap", "truenas", "diskstation", "readynas", " nas"):
        return "NAS"
    if contains(" television", " tv", "roku", "fire tv", "chromecast", "signage"):
        return "TV"
    if services.intersection({"raop", "audio"}) or contains(
        "speaker", "sonos", "homepod", "soundbar", "receiver", "audio", "google home"
    ):
        return "Audio"
    if contains("iphone", "ipad", "android", "phone", "tablet", "pixel"):
        return "Mobile"
    if contains("macbook", "imac", "desktop", "laptop", "workstation", "windows pc"):
        return "Computer"
    if services.intersection({"smb", "netbios"}) and not contains("signage"):
        return "Computer"
    if contains(
        "camera", "thermostat", "doorbell", "light", "bulb", "smart plug",
        "sensor", "nest", "ring", "hue", "iot"
    ):
        return "IoT"
    return "Other"
