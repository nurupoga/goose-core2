# Goose on M5Stack Core2

Experimental port of [Goose](https://github.com/aardappel/goose) to M5Stack Core2 (ESP32 Xtensa LX6) using ESP-IDF.

**Status: experimental. No Goose-generated firmware has been built or run on Core2 yet.**

## Architecture

Host Goose compiler → generated C → ESP-IDF Xtensa toolchain → Core2.

## First milestone

1. Build Goose compiler on host and generate C from a minimal program.
2. Audit generated C and runtime for POSIX, virtual memory, pointer width and threading dependencies.
3. Compile generated C using ESP-IDF (ESP32 target).
4. Implement bounded PSRAM-backed stack allocation and overflow checks if required.
5. Execute Goose-originated arithmetic on a physical Core2 and report result over UART.

## Baseline C smoke test

Install ESP-IDF, then run:

```sh
idf.py set-target esp32
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

This builds **only a C-based smoke test**, not Goose code.

## Upstream

https://github.com/aardappel/goose

Independent experimental project; not an official upstream target.
