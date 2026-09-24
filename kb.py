#!/usr/bin/env python3
"""Inspect and build keyboard layouts.

    ./kb.py list                      layouts and bases
    ./kb.py show fin_dev [--all]      compact key table (dead keys shown as ◌x)
    ./kb.py key fin_dev 30            all states of key code 30
    ./kb.py key -c fin_dev '~'        where a character can be typed
    ./kb.py diff fin_dev [other]      differences (default: against its base)
    ./kb.py install                   build bundles and install them (sudo)

<layout> is a layouts/<name>.py, a base/<name>.keylayout, or a file path.
"""
import argparse, sys
from pathlib import Path

import build
from kbd import State

ROOT = build.ROOT
STATES = list(State)

# macOS virtual key code -> key cap (ISO position); grouped by keyboard row
ROWS = [
    [(10, "§"), (18, "1"), (19, "2"), (20, "3"), (21, "4"), (23, "5"), (22, "6"),
     (26, "7"), (28, "8"), (25, "9"), (29, "0"), (27, "-"), (24, "=")],
    [(12, "q"), (13, "w"), (14, "e"), (15, "r"), (17, "t"), (16, "y"), (32, "u"),
     (34, "i"), (31, "o"), (35, "p"), (33, "["), (30, "]"), (42, "\\")],
    [(0, "a"), (1, "s"), (2, "d"), (3, "f"), (5, "g"), (4, "h"), (38, "j"),
     (40, "k"), (37, "l"), (41, ";"), (39, "'")],
    [(50, "<"), (6, "z"), (7, "x"), (8, "c"), (9, "v"), (11, "b"),
     (45, "n"), (46, "m"), (43, ","), (47, "."), (44, "/")],
    [(49, "space")],
]
CAP = {code: cap for row in ROWS for code, cap in row}
ORDER = [code for row in ROWS for code, _ in row]


def resolve(arg):
    """-> (root element, description) for a layout name or path."""
    p = Path(arg)
    if p.suffix == ".keylayout" and p.exists():
        return build.read_xml(p), arg
    py = ROOT / "layouts" / f"{arg}.py"
    if py.exists():
        layout = build.load(py)
        root = build.read_xml(ROOT / "base" / f"{layout.base}.keylayout")
        build.patch(root, layout.patch)
        return root, f"layouts/{arg}.py (base {layout.base})"
    kl = ROOT / "base" / f"{arg}.keylayout"
    if kl.exists():
        return build.read_xml(kl), f"base/{arg}.keylayout"
    sys.exit(f"unknown layout: {arg}")


def base_of(arg):
    py = ROOT / "layouts" / f"{arg}.py"
    return build.load(py).base if py.exists() else None


def table(root):
    """{(code, State): output}; dead keys are '◌' + the character they produce."""
    terms = {w.get("state"): w.get("output") for w in root.find("terminators")}
    acts = {}
    for a in root.find("actions"):
        w = next((x for x in a if x.get("state") == "none"), None)
        if w is None:
            continue
        acts[a.get("id")] = w.get("output") if w.get("output") is not None else "◌" + terms.get(w.get("next"), "?")
    sets = {ms.get("id"): ms for ms in root.findall("keyMapSet")}

    def keys(ms, idx):
        km = next(k for k in sets[ms] if k.get("index") == str(idx))
        d = keys(km.get("baseMapSet"), km.get("baseIndex")) if km.get("baseMapSet") else {}
        for k in km:
            out = k.get("output")
            d[int(k.get("code"))] = out if out is not None else acts.get(k.get("action"), "?")
        return d

    lay = root.find("layouts")[0]
    return {(code, STATES[i]): out for i in range(len(STATES))
            for code, out in keys(lay.get("mapSet"), i).items()}


def show_char(s):
    return "".join(c if c.isprintable() and c != " " else f"\\u{ord(c):04x}" for c in s) if s else "·"


def cmd_list(_):
    for d in ("layouts", "base"):
        print(f"{d}/:", *(p.stem for p in sorted((ROOT / d).glob("*.py" if d == "layouts" else "*.keylayout"))))


def cmd_show(a):
    root, desc = resolve(a.layout)
    t = table(root)
    states = STATES if a.all else [State.plain, State.shift, State.option, State.shift_option]
    print(f"# {desc}")
    print(f"{'code':>4} {'key':<6}" + "".join(f"{s.value:<13}" for s in states))
    for code in ORDER:
        print(f"{code:>4} {CAP[code]:<6}" + "".join(f"{show_char(t.get((code, s), '')):<13}" for s in states))


def cmd_key(a):
    root, desc = resolve(a.layout)
    t = table(root)
    if not a.char:
        code = int(a.key)
        print(f"# {desc}: code {code} ({CAP.get(code, '?')})")
        for s in STATES:
            print(f"  {s.value:<13}{show_char(t.get((code, s), ''))}")
    else:
        print(f"# {desc}: where {a.key!r} is typed")
        for (code, s), out in sorted(t.items(), key=lambda kv: (kv[0][0], STATES.index(kv[0][1]))):
            if out == a.key:
                print(f"  code {code:<3} ({CAP.get(code, '?')}) {s.value}")


def cmd_diff(a):
    other = a.other or base_of(a.layout)
    if not other:
        sys.exit("no other layout given and no base known")
    ta, tb = table(resolve(other)[0]), table(resolve(a.layout)[0])
    print(f"# {other} -> {a.layout}")
    for k in sorted(set(ta) | set(tb), key=lambda k: (k[0], STATES.index(k[1]))):
        if ta.get(k) != tb.get(k):
            code, s = k
            print(f"code {code:>3} {CAP.get(code, '?'):<5} {s.value:<13} {show_char(ta.get(k, ''))} -> {show_char(tb.get(k, ''))}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    p = sub.add_parser("show"); p.add_argument("layout"); p.add_argument("--all", action="store_true"); p.set_defaults(fn=cmd_show)
    p = sub.add_parser("key"); p.add_argument("layout"); p.add_argument("key", help="key code, or a character with -c"); p.add_argument("-c", "--char", action="store_true"); p.set_defaults(fn=cmd_key)
    p = sub.add_parser("diff"); p.add_argument("layout"); p.add_argument("other", nargs="?"); p.set_defaults(fn=cmd_diff)
    sub.add_parser("install").set_defaults(fn=lambda _: build.install())
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
