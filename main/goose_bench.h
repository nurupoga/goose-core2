#pragma once
#include <stdint.h>

void goose_bench_init(void);
uint32_t goose_bench_expected(void);
uint32_t goose_bench_step(int32_t inner);

void goose_record_arena_init(void);
uint32_t goose_record_arena_run(int64_t n, int64_t inner);
