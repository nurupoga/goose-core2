# Implementation status

| Implementation | Build | Hardware run | Checksum parity |
|---|---|---|---|
| C baseline | verified (ESP-IDF v5.3.1) | verified (Core2, 30 runs, median 96.23 ms) | verified (`33582136` / `2469415251`) |
| C optimized / Arena | verified (ESP-IDF v5.3.1) | verified (Core2, 30 runs, median 57.81 ms / 36.79 ms) | verified (`33582136` / `2469415251`) |
| Rust (`no_std`) | verified (`esp` 1.97.0-nightly) | verified (Core2, 30 runs, median 64.19 ms / 23.68 ms) | verified (`33582136` / `2469415251`) |
| Goose (ported runtime) | verified (ESP-IDF v5.3.1 + PSRAM) | verified (Core2, 30 runs, median 147.54 ms / 55.84 ms) | verified (`33582136` / `2469415251`) |

Do not treat generated examples or unexecuted tests as measurements.

## Acceptance
- [x] 1. C baseline compiles and runs on Core2.
- [x] 2. UART capture yields 30 records and parser CSV.
- [x] 3. Rust and Goose use the same deterministic PRNG input and reduction.
- [x] 4. Add memory peaks and firmware size measurement before publishing comparisons.
