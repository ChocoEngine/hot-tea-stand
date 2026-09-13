cmake_minimum_required(VERSION 3.16)
# This project is specific to the RISC-V ESP32-C6, not the default ESP32.
set(IDF_TARGET "esp32c6")
set(PROJECT_VER "1.0.0")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32c6_zigbee_light)
