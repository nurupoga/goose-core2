#include "benchmark.h"
#include "goose_bench.h"
#include "rust_bench.h"
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define N 1024
#define RUNS 30
#define INNER 1000

#define ARENA_RECORDS 64
#define ARENA_INNER 50

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
static uint32_t array_scan_c(void) {
    uint32_t sum = 0;
    for (unsigned i = 0; i < N; ++i) {
        sum += values[i] >> 16;
    }
    return sum;
}

#if defined(__GNUC__)
__attribute__((noinline))
#endif
static uint32_t array_scan_c_opt(const uint32_t *const __restrict ptr) {
    uint32_t sum = 0;
    const uint32_t *p = ptr;
    const uint32_t *const end = ptr + N;
    while (p < end) {
        sum += *p++ >> 16;
    }
    return sum;
}

/* ----------------- Record Arena Workload ----------------- */

typedef struct {
    int64_t id;
    int64_t val;
    int64_t len;
    uint8_t *payload;
} CRecord;

// 1. C Heap (malloc / free)
#if defined(__GNUC__)
__attribute__((noinline))
#endif
static uint32_t record_arena_c_heap(int64_t n, int64_t inner) {
    uint32_t check = 0;
    static CRecord records[ARENA_RECORDS];
    for (int64_t j = 0; j < inner; ++j) {
        uint32_t state = 0x12345678u + (uint32_t)j;
        for (int64_t i = 0; i < n; ++i) {
            state = state * 1664525u + 1013904223u;
            int64_t len = 16 + (state % 32);
            uint8_t *p = (uint8_t *)malloc((size_t)len);
            for (int64_t k = 0; k < len; ++k) {
                state = state * 1664525u + 1013904223u;
                p[k] = (uint8_t)(state >> 24);
            }
            state = state * 1664525u + 1013904223u;
            int64_t v = (int64_t)(state >> 16);
            records[i] = (CRecord){ .id = i, .val = v, .len = len, .payload = p };
        }

        uint32_t sum = 0;
        for (int64_t i = 0; i < n; ++i) {
            sum += (uint32_t)records[i].id;
            sum += (uint32_t)records[i].val;
            sum += (uint32_t)records[i].len;
            for (int64_t k = 0; k < records[i].len; ++k) {
                sum = (sum * 31) + records[i].payload[k];
            }
            free(records[i].payload);
        }
        check ^= sum;
    }
    return check;
}

// 2. C Arena (Bump allocator)
static uint8_t c_arena_buffer[ARENA_RECORDS * 64];

#if defined(__GNUC__)
__attribute__((noinline))
#endif
static uint32_t record_arena_c_arena(int64_t n, int64_t inner) {
    uint32_t check = 0;
    static CRecord records[ARENA_RECORDS];
    for (int64_t j = 0; j < inner; ++j) {
        uint32_t state = 0x12345678u + (uint32_t)j;
        size_t arena_offset = 0;
        for (int64_t i = 0; i < n; ++i) {
            state = state * 1664525u + 1013904223u;
            int64_t len = 16 + (state % 32);
            uint8_t *p = &c_arena_buffer[arena_offset];
            arena_offset += (size_t)len;
            for (int64_t k = 0; k < len; ++k) {
                state = state * 1664525u + 1013904223u;
                p[k] = (uint8_t)(state >> 24);
            }
            state = state * 1664525u + 1013904223u;
            int64_t v = (int64_t)(state >> 16);
            records[i] = (CRecord){ .id = i, .val = v, .len = len, .payload = p };
        }

        uint32_t sum = 0;
        for (int64_t i = 0; i < n; ++i) {
            sum += (uint32_t)records[i].id;
            sum += (uint32_t)records[i].val;
            sum += (uint32_t)records[i].len;
            for (int64_t k = 0; k < records[i].len; ++k) {
                sum = (sum * 31) + records[i].payload[k];
            }
        }
        check ^= sum;
    }
    return check;
}

void benchmark_run(void) {
    init_data();
    uint32_t expected = array_scan_c();

    /* ================= WORKLOAD 1: array_scan ================= */

    // 1. C Baseline
    printf("BENCH_META,workload=array_scan,impl=c,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", N, INNER, RUNS, expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        uint32_t check = 0;
        int64_t start = esp_timer_get_time();
        for (unsigned j = 0; j < INNER; ++j) {
            check ^= array_scan_c();
        }
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,array_scan,c,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, expected,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(1);
    }

    // 2. C Optimized
    printf("BENCH_META,workload=array_scan,impl=c_opt,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", N, INNER, RUNS, expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        uint32_t check = 0;
        int64_t start = esp_timer_get_time();
        for (unsigned j = 0; j < INNER; ++j) {
            check ^= array_scan_c_opt(values);
        }
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,array_scan,c_opt,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, expected,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(1);
    }

    // 3. Goose array_scan
    goose_bench_init();
    uint32_t goose_expected = goose_bench_expected();
    printf("BENCH_META,workload=array_scan,impl=goose,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", N, INNER, RUNS, goose_expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        int64_t start = esp_timer_get_time();
        uint32_t check = goose_bench_step(INNER);
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,array_scan,goose,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, goose_expected,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(1);
    }

    // 4. Rust array_scan
    rust_bench_init();
    uint32_t rust_expected = rust_array_scan();
    printf("BENCH_META,workload=array_scan,impl=rust,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", N, INNER, RUNS, rust_expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        int64_t start = esp_timer_get_time();
        uint32_t check = rust_array_scan_step(INNER);
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,array_scan,rust,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, rust_expected,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(1);
    }

    /* ================= WORKLOAD 2: record_arena ================= */
    uint32_t arena_expected = 2469415251u;

    // 1. C Heap (malloc / free)
    printf("BENCH_META,workload=record_arena,impl=c_heap,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", ARENA_RECORDS, ARENA_INNER, RUNS, arena_expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        int64_t start = esp_timer_get_time();
        uint32_t check = record_arena_c_heap(ARENA_RECORDS, ARENA_INNER);
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,record_arena,c_heap,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, check,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(1);
    }

    // 2. C Arena (bump pointer)
    printf("BENCH_META,workload=record_arena,impl=c_arena,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", ARENA_RECORDS, ARENA_INNER, RUNS, arena_expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        int64_t start = esp_timer_get_time();
        uint32_t check = record_arena_c_arena(ARENA_RECORDS, ARENA_INNER);
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,record_arena,c_arena,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, check,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(1);
    }

    // 3. Goose record_arena
    goose_record_arena_init();
    printf("BENCH_META,workload=record_arena,impl=goose,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", ARENA_RECORDS, ARENA_INNER, RUNS, arena_expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        int64_t start = esp_timer_get_time();
        uint32_t check = goose_record_arena_run(ARENA_RECORDS, ARENA_INNER);
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,record_arena,goose,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, check,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(1);
    }

    // 4. Rust record_arena
    printf("BENCH_META,workload=record_arena,impl=rust,N=%u,inner=%u,runs=%u,expected=%" PRIu32 "\n", ARENA_RECORDS, ARENA_INNER, RUNS, arena_expected);
    for (unsigned sample = 0; sample < RUNS; ++sample) {
        int64_t start = esp_timer_get_time();
        uint32_t check = rust_record_arena_step(ARENA_RECORDS, ARENA_INNER);
        int64_t elapsed = esp_timer_get_time() - start;
        sink = check;
        printf("BENCH,record_arena,rust,%u,%" PRId64 ",%" PRIu32 ",%u,%u\n",
               sample, elapsed, check,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
        vTaskDelay(1);
    }
}
