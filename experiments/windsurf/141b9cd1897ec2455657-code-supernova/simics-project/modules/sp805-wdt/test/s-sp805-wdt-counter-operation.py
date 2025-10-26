# © 2025 Intel Corporation
# Test: Counter Operation (T018)
# Contract: contracts/interface-behavior.md - Counter Operation

import simics
import stest
import dev_util
from sp805_wdt_common import create_sp805_wdt

# Register offsets
WDOGLOAD_OFFSET = 0x000
WDOGVALUE_OFFSET = 0x004
WDOGCONTROL_OFFSET = 0x008
WDOGLOCK_OFFSET = 0xC00

# Lock/unlock values
UNLOCK_KEY = 0x1ACCE551

def test_counter_enable():
    """Test counter enable contract: INTEN 0→1 reloads and starts counter"""
    dev = create_sp805_wdt('wdt_counter_test')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_counter', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessors
    wdogload = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOAD_OFFSET, size=4)
    wdogvalue = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGVALUE_OFFSET, size=4)
    wdogcontrol = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGCONTROL_OFFSET, size=4)
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Unlock device
    wdoglock.write(UNLOCK_KEY)
    
    # Set load value
    load_value = 0x1000
    wdogload.write(load_value)
    
    # Enable counter (INTEN=1, RESEN=0, step_value=0)
    wdogcontrol.write(0x01)  # bit[0]=1 (INTEN)
    
    # Counter should reload from WDOGLOAD
    counter_value = wdogvalue.read()
    stest.expect_equal(counter_value, load_value, 
                      "Counter should reload from WDOGLOAD on enable")

def test_counter_disable():
    """Test counter disable contract: INTEN 1→0 stops counter"""
    dev = create_sp805_wdt('wdt_counter_test2')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_counter2', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessors
    wdogload = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOAD_OFFSET, size=4)
    wdogvalue = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGVALUE_OFFSET, size=4)
    wdogcontrol = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGCONTROL_OFFSET, size=4)
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Unlock device
    wdoglock.write(UNLOCK_KEY)
    
    # Set load value and enable counter
    wdogload.write(0x1000)
    wdogcontrol.write(0x01)  # Enable
    
    # Run simulation for some cycles
    simics.SIM_run_command("run-cycles 10")
    
    # Get counter value while running
    running_value = wdogvalue.read()
    
    # Disable counter
    wdogcontrol.write(0x00)  # INTEN=0
    
    # Counter should stop (value preserved)
    stopped_value = wdogvalue.read()
    stest.expect_equal(stopped_value, running_value, 
                      "Counter value should be preserved when disabled")
    
    # Run more cycles - counter should not change
    simics.SIM_run_command("run-cycles 10")
    still_stopped = wdogvalue.read()
    stest.expect_equal(still_stopped, stopped_value, 
                      "Counter should not decrement when disabled")

def test_counter_decrement():
    """Test counter decrement contract: counter decrements based on clock divider"""
    dev = create_sp805_wdt('wdt_counter_test3')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_counter3', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessors
    wdogload = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOAD_OFFSET, size=4)
    wdogvalue = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGVALUE_OFFSET, size=4)
    wdogcontrol = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGCONTROL_OFFSET, size=4)
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Unlock device
    wdoglock.write(UNLOCK_KEY)
    
    # Set load value
    wdogload.write(0x100)
    
    # Enable counter with step_value=0 (÷1, no division)
    wdogcontrol.write(0x01)  # INTEN=1, step_value=0
    
    # Get initial counter value
    initial_value = wdogvalue.read()
    
    # Run simulation for some cycles
    cycles = 10
    simics.SIM_run_command(f"run-cycles {cycles}")
    
    # Counter should have decremented
    final_value = wdogvalue.read()
    stest.expect_true(final_value < initial_value, 
                     "Counter should decrement over time")
    
    # With step_value=0 (÷1), counter should decrement by approximately cycles
    # (allowing for some timing variation)
    expected_decrement = cycles
    actual_decrement = initial_value - final_value
    stest.expect_true(abs(actual_decrement - expected_decrement) <= 2,
                     f"Counter should decrement by ~{expected_decrement} (got {actual_decrement})")

def test_counter_reload_on_enable():
    """Test counter reload contract: enabling counter reloads from WDOGLOAD"""
    dev = create_sp805_wdt('wdt_counter_test4')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_counter4', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessors
    wdogload = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOAD_OFFSET, size=4)
    wdogvalue = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGVALUE_OFFSET, size=4)
    wdogcontrol = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGCONTROL_OFFSET, size=4)
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Unlock device
    wdoglock.write(UNLOCK_KEY)
    
    # Set initial load value
    wdogload.write(0x1000)
    
    # Enable counter
    wdogcontrol.write(0x01)
    
    # Run for some cycles
    simics.SIM_run_command("run-cycles 100")
    
    # Disable counter
    wdogcontrol.write(0x00)
    
    # Change load value
    new_load_value = 0x2000
    wdogload.write(new_load_value)
    
    # Re-enable counter - should reload from new WDOGLOAD value
    wdogcontrol.write(0x01)
    
    # Counter should have new load value
    counter_value = wdogvalue.read()
    stest.expect_equal(counter_value, new_load_value,
                      "Counter should reload from WDOGLOAD on re-enable")

# Run all tests
test_counter_enable()
test_counter_disable()
test_counter_decrement()
test_counter_reload_on_enable()

print("Counter operation tests complete (expected to FAIL until implementation)")
