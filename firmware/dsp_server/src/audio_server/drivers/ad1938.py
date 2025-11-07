import logging
import time
from dataclasses import dataclass
from enum import IntEnum

from audio_server.drivers.interfaces.gpio import GPIO_OUTPUT
from audio_server.drivers.interfaces.spi import SPIPeripheral

logger = logging.getLogger(__name__)


# AD1938 SPI Interface:
# - SPI Mode 0 (CPOL=0, CPHA=0)
# - 24-bit (3 byte) transactions
# - Byte 1: Global address (0x04 << 1) | R/W bit
#   - Write: 0x08 (0x04 << 1 | 0)
#   - Read:  0x09 (0x04 << 1 | 1)
# - Byte 2: Register address (0x00-0x10)
# - Byte 3: Data byte
# All registers are reset to 0, except for the DAC volume
# registers that are set to full volume (0x00 = no attenuation).
# Note that the first setting in each control register parameter is the default setting.


class Register:
    ADDR = 0x00

    def __init__(self, device: "AD1938"):
        self.address = self.ADDR
        self.device = device

    @property
    def value(self) -> int:
        return self.device.read_register(self.address)

    @value.setter
    def value(self, value: int):
        logger.info(f"Setting {self.full_name} to {value:02X}")
        self.device.write_register(self.address, value)
        read_value = self.device.read_register(self.address)
        if read_value != value:
            logger.warning(
                f"Write failed {self.full_name}: {read_value:02X} != {value:02X}"
            )

    @property
    def name(self) -> str:
        return type(self).__name__

    @property
    def full_name(self) -> str:
        return f"{self.name}(0x{self.address:02X})"

    def set_bit(self, bit: int, value: bool):
        if value:
            self.value |= 1 << bit
        else:
            self.value &= ~(1 << bit)

    def read_bit(self, bit: int) -> bool:
        return bool(self.value & (1 << bit))

    def set_bits(self, mask: int, value: int):
        self.value = (self.value & ~mask) | (value & mask)


class Field:
    BIT = -1
    BIT_CNT = -1

    def __init__(self, register: Register):
        self.register = register

    def set(self, value: int):
        bit = self.BIT
        bit_cnt = self.BIT_CNT
        assert bit != -1, "BIT must be set"
        assert bit_cnt != -1, "BIT_CNT must be set"
        assert bit + bit_cnt <= 8, "BIT + BIT_CNT must be less than 8"

        mask = (1 << bit_cnt + bit) - 1
        self.register.value = (self.register.value & ~mask) | ((value << bit) & mask)


class FieldBit(Field):
    def __init__(self, register: Register):
        super().__init__(register)
        assert self.BIT != -1, "BIT must be set"

    @property
    def value(self) -> bool:
        return self.register.read_bit(self.BIT)

    @value.setter
    def value(self, value: bool):
        self.register.set_bit(self.BIT, value)


class _Register(IntEnum):
    PLL_AND_CLOCK_CONTROL_0 = 0
    PLL_AND_CLOCK_CONTROL_1 = 1
    DAC_CONTROL_0 = 2
    DAC_CONTROL_1 = 3
    DAC_CONTROL_2 = 4
    DAC_INDIVIDUAL_CHANNEL_MUTES = 5
    DAC_L1_VOLUME_CONTROL = 6
    DAC_R1_VOLUME_CONTROL = 7
    DAC_L2_VOLUME_CONTROL = 8
    DAC_R2_VOLUME_CONTROL = 9
    DAC_L3_VOLUME_CONTROL = 10
    DAC_R3_VOLUME_CONTROL = 11
    DAC_L4_VOLUME_CONTROL = 12
    DAC_R4_VOLUME_CONTROL = 13
    ADC_CONTROL_0 = 14
    ADC_CONTROL_1 = 15
    ADC_CONTROL_2 = 16


class PLLAndClockControl0(Register):
    ADDR = _Register.PLL_AND_CLOCK_CONTROL_0

    class PLL_PowerDown(FieldBit):
        BIT = 0

    class MCLKI_XI_MASTER_CLK_RATE(Field):
        BIT_CNT = 2
        BIT = 1

        class Rate(IntEnum):
            INPUT256 = 0x00
            INPUT384 = 0x01
            INPUT512 = 0x02
            INPUT768 = 0x03

    class MCLKO_XO_MASTER_CLK_RATE(Field):
        BIT_CNT = 2
        BIT = 3

        class PinFunc(IntEnum):
            XTAL_OSC_ENABLED = 0x00
            VCO_256_FS = 0x01
            VCO_512_FS = 0x02
            OFF = 0x03

    class PLL_INPUT_SELECT(Field):
        BIT_CNT = 2
        BIT = 5

        class Input(IntEnum):
            MCLKI_XI = 0x00
            DLRCLK = 0x01
            ALRCLK = 0x02

    class INTERNAL_MASTER_CLK_ENABLE(FieldBit):
        BIT = 7

    def set_pll_input(self, input: "PLLAndClockControl0.PLL_INPUT_SELECT.Input"):
        pll_input = PLLAndClockControl0.PLL_INPUT_SELECT(self)
        pll_input.set(input)


class PLLAndClockControl1(Register):
    ADDR = _Register.PLL_AND_CLOCK_CONTROL_1

    class DAC_CLK_SRC_SELECT(Field):
        BIT_CNT = 1
        BIT = 0

        class Source(IntEnum):
            PLL = 0x00
            MCLK = 0x01

    class ADC_CLK_SRC_SELECT(Field):
        BIT_CNT = 1
        BIT = 1

        class Source(IntEnum):
            PLL = 0x00
            MCLK = 0x01

    class ON_CHIP_VOLTAGE_REFERENCE_DISABLE(FieldBit):
        BIT = 2

    class PLL_LOCK_INDICATOR(FieldBit):
        BIT = 3


class DACControl0(Register):
    ADDR = _Register.DAC_CONTROL_0

    class POWER_DOWN(FieldBit):
        """DAC power-down control. 0=Power-down, 1=Normal operation"""

        BIT = 0

    class SAMPLE_RATE(Field):
        """DAC sample rate selection"""

        BIT_CNT = 2
        BIT = 1

        class Rate(IntEnum):
            FS_32_44_48_KHZ = 0x00  # 32 kHz/44.1 kHz/48 kHz
            FS_64_88_96_KHZ = 0x01  # 64 kHz/88.2 kHz/96 kHz
            FS_128_176_192_KHZ = 0x02  # 128 kHz/176.4 kHz/192 kHz

    class SDATA_DELAY(Field):
        """SDATA delay in BCLK periods"""

        BIT_CNT = 3
        BIT = 3

        class Delay(IntEnum):
            DELAY_1 = 0x00  # 1 BCLK period
            DELAY_0 = 0x01  # 0 BCLK periods
            DELAY_8 = 0x02  # 8 BCLK periods
            DELAY_12 = 0x03  # 12 BCLK periods
            DELAY_16 = 0x04  # 16 BCLK periods

    class SERIAL_FORMAT(Field):
        """DAC serial data format"""

        BIT_CNT = 2
        BIT = 6

        class Format(IntEnum):
            STEREO = 0x00  # Stereo (normal)
            TDM_DAISY_CHAIN = 0x01  # TDM (daisy chain)
            DAC_AUX_MODE = 0x02  # DAC AUX mode (ADC, DAC, TDM-coupled)
            DUAL_LINE_TDM = 0x03  # Dual-line TDM


class DACControl1(Register):
    ADDR = _Register.DAC_CONTROL_1

    class BCLK_ACTIVE_EDGE(Field):
        """BCLK active edge for TDM in"""

        BIT_CNT = 1
        BIT = 0

        class Edge(IntEnum):
            LATCH_MID_CYCLE = 0x00  # Latch in mid cycle (normal)
            LATCH_END_CYCLE = 0x01  # Latch at end of cycle/pipeline

    class BCLKS_PER_FRAME(Field):
        """Number of BCLKs per frame"""

        BIT_CNT = 2
        BIT = 1

        class BCLKs(IntEnum):
            BCLK_64 = 0x00  # 64 BCLKs (2 channels)
            BCLK_128 = 0x01  # 128 BCLKs (4 channels)
            BCLK_256 = 0x02  # 256 BCLKs (8 channels)
            BCLK_512 = 0x03  # 512 BCLKs (16 channels)

    class LRCLK_POLARITY(Field):
        """LRCLK polarity"""

        BIT_CNT = 1
        BIT = 3

        class Polarity(IntEnum):
            LEFT_LOW = 0x00  # Left low
            LEFT_HIGH = 0x01  # Left high

    class LRCLK_MASTER_SLAVE(Field):
        """LRCLK master/slave mode"""

        BIT_CNT = 1
        BIT = 4

        class Mode(IntEnum):
            SLAVE = 0x00  # Slave
            MASTER = 0x01  # Master

    class BCLK_MASTER_SLAVE(Field):
        """BCLK master/slave mode"""

        BIT_CNT = 1
        BIT = 5

        class Mode(IntEnum):
            SLAVE = 0x00  # Slave
            MASTER = 0x01  # Master

    class BCLK_SOURCE(Field):
        """BCLK source"""

        BIT_CNT = 1
        BIT = 6

        class Source(IntEnum):
            DBCLK_PIN = 0x00  # DBCLK pin
            INTERNALLY_GENERATED = 0x01  # Internally generated

    class BCLK_POLARITY(Field):
        """BCLK polarity"""

        BIT_CNT = 1
        BIT = 7

        class Polarity(IntEnum):
            NORMAL = 0x00  # Normal
            INVERTED = 0x01  # Inverted


class DACControl2(Register):
    ADDR = _Register.DAC_CONTROL_2

    class MASTER_MUTE(FieldBit):
        """Master mute control. 0=Unmute, 1=Mute"""

        BIT = 0

    class DE_EMPHASIS(Field):
        """De-emphasis filter selection (32 kHz/44.1 kHz/48 kHz mode only)"""

        BIT_CNT = 2
        BIT = 1

        class Curve(IntEnum):
            FLAT = 0x00  # Flat (no de-emphasis)
            FS_48_KHZ = 0x01  # 48 kHz curve
            FS_44_1_KHZ = 0x02  # 44.1 kHz curve
            FS_32_KHZ = 0x03  # 32 kHz curve

    class WORD_WIDTH(Field):
        """DAC word width"""

        BIT_CNT = 2
        BIT = 3

        class Width(IntEnum):
            WIDTH_24 = 0x00  # 24 bits
            WIDTH_20 = 0x01  # 20 bits
            WIDTH_16 = 0x03  # 16 bits

    class DAC_OUTPUT_POLARITY(Field):
        """DAC output polarity"""

        BIT_CNT = 1
        BIT = 5

        class Polarity(IntEnum):
            NONINVERTED = 0x00  # Noninverted
            INVERTED = 0x01  # Inverted


class DACIndividualChannelMutes(Register):
    ADDR = _Register.DAC_INDIVIDUAL_CHANNEL_MUTES

    def mute_channel(self, channel: int):
        self.set_bit(channel, True)

    def unmute_channel(self, channel: int):
        self.set_bit(channel, False)

    def mute_mask(self, mask: int):
        assert mask & (~0xFF) == 0
        self.value = mask


class DACVolumeControl(Register):
    """Base class for DAC volume control registers.

    Volume control: 0 = No attenuation, 1-254 = -3/8 dB per step, 255 = Full attenuation
    """

    _BASE_ADDR = _Register.DAC_L1_VOLUME_CONTROL

    def __init__(self, device: "AD1938", channel: int):
        assert 0 <= channel <= 7
        super().__init__(device)
        self.address = self._BASE_ADDR + channel

    @property
    def volume(self) -> int:
        """Get volume attenuation value (0-255)"""
        return self.value

    @volume.setter
    def volume(self, value: int):
        """Set volume attenuation value (0-255)"""
        if not 0 <= value <= 255:
            raise ValueError("Volume must be between 0 and 255")
        self.value = value

    def set_db(self, db: float):
        """Set volume in dB (0 to -95.625 dB, or full mute)"""
        if db > 0:
            raise ValueError("Volume must be 0 or negative dB")
        if db <= -95.625:
            self.volume = 255  # Full attenuation
        else:
            # Each step is -3/8 dB = -0.375 dB
            steps = int(abs(db) / 0.375)
            self.volume = min(254, max(1, steps))

    def get_db(self) -> float:
        """Get volume in dB"""
        if self.volume == 0:
            return 0.0
        elif self.volume == 255:
            return float("-inf")  # Full attenuation
        else:
            return -self.volume * 0.375


class ADCControl0(Register):
    ADDR = _Register.ADC_CONTROL_0

    class POWER_DOWN(FieldBit):
        """ADC power-down control. 0=Normal, 1=Power down"""

        BIT = 0

    class HIGH_PASS_FILTER(FieldBit):
        """High-pass filter enable. 0=Off, 1=On"""

        BIT = 1

    class ADC_L1_MUTE(FieldBit):
        """ADC L1 mute. 0=Unmute, 1=Mute"""

        BIT = 2

    class ADC_R1_MUTE(FieldBit):
        """ADC R1 mute. 0=Unmute, 1=Mute"""

        BIT = 3

    class ADC_L2_MUTE(FieldBit):
        """ADC L2 mute. 0=Unmute, 1=Mute"""

        BIT = 4

    class ADC_R2_MUTE(FieldBit):
        """ADC R2 mute. 0=Unmute, 1=Mute"""

        BIT = 5

    class SAMPLE_RATE(Field):
        """ADC output sample rate selection"""

        BIT_CNT = 2
        BIT = 6

        class Rate(IntEnum):
            FS_32_44_48_KHZ = 0x00  # 32 kHz/44.1 kHz/48 kHz
            FS_64_88_96_KHZ = 0x01  # 64 kHz/88.2 kHz/96 kHz
            FS_128_176_192_KHZ = 0x02  # 128 kHz/176.4 kHz/192 kHz


class ADCControl1(Register):
    ADDR = _Register.ADC_CONTROL_1

    class WORD_WIDTH(Field):
        """ADC word width"""

        BIT_CNT = 2
        BIT = 0

        class Width(IntEnum):
            WIDTH_24 = 0x00  # 24 bits
            WIDTH_20 = 0x01  # 20 bits
            WIDTH_16 = 0x03  # 16 bits

    class SDATA_DELAY(Field):
        """SDATA delay in BCLK periods"""

        BIT_CNT = 3
        BIT = 2

        class Delay(IntEnum):
            DELAY_1 = 0x00  # 1 BCLK period
            DELAY_0 = 0x01  # 0 BCLK periods
            DELAY_8 = 0x02  # 8 BCLK periods
            DELAY_12 = 0x03  # 12 BCLK periods
            DELAY_16 = 0x04  # 16 BCLK periods

    class SERIAL_FORMAT(Field):
        """ADC serial data format"""

        BIT_CNT = 2
        BIT = 5

        class Format(IntEnum):
            STEREO = 0x00  # Stereo
            TDM_DAISY_CHAIN = 0x01  # TDM (daisy chain)
            ADC_AUX_MODE = 0x02  # ADC AUX mode (ADC, DAC, TDM-coupled)

    class BCLK_ACTIVE_EDGE(Field):
        """BCLK active edge for TDM in"""

        BIT_CNT = 1
        BIT = 7

        class Edge(IntEnum):
            LATCH_MID_CYCLE = 0x00  # Latch in mid cycle (normal)
            LATCH_END_CYCLE = 0x01  # Latch in at end of cycle (pipeline)


class ADCControl2(Register):
    ADDR = _Register.ADC_CONTROL_2

    class LRCLK_FORMAT(Field):
        """LRCLK format"""

        BIT_CNT = 1
        BIT = 0

        class Format(IntEnum):
            FORMAT_50_50 = (
                0x00  # 50/50 (allows 32, 24, 20, or 16 bit clocks per channel)
            )
            PULSE = 0x01  # Pulse (32 BCLKs per channel)

    class BCLK_POLARITY(Field):
        """BCLK polarity"""

        BIT_CNT = 1
        BIT = 1

        class Polarity(IntEnum):
            DRIVE_FALLING_EDGE = 0x00  # Drive out on falling edge (DEF)
            DRIVE_RISING_EDGE = 0x01  # Drive out on rising edge

    class LRCLK_POLARITY(Field):
        """LRCLK polarity"""

        BIT_CNT = 1
        BIT = 2

        class Polarity(IntEnum):
            LEFT_LOW = 0x00  # Left low
            LEFT_HIGH = 0x01  # Left high

    class LRCLK_MASTER_SLAVE(Field):
        """LRCLK master/slave mode"""

        BIT_CNT = 1
        BIT = 3

        class Mode(IntEnum):
            SLAVE = 0x00  # Slave
            MASTER = 0x01  # Master

    class BCLKS_PER_FRAME(Field):
        """Number of BCLKs per frame"""

        BIT_CNT = 2
        BIT = 4

        class BCLKs(IntEnum):
            BCLK_64 = 0x00  # 64 BCLKs
            BCLK_128 = 0x01  # 128 BCLKs
            BCLK_256 = 0x02  # 256 BCLKs
            BCLK_512 = 0x03  # 512 BCLKs

    class BCLK_MASTER_SLAVE(Field):
        """BCLK master/slave mode"""

        BIT_CNT = 1
        BIT = 6

        class Mode(IntEnum):
            SLAVE = 0x00  # Slave
            MASTER = 0x01  # Master

    class BCLK_SOURCE(Field):
        """BCLK source"""

        BIT_CNT = 1
        BIT = 7

        class Source(IntEnum):
            ABCLK_PIN = 0x00  # ABCLK pin
            INTERNALLY_GENERATED = 0x01  # Internally generated


class AD1938:
    @dataclass
    class Config:
        sample_rate: int
        pll_input_dlrclk: bool
        tdm: bool

    def __init__(
        self,
        gpio_enable: GPIO_OUTPUT,
        spi: SPIPeripheral,
        config: Config,
    ):
        self.spi = spi
        self.spi.set_mode(0b00)
        self.spi.set_speed(100_000)
        self.gpio_enable = gpio_enable

        self.config = config

    def enable(self, reset: bool = True):
        # Reset sequence: low for 1s, then high
        if reset:
            self.gpio_enable.deactivate()
            time.sleep(0.5)

        self.gpio_enable.activate()
        time.sleep(0.5)

        if reset:
            self.configure_pll(self.config.pll_input_dlrclk)
            self.set_sample_rate(self.config.sample_rate)
            if self.config.tdm:
                self.set_tdm()

    def test_read(self):
        base_addr = PLLAndClockControl0.ADDR
        end_addr = ADCControl2.ADDR
        logger.info(f"Reading registers {base_addr:02X} to {end_addr:02X}")
        for addr in range(base_addr, end_addr + 1):
            logger.info(f"Register {addr:02X}: {self.read_register(addr)}")

    def configure_pll(self, pll_input_dlrclk: bool):
        if not pll_input_dlrclk:
            raise NotImplementedError("Only DLRCLK PLL input is supported")

        pll_clk0 = PLLAndClockControl0(self)
        pll_clk0.set_pll_input(PLLAndClockControl0.PLL_INPUT_SELECT.Input.DLRCLK)
        PLLAndClockControl0.INTERNAL_MASTER_CLK_ENABLE(pll_clk0).value = True

    def set_sample_rate(self, sample_rate: int):
        if sample_rate not in [48000, 96000]:
            # TODO support other sample rates
            raise ValueError(f"Invalid sample rate: {sample_rate}")

        _96 = sample_rate == 96000

        # Sample rate
        dac_ctrl0 = DACControl0(self)
        DACControl0.SAMPLE_RATE(dac_ctrl0).set(
            DACControl0.SAMPLE_RATE.Rate.FS_64_88_96_KHZ
            if _96
            else DACControl0.SAMPLE_RATE.Rate.FS_32_44_48_KHZ
        )
        adc_ctrl0 = ADCControl0(self)
        ADCControl0.SAMPLE_RATE(adc_ctrl0).set(
            ADCControl0.SAMPLE_RATE.Rate.FS_64_88_96_KHZ
            if _96
            else ADCControl0.SAMPLE_RATE.Rate.FS_32_44_48_KHZ
        )

    def set_tdm(self):
        # DAC TDM
        dac_ctrl0 = DACControl0(self)
        DACControl0.SERIAL_FORMAT(dac_ctrl0).set(
            DACControl0.SERIAL_FORMAT.Format.TDM_DAISY_CHAIN
        )

        # ADC TDM
        adc_ctrl1 = ADCControl1(self)
        ADCControl1.SERIAL_FORMAT(adc_ctrl1).set(
            ADCControl1.SERIAL_FORMAT.Format.TDM_DAISY_CHAIN
        )

    def invert_output_polarity(self):
        dac_ctrl2 = DACControl2(self)
        DACControl2.DAC_OUTPUT_POLARITY(dac_ctrl2).set(
            DACControl2.DAC_OUTPUT_POLARITY.Polarity.INVERTED
        )

    def write_register(self, register: int, value: int) -> None:
        """
        Write a value to an AD1938 register via SPI.

        24-bit transaction format:
        - Byte 1: 0x08 (global address 0x04 << 1 | write bit 0)
        - Byte 2: Register address
        - Byte 3: Data byte
        """
        msg = [0x08, register, value]
        self.spi.xfer2(msg)

    def read_register(self, register: int) -> int:
        """
        Read a value from an AD1938 register via SPI.

        24-bit transaction format:
        - Byte 1: 0x09 (global address 0x04 << 1 | read bit 1)
        - Byte 2: Register address
        - Byte 3: Dummy byte (0x00), data is clocked out in this byte
        """
        msg = [0x09, register, 0x00]
        response = self.spi.xfer2(msg)
        return response[2]

    def close(self):
        """Close the SPI connection."""
        self.spi.close()
