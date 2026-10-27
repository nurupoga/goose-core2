# Migration roadmap

1. Pin upstream Goose and validate C generation.
2. Audit generated C with ESP-IDF Xtensa compiler.
3. Port bounded data-stack allocation to PSRAM with explicit overflow handling.
4. Adapt runtime OS abstractions for a single FreeRTOS task.
5. Run Goose-originated arithmetic on physical Core2 and capture UART logs.
6. Benchmark Goose vs equivalent C with timing and heap metrics.

Do not claim Core2 support before hardware verification.
