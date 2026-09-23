# Finnish layout for development: no dead keys, ~ and ` on a single keypress.
NAME = "FIN-dev-layout"      # bundle / file name, no spaces
DISPLAY = "FIN dev layout"   # name shown in System Settings
BASE = "FIN"                 # base/FIN.keylayout

# Patches on top of the base layout: {key code: {modifier state: output}}
# Modifier states: plain, shift, caps, option, shift_option, caps_option
PATCH = {
    # e.g. 30: {"plain": "~", "option": "¨"},   # key code 30 = the ¨ key
}
