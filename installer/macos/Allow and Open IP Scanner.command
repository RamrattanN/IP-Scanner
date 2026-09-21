#!/bin/bash
set -euo pipefail
APP="/Applications/IP Scanner.app"
if [[ ! -d "$APP" ]]; then
  echo "Copy IP Scanner.app to Applications, then run this helper again."
  read -r -p "Press Return to close."
  exit 1
fi
xattr -dr com.apple.quarantine "$APP"
open "$APP"
