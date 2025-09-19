from __future__ import annotations
import ipaddress

def cidr_from_adapter(adapter: dict) -> str:
    ipv4 = adapter["ipv4"]
    netmask = adapter.get("netmask") or "255.255.255.0"
    network = ipaddress.IPv4Network((ipv4, netmask), strict=False)
    return f"{network.network_address}/{network.prefixlen}"

def cidr_to_range(cidr: str) -> tuple[str, str]:
    net = ipaddress.IPv4Network(cidr, strict=False)
    # Commonly skip .0 and use .1 as first usable
    hosts = list(net.hosts())
    if not hosts:
        return (str(net.network_address), str(net.broadcast_address))
    start = str(hosts[0])
    end = str(net.broadcast_address)
    return (start, end)
