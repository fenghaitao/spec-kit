# © 2023 Intel Corporation

simics_add_module(watchdog-timer
  CLASSES watchdog_timer
  SOURCES watchdog-timer.dml module_load.py
  SIMICS_API 7
)
add_subdirectory(test)
