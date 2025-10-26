# © 2025 Intel Corporation
# Test: WDOGLOCK Register Access (T013)
# Contract: contracts/register-access.md - WDOGLOCK Register Access

import simics
import stest
import dev_util
from sp805_wdt_common import create_sp805_wdt

# Register offsets
WDOGLOCK_OFFSET = 0xC00

# Lock/unlock values
UNLOCK_KEY = 0x1ACCE551

def test_wdoglock_read_unlocked():
    """Test WDOGLOCK read contract: returns 0x00000000 when unlocked"""
    dev = create_sp805_wdt('wdt_lock_test')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_lock', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessor
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Device should be unlocked initially (reset value)
    value = wdoglock.read()
    stest.expect_equal(value, 0x00000000, "WDOGLOCK should read 0x00000000 when unlocked")

def test_wdoglock_write_lock():
    """Test WDOGLOCK write contract: any value except unlock key locks device"""
    dev = create_sp805_wdt('wdt_lock_test2')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_lock2', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessor
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Write any value except unlock key to lock
    wdoglock.write(0x12345678)
    
    # Read back - should be 0x00000001 (locked)
    value = wdoglock.read()
    stest.expect_equal(value, 0x00000001, "WDOGLOCK should read 0x00000001 when locked")

def test_wdoglock_write_unlock():
    """Test WDOGLOCK write contract: unlock key (0x1ACCE551) unlocks device"""
    dev = create_sp805_wdt('wdt_lock_test3')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_lock3', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessor
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Lock device first
    wdoglock.write(0x00000000)
    stest.expect_equal(wdoglock.read(), 0x00000001, "Device should be locked")
    
    # Unlock with magic key
    wdoglock.write(UNLOCK_KEY)
    
    # Read back - should be 0x00000000 (unlocked)
    value = wdoglock.read()
    stest.expect_equal(value, 0x00000000, "WDOGLOCK should read 0x00000000 after unlock")

def test_wdoglock_immediate_effect():
    """Test WDOGLOCK write contract: lock state change takes effect immediately"""
    dev = create_sp805_wdt('wdt_lock_test4')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_lock4', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessor
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Lock device
    wdoglock.write(0xFFFFFFFF)
    
    # Immediately read - should be locked
    value = wdoglock.read()
    stest.expect_equal(value, 0x00000001, "Lock should take effect immediately")
    
    # Unlock device
    wdoglock.write(UNLOCK_KEY)
    
    # Immediately read - should be unlocked
    value = wdoglock.read()
    stest.expect_equal(value, 0x00000000, "Unlock should take effect immediately")

def test_wdoglock_always_writable():
    """Test WDOGLOCK write contract: always writable (not affected by lock state)"""
    dev = create_sp805_wdt('wdt_lock_test5')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_lock5', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Create register accessor
    wdoglock = dev_util.Register_LE(phys_mem, 0x10000000 + WDOGLOCK_OFFSET, size=4)
    
    # Lock device
    wdoglock.write(0x00000000)
    stest.expect_equal(wdoglock.read(), 0x00000001, "Device should be locked")
    
    # Even when locked, should be able to unlock
    wdoglock.write(UNLOCK_KEY)
    stest.expect_equal(wdoglock.read(), 0x00000000, "Should be able to unlock even when locked")

# Run all tests
test_wdoglock_read_unlocked()
test_wdoglock_write_lock()
test_wdoglock_write_unlock()
test_wdoglock_immediate_effect()
test_wdoglock_always_writable()

print("WDOGLOCK register access tests complete (expected to FAIL until implementation)")
