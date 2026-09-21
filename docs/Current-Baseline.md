# Current Functional Baseline

## Baseline identity

| Field | Value |
| --- | --- |
| Name | Ramrattan IP Scanner v1.0.0 - Discovery Experience Release |
| Release tag | `v1.0.0` |
| Functional commit | `9cd37a98525acda67278d9902c6afcc28be638c4` |
| Main integration commit | `47d0bc66e7af4c979e5a3c281d70148ff5f7cddb` |
| Documentation integration commit | `856fea31658159ec36f0c18fff9a1337c63428d3` |
| Prior accepted baseline | Recovery Baseline 2026.09.21 at `22f2b6ec1dbfe8661daf956bc985539f3ef5c03f` |
| Baseline branch | `main` |
| Review vehicle | Pull request #1, merged 2026-09-21 |
| Historical base | `v1.07` at `fc50a2bbde29c63afb2c2fe443f3bc454c641ad9` |
| Product state | Owner-accepted v1.0.0 source release; standalone installers are not included |

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
- Enriches missing manufacturer values from a bundled local IEEE OUI list for
  valid globally administered MAC addresses.
- Formats MAC addresses consistently and separates shared/proxy status from the
  address value.
- Provides evidence-based device-type icons and sortable history and result
  columns.
- Lets users resize Device Results columns with a pointer or keyboard, restores
  a column by double-click or Home, and retains widths in local browser storage.
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
- Charts total devices and device-type composition over time in stacked bar or
  area form, and charts the latest scan mix as a pie with hover metrics.
- Uses a shared device-type key with matched icons, colours, percentages, and
  counts for both discovery charts.
- Binds the documented application service to the local loopback address.
- Supports keyboard selection of history rows and keyboard dismissal of Help.

## Verification evidence

- Twenty-nine automated tests pass locally.
- Source compilation, JavaScript syntax validation, wheel build, and isolated
  wheel installation pass.
- GitHub Actions run 38 passed all seven jobs against the merged `main`: Ubuntu,
  macOS, and Windows on Python 3.11 and 3.12, plus the package smoke test.
- Owner review on Intel Mac accepted the refreshed discovery interface,
  results, visualizations, device-type summary, and table interactions.

CI validates the shared source and package contents.  Native behavior and final
installers still require hands-on acceptance on each target product.

## Known boundaries

- Identity depends on what devices and local discovery protocols advertise.
- A firewall, client isolation, routed network, sleeping device, or disabled
  multicast can reduce the evidence available.
- Port checks cover a selected common-service set, not every TCP or UDP port.
- Manufacturer and device-type values depend on published registrations and
  observed heuristics.  They are not ownership or security assertions.
- Scans currently run as one request without progress reporting or cancellation.
- Scan history is not a persistent reconciled device inventory.
- Standalone desktop applications, CSV export, IPv6 discovery, and signed
  installers are not available in this source release.

## Change control

- Treat release tag `v1.0.0` on `main` as the protected starting point for
  subsequent work.  Preserve `v1.07` as the audited historical checkpoint.
- Develop material changes on focused branches and merge them only after tests,
  CI, documentation reconciliation, and owner approval.
- Record new behavior in tests, Help, Changelog, Kanban, and this baseline.
- Establish a new named baseline when behavior materially changes.
