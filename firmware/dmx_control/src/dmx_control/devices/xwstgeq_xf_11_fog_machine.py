from dmx_control.mapping.dmx_register import (
    DMXBool,
    DMXRegister,
    Description,
)
from dmx_control.mapping.device import DMXDevice


class XWSTGEQXFI11FogMachine(DMXDevice):
    """
    XWSTGEQ XF-11 1500W Fog Machine
    """

    registers = [
        DMXRegister(
            channel=1,
            functions=[
                DMXBool(
                    description=Description(function="FogItUp", notes="On/Off"),
                ),
            ],
        )
    ]
