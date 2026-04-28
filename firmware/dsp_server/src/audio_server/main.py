import logging
import socket
from dataclasses import dataclass
from pathlib import Path

import typer
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from audio_server.drivers.ad1938 import AD1938
from audio_server.drivers.adau1452 import ADAU1452
from audio_server.drivers.cm5 import CM5
from audio_server.drivers.interfaces.i2c import I2CPeripheral
from audio_server.drivers.interfaces.spi import SPIPeripheral
from audio_server.drivers.rtl8305 import Realtek_RTL8305
from audio_server.dsp_control import DSPControl

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


def setup(
    init: bool = typer.Option(True, help="Initialize hardware on startup"),
):
    """Setup and initialize DSP hardware."""
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
        logger.info("Initializing hardware...")
        dsp.enable()
        for i, codec in enumerate(codecs):
            codec.enable(reset=i == 0)
            # TODO remove this, just a bugfix for hardware issue
            codec.invert_output_polarity()
        for eth in eths:
            eth.enable()
        logger.info("Hardware initialization complete")

    dsp_control = DSPControl(dsp)
    return dsp_control


def webserver(
    init: bool = typer.Option(False, help="Initialize hardware on startup"),
    host: str = typer.Option("0.0.0.0", help="Host address to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
):
    """Run DSP control webserver with volume control interface."""
    dsp_control = setup(init=init)

    app = FastAPI(title="DSP Control")

    class VolumeRequest(BaseModel):
        volume_db: float

    @app.get("/")
    async def read_root():
        html_file = Path(__file__).parent / "html" / "dsp_control.html"
        with open(html_file) as f:
            return HTMLResponse(content=f.read())

    @app.get("/api/volume")
    async def get_volume():
        """Get current volume in dB"""
        volume = dsp_control.get_volume_db()
        return {"volume_db": volume}

    @app.post("/api/volume")
    async def set_volume(request: VolumeRequest):
        """Set volume in dB"""
        logger.info(f"Received volume request: {request.volume_db} dB")
        dsp_control.set_volume(request.volume_db)
        logger.info(f"Volume set successfully to {request.volume_db} dB")
        return {"status": "ok", "volume_db": request.volume_db}

    logger.info(f"Starting webserver on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


app = typer.Typer(help="DSP Audio Server Control")
app.command()(setup)
app.command()(webserver)

if __name__ == "__main__":
    app()
