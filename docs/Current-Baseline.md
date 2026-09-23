# Current Functional Baseline

## Baseline identity

| Field | Value |
| --- | --- |
| Name | Ramrattan IP Scanner v1.1.1 - Desktop Discovery Maintenance Release |
| Release tag | `v1.1.1` |
| Functional commit | `7ee0d6544309b011d9bddc3f59013935edde6e02` |
| Prior accepted baseline | v1.1.0 Desktop Application Release |
| Baseline branch | `main` |
| Review vehicle | Pull request #5, owner-approved 2026-09-23 |
| Historical base | `v1.07` at `fc50a2bbde29c63afb2c2fe443f3bc454c641ad9` |
| Product state | Owner-accepted unsigned desktop release for Intel Mac, Apple silicon Mac, and Windows x64 |

The v1.1.1 release stabilizes packaged discovery and diagnostics, preserves
shared/proxy observations, corrects desktop lifecycle and icon behavior, and
adds the accepted history-first layout with fixed-axis chart zoom.  Version
1.1.0 remains the immediate desktop rollback release.

## Resolved corrective investigation

Testing on 2026-09-22 found that the Finder-launched Intel Mac v1.1.0 package
recorded 236 probe errors across a 255-address scan, while the same source run
from Terminal recorded no probe errors.  Version 1.1.1 bounds packaged resource
use, retries unanswered addresses, preserves settled neighbor snapshots, and
records final probe diagnostics.  Packaged Intel Mac QA confirmed the corrected
behavior before owner approval and publication.

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
- CI run 53 passed at functional checkpoint `7c420b8`, which contains the
  accepted functional changes represented by merge commit `7ee0d65`.
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
- CSV export, IPv6 discovery, and signed installers are not available in this
  release.  The published desktop packages are unsigned.

## Change control

- Treat release tag `v1.1.1` on `main` as the current protected starting point.
  Preserve `v1.1.0` as the immediate desktop rollback release, `v1.0.0` as the
  rollback source release, and `v1.07` as the audited historical checkpoint.
- Develop material changes on focused branches and merge them only after tests,
  CI, documentation reconciliation, and owner approval.
- Record new behavior in tests, Help, Changelog, Kanban, and this baseline.
- Establish a new named baseline when behavior materially changes.
