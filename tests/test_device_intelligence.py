from network_scanner.device_intelligence import infer_identity_from_direct_vendor


def test_infers_selected_identity_from_direct_mac_vendor():
    host = {
        "mac": "70:48:F7:2C:73:DF",
        "mac_vendor": "Nintendo Co.,Ltd",
        "name": None,
        "names": [],
        "notes": {},
    }

    infer_identity_from_direct_vendor(host)

    assert host["name"] == "Nintendo"
    assert host["names"] == [{"source": "MAC vendor inference", "value": "Nintendo"}]
    assert host["notes"]["identity_inferred"] is True


def test_does_not_infer_identity_without_direct_mac():
    host = {
        "mac": None,
        "mac_vendor": None,
        "name": None,
        "names": [],
        "notes": {"shared_proxy_vendor": "Ubiquiti Inc"},
    }

    infer_identity_from_direct_vendor(host)

    assert host["name"] is None
