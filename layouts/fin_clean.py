from kbd import Layout, State as S

# Finnish layout for development: no dead keys, no §°¨, backslash/pipe/tilde/backtick
# on single keypresses. Also built from base FIN; see fin_dev.py for the minimal variant.
LAYOUT = Layout(
    name="FIN-clean-layout",
    display="FIN clean layout",
    base="FIN",
    patch={
        # top left (§ ° key): ~ plain, ` on shift
        10: {S.plain: "~", S.shift: "`", S.caps: "~", S.option: "~", S.shift_option: "`",
             S.caps_option: "~", S.cmd_option: "~"},
        # the ´ key: literal ´ and `, no dead key
        24: {S.plain: "´", S.shift: "`", S.caps: "´"},
        # the ¨ key: \ and |, ^ on option
        30: {S.plain: "\\", S.shift: "|", S.caps: "\\", S.option: "^", S.shift_option: "^",
             S.caps_option: "^", S.cmd_option: "\\"},
    },
)
