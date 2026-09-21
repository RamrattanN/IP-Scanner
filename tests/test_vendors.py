from network_scanner import vendors


def test_vendor_lookup_uses_normalized_global_mac(monkeypatch):
    monkeypatch.setattr(
        vendors, "_vendor_prefixes", lambda: {"001122": "Example Devices, Inc."}
    )
    assert vendors.lookup_mac_vendor("0-11-22-33-44-55") == "Example Devices, Inc."


def test_vendor_lookup_skips_locally_administered_mac(monkeypatch):
    monkeypatch.setattr(vendors, "_vendor_prefixes", lambda: {})
    assert vendors.lookup_mac_vendor("02:11:22:33:44:55") is None
