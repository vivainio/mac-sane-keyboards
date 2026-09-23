from kbd import Layout, State as S

# Finnish layout for development: no dead keys, ~ and ` on a single keypress.
# Based on https://github.com/saneDG/keyboard-layout-FIN-no-deadkeys
LAYOUT = Layout(
    name="FIN-dev-layout",
    display="FIN dev layout",
    base="FIN",
    patch={
        24: {S.plain: "`", S.shift: "´"},                                   # the ´ key
        30: {S.plain: "~", S.shift: "^", S.option: "¨", S.cmd_option: "~"},  # the ¨ key
    },
)
