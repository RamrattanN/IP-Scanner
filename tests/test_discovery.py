import struct

import dns.message
import dns.rrset

from network_scanner.discovery import (
    is_valid_unicast_mac,
    parse_mdns_packets,
    parse_netbios_name,
    parse_ssdp_response,
    subnet_reserved_addresses,
)


def test_mac_and_subnet_artifact_rules():
    assert is_valid_unicast_mac("00:11:22:33:44:55") is True
    assert is_valid_unicast_mac("02:11:22:33:44:55") is True
    assert is_valid_unicast_mac("FF:FF:FF:FF:FF:FF") is False
    assert is_valid_unicast_mac("01:00:5E:00:00:FB") is False
    assert subnet_reserved_addresses("192.168.2.0/24") == {"192.168.2.0", "192.168.2.255"}


def test_parses_netbios_node_status_name():
    transaction_id = 0x1234
    name_entry = b"OFFICEPC".ljust(15, b" ") + b"\x00\x00\x00"
    data = b"\x01" + name_entry
    packet = (
        struct.pack("!HHHHHH", transaction_id, 0x8500, 0, 1, 0, 0)
        + b"\xc0\x0c"
        + struct.pack("!HHIH", 0x21, 1, 0, len(data))
        + data
    )
    assert parse_netbios_name(packet, transaction_id) == "OFFICEPC"


def test_parses_mdns_service_identity():
    message = dns.message.Message(id=0)
    message.answer.extend(
        [
            dns.rrset.from_text(
                "_http._tcp.local.", 120, "IN", "PTR", "Office\\032Printer._http._tcp.local."
            ),
            dns.rrset.from_text(
                "Office\\032Printer._http._tcp.local.", 120, "IN", "SRV", "0 0 80 printer.local."
            ),
            dns.rrset.from_text("printer.local.", 120, "IN", "A", "192.0.2.25"),
            dns.rrset.from_text(
                "Office\\032Printer._http._tcp.local.", 120, "IN", "TXT", '"note=Upstairs"'
            ),
        ]
    )

    devices = parse_mdns_packets([message.to_wire()])

    assert devices["192.0.2.25"]["name"] == "Office Printer"
    assert devices["192.0.2.25"]["services"] == ["HTTP"]
    assert devices["192.0.2.25"]["properties"]["note"] == "Upstairs"


def test_parses_ssdp_headers():
    payload = (
        b"HTTP/1.1 200 OK\r\n"
        b"LOCATION: http://192.0.2.1:5000/root.xml\r\n"
        b"SERVER: ExampleOS UPnP/1.1\r\n\r\n"
    )
    assert parse_ssdp_response(payload)["location"] == "http://192.0.2.1:5000/root.xml"
