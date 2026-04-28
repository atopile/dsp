import math
import time

from audio_server.drivers.adau1452 import ADAU1452


class Params:
    GAIN_L = 0x03B8
    GAIN_R = 0x03B9
    MUTE = 0x0376


class DSPControl:
    def __init__(self, adau1452: ADAU1452):
        self.adau1452 = adau1452

    def get_volume_db(self) -> float:
        gain_l = self.adau1452.read_float_parameter(Params.GAIN_L)
        l_db = 20 * math.log10(gain_l)

        return l_db

    def _set_gain(self, gain_db: float):
        # convert db to float (0dB = 1.0; 6db = 2.0)
        gain_float = 10 ** (gain_db / 20)
        self.adau1452.set_float_parameter(Params.GAIN_L, gain_float)
        self.adau1452.set_float_parameter(Params.GAIN_R, gain_float)

    def set_volume(self, volume_db: float, ramp_time_s_per_db: float = 0.1):
        # TODO use TIME_RESOLUTION_S for the loop
        # TODO do exponential ramp
        TIME_RESOLUTION_S = 0.010  # 10ms
        assert ramp_time_s_per_db > TIME_RESOLUTION_S

        cur_db = self.get_volume_db()
        dif = volume_db - cur_db

        dif_iter = abs(dif)
        direction = 1 if dif > 0 else -1
        while dif_iter > 0:
            cur_db += direction
            self._set_gain(cur_db)
            time.sleep(ramp_time_s_per_db)
            dif_iter -= 1

        print("Done setting volume")

    def set_mute(self, mute: bool):
        self.adau1452.set_bool_parameter(Params.MUTE, mute)
