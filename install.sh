#!/bin/bash
# Install a keyboard layout from the latest GitHub release.
#   curl -fsSL https://raw.githubusercontent.com/vivainio/mac-sane-keyboards/main/install.sh | bash
#   ... | bash -s FIN-dev-layout      # pick a layout (default: FIN-dev-layout)
set -euo pipefail

NAME="${1:-FIN-dev-layout}"
URL="https://github.com/vivainio/mac-sane-keyboards/releases/latest/download/$NAME.zip"
DEST="/Library/Keyboard Layouts"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Downloading $URL"
curl -fsSL "$URL" -o "$tmp/$NAME.zip"
unzip -q "$tmp/$NAME.zip" -d "$tmp"

sudo mkdir -p "$DEST"
sudo rm -rf "$DEST/$NAME.bundle"
sudo cp -R "$tmp/$NAME.bundle" "$DEST/"

echo "Installed $NAME. Log out and back in, then add it in"
echo "System Settings > Keyboard > Text Input > Edit > + ."
