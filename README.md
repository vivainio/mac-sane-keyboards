# mac-sane-keyboards

macOS keyboard layouts defined as a base `.keylayout` plus small Python patches.

    base/FIN.keylayout    stock macOS Finnish layout (dumped with tools/dump_layout.swift)
    layouts/fin_dev.py    layout definition: name, base, PATCH table
    build.py              build library used by kb.py
    kb.py                 CLI: list/show/key/diff/install/package

    ./kb.py install       build into build/ + copy to /Library/Keyboard Layouts (sudo)
    ./kb.py package       zip bundles into dist/ (release assets)

## Install from a release

    curl -fsSL https://raw.githubusercontent.com/vivainio/mac-sane-keyboards/main/install.sh | bash

Downloads `FIN-dev-layout.zip` from the latest GitHub release and copies the bundle to
`/Library/Keyboard Layouts` (sudo). Pass a layout name to pick another:
`... | bash -s <name>`.

To publish a release, push a tag: `git tag v1.0 && git push --tags` (the
`release.yml` workflow builds the zips and attaches them).

After installing, log out and back in, then add the layout under
System Settings → Keyboard → Text Input.

## Defining a layout

Add `layouts/<name>.py` defining `LAYOUT`:

    from kbd import Layout, State

    LAYOUT = Layout(
        name="FIN-my-layout",     # no spaces
        display="FIN my layout",
        base="FIN",
        patch={
            30: {State.plain: "~", State.option: "¨"},   # key code -> state -> output
        },
    )

`State`: plain, shift, caps, option, shift_option, caps_option, cmd_option, control.

## Tools

    swift tools/dump_layout.swift com.apple.keylayout.Finnish FIN > base/FIN.keylayout
    ./kb.py show|key|diff ...     # inspect layouts compactly (see ./kb.py -h)
