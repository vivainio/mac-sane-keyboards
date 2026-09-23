#!/usr/bin/env python3
"""Print key outputs that differ between two .keylayout files (dead keys shown as DEAD).

    tools/diff_layouts.py a.keylayout b.keylayout
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import build  # noqa: E402  (build.main() only runs via __main__)

STATES = ["plain", "shift", "caps", "option", "shift_option", "caps_option", "cmd_option", "control"]


def table(path):
    root = build.read_xml(Path(path))
    acts = {}
    for a in root.find("actions"):
        w = [x for x in a if x.get("state") == "none"]
        acts[a.get("id")] = w[0].get("output") if w and w[0].get("output") is not None else "DEAD"
    sets = {ms.get("id"): ms for ms in root.findall("keyMapSet")}

    def keys(ms, idx):
        km = next(k for k in sets[ms] if k.get("index") == str(idx))
        d = keys(km.get("baseMapSet"), km.get("baseIndex")) if km.get("baseMapSet") else {}
        for k in km:
            d[int(k.get("code"))] = k.get("output") if k.get("output") is not None else acts[k.get("action")]
        return d

    t = {}
    lay = root.find("layouts")[0]  # first/last are keyboard types, not key codes
    for idx in range(8):
        for code, out in keys(lay.get("mapSet"), idx).items():
            t[(code, STATES[idx])] = out
    return t


a, b = table(sys.argv[1]), table(sys.argv[2])
for k in sorted(set(a) | set(b)):
    if a.get(k) != b.get(k):
        print(f"code {k[0]:3} {k[1]:13} {a.get(k)!r} -> {b.get(k)!r}")
