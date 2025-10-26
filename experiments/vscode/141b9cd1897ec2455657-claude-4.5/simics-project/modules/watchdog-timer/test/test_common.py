# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
Common test utilities for watchdog timer tests
"""

import simics
import conf

def create_watchdog_with_clock(name='wdog_test'):
    """
    Create a watchdog timer device with a clock for simulation
    
    Returns:
        tuple: (device, clock) - The watchdog device and clock objects
    """
    # Create clock for time progression
    clock = simics.pre_conf_object(f'{name}_clk', 'clock')
    clock.freq_mhz = 1  # 1 MHz for simple testing
    
    # Create watchdog device
    wdog = simics.pre_conf_object(name, 'watchdog_timer')
    wdog.queue = clock
    
    # Add configuration
    simics.SIM_add_configuration([clock, wdog], None)
    
    # Get configured objects
    return getattr(conf, name), getattr(conf, f'{name}_clk')
