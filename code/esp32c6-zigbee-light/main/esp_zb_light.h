#pragma once
#include "esp_zigbee_core.h"
#define HA_ESP_LIGHT_ENDPOINT 10
#define ESP_ZB_PRIMARY_CHANNEL_MASK (1UL << 25)
#define ESP_ZB_ZED_CONFIG() { .esp_zb_role = ESP_ZB_DEVICE_TYPE_ED, .install_code_policy = false, .nwk_cfg.zed_cfg = { .ed_timeout = ESP_ZB_ED_AGING_TIMEOUT_64MIN, .keep_alive = 3000 } }
#define ESP_ZB_DEFAULT_RADIO_CONFIG() { .radio_mode = ZB_RADIO_MODE_NATIVE }
#define ESP_ZB_DEFAULT_HOST_CONFIG() { .host_connection_mode = ZB_HOST_CONNECTION_MODE_NONE }
