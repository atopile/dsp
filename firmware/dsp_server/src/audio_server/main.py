import logging
import socket
from dataclasses import dataclass

import typer

from audio_server.drivers.ad1938 import AD1938
from audio_server.drivers.adau1452 import ADAU1452
from audio_server.drivers.cm5 import CM5
from audio_server.drivers.interfaces.i2c import I2CPeripheral
from audio_server.drivers.interfaces.spi import SPIPeripheral
from audio_server.drivers.rtl8305 import Realtek_RTL8305

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def signal_handler(instances: list, signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down...")
    for instance in instances:
        print("Setting", instance, "running to False")
        instance.running = False


@dataclass
class Config:
    pass


PER_HOST_DEFAULTS = {
    "nonos-2": Config(),
    "nonos-3": Config(),
    "nonos-4": Config(),
}
hostname = socket.gethostname()
HOST_CONFIG = PER_HOST_DEFAULTS.get(hostname, {})


def main(
    init: bool = True,
):
    # Device Tree
    cm5 = CM5()
    dsp = ADAU1452(
        i2c=I2CPeripheral(i2c_bus=cm5.i2c[0], device_addr=0x38),
        gpio_enable=CM5._GPIO_OUTPUT(24, True),
    )
    codecs = [
        AD1938(
            spi=SPIPeripheral(spi=cm5.spi[0], cs=i),
            gpio_enable=CM5._GPIO_OUTPUT(17, True),
            config=AD1938.Config(
                sample_rate=96000,
                pll_input_dlrclk=True,
                tdm=True,
            ),
        )
        for i in range(2)
    ]
    eths = [
        Realtek_RTL8305(CM5._GPIO_OUTPUT(25, True)),
        Realtek_RTL8305(CM5._GPIO_OUTPUT(26, True)),
        Realtek_RTL8305(CM5._GPIO_OUTPUT(27, True)),
    ]

    # Init

    if init:
        dsp.enable()
        for codec in codecs:
            codec.enable(reset=True)
            # TODO remove this, just a bugfix for hardware issue
            codec.invert_output_polarity()
        for eth in eths:
            eth.enable()

    print("DONE INIT")

    # signal.signal(
    #     signal.SIGINT,
    #     lambda signum, frame: signal_handler([buttons], signum, frame),
    # )


if __name__ == "__main__":
    typer.run(main)
