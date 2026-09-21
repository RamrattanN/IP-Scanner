from __future__ import annotations

import asyncio
import ipaddress
import random
import re
import socket
import struct
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Any
from urllib.parse import urlparse

import dns.message
import dns.name
import dns.rdataclass
import dns.rdatatype
import dns.rrset
import httpx


MDNS_SERVICE_TYPES = (
    "_device-info._tcp.local.",
    "_workstation._tcp.local.",
    "_http._tcp.local.",
    "_https._tcp.local.",
    "_airplay._tcp.local.",
    "_raop._tcp.local.",
    "_ipp._tcp.local.",
    "_printer._tcp.local.",
    "_googlecast._tcp.local.",
    "_smb._tcp.local.",
)


def _netbios_query(transaction_id: int) -> bytes:
    raw_name = b"*" + (b"\x00" * 15)
    encoded = b"".join(
        bytes((65 + (value >> 4), 65 + (value & 0x0F))) for value in raw_name
    )
    header = struct.pack("!HHHHHH", transaction_id, 0, 1, 0, 0, 0)
    return header + bytes((len(encoded),)) + encoded + b"\x00\x00\x21\x00\x01"


def _skip_dns_name(packet: bytes, offset: int) -> int:
    while offset < len(packet):
        length = packet[offset]
        if length & 0xC0 == 0xC0:
            return offset + 2
        offset += 1
        if length == 0:
            return offset
        offset += length
    raise ValueError("Truncated DNS name")


def parse_netbios_name(packet: bytes, transaction_id: int | None = None) -> str | None:
    """Extract the best unique workstation/server name from an NBSTAT reply."""
    if len(packet) < 12:
        return None
    response_id, flags, questions, answers, _authority, _additional = struct.unpack(
        "!HHHHHH", packet[:12]
    )
    if transaction_id is not None and response_id != transaction_id:
        return None
    if not flags & 0x8000:
        return None
    try:
        offset = 12
        for _ in range(questions):
            offset = _skip_dns_name(packet, offset) + 4
        candidates: list[tuple[int, str]] = []
        for _ in range(answers):
            offset = _skip_dns_name(packet, offset)
            record_type, _record_class, _ttl, length = struct.unpack(
                "!HHIH", packet[offset : offset + 10]
            )
            offset += 10
            data = packet[offset : offset + length]
            offset += length
            if record_type != 0x21 or not data:
                continue
            count = data[0]
            for index in range(count):
                entry = data[1 + (index * 18) : 1 + ((index + 1) * 18)]
                if len(entry) != 18:
                    continue
                name = entry[:15].decode("ascii", errors="ignore").strip()
                suffix = entry[15]
                entry_flags = struct.unpack("!H", entry[16:18])[0]
                is_group = bool(entry_flags & 0x8000)
                if name and name != "*" and not is_group and suffix in {0x00, 0x20}:
                    candidates.append((0 if suffix == 0x00 else 1, name))
        return min(candidates, default=(99, ""))[1] or None
    except (IndexError, struct.error, ValueError):
        return None


def _query_netbios(ip: str, timeout: float) -> str | None:
    transaction_id = random.randint(1, 65535)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(timeout)
        sock.sendto(_netbios_query(transaction_id), (ip, 137))
        packet, _address = sock.recvfrom(4096)
        return parse_netbios_name(packet, transaction_id)
    except (OSError, TimeoutError):
        return None
    finally:
        sock.close()


async def discover_netbios_name(ip: str, timeout: float = 0.55) -> str | None:
    return await asyncio.to_thread(_query_netbios, ip, timeout)


def _mdns_query() -> bytes:
    message = dns.message.Message(id=0)
    for service_type in MDNS_SERVICE_TYPES:
        message.question.append(
            dns.rrset.RRset(
                dns.name.from_text(service_type),
                dns.rdataclass.IN | 0x8000,
                dns.rdatatype.PTR,
            )
        )
    return message.to_wire()


def parse_mdns_packets(packets: list[bytes]) -> dict[str, dict[str, Any]]:
    instances: dict[str, str] = {}
    servers: dict[str, tuple[str, int]] = {}
    addresses: dict[str, set[str]] = defaultdict(set)
    properties: dict[str, dict[str, str]] = defaultdict(dict)

    for packet in packets:
        try:
            message = dns.message.from_wire(packet, ignore_trailing=True)
        except Exception:
            continue
        for rrset in (*message.answer, *message.authority, *message.additional):
            owner = str(rrset.name).rstrip(".")
            for record in rrset:
                if rrset.rdtype == dns.rdatatype.PTR:
                    instances[str(record.target).rstrip(".")] = owner
                elif rrset.rdtype == dns.rdatatype.SRV:
                    servers[owner] = (str(record.target).rstrip("."), int(record.port))
                elif rrset.rdtype == dns.rdatatype.A:
                    addresses[owner].add(str(record.address))
                elif rrset.rdtype == dns.rdatatype.TXT:
                    for item in record.strings:
                        text = item.decode("utf-8", errors="replace")
                        key, separator, value = text.partition("=")
                        if separator:
                            properties[owner][key.casefold()] = value

    devices: dict[str, dict[str, Any]] = {}
    for instance, service_type in instances.items():
        server, port = servers.get(instance, ("", 0))
        service_addresses = addresses.get(server, set())
        if not service_addresses:
            continue
        suffix = "." + service_type
        instance_name = instance[: -len(suffix)] if instance.endswith(suffix) else instance
        try:
            friendly_name = dns.name.from_text(instance_name).labels[0].decode(
                "utf-8", errors="replace"
            )
        except (IndexError, UnicodeError):
            friendly_name = instance_name
        service_label = service_type.split(".")[0].removeprefix("_").upper()
        for ip in service_addresses:
            device = devices.setdefault(
                ip,
                {"name": friendly_name, "services": [], "properties": {}, "source": "mDNS"},
            )
            if service_label and service_label not in device["services"]:
                device["services"].append(service_label)
            if port:
                device["properties"][f"{service_label.casefold()}_port"] = str(port)
            device["properties"].update(properties.get(instance, {}))
    return devices


def discover_mdns(timeout: float = 1.5) -> dict[str, dict[str, Any]]:
    packets: list[bytes] = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(0.2)
        query = _mdns_query()
        deadline = time.monotonic() + timeout
        sock.sendto(query, ("224.0.0.251", 5353))
        sent_again = False
        while time.monotonic() < deadline:
            if not sent_again and time.monotonic() > deadline - (timeout / 2):
                sock.sendto(query, ("224.0.0.251", 5353))
                sent_again = True
            try:
                packet, _address = sock.recvfrom(65535)
                packets.append(packet)
            except socket.timeout:
                continue
    except (OSError, ValueError):
        return {}
    finally:
        sock.close()
    return parse_mdns_packets(packets)


def parse_ssdp_response(payload: bytes) -> dict[str, str]:
    text = payload.decode("iso-8859-1", errors="replace")
    headers: dict[str, str] = {}
    for line in text.replace("\r\n", "\n").split("\n")[1:]:
        key, separator, value = line.partition(":")
        if separator:
            headers[key.strip().casefold()] = value.strip()
    return headers


def _xml_text(root: ET.Element, local_name: str) -> str | None:
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] == local_name and element.text:
            value = element.text.strip()
            if value:
                return value
    return None


def _upnp_description(location: str, source_ip: str) -> dict[str, str]:
    parsed = urlparse(location)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return {}
    try:
        resolved = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, parsed.port)}
    except (OSError, ValueError):
        return {}
    if source_ip not in resolved:
        return {}
    try:
        with httpx.Client(
            timeout=1.0, verify=False, follow_redirects=True, trust_env=False
        ) as client:
            response = client.get(location, headers={"Accept": "application/xml,text/xml"})
            response.raise_for_status()
            content = response.content[:524288]
        root = ET.fromstring(content)
    except (httpx.HTTPError, ET.ParseError, OSError):
        return {}
    return {
        key: value
        for key, value in {
            "name": _xml_text(root, "friendlyName"),
            "manufacturer": _xml_text(root, "manufacturer"),
            "model": _xml_text(root, "modelName"),
        }.items()
        if value
    }


def discover_upnp(timeout: float = 1.5) -> dict[str, dict[str, Any]]:
    request = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        'MAN: "ssdp:discover"\r\n'
        "MX: 1\r\n"
        "ST: ssdp:all\r\n\r\n"
    ).encode("ascii")
    responses: dict[str, dict[str, str]] = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(0.2)
        sock.sendto(request, ("239.255.255.250", 1900))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                payload, address = sock.recvfrom(65535)
            except socket.timeout:
                continue
            headers = parse_ssdp_response(payload)
            if headers.get("location"):
                responses[address[0]] = headers
    except OSError:
        return {}
    finally:
        sock.close()

    devices: dict[str, dict[str, Any]] = {}
    for ip, headers in responses.items():
        description = _upnp_description(headers["location"], ip)
        devices[ip] = {
            **description,
            "source": "UPnP",
            "services": ["UPnP"],
            "properties": {
                "server": headers.get("server", ""),
                "usn": headers.get("usn", ""),
            },
        }
    return devices


def format_mac_address(mac: str | None) -> str | None:
    if not isinstance(mac, str) or not mac:
        return None
    try:
        parts = mac.replace("-", ":").split(":")
        if len(parts) != 6 or any(not part or len(part) > 2 for part in parts):
            return None
        octets = bytes(int(part, 16) for part in parts)
    except (ValueError, TypeError):
        return None
    return ":".join(f"{octet:02X}" for octet in octets)


def is_valid_unicast_mac(mac: str | None) -> bool:
    formatted = format_mac_address(mac)
    if not formatted:
        return False
    octets = bytes(int(part, 16) for part in formatted.split(":"))
    return len(octets) == 6 and any(octets) and octets != b"\xff" * 6 and not (octets[0] & 1)


def subnet_reserved_addresses(cidr: str | None) -> set[str]:
    if not cidr:
        return set()
    try:
        network = ipaddress.IPv4Network(cidr, strict=False)
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
        return set()
    if network.prefixlen >= 31:
        return set()
    return {str(network.network_address), str(network.broadcast_address)}
