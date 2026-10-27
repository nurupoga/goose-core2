#include "benchmark.h"
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include "esp_timer.h"
#include "esp_heap_caps.h"

#define N 1024
#define RUNS 30
#define INNER 1000

static uint32_t values[N];
static volatile uint32_t sink;

static void init_data(void) {
    uint32_t state = 0x12345678u;
    for (unsigned i = 0; i < N; ++i) {
        state = state * 1664525u + 1013904223u;
        values[i] = state;
    }
}

#if defined(__GNUC__)
__attribute__((noinline))
#endif
static uint32_t array_scan(void) {
    uint32_t sum = 0;
    for (unsigned i = 0; i < N; ++i) {
        sum += values[i] >> 16;
    }
    return sum;
}

void benchmark_run(void) {
    init_data();
    uint32_t expected = array_scan();
    printf("BENCH_META,workload=array_scan,impl=c,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", N, INNER, RUNS, expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        uint32_t check = 0;
        int64_t start = esp_timer_get_time();
        for (unsigned j = 0; j < INNER; ++j) {
            check ^= array_scan();
        }
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,array_scan,c,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, expected,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    }
}
