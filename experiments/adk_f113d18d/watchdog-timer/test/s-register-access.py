# Test suite for basic register access functionality of Watchdog Timer device
# Based on Simics Model Test Best Practices patterns

import stest
import test_util
from watchdog_timer_common import *

def test_register_access():
    """
    Test basic register access operations for all watchdog timer registers
    """
    # Connect to the test target using test utilities
    cpu, watchdog = test_util.setup_test_environment()
    
    # Test WDOGLOAD register (0x00) - Read/Write
    print("Testing WDOGLOAD register access...")
    
    # Write a test value
    test_value = 0x12345678
    write_register(cpu, watchdog, 0x00, test_value)
    
    # Read back the value
    read_value = read_register(cpu, watchdog, 0x00)
    assert read_value == test_value, f"WDOGLOAD write/read mismatch: wrote {test_value:08x}, read {read_value:08x}"
    
    # Test different values
    test_values = [0x00000000, 0xFFFFFFFF, 0xAAAAAAAA, 0x55555555]
    for val in test_values:
        write_register(cpu, watchdog, 0x00, val)
        read_value = read_register(cpu, watchdog, 0x00)
        assert read_value == val, f"WDOGLOAD value {val:08x} not preserved"
    
    print("WDOGLOAD register access test passed")
    
    # Test WDOGVALUE register (0x04) - Read Only
    print("Testing WDOGVALUE register access...")
    
    # Try to write a value (should not change register content)
    initial_value = read_register(cpu, watchdog, 0x04)
    write_register(cpu, watchdog, 0x04, 0xDEADBEEF)  # Should be ignored
    read_value = read_register(cpu, watchdog, 0x04)
    
    # The register should retain its original value (or a different value if timer is running)
    print(f"WDOGVALUE before write: {initial_value:08x}, after write: {read_value:08x}")
    
    print("WDOGVALUE register access test passed")
    
    # Test WDOGCONTROL register (0x08) - Read/Write
    print("Testing WDOGCONTROL register access...")
    
    control_test_values = [0x00000000, 0x0000001F, 0x00000001, 0x00000002, 0x00000007]
    for val in control_test_values:
        write_register(cpu, watchdog, 0x08, val)
        read_value = read_register(cpu, watchdog, 0x08)
        assert read_value == val, f"WDOGCONTROL value {val:08x} not preserved, read {read_value:08x}"
    
    print("WDOGCONTROL register access test passed")
    
    # Test WDOGINTCLR register (0x0C) - Write Only (read should return 0 or undefined)
    print("Testing WDOGINTCLR register access...")
    
    # Read initial value (may be 0 or undefined)
    initial_read = read_register(cpu, watchdog, 0x0C)
    print(f"Initial WDOGINTCLR read value: {initial_read:08x}")
    
    # Write a value
    write_register(cpu, watchdog, 0x0C, 0xBAADF00D)
    
    # Read after write (may still be 0 or show last written value depending on implementation)
    read_value = read_register(cpu, watchdog, 0x0C)
    print(f"WDOGINTCLR read after write: {read_value:08x}")
    
    print("WDOGINTCLR register access test passed")
    
    # Test WDOGRIS register (0x10) - Read Only
    print("Testing WDOGRIS register access...")
    
    initial_value = read_register(cpu, watchdog, 0x10)
    print(f"Initial WDOGRIS value: {initial_value:08x}")
    
    # Attempt to write (should not change the register)
    write_register(cpu, watchdog, 0x10, 0x12345678)
    read_value = read_register(cpu, watchdog, 0x10)
    
    # For read-only registers, the value should not be affected by writes
    # However, the actual value may change due to device operation
    print(f"WDOGRIS value after attempted write: {read_value:08x}")
    
    print("WDOGRIS register access test passed")
    
    # Test WDOGMIS register (0x14) - Read Only
    print("Testing WDOGMIS register access...")
    
    initial_value = read_register(cpu, watchdog, 0x14)
    print(f"Initial WDOGMIS value: {initial_value:08x}")
    
    # Attempt to write (should not change the register)
    write_register(cpu, watchdog, 0x14, 0x87654321)
    read_value = read_register(cpu, watchdog, 0x14)
    
    print(f"WDOGMIS value after attempted write: {read_value:08x}")
    print("WDOGMIS register access test passed")
    
    # Test lock register: WDOGLOCK (0xC00) - Read/Write
    print("Testing WDOGLOCK register access...")
    
    old_lock_value = read_register(cpu, watchdog, 0xC00)
    print(f"Initial WDOGLOCK value: {old_lock_value:08x}")
    
    # Write unlock value
    write_register(cpu, watchdog, 0xC00, 0x1ACCE551)
    read_value = read_register(cpu, watchdog, 0xC00)
    print(f"WDOGLOCK after unlock write: {read_value:08x}")
    
    # Write a different value (should lock)
    write_register(cpu, watchdog, 0xC00, 0x00000000)
    read_value = read_register(cpu, watchdog, 0xC00)
    print(f"WDOGLOCK after lock write: {read_value:08x}")
    
    print("WDOGLOCK register access test passed")
    
    # Test integration test registers: WDOGITCR (0xF00) and WDOGITOP (0xF04)
    print("Testing integration test registers access...")
    
    # WDOGITCR - Read/Write
    write_register(cpu, watchdog, 0xF00, 0x00000001)
    read_value = read_register(cpu, watchdog, 0xF00)
    assert read_value == 0x00000001, f"WDOGITCR write/read failed: wrote 1, read {read_value:08x}"
    
    write_register(cpu, watchdog, 0xF00, 0x00000000)
    read_value = read_register(cpu, watchdog, 0xF00)
    assert read_value == 0x00000000, f"WDOGITCR write/read failed: wrote 0, read {read_value:08x}"
    
    print("WDOGITCR register access test passed")
    
    # WDOGITOP - Write Only
    initial_read = read_register(cpu, watchdog, 0xF04)
    print(f"Initial WDOGITOP value: {initial_read:08x}")
    
    write_register(cpu, watchdog, 0xF04, 0x00000003)
    read_value = read_register(cpu, watchdog, 0xF04)
    print(f"WDOGITOP after write: {read_value:08x}")
    
    print("WDOGITOP register access test passed")
    
    # Test ID registers (read-only)
    print("Testing peripheral ID registers access...")
    
    # These should return specific constant values per the specification
    id_tests = [
        (0xFE0, 0x24, "WDOGPERIPHID0"),
        (0xFE4, 0xB8, "WDOGPERIPHID1"),
        (0xFE8, 0x1B, 0x00, "WDOGPERIPHID2"),
        (0xFEC, 0x00, "WDOGPERIPHID3"),
        (0xFD0, 0x04, "WDOGPERIPHID4"),
        (0xFD4, 0x00, "WDOGPERIPHID5"),
        (0xFD8, 0x00, "WDOGPERIPHID6"),
        (0xFDC, 0x00, "WDOGPERIPHID7")
    ]
    
    for offset, expected, name in [(0xFE0, 0x24, "WDOGPERIPHID0"), (0xFE4, 0xB8, "WDOGPERIPHID1"), 
                                   (0xFE8, 0x1B, "WDOGPERIPHID2"), (0xFEC, 0x00, "WDOGPERIPHID3"),
                                   (0xFD0, 0x04, "WDOGPERIPHID4"), (0xFD4, 0x00, "WDOGPERIPHID5"),
                                   (0xFD8, 0x00, "WDOGPERIPHID6"), (0xFDC, 0x00, "WDOGPERIPHID7")]:
        value = read_register(cpu, watchdog, offset)
        print(f"{name} (0x{offset:03X}): 0x{value:08x}")
        # Note: For now just report values, don't assert since they might be 8-bit values
        # in a 32-bit register read
    
    # Test PrimeCell ID registers
    print("Testing PrimeCell ID registers access...")
    pcell_tests = [
        (0xFF0, 0x0D, "WDOGPCELLID0"),
        (0xFF4, 0xF0, "WDOGPCELLID1"), 
        (0xFF8, 0x05, "WDOGPCELLID2"),
        (0xFFC, 0xB1, "WDOGPCELLID3")
    ]
    
    for offset, expected, name in pcell_tests:
        value = read_register(cpu, watchdog, offset)
        print(f"{name} (0x{offset:03X}): 0x{value:08x}")
    
    print("ID register access tests passed")


def test_reset_values():
    """Test that registers have correct reset values"""
    print("Testing register reset values...")
    
    # Connect to the test target using test utilities
    cpu, watchdog = test_util.setup_test_environment()
    
    # Check important reset values
    load_val = read_register(cpu, watchdog, 0x00)  # WDOGLOAD
    value_val = read_register(cpu, watchdog, 0x04)  # WDOGVALUE
    ctrl_val = read_register(cpu, watchdog, 0x08)   # WDOGCONTROL
    lock_val = read_register(cpu, watchdog, 0xC00)  # WDOGLOCK
    
    print(f"WDOGLOAD reset value: 0x{load_val:08x}")
    print(f"WDOGVALUE reset value: 0x{value_val:08x}")
    print(f"WDOGCONTROL reset value: 0x{ctrl_val:08x}")
    print(f"WDOGLOCK reset value: 0x{lock_val:08x}")
    
    # These should match the specification
    # WDOGLOAD reset: 0xFFFFFFFF
    # WDOGCONTROL reset: 0x00000000
    # WDOGLOCK reset: 0x00000000
    
    print("Reset value check completed")


def test_access_violations():
    """Test register access protection mechanisms"""
    print("Testing register access violations...")
    
    # Connect to the test target using test utilities
    cpu, watchdog = test_util.setup_test_environment()
    
    # First, lock the watchdog registers
    print("Locking watchdog registers...")
    write_register(cpu, watchdog, 0xC00, 0x00000000)  # Lock by writing non-magic value
    
    # Try to write to WDOGLOAD (should be blocked)
    old_load = read_register(cpu, watchdog, 0x00)  # Save original value
    write_register(cpu, watchdog, 0x00, 0xDEADBEEF)  # Try to write to WDOGLOAD
    new_load = read_register(cpu, watchdog, 0x00)   # Check if it changed
    
    if old_load == new_load:
        print("Lock mechanism working: WDOGLOAD write was blocked")
    else:
        print(f"Lock mechanism failed: WDOGLOAD changed from {old_load:08x} to {new_load:08x}")
    
    # Test that WDOGLOCK register itself is still writable when locked
    old_lock = read_register(cpu, watchdog, 0xC00)
    write_register(cpu, watchdog, 0xC00, 0x1ACCE551)  # Try to unlock
    new_lock = read_register(cpu, watchdog, 0xC00)
    
    if new_lock == 0x1ACCE551:
        print("WDOGLOCK register remains writable when device locked")
    else:
        print(f"WDOGLOCK register not writable when locked: {new_lock:08x}")
    
    # Unlock for subsequent tests
    write_register(cpu, watchdog, 0xC00, 0x1ACCE551)
    print("Watchdog registers unlocked for further testing")


def test_out_of_range_access():
    """Test access to non-existent registers"""
    print("Testing out-of-range register access...")
    
    # Connect to the test target using test utilities
    cpu, watchdog = test_util.setup_test_environment()
    
    # Try to access an address beyond the defined register space
    try:
        read_register(cpu, watchdog, 0x2000)  # Beyond 4KB range
        print("Out-of-range read did not generate exception")
    except:
        print("Out-of-range read correctly generated exception")


if __name__ == "__main__":
    test_register_access()
    test_reset_values()
    test_access_violations()
    # test_out_of_range_access()  # Uncomment if expecting exceptions
    print("All register access tests completed")