# Panel connectors

`vendor/panel-connectors/panel-connectors.ato` owns physical parts and pin mapping.
`main.ato` composes them with two codecs, fourteen balanced line drivers, three
Ethernet switches and the CM5. All new catalog imports are pinned to `0.1.0`.

| Instances | Part | Catalog | Wiring |
| --- | --- | --- | --- |
| 2 combo audio inputs | Neutrik NCJ6FA-H | `jlc/C368458` | XLR 2 / tip positive, XLR 3 / ring negative; shield to chassis |
| 6 audio outputs | Neutrik NC3MAAH | `jlc/C368463` | 2 positive, 3 negative; 1 and shell to chassis |
| 2 four-channel analog outputs | Neutrik NE8FAH-C5 | `jlc/C368528` | Balanced pairs 4/5, 3/6, 1/2, 7/8; shell to chassis |
| 1 DMX input | Neutrik NC5MAH | `jlc/C368509` | 1 common, 2 data-, 3 data+; shell to chassis |
| 1 DMX output | Neutrik NC5FAH | `jlc/C368501` | 1 common, 2 data-, 3 data+; shell to chassis |
| 1 eight-port Ethernet block | HCTL HC-RJ45-059C-2*4-1 | `jlc/C5296839` | Original eight external switch ports; shell to chassis |
| 1 USB-C | SHOU HAN TYPE-C 16PIN 2MD(073) | `jlc/C2765186` | CM5 USB data, two 5.1 kohm CC pulldowns; VBUS unconnected |
| 1 USBI debug header | CJT A2541WV-2x5P | `jlc/C225520` | 1 SCL, 3 SDA, 6 reset, 10 ground; pin 4 supply unconnected |

The EtherCON connectors carry analog audio, not Ethernet. Codec 0 supplies the
six XLR outputs and receives the two audio inputs; codec 1 supplies eight analog
outputs through the two EtherCON connectors. DMX input/output share one
non-isolated SP3485 bus; secondary data pins 4/5 are unused.

## Remaining electrical and mechanical work

The HCTL manufacturer drawing shows a passive connector without integrated
magnetics. External isolation, PHY bias/termination and the inherited direct
PHY-to-PHY connections require completion and qualification. The switch and
connector models alone do not form a qualified Ethernet interface.

The original panel positions and mounting-hole pattern are restored. The female
DMX footprint uses its own orientation to face outward. Actual catalog 3D models
are included. Panel cutouts and fastening hardware still require mechanical
qualification. The CM5 uses a combined carrier footprint; separate mating socket
procurement is not provided. USB ESD protection and device operation remain to
be qualified; external 5 V powers the board.
