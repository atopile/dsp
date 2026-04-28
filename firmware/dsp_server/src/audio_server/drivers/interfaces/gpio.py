from typing import Protocol


class GPIO_OUTPUT(Protocol):
    def activate(self) -> None:
        self.set(True)

    def deactivate(self) -> None:
        self.set(False)

    def set(self, active: bool) -> None: ...
