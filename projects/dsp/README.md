# DSP — ato v2

This version preserves the [original DSP v1 circuit and routed layout](https://github.com/atopile/dsp/tree/677818ae8344790a40ca80b10a1c6da4f5feb262/projects/dsp) while
building with the ato v2 runtime from
[monopile PR #4375](https://github.com/atopile/monopile/pull/4375), commit
`c59f4ae02c08cfa813941ea062c983b40992f508`
(`0.16.11.post1.dev843+gc59f4ae02`).

## Build

Open this project with that runtime and library access configured, then run:

```sh
ato build
```

The entry point is `main.ato:DspBoard`. A standalone CLI needs
`ATO_SERVICES_LIBRARY_URL` and a signed-in session or `ATO_SERVICES_LIBRARY_TOKEN`.
No credentials are stored in this project.

## Circuit and layout

`main.ato` connects reusable circuit blocks in `circuits/`: audio channel,
codec, DSP, Ethernet switch, Ethernet ports, host, USB, panel and control.
The block wiring and net names preserve the original board's connectivity.
This includes the input/output coupling capacitors, clamp diodes, reference and
supply decoupling, USB protection, LED resistors and control jumpers omitted from
the earlier simplified fixture. Catalog imports are pinned to `0.1.0`.

The native board preserves the v1 footprint geometry, component positions,
4,994 track segments, 548 vias and 18 copper-fill definitions. Its original
359.01 x 73.78 mm outline has four true rounded corners, ten mounting holes and
the original isolation slot. Import errors in perimeter ordering and a copper
polygon mistakenly classified as a cutout have been corrected.

The board has two combo audio inputs, six XLR audio outputs, two four-channel
analog EtherCON outputs, eight Ethernet ports, DMX input/output, USB-C and a
USBI debug header. See [connector details](CONNECTORS.md).

The CM5 is the real catalog CM5104032. Its carrier footprint incorporates the
two original socket pad banks in place, with their pad numbers translated to
CM5 numbering. Its model aligns to the original four mounting studs. The
combined footprint does not separately procure the two mating sockets.

## Deliberate differences and remaining work

The earlier external-5V power completion is retained in `power.ato`; the
unsolicited three-bank expansion and broad re-placement are reverted. Existing
power ICs retain their original positions, and new support components occupy
the power area. See [power implementation and limits](POWER.md).

The native board contains 424 footprint records: 419 populated/catalog parts
and five board-only features (four test pads and the logo). Compared with v1,
the power section has four more parts and the CM5's three footprint records
(module and two sockets) are represented by one combined carrier footprint.

DRC and physical-check configuration is unchanged. Original routing is retained
for review, not declared manufacturing-ready. The updated power circuit needs
routing reconciliation and its full-channel load exceeds the retained supply
budget. Ethernet magnetics/coupling, USB power behavior, firmware and mechanical
qualification also remain engineering work. Existing check findings are not
hidden by moving the v1 circuitry.

No fallback or migration code is required to build this project. Native
`adopt-board` footprint metadata preserves the intentional v1 pad geometry.
