from kbd import Layout, State as S

# Finnish layout for development: no dead keys, no §°¨. Tilde, backtick, brackets,
# braces, backslash and pipe are all on the top-left/top-right keys without option chords.
LAYOUT = Layout(
    name="FIN-clean-layout",
    display="FIN clean layout",
    base="FIN",
    patch={
        # top left (§ ° key): ~ plain, ` on shift
        10: {S.plain: "~", S.shift: "`", S.caps: "~", S.option: "~", S.shift_option: "`",
             S.caps_option: "~", S.cmd_option: "~"},
        # top right (´ key): [ {, with \ and | on option
        24: {S.plain: "[", S.shift: "{", S.caps: "[", S.option: "\\", S.shift_option: "|",
             S.caps_option: "\\", S.cmd_option: "["},
        # the ¨ key: ] }, with ^ and ´ on option
        30: {S.plain: "]", S.shift: "}", S.caps: "]", S.option: "^", S.shift_option: "´",
             S.caps_option: "^", S.cmd_option: "]"},
    },
)
