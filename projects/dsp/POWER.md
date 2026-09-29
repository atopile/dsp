# Power implementation

`power.ato` owns the rail requirements and composition. Each device driver owns
its physical part, pin wiring and support components. New catalog imports are
pinned to version `0.1.0`; their sources are fetched by the normal build.

| Function | Implementation | Catalog import |
| --- | --- | --- |
| External 5 V input | DB2ERC-5.08-2P-BK, pin 1 +5 V, pin 2 GND | `jlc/C430456` |
| Digital 3.3 V | TPSM863257 buck module | `jlc/C19190416` |
| Analog 3.3 V | Existing TLV75901, now with calculated feedback | Existing vendored part |
| Two floating 24 V supplies | B0524S-2WR3 | `jlc/C5369477` |
| Two 18 V post-regulators | TPS7A4700 | `jlc/C28286` |

The 5 V input must remain within 4.75–5.25 V at the board, including cable drop.
Size the external supply for the CM5 plus the actual peripheral load; the legacy
library does not automatically prove a whole-board current or thermal budget.
The two 3.3 V rails retain their existing +/-3% requirements.

## Feedback and support circuitry

The standard resistor-divider model relates the requested output to the device's
feedback reference. The successful build selected 115 kohm / 25.5 kohm for the
buck (nominal 3.306 V) and 9.09 kohm / 1.82 kohm for the LDO (nominal 3.297 V).
The source constrains requirements, not those selected top-resistor values.

The buck includes input bypass/bulk capacitance, 44 uF nominal output
capacitance, 22 pF feedforward and an enable pull-up. The analog LDO includes
4.7 uF input/output capacitors. Capacitor effective values under DC bias and
regulator thermal/transient performance still require board qualification.

Each isolated module has a 4.7 uF input capacitor, 470 nF output capacitor and
four parallel 8.2 kohm, 0.5 W preload resistors. Over the modeled 24 V +/-15%
range, the preload draws 9.85–13.60 mA; each resistor dissipates at most 94 mW.
This meets the datasheet's 10% minimum load and >5x resistor-power guidance.
The +/-15% output envelope is the datasheet's nominal-input characterization,
not a verified bound over input, load and temperature corners.

Allow at most 60 mA external load per 18 V rail, reserving the rest of each
83 mA converter rating for preload and regulator current. This is a design
budget, not a load-summing check. Each post-regulator has a 10 uF input capacitor,
44 uF nominal output capacitance and 1 uF noise-reduction capacitor. All capacitors
on the 24/18 V stages are rated at least 50 V (the NR capacitor sees the reference
voltage and is rated 16 V). The downstream line-driver supply capacitors are rated
at least 35 V.

TPS7A4700 active-low programming straps select exactly
`1.4 + 6.4 + 6.4 + 3.2 + 0.4 + 0.2 = 18.0 V`.
P0P8V stays open; grounding it, as in the old source, would select 18.8 V.
The negative rail is another positive regulator on an isolated secondary:
its positive output is system ground and its return is -18 V. Neither isolated
converter's input ground is wired to its secondary ground inside the driver.

## Sources

- [TI TPSM86325x datasheet](https://www.ti.com/lit/gpn/tpsm863257), pin functions
  and application section/table 8-2.
- [TI TLV759P datasheet](https://www.ti.com/lit/ds/symlink/tlv759p.pdf), feedback
  equation and input/output capacitor requirements.
- [TI TPS7A47 datasheet](https://www.ti.com/lit/ds/symlink/tps7a47.pdf), ANY-OUT
  programming and required input/output/NR capacitors.
- YLPTEC B_S-2WR3 manufacturer datasheet, pages 1–4, distributed with catalog
  part `jlc/C5369477@0.1.0` as `YLPTEC_B0524S_2WR3.datasheet.pdf`.
- [Raspberry Pi CM5 datasheet](https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf),
  power input, ground contacts and GPIO_VREF connection.

## Full v1 circuit load

The three-bank expansion has been reverted. The original single bipolar supply
arrangement is retained with the previously completed regulator circuits.
Fourteen DRV135s can consume about 77 mA quiescent per rail at 5.5 mA each,
exceeding the 60 mA external-load budget above. Full-channel operation therefore
still needs a power-capacity decision; the restored layout is not power-qualified.
The original copper is preserved, including the power region. New support parts
and changed regulator programming require routing reconciliation before fabrication.
