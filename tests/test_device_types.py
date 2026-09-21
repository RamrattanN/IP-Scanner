from network_scanner.device_types import classify_device_type


def host(name="", services=None, gateway=False, manufacturer=None, model=None):
    return {
        "name": name,
        "names": [],
        "services": services or [],
        "manufacturer": manufacturer,
        "model": model,
        "flags": {"G": gateway},
    }


def test_classifies_common_device_types_from_observed_evidence():
    assert classify_device_type(host(gateway=True)) == "Router"
    assert classify_device_type(host("HP OfficeJet", ["IPP"])) == "Printer"
    assert classify_device_type(host("Synology DiskStation", ["SMB"])) == "NAS"
    assert classify_device_type(host("Downstairs TV", ["AIRPLAY"])) == "TV"
    assert classify_device_type(host("Living Room Speaker", ["RAOP"])) == "Audio"
    assert classify_device_type(host("MacBook Pro", ["SMB"])) == "Computer"
    assert classify_device_type(host("Front door camera")) == "IoT"
    assert classify_device_type(host("Unidentified host")) == "Other"
