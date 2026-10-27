# Implementation status

| Implementation | Build | Hardware run | Checksum parity |
|---|---|---|---|
| C baseline | verified (ESP-IDF v5.3.1) | verified (Core2, 30 runs, median 96.23 ms) | verified (`33582136`) |
| C optimized | verified (ESP-IDF v5.3.1) | verified (Core2, 30 runs, median 57.82 ms) | verified (`33582136`) |
| Goose (ported runtime) | verified (ESP-IDF v5.3.1 + PSRAM) | verified (Core2, 30 runs, median 147.55 ms) | verified (`33582136`) |
| Rust | pending toolchain | pending | pending |

Do not treat generated examples or unexecuted tests as measurements.

## Acceptance
- [x] 1. C baseline compiles and runs on Core2.
- [x] 2. UART capture yields 30 records and parser CSV.
- [ ] 3. Rust and Goose use the same deterministic PRNG input and reduction.
- [ ] 4. Add memory peaks and firmware size measurement before publishing comparisons.
