// One-off: dump an installed macOS keyboard layout to a .keylayout XML file.
//   swift tools/dump_layout.swift com.apple.keylayout.Finnish > base/FIN.keylayout
import Carbon
import Foundation

let sourceID = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "com.apple.keylayout.Finnish"
let name = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : "FIN"

let filter = [kTISPropertyInputSourceID as String: sourceID] as CFDictionary
guard let list = TISCreateInputSourceList(filter, true)?.takeRetainedValue() as? [TISInputSource],
      let source = list.first,
      let ptr = TISGetInputSourceProperty(source, kTISPropertyUnicodeKeyLayoutData) else {
    FileHandle.standardError.write("layout not found: \(sourceID)\n".data(using: .utf8)!)
    exit(1)
}
let data = Unmanaged<CFData>.fromOpaque(ptr).takeUnretainedValue() as Data
let kbdType = UInt32(KBGetLayoutType(Int16(LMGetKbdType())))  // physical keyboard type

// keyMap index -> UCKeyTranslate modifier state (shift=2 caps=4 option=8 control=16)
let modStates: [UInt32] = [0, 2, 4, 8, 10, 12, 8, 16]
let keyCodes = Array(0..<128)

func translate(_ layout: UnsafePointer<UCKeyboardLayout>, _ code: Int, _ mods: UInt32,
               _ dead: inout UInt32) -> String {
    var chars = [UniChar](repeating: 0, count: 8)
    var len = 0
    let st = UCKeyTranslate(layout, UInt16(code), UInt16(kUCKeyActionDown), mods, kbdType,
                            0, &dead, 8, &len, &chars)
    return st == noErr ? String(utf16CodeUnits: chars, count: len) : ""
}

func esc(_ s: String) -> String {
    s.unicodeScalars.map { u -> String in
        switch u {
        case "&": return "&#x0026;"
        case "<": return "&#x003C;"
        case ">": return "&#x003E;"
        case "\"": return "&#x0022;"
        case "'": return "&#x0027;"
        default: return u.value < 0x20 || u.value == 0x7f ? String(format: "&#x%04X;", u.value) : String(u)
        }
    }.joined()
}

struct Table {
    var outputs: [Int: [Int: String]] = [:]      // map index -> code -> output
    var deadKeys: [Int: [Int: Int]] = [:]        // map index -> code -> dead state number
    var states: [String] = []                    // dead state ids
    var whenState: [[String: String]] = []       // per dead state: base char -> output
    var terminators: [String] = []               // standalone output per dead state
}

var t = Table()
data.withUnsafeBytes { raw in
    let layout = raw.baseAddress!.assumingMemoryBound(to: UCKeyboardLayout.self)
    // dead state value (from UCKeyTranslate) -> our state index
    var known: [UInt32: Int] = [:]
    for (mi, mods) in modStates.enumerated() {
        for code in keyCodes {
            var dead: UInt32 = 0
            let out = translate(layout, code, mods, &dead)
            if dead != 0 {
                if known[dead] == nil {
                    known[dead] = t.terminators.count
                    var d2 = dead
                    t.terminators.append(translate(layout, 49, 0, &d2))  // space -> standalone char
                    t.whenState.append([:])
                }
                t.deadKeys[mi, default: [:]][code] = known[dead]!
            } else if !out.isEmpty {
                t.outputs[mi, default: [:]][code] = out
            }
        }
    }
    // outputs of every key after each dead state (plain + shift + option maps)
    for (dv, si) in known {
        for mods in modStates[0...5] {
            for code in keyCodes {
                var d = dv
                let out = translate(layout, code, mods, &d)
                if out.unicodeScalars.count == 1, out != t.terminators[si] {
                    // record by base char (the char that key gives with no dead state)
                    var d0: UInt32 = 0
                    let base = translate(layout, code, mods, &d0)
                    if d0 == 0, !base.isEmpty { t.whenState[si][base] = out }
                }
            }
        }
    }
}

func composable(_ c: String) -> Bool { t.whenState.contains { $0[c] != nil } }
func charAction(_ c: String) -> String { "c" + c.unicodeScalars.map { String($0.value, radix: 16) }.joined(separator: "_") }

var x = """
<?xml version="1.1" encoding="UTF-8"?>
<!DOCTYPE keyboard SYSTEM "file://localhost/System/Library/DTDs/KeyboardLayout.dtd">
<keyboard group="126" id="-21847" name="\(name)" maxout="2">
    <layouts>
        <layout first="0" last="207" mapSet="ms" modifiers="mm"/>
    </layouts>
    <modifierMap id="mm" defaultIndex="0">
        <keyMapSelect mapIndex="0"><modifier keys="command?"/><modifier keys="anyShift caps? command"/></keyMapSelect>
        <keyMapSelect mapIndex="1"><modifier keys="anyShift caps?"/></keyMapSelect>
        <keyMapSelect mapIndex="2"><modifier keys="caps command?"/></keyMapSelect>
        <keyMapSelect mapIndex="3"><modifier keys="anyOption"/></keyMapSelect>
        <keyMapSelect mapIndex="4"><modifier keys="anyShift caps? anyOption command?"/></keyMapSelect>
        <keyMapSelect mapIndex="5"><modifier keys="caps anyOption command?"/></keyMapSelect>
        <keyMapSelect mapIndex="6"><modifier keys="anyOption command"/></keyMapSelect>
        <keyMapSelect mapIndex="7"><modifier keys="anyControl"/></keyMapSelect>
    </modifierMap>
    <keyMapSet id="ms">

"""
for mi in 0..<modStates.count {
    x += "        <keyMap index=\"\(mi)\">\n"
    for code in keyCodes {
        if let si = t.deadKeys[mi]?[code] {
            x += "            <key code=\"\(code)\" action=\"d\(si)_\(code)_\(mi)\"/>\n"
        } else if let out = t.outputs[mi]?[code] {
            if composable(out) {
                x += "            <key code=\"\(code)\" action=\"\(charAction(out))\"/>\n"
            } else {
                x += "            <key code=\"\(code)\" output=\"\(esc(out))\"/>\n"
            }
        }
    }
    x += "        </keyMap>\n"
}
x += "    </keyMapSet>\n    <actions>\n"
for (mi, keys) in t.deadKeys.sorted(by: { $0.key < $1.key }) {
    for (code, si) in keys.sorted(by: { $0.key < $1.key }) {
        x += "        <action id=\"d\(si)_\(code)_\(mi)\">\n            <when state=\"none\" next=\"s\(si)\"/>\n        </action>\n"
    }
}
var chars = Set<String>()
for m in t.whenState { chars.formUnion(m.keys) }
for c in chars.sorted() {
    x += "        <action id=\"\(charAction(c))\">\n            <when state=\"none\" output=\"\(esc(c))\"/>\n"
    for si in 0..<t.terminators.count {
        if let out = t.whenState[si][c] { x += "            <when state=\"s\(si)\" output=\"\(esc(out))\"/>\n" }
    }
    x += "        </action>\n"
}
x += "    </actions>\n    <terminators>\n"
for si in 0..<t.terminators.count {
    x += "        <when state=\"s\(si)\" output=\"\(esc(t.terminators[si]))\"/>\n"
}
x += "    </terminators>\n</keyboard>\n"
print(x)
