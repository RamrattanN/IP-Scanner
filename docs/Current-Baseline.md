# Current Functional Baseline

## Baseline identity

| Field | Value |
| --- | --- |
| Name | Ramrattan IP Scanner v1.1.0 - Desktop Application Release |
| Release tag | `v1.1.0` |
| Functional commit | `1e87518bb030fa8cf5d6ca84518cd0644f3691ad` |
| Prior accepted baseline | v1.0.0 Discovery Experience Release |
| Baseline branch | `main` |
| Review vehicle | Pull request #4, owner-approved 2026-09-21 |
| Historical base | `v1.07` at `fc50a2bbde29c63afb2c2fe443f3bc454c641ad9` |
| Product state | Owner-accepted unsigned desktop release for Intel Mac, Apple silicon Mac, and Windows x64 |

The v1.1.0 release adds scheduled collection and native desktop packaging
without changing the accepted discovery model.  The v1.0.0 source release
remains the documented rollback baseline.

## Active corrective candidate

Testing on 2026-09-22 found that the Finder-launched Intel Mac v1.1.0 package
recorded 236 probe errors across a 255-address scan, while the same source run
from Terminal recorded no probe errors.  The accepted v1.1.0 tag remains
unchanged.  Corrective work is isolated on `fix/v1.1.1-macos-discovery` and is
not a new baseline until packaged Intel Mac QA and owner approval are complete.

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
- Supports configurable automatic detected-network scans, serialized with
  manual scans, with explicit freshness and next-run information.
- Provides a shared single-instance desktop lifecycle on Intel Mac, Apple
  silicon Mac, and Windows x64.
- Uses the Ramrattan shield favicon and Apple touch icon shared with Speedtest
  Monitor.
- Supports keyboard selection of history rows and keyboard dismissal of Help.

## Verification evidence

- The automated regression suite, source compilation, JavaScript syntax
  validation, wheel build, and isolated wheel installation pass.
- CI run 44 passed at functional checkpoint `1e87518`.
- The Intel Mac, Apple silicon Mac, and Windows x64 workflows built and
  smoke-tested their target-native packages successfully.
- Owner QA accepted all three target packages for publication.

CI validates the shared source and package contents.  Owner QA provides the
target-native acceptance evidence for this release.

## Known boundaries

- Identity depends on what devices and local discovery protocols advertise.
- A firewall, client isolation, routed network, sleeping device, or disabled
  multicast can reduce the evidence available.
- Port checks cover a selected common-service set, not every TCP or UDP port.
- Manufacturer and device-type values depend on published registrations and
  observed heuristics.  They are not ownership or security assertions.
- Scans currently run as one request without progress reporting or cancellation.
- Scan history is not a persistent reconciled device inventory.
- The published Intel Mac v1.1.0 package can exhaust the lower open-file limit
  of a Finder-launched process on a broad scan.  Use the source version for the
  most complete discovery until the v1.1.1 candidate is accepted.
- CSV export, IPv6 discovery, and signed installers are not available in this
  release.  The published desktop packages are unsigned.

## Change control

- Treat release tag `v1.1.0` on `main` as the current protected starting
  point.  Preserve `v1.0.0` as the rollback source release and `v1.07` as the
  audited historical checkpoint.
- Develop material changes on focused branches and merge them only after tests,
  CI, documentation reconciliation, and owner approval.
- Record new behavior in tests, Help, Changelog, Kanban, and this baseline.
- Establish a new named baseline when behavior materially changes.
