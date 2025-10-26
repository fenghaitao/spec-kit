# © 2023 Intel Corporation

simics_add_module(sp805-wdt
  CLASSES sp805_wdt
  SOURCES sp805-wdt.dml module_load.py
  SIMICS_API 7
)
add_subdirectory(test)
