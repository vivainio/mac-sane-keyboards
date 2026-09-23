# mac-sane-keyboards

macOS keyboard layouts defined as a base `.keylayout` plus small Python patches.

    base/FIN.keylayout    base layout (Finnish, no dead keys)
    layouts/fin_dev.py    layout definition: name, base, PATCH table
    build.py              builds bundles into build/

    ./build.py            build
    ./build.py install    build + copy to /Library/Keyboard Layouts (sudo)

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

`State`: plain, shift, caps, option, shift_option, caps_option.

`base/FIN.keylayout` is from
https://github.com/saneDG/keyboard-layout-FIN-no-deadkeys
(`~` and backtick on single keys, `¨` behind Option, no dead keys).
