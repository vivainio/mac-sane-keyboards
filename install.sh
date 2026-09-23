#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
sudo mkdir -p "/Library/Keyboard Layouts"
sudo rm -rf "/Library/Keyboard Layouts/FIN-dev-layout.bundle"
sudo cp -R FIN-dev-layout.bundle "/Library/Keyboard Layouts/"
echo "Installed. Log out and back in, then add 'FIN dev layout' in System Settings -> Keyboard -> Text Input."
