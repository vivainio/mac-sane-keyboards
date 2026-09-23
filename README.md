# mac-sane-keyboards

FIN-dev-layout:

Finnish Mac keyboard layout without dead keys, for development.

- `~` and backtick are single keypresses (no Option, no dead key).
- `´` is behind Shift (swapped with backtick), `¨` is behind Option.
- `^` still needs Shift but is no longer a dead key.
- Everything else is the standard Finnish layout.

Based on https://github.com/saneDG/keyboard-layout-FIN-no-deadkeys

## Install

    ./install.sh

Copies the bundle to `/Library/Keyboard Layouts/` (needs sudo). Log out and back in,
then add "FIN dev layout" in System Settings → Keyboard → Text Input.
