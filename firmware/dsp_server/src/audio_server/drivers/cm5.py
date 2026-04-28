import logging
import subprocess

from audio_server.drivers.interfaces.gpio import GPIO_OUTPUT
from audio_server.drivers.interfaces.i2c import I2C
from audio_server.drivers.interfaces.spi import SPI

logger = logging.getLogger(__name__)


class CM5:
    class _GPIO_OUTPUT(GPIO_OUTPUT):
        def __init__(self, gpio_number: int, active_high: bool):
            self.gpio_number = gpio_number
            self.active_high = active_high

        def set(self, active: bool):
            high = active ^ (not self.active_high)

            logger.info(
                f"Setting GPIO {self.gpio_number} to {'active' if active else 'inactive'}"
            )
            subprocess.check_output(["pinctrl", "set", str(self.gpio_number), "op"])
            subprocess.check_output(
                ["pinctrl", "set", str(self.gpio_number), f"d{'h' if high else 'l'}"]
            )

    def __init__(self) -> None:
        self.i2c = [I2C("/dev/i2c-0"), I2C("/dev/i2c-1")]
        self.spi = [SPI(0)]
