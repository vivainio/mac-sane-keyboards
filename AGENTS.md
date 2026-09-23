# AGENTS.md

Guide for agents customizing the user's macOS keyboard layout in this repo.
A layout = a stock base `.keylayout` (`base/`) + a small Python patch (`layouts/`).
Never hand-edit `.keylayout` XML; change the patch and rebuild.

## Workflow

1. Find the key code(s) to change (see "Key codes").
2. Edit the existing `layouts/*.py`, or copy `layouts/fin_dev.py` to a new file
   for a separate layout. The file must define `LAYOUT = Layout(...)`.
3. Run `./build.py` (output goes to `build/`). Fix any errors.
4. Verify with `./kb.py diff <name>` (compares against its base): only the intended
   keys/states should differ. `./kb.py show <name>` prints a compact key table,
   `./kb.py key <name> <code>` shows one key, `./kb.py key -c <name> '~'` finds where a
   character is typed. Dead keys appear as `◌x`.
5. Installing needs sudo, so tell the user to run `./build.py install` themselves
   rather than running it. Afterwards they must log out and back in, then add the
   layout under System Settings → Keyboard → Text Input.

## Layout file

```python
from kbd import Layout, State as S

LAYOUT = Layout(
    name="FIN-my-layout",      # bundle/file name, no spaces
    display="FIN my layout",   # shown in System Settings
    base="FIN",                # uses base/FIN.keylayout
    patch={
        30: {S.plain: "~", S.shift: "^", S.option: "¨"},  # key code -> state -> output
    },
)
```

- `State`: plain, shift, caps, option, shift_option, caps_option, cmd_option, control.
- Only list the keys/states that change; everything else is inherited from the base.
- Outputs are literal strings. To remove dead keys, patch the key to output the character directly.
- Comment each patch line with the physical key it affects.

## Key codes

Key codes are macOS virtual key codes for the physical key (ANSI/ISO position),
not characters. To find one, look up the key in `base/FIN.keylayout`
(`<key code="N" .../>` in the relevant `keyMap`), or diff two layouts.
Example: 24 is the ´ key, 30 is the ¨ key on Finnish ISO.

Tip: the `unxml` command is handy for peeking into `.keylayout` files
(e.g. `unxml base/FIN.keylayout`) without wading through raw XML.

## Using a different base layout

Dump the stock layout from macOS, then reference it via `base=`:

```bash
swift tools/dump_layout.swift com.apple.keylayout.<InputSourceID> <BASE> > base/<BASE>.keylayout
```

`<InputSourceID>` is e.g. `Finnish`, `US`, `Swedish`. Also copy an `.icns` to
`base/<BASE>.icns` if the build expects one.

## Gotchas

- Layout `name` must not contain spaces (`Layout` raises otherwise).
- The base file contains XML 1.1 control-char references; `build.py` handles
  them, so don't parse/rewrite the file with other tools.
- `build/` is generated; don't commit it.
- Keep patches minimal so the diff against stock stays reviewable.
