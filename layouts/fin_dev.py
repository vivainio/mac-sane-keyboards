from kbd import Layout, State

# Finnish layout for development: no dead keys, ~ and ` on a single keypress.
LAYOUT = Layout(
    name="FIN-dev-layout",
    display="FIN dev layout",
    base="FIN",
    patch={
        # 30: {State.plain: "~", State.option: "¨"},   # key code 30 = the ¨ key
    },
)
