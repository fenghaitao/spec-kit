# © 2010 Intel Corporation

import simics

# Extend this function if your device requires any additional attributes to be
# set. It is often sensible to make additional arguments to this function
# optional, and let the function create mock objects if needed.
def create_wdt(name = None):
    '''Create a new wdt object'''
    wdt = simics.pre_conf_object(name, 'wdt')
    simics.SIM_add_configuration([wdt], None)
    return simics.SIM_get_object(wdt.name)
