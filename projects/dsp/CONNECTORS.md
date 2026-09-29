# Original DSP connector set

The connector circuits and placements match the original v1 board. Physical
parts come from versioned catalog imports in `circuits/Panel.ato`,
`circuits/EthernetPorts.ato` and `circuits/Usb.ato`.

| Quantity | Role | Part / catalog |
| --- | --- | --- |
| 2 | Combo XLR/TRS audio inputs | Neutrik NCJ6FA-H / C368458 |
| 6 | Balanced XLR audio outputs | Neutrik NC3MAAH / C368463 |
| 2 | Four balanced analog channels per EtherCON | Neutrik NE8FAH-C5 / C368528 |
| 1 | Eight Ethernet ports in a 2x4 block | HCTL HC-RJ45-059C-2*4-1 / C5296839 |
| 1 | Original three-pin DMX input | Neutrik NC3MAAH / C368463 |
| 1 | Original combo-connector DMX output | Neutrik NCJ6FA-H / C368458 |
| 1 | USB-C | SHOU HAN TYPE-C 16PIN 2MD(073) / C2765186 |
| 1 | USBI debug header | CJT A2541WV-2x5P / C225520 |

The EtherCON connectors carry analog audio, not Ethernet. The two codecs feed
fourteen line drivers through the original coupling and protection networks.
The original DMX connectors are restored rather than substituted with five-pin
parts. This preserves the v1 panel geometry; it is not a claim of DMX connector
standard compliance.

The HCTL block has no integrated magnetics. External isolation, bias and the
original direct PHY links remain unqualified. The original USB fuse, bypass
resistor, CC resistors and protection circuit are restored, including its VBUS
wiring; review interaction with the external 5 V input before connecting USB
power. Panel cutouts, sockets and fastening hardware still require mechanical
qualification.
