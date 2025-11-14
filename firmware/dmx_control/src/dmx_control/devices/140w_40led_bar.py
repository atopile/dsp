from dmx_control.register.dmx_register import (
    DMXBrightness,
    DMXEnum,
    DMXFunction,
    DMXRegister,
    DMXValue,
    Description,
)


class Interface:
    pass


class Device:
    def __init__(self, name: str, interface: Interface):
        self.name = name


class DMXDevice(Device):
    def __init__(
        self,
        name: str,
        base_channel: int,
        interface: Interface,
        registers: list[DMXRegister],
    ):
        super().__init__(name, interface)
        self.base_channel = base_channel
        self.registers = registers


class LEDBar140W40LED:
    """
    140W 40LED Bar
    In 13 channel mode
    """

    registers = [
        DMXRegister(
            channel=1,
            functions=[
                DMXBrightness(
                    description=Description(
                        function="Master brightness", notes="0%-100%"
                    ),
                    value_range=(0, 255),
                ),
            ],
        ),
        *[
            DMXRegister(
                channel=i,
                functions=[
                    DMXFunction(
                        description=Description(function=f"Red_{i}", notes="0%-100%"),
                        value_range=(0, 255),
                    ),
                    DMXFunction(
                        description=Description(function=f"Green_{i}", notes="0%-100%"),
                        value_range=(0, 255),
                    ),
                    DMXFunction(
                        description=Description(function=f"Blue_{i}", notes="0%-100%"),
                        value_range=(0, 255),
                    ),
                ],
            )
            for i in range(2, 13)
        ],
    ]
