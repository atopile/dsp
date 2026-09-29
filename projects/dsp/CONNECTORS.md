# Panel connectors

`vendor/panel-connectors/panel-connectors.ato` owns the physical connectors and
pin mapping. `main.ato` composes them with the existing audio, Ethernet and DMX
subsystems. Each catalog import is pinned to `0.1.0`.

| Instances | Part | Catalog import | Wiring |
| --- | --- | --- | --- |
| 2 audio inputs | Neutrik NCJ6FA-H | `jlc/C368458` | XLR 2 / TRS tip positive; XLR 3 / ring negative; XLR 1 / sleeve / G to chassis |
| 2 audio outputs | Neutrik NC3MAAH | `jlc/C368463` | 2 positive, 3 negative, 1 and shell contact (catalog pad 4) to chassis |
| 1 DMX output | Neutrik NC5FAH | `jlc/C368501` | 3 data+, 2 data-, 1 transceiver common; G to chassis |
| 2 Ethernet ports | HanRun HR911105A | `jlc/C12074` | RD+/RD- to switch RX, TD+/TD- to switch TX; SH1/SH2 to chassis; CHSGND to PCB ground |

The combo input's two tip contacts are connected together. The DMX connector
is a five-pin female output, replacing the fixture's generic male audio-style
placeholder. Secondary DMX data pins 4/5 are unused; catalog mechanical pads 6/7
are left unconnected. DMX common is the non-isolated SP3485's board ground,
separate from the connector shell's chassis net.

The Ethernet pair convention follows this project's Realtek driver: pair 0 is
RX and pair 1 is TX. The jack contains the cable-side transformers, common-mode
chokes, 75-ohm termination network and 1 nF / 2 kV termination capacitor. Pin 8
returns that internal capacitor to PCB ground, as specified by HanRun. The shell
has a separate chassis connection. The jack's LEDs are intentionally unused,
matching the existing switch driver, and pin 7 is NC.

## Remaining electrical and mechanical work

The PHY-side TX/RX center taps (pins 4/5) are exposed as `tx_center_tap` and
`rx_center_tap` and currently unconnected. The retrieved RTL8305NB-VB datasheet
does not specify the transformer bias circuit; confirm its reference schematic
before selecting bias or AC-ground components. Do not interpret these catalog
imports as a qualified Ethernet interface. The inherited direct CM5-to-switch
PHY connection also needs review of coupling, pair assignment and link mode.

This change adds the actual connectors to the BOM and generated layout. Panel
cutouts, mounting hardware, final placement and routing remain deferred together
with the existing DRC/physical-check issues. The selected CM5 still uses its
combined catalog carrier footprint; separate mating sockets are not added here.

## Sources

- [Neutrik NCJ6FA-H](https://www.neutrik.com/en/product/ncj6fa-h), mechanical
  drawing supplied with catalog part `C368458`.
- [Neutrik NC3MAAH](https://www.neutrik.com/en/product/nc3maah), mechanical
  drawing and separate shell contact supplied with `C368463`.
- [Neutrik NC5FAH](https://www.neutrik.com/en/product/nc5fah), mechanical drawing
  supplied with `C368501`.
- [ETC DMX connector pinout](https://support.etcconnect.com/ETC/Networking/Response_Classic/Response_96_In),
  common/data-/data+ assignment.
- HanRun HR911105A manufacturer datasheet, revision A/2, page 1, distributed
  with `jlc/C12074@0.1.0` as `HANRUN_HR911105A.datasheet.pdf`.
- [Realtek RTL8305NB-VB datasheet](https://datasheet.lcsc.com/datasheet/pdf/0bad82140d1f6af3f41d0f91c198c363.pdf?productCode=C3010343).
