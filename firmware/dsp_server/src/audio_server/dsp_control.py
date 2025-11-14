from audio_server.drivers.adau1452 import ADAU1452


class DSPControl:
    def __init__(self, adau1452: ADAU1452):
        self.adau1452 = adau1452

    def get_volume(self) -> float:
        # TODO implement
        return 0.0

    def set_volume(self, volume_db: float):
        # TODO implement
        pass
