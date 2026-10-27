#pragma once
#include <stdint.h>

void goose_bench_init(void);
uint32_t goose_bench_expected(void);
uint32_t goose_bench_step(int32_t inner);
