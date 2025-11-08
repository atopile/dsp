import logging

from audio_server.drivers.interfaces.gpio import GPIO_OUTPUT

logger = logging.getLogger(__name__)


class Realtek_RTL8305:
    def __init__(self, reset_pin: GPIO_OUTPUT) -> None:
        self.reset_pin = reset_pin

    def enable(self) -> None:
        self.reset_pin.activate()
