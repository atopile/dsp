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
placement file with 69 components. The checked-in layout was synchronized by
that build. The original nine parts’ STEP/GLB assets were restored from
Narayan’s earlier commit
[`63ba9e409b`](https://github.com/atopile/monopile/commit/63ba9e409b),
before they were stripped from the visualization fixture.

## Scope

This remains a visualization fixture with simplified drivers, including a
structural CM5 stand-in and abstract power-conversion blocks. It is not a
hardware-qualified replacement for the original DSP board.

The successful build reports 10 physical-check warnings for courtyard
intersections and 3D body clashes around the line-driver decoupling capacitors.
The inherited configuration excludes `PCB.requires_drc_check`; successful
output generation does not establish DRC clearance or manufacturing readiness.
