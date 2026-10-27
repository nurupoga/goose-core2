#include "esp_log.h"
#include "esp_heap_caps.h"

static const char *TAG = "goose_core2";

void app_main(void) {
    ESP_LOGI(TAG, "Core2 ESP-IDF baseline (Goose not integrated yet)");
    ESP_LOGI(TAG, "Free internal heap: %u bytes", (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL));
    ESP_LOGI(TAG, "Free PSRAM heap: %u bytes", (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
}
