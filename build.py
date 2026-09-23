#!/usr/bin/env python3
"""Build macOS keyboard layout bundles from base/*.keylayout + layouts/*.py.

    ./build.py            build all layouts into build/
    ./build.py install    build, then copy to /Library/Keyboard Layouts (sudo)
"""
import importlib.util, plistlib, re, shutil, subprocess, sys, zlib
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
STATES = dict(plain=0, shift=1, caps=2, option=3, shift_option=4, caps_option=5)
HEADER = ('<?xml version="1.1" encoding="UTF-8"?>\n'
          '<!DOCTYPE keyboard SYSTEM "file://localhost/System/Library/DTDs/KeyboardLayout.dtd">\n')


# The base file has XML 1.1 control-char references (&#x0001;) that expat rejects;
# swap them for private-use chars while parsing and swap back on output.
CTRL = re.compile(r"&#x00([01][0-9A-Fa-f]);")
PUA = re.compile("[\uf000-\uf01f]")


def read_xml(path):
    text = path.read_text()
    text = CTRL.sub(lambda m: chr(0xF000 + int(m.group(1), 16)), text)
    return ET.fromstring(text.split("?>", 1)[1])


def write_xml(root):
    text = ET.tostring(root, encoding="unicode")
    return HEADER + PUA.sub(lambda m: f"&#x{ord(m.group()) - 0xF000:04X};", text)


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def keymap(root, code, index):
    """The keyMap element that holds `code` for modifier state `index`."""
    for lay in root.find("layouts"):
        if int(lay.get("first")) <= code <= int(lay.get("last")):
            mapset = lay.get("mapSet")
            break
    else:
        sys.exit(f"key code {code} not in layout")
    for ms in root.findall("keyMapSet"):
        if ms.get("id") == mapset:
            for km in ms:
                if km.get("index") == str(index):
                    return km
    sys.exit(f"no keyMap {index} for key code {code}")


def patch(root, patches):
    for code, states in patches.items():
        for state, out in states.items():
            km = keymap(root, code, STATES[state])
            key = next((k for k in km if k.get("code") == str(code)), None)
            if key is None:
                key = ET.SubElement(km, "key", code=str(code))
            key.attrib.pop("action", None)
            key.set("output", out)


def build(layout):
    ident = "com.vivainio.keyboardlayout." + layout.NAME.replace("-", "").lower()
    root = read_xml(ROOT / "base" / f"{layout.BASE}.keylayout")
    root.set("name", layout.NAME)
    root.set("id", str(-(zlib.crc32(layout.NAME.encode()) % 30000 + 1)))
    patch(root, layout.PATCH)

    contents = ROOT / "build" / f"{layout.NAME}.bundle" / "Contents"
    res = contents / "Resources"
    shutil.rmtree(contents.parent, ignore_errors=True)
    (res / "fi_FI.lproj").mkdir(parents=True)
    ET.indent(root)
    (res / f"{layout.NAME}.keylayout").write_text(write_xml(root))
    icon = ROOT / "base" / f"{layout.BASE}.icns"
    if icon.exists():
        shutil.copy(icon, res / f"{layout.NAME}.icns")
    (res / "fi_FI.lproj" / "InfoPlist.strings").write_text(
        f'"{layout.NAME}" = "{layout.DISPLAY}";\n', encoding="utf-16")
    with open(contents / "Info.plist", "wb") as f:
        plistlib.dump({
            "CFBundleIdentifier": ident,
            "CFBundleName": layout.NAME,
            "CFBundleVersion": "1.0",
            "CFBundleShortVersionString": "1.0",
            f"KLInfo_{layout.NAME}": {
                "TISInputSourceID": f"{ident}.{layout.NAME.replace('-', '').lower()}",
                "TISIntendedLanguage": "fi",
                "TICapsLockLanguageSwitchCapable": False,
                "TISIconIsTemplate": False,
            },
        }, f)
    return contents.parent


def main():
    bundles = [build(load(p)) for p in sorted((ROOT / "layouts").glob("*.py"))]
    for b in bundles:
        print("built", b.relative_to(ROOT))
    if sys.argv[1:] == ["install"]:
        dest = Path("/Library/Keyboard Layouts")
        subprocess.run(["sudo", "mkdir", "-p", str(dest)], check=True)
        for b in bundles:
            subprocess.run(["sudo", "rm", "-rf", str(dest / b.name)], check=True)
            subprocess.run(["sudo", "cp", "-R", str(b), str(dest)], check=True)
        print("Installed. Log out/in, then add the layout in System Settings > Keyboard > Text Input.")


main()
