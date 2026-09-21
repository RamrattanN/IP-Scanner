# Current Functional Baseline

## Baseline identity

| Field | Value |
| --- | --- |
| Name | Inventory Baseline Candidate 2026.09.21 |
| Functional commit | `7b1602dfc4123e5159e54e3b6a7347f7741e8d2e` |
| Prior accepted checkpoint | Recovery Baseline 2026.09.21 at `22f2b6ec1dbfe8661daf956bc985539f3ef5c03f` |
| Development branch | `recovery/cross-platform-desktop` |
| Review vehicle | Draft pull request #1 |
| Historical base | `v1.07` at `fc50a2bbde29c63afb2c2fe443f3bc454c641ad9` |
| Product state | Development candidate awaiting inventory acceptance, not a production release |

Documentation commits after the functional commit may clarify the checkpoint
without changing the functional identity above.  Any later behavioral change
must establish a new functional checkpoint.

## Available behavior

### Scan coverage

- Detects the active IPv4 adapter and default gateway on macOS, Windows, and
  Linux.
- Accepts either the detected network or an inclusive custom IPv4 start-to-end
  range.
- Attempts every requested address, subject to the 4,096-address safety limit.
- Records requested, attempted, probe-error, confirmed-device, and observed
  ARP-only counts separately.

### Device discovery

- Combines ICMP, selected TCP connections, and the operating system neighbor
  table instead of requiring an ICMP reply.
- Enriches identity with reverse DNS, Bonjour/mDNS, UPnP, NetBIOS, and safe web
  metadata when a device publishes those facts.
- Records MAC addresses, evidence, common open services, gateway role,
  identity source, manufacturer or model when advertised, and confidence.
- Uses High, Medium, and Observed confidence without presenting confidence as a
  security or ownership rating.

### Result integrity

- Excludes subnet network and broadcast addresses from device totals while
  retaining them in attempted coverage.
- Rejects invalid, all-zero, broadcast, and multicast MAC addresses.
- Suppresses repeated proxy-ARP-only artifacts.  An actively responding IP
  remains visible and is labelled when its MAC response is shared.
- Uses `Not advertised` and `Not available` when a fact cannot be established.

### Application experience

- Uses the Ramrattan Network Tools family header, logo, palette, buttons,
  cards, tables, empty states, and right-side Help pattern.
- Stores selectable scan history and device-level results locally.
- Binds the documented application service to the local loopback address.
- Supports keyboard selection of history rows and keyboard dismissal of Help.
- Maintains a separate local device inventory with first-seen and last-seen
  timestamps, observation counts, current evidence, and private user labels.
- Seeds a new inventory from the most recent existing completed scan and then
  reconciles every subsequent scan.

## Verification evidence

- Thirty-one automated tests pass locally and in the operating-system CI matrix.
- Source compilation, JavaScript syntax validation, wheel build, and isolated
  wheel installation pass.
- GitHub Actions push run 9 and pull-request run 10 each passed all seven jobs:
  Ubuntu, macOS, and Windows on Python 3.11 and 3.12, plus package smoke test.
- Owner review on Intel Mac accepted the refreshed discovery interface and
  results.  Inventory layout, seeding, repeat counts, and label editing remain
  open for owner acceptance.

CI validates the shared source and package contents.  Native behavior and final
installers still require hands-on acceptance on each target product.

## Known boundaries

- Identity depends on what devices and local discovery protocols advertise.
- A firewall, client isolation, routed network, sleeping device, or disabled
  multicast can reduce the evidence available.
- Port checks cover a selected common-service set, not every TCP or UDP port.
- Scans currently run as one request without progress reporting or cancellation.
- Inventory reconciliation is intentionally conservative and may retain
  separate records when evidence is insufficient to prove they are one device.
- CSV export, IPv6 discovery, offline MAC-vendor data, signed installers, and
  release publishing are not available in this baseline.

## Change control

- Keep `main` and `v1.07` unchanged until explicit merge approval.
- Keep pull request #1 in draft while target-native acceptance remains open.
- Record new behavior in tests, Help, Changelog, Kanban, and this baseline.
- Establish a new named baseline when behavior materially changes.
