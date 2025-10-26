# © 2010 Intel Corporation

import simics

def create_sp805_wdt(name = None):
    '''Create a new sp805_wdt object with proper memory mapping'''
    if name is None:
        name = 'sp805_wdt_' + str(simics.SIM_get_unique_number())

    # Create the device
    sp805_wdt = simics.pre_conf_object(name, 'sp805_wdt')
    simics.SIM_add_configuration([sp805_wdt], None)

    # Create memory space and map the device
    phys_mem = simics.pre_conf_object(name + '_mem', 'memory-space')
    simics.SIM_add_configuration([phys_mem], None)

    # Map device to memory address 0x10000000
    phys_mem.map = [[0x10000000, sp805_wdt, 0, 0, 0x1000]]

    return sp805_wdt, phys_mem
