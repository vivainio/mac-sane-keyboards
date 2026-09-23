from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class State(str, Enum):
    """Modifier state, valued by keyMap index in the keylayout."""
    plain = "plain"
    shift = "shift"
    caps = "caps"
    option = "option"
    shift_option = "shift_option"
    caps_option = "caps_option"

    @property
    def index(self) -> int:
        return list(State).index(self)


@dataclass
class Layout:
    name: str                 # bundle / file name, no spaces
    display: str              # name shown in System Settings
    base: str                 # base/<base>.keylayout
    patch: dict[int, dict[State, str]] = field(default_factory=dict)  # key code -> state -> output

    def __post_init__(self):
        if " " in self.name:
            raise ValueError(f"layout name must not contain spaces: {self.name!r}")
        self.patch = {code: {State(s): out for s, out in states.items()}
                      for code, states in self.patch.items()}

    @property
    def identifier(self) -> str:
        return "com.vivainio.keyboardlayout." + self.name.replace("-", "").lower()
