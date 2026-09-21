# Third-Party Notices

## mac-vendor-lookup

IP Scanner uses `mac-vendor-lookup` to access a bundled local copy of the IEEE
OUI prefix list for manufacturer enrichment.

- Project: [bauerj/mac_vendor_lookup](https://github.com/bauerj/mac_vendor_lookup)
- Package: [mac-vendor-lookup on PyPI](https://pypi.org/project/mac-vendor-lookup/)
- License: Apache License 2.0
- Data source: [IEEE Registration Authority OUI list](https://standards-oui.ieee.org/oui/oui.txt)

The application reads the packaged local list.  It does not invoke the package's
optional network updater during scanning or history review, and it does not send
scanned MAC addresses to a vendor lookup service.
