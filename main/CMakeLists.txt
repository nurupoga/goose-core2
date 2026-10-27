idf_component_register(
    SRCS "app_main.c" "benchmark.c" "goose_array_scan.c" "goose_record_arena.c" "goose_runtime.c"
    INCLUDE_DIRS "."
    REQUIRES esp_timer esp_psram freertos heap log
)

target_link_libraries(${COMPONENT_LIB} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/rust_bench.o")

target_compile_options(${COMPONENT_LIB} PRIVATE
    -Wno-error
    -Wno-unused-const-variable
    -Wno-unused-variable
    -Wno-unused-function
    -Wno-maybe-uninitialized
)
