from dmx_control.mapping.dmx_register import DMXRegister
from dmx_control.mapping.interface import Interface


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
