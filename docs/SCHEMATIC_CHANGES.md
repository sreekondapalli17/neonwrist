# Schematic rewrite: labels only, MK-II parts

Every connection is now a net label sitting exactly on a pin tip. There are no wires. Two pins with the same label name are connected.

## How to check it
1. Open `pcb/neonwrist/neonwrist.kicad_sch` in KiCad.
2. Inspect > Electrical Rules Checker > Run ERC.
3. Hover any label and press the highlight key to light up its whole net.

## Parts removed
- MCP73831 charger and its PROG resistor, replaced by BQ24072 (charges and powers the watch at the same time).
- USB-C connector and the two 5.1k CC resistors. They move to the separate dock board.
- TPS22917 load switch. The TPS610997 boost fully disconnects when EN is low, so it is not needed.

## Parts added
- J1 Pogo_Pads (Conn_01x04): VBUS, USB D+, USB D-, GND from the magnetic dock.
- U2 BQ24072RGTR power-path charger. ISET 8.87k = 100 mA charge, ILIM 3.24k, EN1 high = 500 mA USB mode, TS 10k (no thermistor), TD low, TMR open.
- U7 TPS610997DRVR fixed 5 V boost + L1 2.2 uH, FB to GND, EN from GPIO1 with a 100k pull-down.
- U8 74AHCT1G125 level shifter, 3.3 V data to 5 V data for the LEDs.
- U4 LC709203F fuel gauge on VBAT (I2C).
- U9 DRV2605L haptic driver, M1 is now the LRA.
- U10 LTR-303ALS-01 ambient light sensor (I2C), interrupt on GPIO21.
- SW4 and SW5 crown buttons on GPIO4 and GPIO5.
- D1 to D60 minute ring (XL-1010RGBC-WS2812B), D61 to D72 hour ring (WS2812B-2020), one data chain LD1 to LD72.
- PWR_FLAGs on VBUS and GND so ERC knows where power comes from.

## ESP32 pin map
GPIO0 CHG, GPIO1 LED_EN, GPIO2 strap pull-up, GPIO3 IMU_INT, GPIO4 BTN_A, GPIO5 BTN_B, GPIO6 SDA, GPIO7 SCL, GPIO8 strap pull-up, GPIO9 BOOT, GPIO10 LED data, GPIO18/19 USB, GPIO20 PGOOD, GPIO21 ALS_INT.

## Things to verify before layout
- D1 to D60 use the WS2812B-2020 symbol. The 1010 LED has its own pad numbering, so make or pick a 1010 footprint whose pad numbers match DOUT=1, VSS=2, DIN=3, VDD=4, or adjust.
- LC709203F TEST pin is tied to GND and TSENSE has a 10k to GND. Confirm both against its datasheet (medium confidence).
- LSM6DS3TR-C SDx and SCx are tied to GND. Confirm in its datasheet (medium confidence).
- I2C addresses of U4, U5, U9, U10 must not collide.
- Footprints for J1 pogo pads, J2 battery pads, buttons, and the 1010 LEDs are still empty.

The old wired version is in git history at commit 58bda6f.
