from network_scanner.cidr import cidr_to_range

def test_range_basic():
    start, end = cidr_to_range("192.168.1.0/24")
    assert start == "192.168.1.1"
    assert end == "192.168.1.255"
