# © 2025 Intel Corporation
# Test: Identification Registers (T016)
# Contract: contracts/register-access.md - Identification Registers

import simics
import stest
import dev_util
from sp805_wdt_common import create_sp805_wdt

# Register offsets and expected values (from data-model.md)
ID_REGISTERS = {
    'WDOGPERIPHID4': (0xFD0, 0x04),
    'WDOGPERIPHID5': (0xFD4, 0x00),
    'WDOGPERIPHID6': (0xFD8, 0x00),
    'WDOGPERIPHID7': (0xFDC, 0x00),
    'WDOGPERIPHID0': (0xFE0, 0x24),
    'WDOGPERIPHID1': (0xFE4, 0xB8),
    'WDOGPERIPHID2': (0xFE8, 0x1B),
    'WDOGPERIPHID3': (0xFEC, 0x00),
    'WDOGPCELLID0':  (0xFF0, 0x0D),
    'WDOGPCELLID1':  (0xFF4, 0xF0),
    'WDOGPCELLID2':  (0xFF8, 0x05),
    'WDOGPCELLID3':  (0xFFC, 0xB1),
}

def test_identification_registers_read():
    """Test identification registers read contract: return constant values"""
    dev = create_sp805_wdt('wdt_id_test')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_id', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Test each identification register
    for reg_name, (offset, expected_value) in ID_REGISTERS.items():
        reg = dev_util.Register_LE(phys_mem, 0x10000000 + offset, size=4)
        value = reg.read()
        stest.expect_equal(value, expected_value, 
                          f"{reg_name} should read 0x{expected_value:02X}")

def test_identification_registers_read_only():
    """Test identification registers write contract: writes ignored"""
    dev = create_sp805_wdt('wdt_id_test2')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_id2', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Test that writes are ignored for each identification register
    for reg_name, (offset, expected_value) in ID_REGISTERS.items():
        reg = dev_util.Register_LE(phys_mem, 0x10000000 + offset, size=4)
        
        # Try to write
        reg.write(0xDEADBEEF)
        
        # Read back - should still be constant value
        value = reg.read()
        stest.expect_equal(value, expected_value, 
                          f"{reg_name} write should be ignored")

def test_identification_registers_no_side_effects():
    """Test identification registers have no side effects"""
    dev = create_sp805_wdt('wdt_id_test3')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_id3', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Read all identification registers multiple times
    for reg_name, (offset, expected_value) in ID_REGISTERS.items():
        reg = dev_util.Register_LE(phys_mem, 0x10000000 + offset, size=4)
        
        # Read multiple times - should be consistent
        value1 = reg.read()
        value2 = reg.read()
        value3 = reg.read()
        
        stest.expect_equal(value1, expected_value, f"{reg_name} first read")
        stest.expect_equal(value2, expected_value, f"{reg_name} second read")
        stest.expect_equal(value3, expected_value, f"{reg_name} third read")

def test_arm_primecell_signature():
    """Test ARM PrimeCell identification signature"""
    dev = create_sp805_wdt('wdt_id_test4')
    
    # Map device to memory
    phys_mem = simics.SIM_create_object('memory-space', 'phys_mem_id4', [])
    phys_mem.map = [[0x10000000, dev, 0, 0, 0x1000]]
    
    # Read PrimeCell ID registers to form signature
    pcellid0 = dev_util.Register_LE(phys_mem, 0x10000000 + 0xFF0, size=4).read()
    pcellid1 = dev_util.Register_LE(phys_mem, 0x10000000 + 0xFF4, size=4).read()
    pcellid2 = dev_util.Register_LE(phys_mem, 0x10000000 + 0xFF8, size=4).read()
    pcellid3 = dev_util.Register_LE(phys_mem, 0x10000000 + 0xFFC, size=4).read()
    
    # Form 32-bit signature
    signature = (pcellid3 << 24) | (pcellid2 << 16) | (pcellid1 << 8) | pcellid0
    expected_signature = 0xB105F00D  # ARM PrimeCell signature
    
    stest.expect_equal(signature, expected_signature, 
                      "ARM PrimeCell signature should be 0xB105F00D")

# Run all tests
test_identification_registers_read()
test_identification_registers_read_only()
test_identification_registers_no_side_effects()
test_arm_primecell_signature()

print("Identification register tests complete (expected to FAIL until implementation)")
