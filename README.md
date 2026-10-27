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

## Baseline C smoke test & Benchmark

Install ESP-IDF, then run:

```sh
idf.py set-target esp32
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

This builds and executes the **C baseline benchmark** on Core2.

### Benchmark Results (Physical Core2 Hardware)

Measurements captured from physical M5Stack Core2 hardware across 30 repeated runs ([Issue #7](https://github.com/nurupoga/goose-core2/issues/7), [Issue #6](https://github.com/nurupoga/goose-core2/issues/6)).

![Core2 Benchmark Results](benchmarks/results/benchmark_results.png)

#### Workload: `array_scan` (1,024 elements × 1,000 inner iterations)

| Implementation | Status | Samples | Median (μs) | P95 (μs) | Min (μs) | Max (μs) | Checksum | Free Internal Heap | Free PSRAM |
|---|---|---|---|---|---|---|---|---|---|
| **C Baseline** | **Verified on Core2** | 30 | 96,234.0 | 96,235 | 96,226 | 96,235 | `33582136` | 363,171 B | 4,191,744 B |
| C (Arena-opt) | Pending | - | - | - | - | - | - | - | - |
| Rust | Pending | - | - | - | - | - | - | - | - |
| Goose | Pending runtime port | - | - | - | - | - | - | - | - |

- **Hardware**: M5Stack Core2 (ESP32-D0WDQ6-V3 revision v3.1 @ 160MHz, 8MB PSRAM / 4MB mapped)
- **Toolchain**: ESP-IDF v5.3.1 (`xtensa-esp-elf-gcc 13.2.0`, `-Os` optimization)
- **Binary Footprint**: `goose_core2.bin` 227,408 bytes (0x37850)
- **Raw Artifacts**: Log capture at [`benchmarks/results/raw_core2.log`](benchmarks/results/raw_core2.log), summary CSV at [`benchmarks/results/benchmark-summary.csv`](benchmarks/results/benchmark-summary.csv)

## Upstream

https://github.com/aardappel/goose

Independent experimental project; not an official upstream target.
