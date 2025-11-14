from dmx_control.mapping.dmx_register import (
    DMXBrightness,
    DMXFunction,
    DMXRegister,
    Description,
)
from dmx_control.mapping.device import DMXDevice


class LEDBar140W40LED(DMXDevice):
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
                ),
            ],
        ),
        *[
            DMXRegister(
                channel=i,
                functions=[
                    DMXFunction(
                        description=Description(function=f"Red_{i}", notes="0%-100%"),
                    ),
                    DMXFunction(
                        description=Description(function=f"Green_{i}", notes="0%-100%"),
                    ),
                    DMXFunction(
                        description=Description(function=f"Blue_{i}", notes="0%-100%"),
                    ),
                ],
            )
            for i in range(2, 13)
        ],
    ]
