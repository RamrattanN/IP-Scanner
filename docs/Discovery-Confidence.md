# Discovery Evidence and Confidence

IP Scanner reports only facts observed locally.  It does not infer a device
name, manufacturer, model, or service when the network does not advertise that
information.

## Discovery sources

| Source | Meaning | Typical devices |
| --- | --- | --- |
| ICMP | The address answered an IPv4 echo request | Routers, computers, printers |
| TCP | One or more selected TCP services accepted a connection | Computers, NAS, printers, web devices |
| ARP | The operating system observed an IPv4-to-MAC association | Devices on the local layer-2 network |
| mDNS | A Bonjour/mDNS service announced an address and identity | Apple, printers, media and smart-home devices |
| UPnP | A device answered SSDP and optionally supplied a description | Routers, TVs, media and smart-home devices |
| NetBIOS | A device returned a unique node-status name | Windows and compatible file-sharing devices |

## Confidence levels

- **High:** A discovery protocol supplied identity, or multiple active sources
  independently answered.
- **Medium:** One active source, such as ICMP or TCP, answered.
- **Observed:** Only a unique ARP association was available.  The address may
  represent a sleeping device or a recently cached neighbor.

Confidence describes the strength of the current observation.  It is not a
security rating and does not establish device ownership.

## Artifact controls

- Every address in the requested range is attempted and counted in coverage.
- Subnet network and broadcast addresses are excluded from device totals.
- Broadcast, multicast, all-zero, and malformed MAC addresses are rejected.
- When one MAC appears across four or more requested IP addresses, ARP-only
  entries using that MAC are treated as likely proxy-ARP artifacts and excluded.
- An IP with an active response remains visible even when its ARP MAC is shared.
  The MAC is labelled as a shared or proxy response instead of being presented
  as that device's confirmed hardware address.

## Expected unknown values

A device may legitimately show `Not advertised` when it does not publish a
name or product description through reverse DNS, mDNS, UPnP, or NetBIOS.  A MAC
address may show `Not available` when the device is routed, isolated, or hidden
behind a network intermediary.  IP Scanner preserves those boundaries rather
than presenting a guess as a discovered fact.

## MAC addresses and manufacturers

- MAC addresses use uppercase colon-separated formatting.
- `Observed` in the MAC status column means the address was associated with one
  displayed device during the scan.
- `Shared/proxy response` means the same address appeared for multiple IPs.  It
  remains visible as evidence but is not presented as confirmed device hardware.
- When a valid globally administered MAC is available and the discovery
  protocols do not publish a manufacturer, IP Scanner checks the bundled local
  IEEE OUI list.
- Locally administered and randomized MAC addresses are not assigned an OUI
  manufacturer.
- Vendor lookup happens locally.  Scanned MAC addresses are not sent to an
  external lookup service.

## Device type icons

Type icons summarize observed names, services, manufacturer or model, and
gateway role.  Supported labels are Router, Computer, Printer, TV, Audio, NAS,
Mobile, IoT, and Other.  They are navigation aids, not authoritative identity
claims.  Other is used when evidence is insufficient.
