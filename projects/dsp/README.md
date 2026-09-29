# DSP — ato v2

Imported from Narayan Powderly’s `claude/prism-visualization-gauntlet-7463ee`
branch in `atopile/monopile`, commit
[`ff7e666de1a7fa892878866a801b0b639f34e60f`](https://github.com/atopile/monopile/commit/ff7e666de1a7fa892878866a801b0b639f34e60f),
from `apps/gauntlet/suites/prism-viz/fixtures/dsp`.
See [the originating PR](https://github.com/atopile/monopile/pull/2657).

The snapshot includes ato v2 source, vendored drivers, referenced parts, and
native layout files. It models the CM5 host, ADAU1452 DSP, AD1938 codec,
balanced audio I/O, Ethernet, DMX output, and power supplies.

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
placement file with 110 components. The checked-in layout was synchronized by
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
- Two B0524S-2WR3 isolated 24 V modules, each followed by a TPS7A4700 set to
  18.0 V. Their floating outputs are stacked around system ground for +/-18 V.
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

All seven panel connectors now use versioned catalog parts with footprints and
3D models: two Neutrik NCJ6FA-H combo audio inputs, two NC3MAAH audio outputs,
one NC5FAH five-pin female DMX output, and two HanRun HR911105A 10/100 RJ45
jacks with integrated magnetics. See [connector wiring and limits](CONNECTORS.md).

## Remaining scope

The RJ45 PHY-side center taps remain unconnected pending confirmation of the
RTL8305NB-VB bias/termination circuit. The existing direct CM5-to-switch PHY
connection also needs electrical review; a successful build does not establish
working Ethernet. The jack LEDs are not wired.

The inherited routing and board outline still need reconciliation with the circuit. DRC and
physical-check configuration are unchanged: `PCB.requires_drc_check` remains
excluded, and the latest saved reports are unresolved DRC (135 findings) and
four courtyard overlaps plus four body clashes. These are not manufacturing
clearance; this change completes circuit capture and the build, not PCB layout.
