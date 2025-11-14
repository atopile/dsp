from dataclasses import dataclass


class DMXError(Exception):
    pass


class DMXValueError(DMXError):
    pass


@dataclass
class Description:
    function: str
    notes: str


@dataclass
class DMXFunction:
    description: Description
    value_range: tuple[int, int] = (0, 255)

    def __post_init__(self):
        if not 0 <= self.value_range[0] <= 255 and 0 <= self.value_range[1] <= 255:
            raise DMXValueError(f"Value range [{self.value_range}] out of range 0-255")


@dataclass
class DMXValue(DMXFunction):
    pass


@dataclass
class DMXBrightness(DMXValue):
    pass


@dataclass
class DMXMode(DMXFunction):
    pass


@dataclass
class DMXEnum(DMXValue):
    pass


@dataclass
class DMXBool(DMXEnum):
    true_value: int = 255
    false_value: int = 0


@dataclass
class DMXRegister:
    channel: int
    functions: list[DMXFunction]

    def __post_init__(self):
        # TODO: Check if the function value ranges are overlapping or total value range is not 0-255
        pass
