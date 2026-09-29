# DSP — ato v2

Imported from Narayan Powderly’s `claude/prism-visualization-gauntlet-7463ee`
branch in `atopile/monopile`, commit
[`ff7e666de1a7fa892878866a801b0b639f34e60f`](https://github.com/atopile/monopile/commit/ff7e666de1a7fa892878866a801b0b639f34e60f),
from `apps/gauntlet/suites/prism-viz/fixtures/dsp`.
See [the originating PR](https://github.com/atopile/monopile/pull/2657).

The snapshot includes ato v2 source, vendored drivers, referenced parts, and
native layout files. It models the CM5 host, ADAU1452 DSP, AD1938 codec,
balanced audio I/O, Ethernet, DMX output, and power supplies.

The entry point is `main.ato:DspBoard`; `ato.yaml` declares atopile `^0.16.0`.
From this directory, the build command is `ato build`.

This was authored as a visualization fixture, with simplified drivers.
Compatibility with the latest tool and hardware readiness have not been
verified by this import. The source configuration excludes
`PCB.requires_drc_check`; a successful build does not establish DRC clearance.
