#pragma once
#include <stdint.h>

void rust_bench_init(void);
uint32_t rust_array_scan(void);
uint32_t rust_array_scan_step(int32_t inner);
uint32_t rust_record_arena_step(int64_t n, int64_t inner);
