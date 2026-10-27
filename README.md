# Goose on M5Stack Core2

Experimental port of [Goose](https://github.com/aardappel/goose) to M5Stack Core2 (ESP32 Xtensa LX6) using ESP-IDF.

**Status: Experimental port. C baseline, C optimized, and Goose-generated firmware have been verified and benchmarked on physical Core2.**

## Architecture

Host Goose compiler → generated C + ESP-IDF FreeRTOS/PSRAM runtime → ESP-IDF Xtensa toolchain → Core2.

## Milestone Status

1. [x] Build Goose compiler on host and generate C from minimal and benchmark programs ([Issue #1](https://github.com/nurupoga/goose-core2/issues/1)).
2. [x] Audit generated C and runtime for POSIX, virtual memory, pointer width and threading dependencies ([Issue #2](https://github.com/nurupoga/goose-core2/issues/2)).
3. [x] Compile generated C using ESP-IDF (ESP32 Xtensa target) ([Issue #2](https://github.com/nurupoga/goose-core2/issues/2)).
4. [x] Implement bounded PSRAM-backed stack allocation and FreeRTOS runtime port ([Issue #3](https://github.com/nurupoga/goose-core2/issues/3), [Issue #4](https://github.com/nurupoga/goose-core2/issues/4)).
5. [x] Execute Goose-originated arithmetic on physical Core2 and report deterministic result over UART ([Issue #5](https://github.com/nurupoga/goose-core2/issues/5)).
6. [x] Benchmark C vs C-Opt vs Goose on Core2 hardware ([Issue #6](https://github.com/nurupoga/goose-core2/issues/6), [Issue #7](https://github.com/nurupoga/goose-core2/issues/7)).

## Baseline & Benchmark Run

Install ESP-IDF, then run:

```sh
idf.py set-target esp32
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

### Benchmark Results (Physical Core2 Hardware)

Measurements captured from physical M5Stack Core2 hardware across 30 repeated runs each (90 runs total) ([Issue #7](https://github.com/nurupoga/goose-core2/issues/7), [Issue #6](https://github.com/nurupoga/goose-core2/issues/6)).

![Core2 Benchmark Results](benchmarks/results/benchmark_results.png)

#### Workload: `array_scan` (1,024 elements × 1,000 inner iterations)

| Implementation | Status | Samples | Median (μs) | P95 (μs) | Min (μs) | Max (μs) | Checksum | Free Internal Heap | Free PSRAM |
|---|---|---|---|---|---|---|---|---|---|
| **C (Optimized)** | **Verified on Core2** | 30 | 57,820.0 | 57,821 | 57,811 | 57,832 | `33582136` | 358,863 B | 4,191,744 B |
| **C (Baseline)** | **Verified on Core2** | 30 | 96,234.0 | 96,234 | 96,225 | 96,235 | `33582136` | 358,863 B | 4,191,744 B |
| **Goose (Ported Runtime)** | **Verified on Core2** | 30 | 147,551.0 | 147,555 | 147,542 | 190,104 | `33582136` | 358,955 B | 2,094,588 B |
| Rust | Pending toolchain | - | - | - | - | - | - | - | - |

- **Hardware**: M5Stack Core2 (ESP32-D0WDQ6-V3 revision v3.1 @ 160MHz, 8MB PSRAM / 4MB mapped)
- **Toolchain**: ESP-IDF v5.3.1 (`xtensa-esp-elf-gcc 13.2.0`, `-Os` optimization)
- **Goose Runtime Port**:
  - Upstream compiler transpile target: [`benchmarks/goose/array_scan.goose`](benchmarks/goose/array_scan.goose) → [`main/goose_array_scan.c`](main/goose_array_scan.c)
  - Bounded data stack backed by ESP32 PSRAM (~2.1 MB arena mapped into external RAM)
  - FreeRTOS single-task port (`main/goose_runtime.c` adapts POSIX `mman` / `signal` / `pthread` dependencies)
- **Parity Validation**: Checksum `33582136` matches identically across all 90 runs of C, C-Opt, and Goose.
- **Binary Footprint**: `goose_core2.bin` 230,096 bytes (0x382d0)
- **Raw Artifacts**: Log capture at [`benchmarks/results/raw_core2.log`](benchmarks/results/raw_core2.log), summary CSV at [`benchmarks/results/benchmark-summary.csv`](benchmarks/results/benchmark-summary.csv)

## Upstream

https://github.com/aardappel/goose

Independent experimental project; not an official upstream target.
