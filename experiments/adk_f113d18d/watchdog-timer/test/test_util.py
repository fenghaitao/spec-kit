"""
Utility functions for watchdog timer tests
"""
import simics
import stest
import dev_util

def write_register(cpu, device, offset, value):
    """
    Write a value to a register at a given offset
    For direct test access to the watchdog timer registers 
    """
    if cpu:
        try:
            # Try direct physical memory access
            # Find the device's address if it has one
            if hasattr(device, 'attr') and hasattr(device.attr, 'address'):
                addr = device.attr.address + offset
                simics.SIM_write_phys_memory(cpu, addr, value, 4)
            else:
                # Use the register bank interface if available
                if hasattr(device, 'iface') and hasattr(device.iface, 'register_bank'):
                    bank = device.iface.register_bank
                    bank.write(offset, value, 4)
        except:
            # Alternative: try to access via object attributes if possible
            # This is more complex and depends on how the device is implemented
            pass
    else:
        # Without CPU access, we have to use alternative methods if available
        try:
            # Use the register bank interface if available
            if hasattr(device, 'iface') and hasattr(device.iface, 'register_bank'):
                bank = device.iface.register_bank
                bank.write(offset, value, 4)
        except:
            pass

def read_register(cpu, device, offset):
    """
    Read a value from a register at a given offset
    """
    if cpu:
        try:
            # Try direct physical memory access
            if hasattr(device, 'attr') and hasattr(device.attr, 'address'):
                addr = device.attr.address + offset
                return simics.SIM_read_phys_memory(cpu, addr, 4)
            else:
                # Use the register bank interface if available
                if hasattr(device, 'iface') and hasattr(device.iface, 'register_bank'):
                    bank = device.iface.register_bank
                    return bank.read(offset, 4)
        except:
            # Return 0 if reading fails
            return 0
    else:
        try:
            # Use the register bank interface if available
            if hasattr(device, 'iface') and hasattr(device.iface, 'register_bank'):
                bank = device.iface.register_bank
                return bank.read(offset, 4)
        except:
            # Return 0 if reading fails
            return 0

def setup_test_environment():
    """
    Set up a basic test environment with CPU and watchdog timer
    """
    # Get the currently running CPU object if any, or create a simple test object
    # First try to get an existing CPU in the configuration
    cpu = None
    try:
        # Try to get a valid CPU in the config (like x86 cpu or other)
        all_objects = simics.SIM_get_all_objects()
        for obj in all_objects:
            if hasattr(obj, 'ifc') and 'cpu' in obj.ifc:
                cpu = obj
                break
    except:
        pass
    
    # If no CPU found, try to use the first object or create a dummy reference
    if not cpu:
        try:
            all_objects = simics.SIM_get_all_objects()
            if all_objects:
                cpu = all_objects[0]
        except:
            # If no objects exist, we'll have to handle this situation differently
            # For register access, we may not need a real CPU if we access device directly
            cpu = None
    
    # Get or create the watchdog timer device
    watchdog = None
    try:
        watchdog = simics.SIM_get_object("watchdog-timer")
    except:
        try:
            watchdog = simics.SIM_create_object("watchdog_timer", "watchdog-timer", [])
        except Exception as e:
            # If we can't create the object, try to find it by a different name
            all_objects = simics.SIM_get_all_objects()
            for obj in all_objects:
                if hasattr(obj, 'class_name') and 'watchdog' in obj.class_name.lower():
                    watchdog = obj
                    break
    
    if not watchdog:
        raise Exception("No watchdog timer device available")
    
    # Return the objects
    return cpu, watchdog

def get_watchdog_device():
    """
    Get the watchdog timer device instance
    """
    # Get the watchdog timer device
    watchdog = None
    try:
        watchdog = simics.SIM_get_object("watchdog-timer")
    except:
        # Look for the watchdog device by class name if it's in the config
        all_objects = simics.SIM_get_all_objects()
        for obj in all_objects:
            if hasattr(obj, 'class_name') and 'watchdog' in obj.class_name.lower():
                watchdog = obj
                break
    
    if not watchdog:
        raise Exception("No watchdog timer device available")
    
    return watchdog