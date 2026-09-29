# DSP — ato v2

Imported from Narayan Powderly’s `claude/prism-visualization-gauntlet-7463ee`
branch in `atopile/monopile`, commit
[`ff7e666de1a7fa892878866a801b0b639f34e60f`](https://github.com/atopile/monopile/commit/ff7e666de1a7fa892878866a801b0b639f34e60f),
from `apps/gauntlet/suites/prism-viz/fixtures/dsp`.
See [the originating PR](https://github.com/atopile/monopile/pull/2657).

The snapshot includes ato v2 source, vendored drivers, referenced parts, and
native layout files. It models the CM5 host, ADAU1452 DSP, two AD1938 codecs,
balanced audio I/O, Ethernet, DMX input/output, and power supplies.

## Build

The entry point is `main.ato:DspBoard`; `ato.yaml` requires atopile `^0.16.11`.
The complete build was run with the tool from
[monopile PR #4375](https://github.com/atopile/monopile/pull/4375), commit
[`c59f4ae02c08cfa813941ea062c983b40992f508`](https://github.com/atopile/monopile/commit/c59f4ae02c08cfa813941ea062c983b40992f508),
installed as `0.16.11.post1.dev843+gc59f4ae02`.
The version requirement expresses the release baseline; the commit identifies
exactly which development tool was used.

Open this directory in an IDE running that tool revision, with library access
configured and signed in, then run:

```sh
ato build
```

A standalone CLI also needs `ATO_SERVICES_LIBRARY_URL` set to its library
server and a valid sign-in session or `ATO_SERVICES_LIBRARY_TOKEN`. This build
used the local development library. No library credentials are stored here.

The build produces the BOM, connectivity, native layout, Gerbers, and a JLCPCB
placement file with 250 components. The checked-in layout was synchronized by
that build. The original nine parts’ STEP/GLB assets were restored from
Narayan’s earlier commit
[`63ba9e409b`](https://github.com/atopile/monopile/commit/63ba9e409b),
before they were stripped from the visualization fixture.

## Power and CM5

The power section now has physical catalog parts for every conversion stage:

- External regulated 5 V input on the two-pin terminal block (pin 1 positive,
  pin 2 return); no onboard mains supply is instantiated.
- TPSM863257 buck for digital 3.3 V and TLV75901 LDO for analog 3.3 V.
  Both feedback dividers are calculated from the output-voltage requirement.
- Three independent +/-18 V banks, each using two B0524S-2WR3 isolated 24 V
  modules followed by TPS7A4700 regulators. The banks supply 6/4/4 line drivers.
- Input/output capacitors, buck feedforward and enable circuitry, LDO noise
  reduction, and minimum-load resistors are included with voltage/power ratings.

The CM5 stand-in is replaced by the catalog CM5104032 (4 GB RAM, 32 GB eMMC,
wireless), imported as `jlc/C42394220@0.1.0`. All supply and ground contacts and
the used I2C/SPI/I2S/UART/Ethernet/GPIO signals are connected. GPIO_VREF connects
to the module's own 3.3 V output. Firmware still needs the corresponding pinmux
configuration. The module uses the catalog's combined carrier footprint; separate
socket procurement and mechanical qualification are not supplied by this driver.

See [power implementation and limits](POWER.md) for the circuit sources and
operating assumptions.

## Panel connectors

The original connector complement is restored with physical catalog parts:
two combo audio inputs, six XLR audio outputs, two EtherCON connectors carrying
four balanced analog outputs each, eight Ethernet ports in one 2x4 block,
five-pin DMX input/output, USB-C, and a ten-pin USBI debug header.
See [connector wiring and limits](CONNECTORS.md).

## Layout and remaining scope

The native layout restores the original 359.01 x 73.78 mm board envelope and ten
mounting holes. All 250 components are placed, with the panel connectors along
the original edge. Placement was inspected using the actual catalog 3D models;
the native physical check reports zero courtyard overlaps or body clashes.

Obsolete copper from the earlier circuit was removed. This is a placed, unrouted
board, not manufacturing-ready artwork. DRC/physical-check configuration is
unchanged; `PCB.requires_drc_check` remains excluded. The current DRC reports
202 disconnected copper findings, eight short-circuit and seven shorted-component
findings around the DSP exposed-pad geometry, and nine unsupported artwork checks.
These DRC findings are separate from the passing component-overlap check. Panel
hardware, signal integrity, clearance and routing still require engineering review.

The original eight-port RJ45 block has no integrated magnetics. External Ethernet
isolation/bias circuitry and the direct PHY-to-PHY links remain unfinished; a
successful build does not establish working Ethernet. USB-C has data and CC
connections but VBUS is left unconnected because the board is externally powered.
Firmware, USB protection and the complete operating power budget still need
qualification. No fallback or migration logic is introduced.
