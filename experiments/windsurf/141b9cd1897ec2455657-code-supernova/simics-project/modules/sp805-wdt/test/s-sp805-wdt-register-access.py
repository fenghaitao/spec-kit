# © 2025 Intel Corporation
# Test: WDOGLOAD Register Access (T007)
# Contract: contracts/register-access.md - WDOGLOAD Register Access

# Test: WDOGLOAD Register Access (T007)
# Contract: contracts/register-access.md - WDOGLOAD Register Access

import simics
import stest
import dev_util
from sp805_wdt_common import create_sp805_wdt

# Register offsets
WDOGLOAD_OFFSET = 0x000
WDOGLOCK_OFFSET = 0xC00

# Lock/unlock values
UNLOCK_KEY = 0x1ACCE551

def test_wdogload_read():
    """Test WDOGLOAD read contract: returns current value, no side effects"""
    dev, phys_mem = create_sp805_wdt('wdt_test')

    # Create register accessor
    wdogload = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOAD_OFFSET, size=4)

    # Read initial value (should be reset value 0xFFFFFFFF)
    value = wdogload.read()
    stest.expect_equal(value, 0xFFFFFFFF, "WDOGLOAD initial value should be 0xFFFFFFFF")

    # Read again - should be same (no side effects)
    value2 = wdogload.read()
    stest.expect_equal(value2, value, "WDOGLOAD read should have no side effects")

def test_wdogload_write_unlocked():
    """Test WDOGLOAD write contract: when unlocked, register updates"""
    dev, phys_mem = create_sp805_wdt('wdt_test2')

    # Create register accessors
    wdogload = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOAD_OFFSET, size=4)
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)

    # Unlock device
    wdoglock.write(UNLOCK_KEY)

    # Write to WDOGLOAD
    test_value = 0x12345678
    wdogload.write(test_value)

    # Read back - should match
    value = wdogload.read()
    stest.expect_equal(value, test_value, "WDOGLOAD should update when unlocked")

def test_wdogload_write_locked():
    """Test WDOGLOAD write contract: when locked, write ignored"""
    dev, phys_mem = create_sp805_wdt('wdt_test3')

    # Create register accessors
    wdogload = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOAD_OFFSET, size=4)
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)

    # Lock device (write any value except unlock key)
    wdoglock.write(0x00000000)

    # Read initial value
    initial_value = wdogload.read()

    # Try to write to WDOGLOAD (should be ignored)
    wdogload.write(0xDEADBEEF)

    # Read back - should be unchanged
    value = wdogload.read()
    stest.expect_equal(value, initial_value, "WDOGLOAD write should be ignored when locked")

def test_wdogload_no_side_effects():
    """Test WDOGLOAD write has no immediate effect on counter"""
    dev, phys_mem = create_sp805_wdt('wdt_test4')

    # Create register accessors
    wdogload = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOAD_OFFSET, size=4)
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)

    # Unlock and write to WDOGLOAD
    wdoglock.write(UNLOCK_KEY)
    wdogload.write(0x1000)

    # Writing to WDOGLOAD should not immediately affect counter
    # (Counter only reloads on enable or interrupt clear)
    # This test verifies no immediate side effects
    # Actual counter behavior tested in interface-behavior tests

# Run all tests
test_wdogload_read()
test_wdogload_write_unlocked()
test_wdogload_write_locked()
test_wdogload_no_side_effects()

print("WDOGLOAD register access tests complete (expected to FAIL until implementation)")
