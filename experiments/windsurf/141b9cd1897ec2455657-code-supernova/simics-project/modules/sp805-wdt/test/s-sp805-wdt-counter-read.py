# © 2025 Intel Corporation
# Test: WDOGVALUE Register Access (T008)
# Contract: contracts/register-access.md - WDOGVALUE Register Access

import simics
import stest
import dev_util
from sp805_wdt_common import create_sp805_wdt

# Register offsets
WDOGVALUE_OFFSET = 0x004

def test_wdogvalue_read():
    """Test WDOGVALUE read contract: returns current counter value"""
    dev = create_sp805_wdt('wdt_value_test')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_value', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessor
    wdogvalue = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGVALUE_OFFSET, size=4)
    
    # Read initial value (should be reset value 0xFFFFFFFF)
    value = wdogvalue.read()
    stest.expect_equal(value, 0xFFFFFFFF, "WDOGVALUE initial value should be 0xFFFFFFFF")

def test_wdogvalue_read_only():
    """Test WDOGVALUE write contract: writes ignored (read-only)"""
    dev = create_sp805_wdt('wdt_value_test2')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_value2', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessor
    wdogvalue = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGVALUE_OFFSET, size=4)
    
    # Read initial value
    initial_value = wdogvalue.read()
    
    # Try to write (should be ignored)
    wdogvalue.write(0x12345678)
    
    # Read back - should be unchanged
    value = wdogvalue.read()
    stest.expect_equal(value, initial_value, "WDOGVALUE write should be ignored (read-only)")

def test_wdogvalue_no_side_effects():
    """Test WDOGVALUE read has no side effects"""
    dev = create_sp805_wdt('wdt_value_test3')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_value3', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessor
    wdogvalue = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGVALUE_OFFSET, size=4)
    
    # Read multiple times - should be consistent (no side effects)
    value1 = wdogvalue.read()
    value2 = wdogvalue.read()
    value3 = wdogvalue.read()
    
    stest.expect_equal(value2, value1, "WDOGVALUE read should have no side effects")
    stest.expect_equal(value3, value1, "WDOGVALUE read should have no side effects")

# Run all tests
test_wdogvalue_read()
test_wdogvalue_read_only()
test_wdogvalue_no_side_effects()

print("WDOGVALUE register access tests complete (expected to FAIL until implementation)")
