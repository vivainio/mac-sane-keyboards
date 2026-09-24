from kbd import Layout, State as S

# Finnish layout for development: no dead keys, no §°¨. Tilde, backtick, slash,
# { } \ and | are on single keys; [ ] stay on option+8/9.
LAYOUT = Layout(
    name="FIN-dev-layout",
    display="FIN dev layout",
    base="FIN",
    patch={
        # the å key: / plain, ? on shift; å moved to option
        33: {S.plain: "/", S.shift: "?", S.caps: "/", S.option: "å", S.shift_option: "Å",
             S.caps_option: "Å"},
        # the ¨ key: \ plain, | on shift, ^ and ´ on option
        30: {S.plain: "\\", S.shift: "|", S.caps: "\\", S.option: "^", S.shift_option: "´",
             S.caps_option: "^", S.cmd_option: "\\"},
        # the a key: å on option
        0: {S.option: "å", S.shift_option: "Å", S.caps_option: "Å"},
        # the 4 key: $ on shift
        21: {S.shift: "$"},
        # the e key: € on option
        14: {S.option: "€", S.caps_option: "€"},
        # top left (§ ° key): ~ plain, ` on shift
        10: {S.plain: "~", S.shift: "`", S.caps: "~", S.option: "~", S.shift_option: "`",
             S.caps_option: "~", S.cmd_option: "~"},
        # top right (´ key): { plain, } on shift
        24: {S.plain: "{", S.shift: "}", S.caps: "{", S.cmd_option: "{"},
    },
)
