import logging

import spidev

logger = logging.getLogger(__name__)


class SPI:
    def __init__(self, bus: int):
        self.bus = bus


class SPIPeripheral:
    def __init__(self, spi: SPI, cs: int):
        self._spi = spi
        self.cs = cs
        self.spi = spidev.SpiDev()
        self.spi.open(self._spi.bus, self.cs)

    def xfer2(self, data: list[int]) -> list[int]:
        return self.spi.xfer2(data)

    def close(self):
        self.spi.close()

    def set_speed(self, speed: int):
        self.spi.max_speed_hz = speed

    def set_mode(self, mode: int):
        self.spi.mode = mode
