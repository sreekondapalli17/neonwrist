# NEON//WRIST MK-II: all-out design

Personal project, no program rules, no budget cap. Built to look like a piece of Night City hardware: a black-and-gold PCB sandwich with a 60-pixel minute ring, a 12-pixel hour ring, real haptics, a fuel gauge, and a magnetic pogo-pin charging dock.

Confidence tags: [high] checked against a datasheet or shop page, [medium] standard practice or my knowledge, [low] rough estimate. Verify every pin and footprint against the datasheet before ordering.

## 1. The concept

Three boards, all designed in KiCad:

| Board | What it is | Layers | Look |
|---|---|---|---|
| MAIN | The electronics: ESP32, power, sensors, 72 LEDs | 4 | Matte-ish black mask, ENIG gold, white silkscreen |
| FACE | Faceplate PCB that sits about 2 mm above MAIN on brass spacers. Holes over every LED make a pixel grid. Exposed gold "circuit tattoo" art, bare bus-wire loops, decorative unconnected parts | 2 | Black mask, ENIG, exposed copper art |
| DOCK | Tiny charging and flashing dock: USB-C in, magnetic pogo pins out | 2 | Black, ENIG |

Case: a smoked translucent resin mid-ring between FACE and MAIN (edge glow from the LEDs) and a back cover, printed in SLA resin or CNC-machined in aluminum. JLCPCB's 3D printing service can do both [medium].

Why a sandwich: the FACE board turns cheap PCB manufacturing into the watch face itself. Light leaks through the LED holes as crisp pixels, the gold art catches light, and the gap shows the real circuit underneath.

## 2. Biggest risks, read first

1. The 1010 LEDs need 4.5 to 5.5 V [high, LCSC listing]. A LiPo gives 3.0 to 4.2 V, so MAIN needs a 5 V boost converter for the LEDs. Their data input then needs a 5 V level shifter, because 3.3 V logic is below the input-high threshold at 5 V [medium].
2. The 1010 LEDs (about 1 x 1 mm) and the QFN charger cannot realistically be hand soldered. Plan on JLCPCB assembly (PCBA) for MAIN [high].
3. Antenna: the ESP32 PCB antenna sits under part of the LED ring and under FACE. Keep copper off FACE above the antenna zone and test BLE at 1 m early. Fallback is setting time over USB [high on the risk].
4. Current: 72 LEDs at full white is about 1 A at 5 V. Firmware caps brightness and lights only what the face needs [medium].
5. Cost and lead time: double-sided PCBA on a 4-layer board costs real money and takes weeks. Get a JLCPCB quote before committing [low on exact cost].
6. Battery polarity: check with a multimeter before connecting. Cut a JST lead one wire at a time and tape the ends [high].

## 3. Feature list

- 60-pixel minute ring plus 12-pixel hour ring, smooth sweeping seconds trail
- Glitch boot animation, matrix-rain mode, scan-line mode, "corrupted" time flicker
- Auto brightness from a digital ambient light sensor, cover-to-snooze
- Raise-to-wake, double-tap to change face, shake for glitch burst (IMU)
- Crisp haptic taps and patterns through a linear resonant actuator (LRA) and driver chip
- Accurate battery percentage from a fuel gauge chip
- Charges and runs at the same time (power-path charger)
- Magnetic pogo-pin dock for charging and USB flashing, no port on the watch
- BLE time sync, phone notifications (iPhone ANCS or Android Gadgetbridge style) [medium]
- Over-the-air firmware updates [medium]
- Two side buttons like a crown, plus a hidden BOOT button
- True-off slide switch
- Exposed gold art, bare wire loops, decorative "fake" circuitry on FACE

## 4. What changes from your current schematic

Stays: U1 ESP32-C3-MINI-1, U3 AP2112K-3.3, U5 LSM6DS3, SW1 slide switch, SW2 BOOT, SW3 reset, J2 battery.

Changes:
- J1 USB-C moves to the DOCK. On MAIN it becomes four pogo target pads (Conn_01x04): VBUS, D+, D-, GND. R1 and R2 (CC 5.1k) move to the DOCK too.
- U2 MCP73831 is replaced by a power-path charger (BQ24072, VQFN-16) [high that it exists, medium on fit]. R3 goes away.
- M1 coin motor is replaced by an LRA driven by a DRV2605L.
- U6 TPS22917 load switch is removed. The TPS610997 boost fully disconnects its output when EN is low [high, TI datasheet].
- New: 5 V boost, 74AHCT1G125 level shifter, LC709203F fuel gauge, LTR-303ALS-01 light sensor, two more buttons, 72 LEDs.

## 5. Parts

KiCad search names first. Exact buy part in the second column.

| Ref | KiCad search | Buy part | Package | Job |
|---|---|---|---|---|
| U1 | ESP32-C3-MINI-1 | ESP32-C3-MINI-1-N4 | module 16.6 x 13.2 | brain, BLE |
| U2 | BQ24072 | BQ24072RGTR | VQFN-16 3x3 | power-path LiPo charger |
| U3 | AP2112K-3.3 | AP2112K-3.3TRG1 | SOT-23-5 | 3.3 V regulator |
| U4 | LC709203F | LC709203FQH-01TWG | WDFN-12 | fuel gauge, battery percent |
| U5 | LSM6DS3 | LSM6DS3TR-C | LGA-14 | IMU, wrist tilt, taps |
| U7 | TPS610997DRV | TPS610997DRVR | WSON-6 2x2 | 5 V boost for the LEDs, true off when EN is low |
| U8 | 74AHCT1G125 | 74AHCT1G125GW | SOT-353 | 3.3 V to 5 V LED data |
| U9 | DRV2605L | DRV2605LDGSR | VSSOP-10 | haptic driver |
| U10 | LTR-303ALS-01 | LTR-303ALS-01 | 2 x 2 mm | digital ambient light |
| D1 to D60 | WS2812B (make symbol if missing) | XL-1010RGBC-WS2812B | 1 x 1 mm | minute ring |
| D61 to D72 | WS2812B-2020 | WS2812B-2020 | 2 x 2 mm | hour ring |
| LRA1 | Motor_DC (or Conn_01x02) | 8 to 10 mm coin LRA | pads | haptics |
| J1 | Conn_01x04 | pogo target pads | pads | charge and USB from dock |
| J2 | Conn_01x02 | battery wire pads | pads | battery |
| SW1 | SW_SPDT | MSK12C02 | SMD | true off, on regulator EN |
| SW2 | SW_Push | PTCF-V-T/R | side push | BOOT |
| SW3 | SW_Push | PTCF-V-T/R | side push | reset (or hide it as a pad) |
| SW4, SW5 | SW_Push | PTCF-V-T/R | side push | crown top and bottom |
| BT1 | none | Adafruit 1570 100 mAh, or about 200 mAh if the case allows | 31 x 11.5 x 3.8 | battery |

Notes:
- Part numbers marked "class" or "or any" are suggestions. Pick an in-stock JLCPCB part and use its footprint.
- The DRV2605L showed low stock on one LCSC listing [medium]. Check before designing around it.
- Passives: 0402 on MAIN since it is machine assembled, 0603 if you hand solder anything.

## 6. Power tree

```
DOCK USB-C -> pogo -> VBUS -> U2 BQ24072 -> SYS (runs watch while charging)
                                   |
                                   +-> BAT <-> J2 battery
SYS -> U3 AP2112K (EN from SW1) -> 3V3 -> ESP32, IMU, gauge, light, haptic
SYS -> U7 TPS610997 boost (EN = GPIO1) -> 5V_LED -> 72 LEDs, U8
U4 LC709203F sits on BAT and talks over I2C
```

## 7. Netlist (labels)

Power
- J1 VBUS -> label VBUS. J1 GND -> GND.
- U2: IN -> VBUS (1 uF). BAT -> VBAT (4.7 uF). OUT -> SYS (4.7 uF). ISET 8.87k (100 mA charge), ILIM 3.24k, EN2 low and EN1 high through 10k to VBUS (500 mA USB mode), CE low, TD low (termination on), TMR open (default timers), TS 10k to GND (no thermistor) [high, TI datasheet].
- U2 CHG and PGOOD are open-drain: 10k pull-ups to 3V3, then CHG -> GPIO0 and PGOOD -> GPIO20.
- J2 pin 1 -> VBAT, pin 2 -> GND.
- U3: VIN -> SYS (10 uF). EN -> SW1 common. SW1 sides -> SYS and GND. VOUT -> 3V3 (10 uF).
- U7 TPS610997 boost: VI -> SYS (10 uF), 2.2 uH inductor from SYS to SW, EN -> GPIO1 with 100k to GND (LEDs stay off during boot), FB -> GND (fixed 5 V version) [high, TI datasheet], VOUT -> 5V_LED (2 x 22 uF).

ESP32 (U1)
- 3V3 -> 3V3 with 10 uF and 100 nF at the pins. GND -> GND.
- EN -> 10k to 3V3, 1 uF to GND, SW3 to GND.
- GPIO9 -> 10k to 3V3, SW2 to GND. GPIO2 -> 10k to 3V3. GPIO8 -> 10k to 3V3 (keeps download mode reliable) [medium].
- GPIO19 -> USB_DP. GPIO18 -> USB_DN. J1 D+ -> USB_DP, J1 D- -> USB_DN.

I2C bus (SDA = GPIO6, SCL = GPIO7, 4.7k pull-ups to 3V3)
- U4 LC709203F, U5 LSM6DS3TR-C, U9 DRV2605L, U10 LTR-303ALS-01 all on SDA and SCL. Check that their addresses do not collide [medium].
- U5 INT1 -> GPIO3 (wake from deep sleep).
- U9 EN -> 3V3, IN/TRIG -> GND, OUT+ and OUT- -> LRA1.

LEDs
- GPIO10 -> U8 input (100 ohm series). U8 powered from 5V_LED, OE tied low. U8 output -> 330 ohm -> D1 DIN.
- D1 DOUT -> D2 DIN ... D60 DOUT -> D61 DIN ... D72. One chain, 72 pixels.
- Every LED VDD -> 5V_LED, GND -> GND. 100 nF per 4 to 6 LEDs, plus 22 uF bulk.

Buttons
- SW4 -> GPIO4 to GND, SW5 -> GPIO5 to GND, internal pull-ups. GPIO0 to GPIO5 can wake the C3 from deep sleep [medium].

Pin map: GPIO0 CHG, GPIO1 LED power, GPIO2 strap pull-up, GPIO3 IMU INT, GPIO4 and GPIO5 crown buttons, GPIO6 SDA, GPIO7 SCL, GPIO8 strap pull-up, GPIO9 BOOT, GPIO10 LED data, GPIO18 and GPIO19 USB, GPIO20 PGOOD, GPIO21 spare debug pad.

## 8. PCB specs to order

| | MAIN | FACE | DOCK |
|---|---|---|---|
| Layers | 4 (top, GND, power, bottom) | 2 | 2 |
| Thickness | 1.0 mm if offered for 4 layers, else 1.6 [medium] | 1.0 mm | 1.6 mm |
| Mask | Black (JLCPCB says not too matte or glossy) [high] | Black | Black |
| Finish | ENIG (flat pads for 1 mm LEDs and QFN) | ENIG (gold art) | ENIG |
| Silkscreen | White | White, or none for a cleaner look | White |
| Assembly | JLCPCB PCBA, both sides | none, hand solder decor | optional |

## 9. MAIN layout

Board: 42 mm circle, origin at center, KiCad Y points down.

Front: outer ring of 60 LEDs at 18 mm radius (about 1.88 mm pitch), inner ring of 12 LEDs at 12 mm radius, light sensor at 12 o'clock just inside the inner ring, a clear center for decor visible through FACE.

Back: ESP32 in the center with the antenna toward 9 o'clock, pogo pads in a row near 6 o'clock, power cluster (charger, regulator, boost, load switch) between the module and 3 o'clock, IMU near center away from the LRA, LRA at 12 o'clock, buttons on the 2 to 4 o'clock rim like a crown, slide switch at 5 o'clock, well clear of the antenna.

Rules
- No copper on any layer of MAIN or FACE over the antenna keep-out (datasheet Zone A).
- Boost converter: tight loop, inductor right next to the chip, solid GND under it, far from the antenna.
- Route the LED data chain around the ring on one layer, 5V_LED as a wide ring on the inner power layer.
- USB D+ and D- short and paired from the pogo pads to the module.
- Mounting holes for 3 brass spacers (M1.6) at 120 degrees on a 15 mm radius, in the gap between the two LED rings. The rim outside the outer ring is only about 2.5 mm wide, too thin for holes [medium].

Outer ring (D1 to D60, radius 18 mm)

| LED | angle (deg) | X (mm) | Y (mm) | rotation |
|---|---|---|---|---|
| D1 | 0 | 0.00 | -18.00 | 0 |
| D2 | 6 | 1.88 | -17.90 | 6 |
| D3 | 12 | 3.74 | -17.61 | 12 |
| D4 | 18 | 5.56 | -17.12 | 18 |
| D5 | 24 | 7.32 | -16.44 | 24 |
| D6 | 30 | 9.00 | -15.59 | 30 |
| D7 | 36 | 10.58 | -14.56 | 36 |
| D8 | 42 | 12.04 | -13.38 | 42 |
| D9 | 48 | 13.38 | -12.04 | 48 |
| D10 | 54 | 14.56 | -10.58 | 54 |
| D11 | 60 | 15.59 | -9.00 | 60 |
| D12 | 66 | 16.44 | -7.32 | 66 |
| D13 | 72 | 17.12 | -5.56 | 72 |
| D14 | 78 | 17.61 | -3.74 | 78 |
| D15 | 84 | 17.90 | -1.88 | 84 |
| D16 | 90 | 18.00 | -0.00 | 90 |
| D17 | 96 | 17.90 | 1.88 | 96 |
| D18 | 102 | 17.61 | 3.74 | 102 |
| D19 | 108 | 17.12 | 5.56 | 108 |
| D20 | 114 | 16.44 | 7.32 | 114 |
| D21 | 120 | 15.59 | 9.00 | 120 |
| D22 | 126 | 14.56 | 10.58 | 126 |
| D23 | 132 | 13.38 | 12.04 | 132 |
| D24 | 138 | 12.04 | 13.38 | 138 |
| D25 | 144 | 10.58 | 14.56 | 144 |
| D26 | 150 | 9.00 | 15.59 | 150 |
| D27 | 156 | 7.32 | 16.44 | 156 |
| D28 | 162 | 5.56 | 17.12 | 162 |
| D29 | 168 | 3.74 | 17.61 | 168 |
| D30 | 174 | 1.88 | 17.90 | 174 |
| D31 | 180 | 0.00 | 18.00 | 180 |
| D32 | 186 | -1.88 | 17.90 | 186 |
| D33 | 192 | -3.74 | 17.61 | 192 |
| D34 | 198 | -5.56 | 17.12 | 198 |
| D35 | 204 | -7.32 | 16.44 | 204 |
| D36 | 210 | -9.00 | 15.59 | 210 |
| D37 | 216 | -10.58 | 14.56 | 216 |
| D38 | 222 | -12.04 | 13.38 | 222 |
| D39 | 228 | -13.38 | 12.04 | 228 |
| D40 | 234 | -14.56 | 10.58 | 234 |
| D41 | 240 | -15.59 | 9.00 | 240 |
| D42 | 246 | -16.44 | 7.32 | 246 |
| D43 | 252 | -17.12 | 5.56 | 252 |
| D44 | 258 | -17.61 | 3.74 | 258 |
| D45 | 264 | -17.90 | 1.88 | 264 |
| D46 | 270 | -18.00 | 0.00 | 270 |
| D47 | 276 | -17.90 | -1.88 | 276 |
| D48 | 282 | -17.61 | -3.74 | 282 |
| D49 | 288 | -17.12 | -5.56 | 288 |
| D50 | 294 | -16.44 | -7.32 | 294 |
| D51 | 300 | -15.59 | -9.00 | 300 |
| D52 | 306 | -14.56 | -10.58 | 306 |
| D53 | 312 | -13.38 | -12.04 | 312 |
| D54 | 318 | -12.04 | -13.38 | 318 |
| D55 | 324 | -10.58 | -14.56 | 324 |
| D56 | 330 | -9.00 | -15.59 | 330 |
| D57 | 336 | -7.32 | -16.44 | 336 |
| D58 | 342 | -5.56 | -17.12 | 342 |
| D59 | 348 | -3.74 | -17.61 | 348 |
| D60 | 354 | -1.88 | -17.90 | 354 |

Inner ring (D61 to D72, radius 12 mm)

| LED | angle (deg) | X (mm) | Y (mm) | rotation |
|---|---|---|---|---|
| D61 | 0 | 0.00 | -12.00 | 0 |
| D62 | 30 | 6.00 | -10.39 | 30 |
| D63 | 60 | 10.39 | -6.00 | 60 |
| D64 | 90 | 12.00 | -0.00 | 90 |
| D65 | 120 | 10.39 | 6.00 | 120 |
| D66 | 150 | 6.00 | 10.39 | 150 |
| D67 | 180 | 0.00 | 12.00 | 180 |
| D68 | 210 | -6.00 | 10.39 | 210 |
| D69 | 240 | -10.39 | 6.00 | 240 |
| D70 | 270 | -12.00 | 0.00 | 270 |
| D71 | 300 | -10.39 | -6.00 | 300 |
| D72 | 330 | -6.00 | -10.39 | 330 |

## 10. FACE board

- Same 42 mm outline and the same 3 spacer holes.
- A 1.2 mm drilled hole over every LED. Use non-plated holes so they stay black inside [medium].
- Exposed copper art: draw on F.Cu and add matching F.Mask openings so it comes out gold.
- Bare bus-wire loops soldered between plated pads, connected to nothing.
- Optional decorative 0603 resistors and an old-style chip footprint, unconnected, for the "visible tech" look.
- Keep copper off the antenna area, same as MAIN.

## 11. DOCK board

- USB-C 16P receptacle with CC1 and CC2 5.1k to GND (your current R1 and R2 move here).
- 4-pin magnetic pogo connector: VBUS, D+, D-, GND. Matching magnetic target on the watch back, wired to J1.
- Keep D+ and D- short. USB full speed over short pogo pins usually works [medium].
- Optional: a status LED and a little NEON//WRIST logo.

## 12. Firmware plan

1. LED chain test at very low brightness.
2. Clock faces: minute ring, hour ring, seconds trail.
3. Light sensor auto brightness and current cap.
4. IMU: raise-to-wake, double tap, shake glitch. Deep sleep with wake on GPIO3, 4, 5.
5. Fuel gauge percent, charging animation from CHG and PGOOD.
6. Haptic patterns through DRV2605L library effects.
7. BLE time sync, then notifications, then OTA updates.

Before turning LED power off, drive GPIO10 low so the level shifter is not back-powered [medium].

## 13. Order of work

1. Finish the MAIN schematic with labels, run ERC.
2. Draw FACE and DOCK as separate KiCad projects.
3. Pick exact in-stock JLCPCB parts and assign footprints.
4. Lay out MAIN (4 layers), then FACE to match, then DOCK.
5. Get the PCBA quote, then order.
6. Case CAD around the stack while boards ship.
