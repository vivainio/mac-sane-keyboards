# mac-sane-keyboards

**FIN dev layout**: the stock macOS Finnish layout, changed so that programming
characters are easy to type. It has no dead keys and puts `~ / \ ( )` on single keys.

## What changed

Everything else is stock Finnish. Only these keys differ:

| Key (Finnish label) | Was | Now | Why |
|---|---|---|---|
| top left `§ °` | `§` `°` | `~` plain, `` ` `` shift | `§` and `°` are rarely needed; tilde and backtick are common in code and shells |
| `´` key, right of `+` | dead key `´` `` ` `` | `(` plain, `)` shift | dead key removed; parens without reaching for shift+8/9 |
| `¨` key | dead key `¨` `^` `~` | `\` plain, `\|` shift, `^` option | dead key removed; backslash is an option+shift chord on stock |
| `å` key | `å` `Å` | `/` plain, `?` shift | slash is shift+7 on stock; `å` moves to option (below) |
| option + `å` key | `˙` `˚` | `å` `Å` | `å` is still reachable on its own key |
| option + `a` | Apple logo | `å` `Å` | same as on a US Mac layout, easy to remember |
| option + `e` | `é` | `€` | euro stays available |
| shift + `4` | `€` | `$` | dollar on a plain shift, like on a US keyboard |

Notes:

- No key on this layout is a dead key, in any state (including Caps Lock), so what
  you press is what you get.
- `[ ] { }` are still on option+8/9 (with shift for the curlies), and `|` is still on option+7.
- `ä` and `ö` are unchanged.

See also the Mac tutorial
[Everyday Shortcuts](https://vivainio.github.io/articles/learning-mac/everyday-shortcuts/)
for the modifier keys, common shortcuts and other ways to make the keyboard fit you.

## Install

    curl -fsSL https://raw.githubusercontent.com/vivainio/mac-sane-keyboards/main/install.sh | bash

Downloads `FIN-dev-layout.zip` from the latest GitHub release and copies the bundle to
`/Library/Keyboard Layouts` (asks for sudo). Then log out and back in and add
"FIN dev layout" under System Settings → Keyboard → Text Input → Edit… → **+**.

## Function keys

Making F1–F12 work without holding Fn is a macOS setting, not part of a layout:
System Settings → Keyboard → Keyboard Shortcuts… → Function Keys → "Use F1, F2, etc.
keys as standard function keys", or

    defaults write -g com.apple.keyboard.fnState -bool true

Log out and back in if it doesn't apply right away.

## Building and changing the layout

The layout is the stock Finnish `.keylayout` (`base/FIN.keylayout`, dumped from macOS with
`tools/dump_layout.swift`) plus a small Python patch in [layouts/fin_dev.py](layouts/fin_dev.py):

    ./kb.py show fin_dev          compact key table
    ./kb.py diff fin_dev          what differs from stock
    ./kb.py key fin_dev 30        one key, all modifier states
    ./kb.py key -c fin_dev '~'    where a character is typed
    ./kb.py install               build and install from source (sudo)
    ./kb.py package               zip the bundle into dist/
    ./kb.py release v1.0          package and publish a GitHub release (needs gh)

Layouts are `layouts/<name>.py` files defining `LAYOUT`:

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
See [AGENTS.md](AGENTS.md) for details.
