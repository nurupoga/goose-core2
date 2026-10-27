# Core2 benchmark protocol

Status: scaffold only. No measured performance claims.

## Workloads
- `array_scan`: deterministic 32-bit integer array reduction with checksum.
- `sensor_pipeline` (planned): filter + aggregate fixed-point samples.
- `message_encode` (planned): deterministic framed message serialization.

## Fairness
- Identical input bytes, output checksum and algorithm across C, Rust and Goose.
- Compare both straightforward C and arena-optimized C, and report both.
- Record compiler versions, optimization flags, ESP-IDF version, Goose commit, Rust target/toolchain, CPU frequency, flash/PSRAM settings.
- Measure warm runs separately from cold start. Run >=30 samples and report median, p95, min/max.
- Measure internal RAM and PSRAM separately, and record baseline heap before each workload.
- Do not compare different algorithms or use host-side benchmarks as ESP32 results.
- Avoid printf inside timed loops. Verify checksums after timing.
- Use the same dataset size and repetitions, ensuring total runtime exceeds timer resolution.
- Run tests with Wi-Fi/BLE disabled or explicitly report their state.
- Flash size from build artifacts is not equivalent to runtime RAM.

## Commands
```sh
idf.py set-target esp32
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

This currently executes a **C baseline** only. Rust and Goose implementations are pending toolchain/runtime validation.

## Output
UART records prefixed `BENCH,` contain workload, implementation, sample index, elapsed microseconds, checksum, free internal heap and free PSRAM. This is not peak memory; add heap tracing or explicit high-water instrumentation before making peak-memory claims.
