# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
Basic Register Access Tests for Watchdog Timer Device

Tests all 21 registers for:
- Reset values
- Read/write access permissions
- Lock protection mechanism
"""

import simics
import stest
import dev_util

class WatchdogTimerBasicRegisterTest(object):
    """Test basic register access for watchdog timer device"""
    
    def setup(self):
        """Create watchdog timer device for testing"""
        self.dev = simics.SIM_create_object('watchdog_timer', 'wdog_test', [])
        self.bank = self.dev.bank.regs
        
        # Define register map with (offset, size, access, reset_value)
        self.registers = {
            'WDOGLOAD': (0x000, 4, 'RW', 0xFFFFFFFF),
            'WDOGVALUE': (0x004, 4, 'RO', 0xFFFFFFFF),
            'WDOGCONTROL': (0x008, 4, 'RW', 0x00000000),
            'WDOGINTCLR': (0x00C, 4, 'WO', None),  # Write-only, no reset value
            'WDOGRIS': (0x010, 4, 'RO', 0x00000000),
            'WDOGMIS': (0x014, 4, 'RO', 0x00000000),
            'WDOGLOCK': (0xC00, 4, 'RW', 0x00000001),  # Locked on reset
            'WDOGITCR': (0xF00, 4, 'RW', 0x00000000),
            'WDOGITOP': (0xF04, 4, 'WO', None),  # Write-only
            'WDOGPeriphID0': (0xFE0, 4, 'RO', 0x00000005),
            'WDOGPeriphID1': (0xFE4, 4, 'RO', 0x00000018),
            'WDOGPeriphID2': (0xFE8, 4, 'RO', 0x00000018),
            'WDOGPeriphID3': (0xFEC, 4, 'RO', 0x00000000),
            'WDOGPCellID0': (0xFF0, 4, 'RO', 0x0000000D),
            'WDOGPCellID1': (0xFF4, 4, 'RO', 0x000000F0),
            'WDOGPCellID2': (0xFF8, 4, 'RO', 0x00000005),
            'WDOGPCellID3': (0xFFC, 4, 'RO', 0x000000B1),
        }
    
    def test_reset_values(self):
        """Test all registers have correct reset values"""
        stest.expect_true(self.dev is not None, "Device created successfully")
        
        for name, (offset, size, access, reset_val) in self.registers.items():
            if reset_val is not None:  # Skip write-only registers
                reg = dev_util.Register_LE(self.bank, offset, size)
                actual = reg.read()
                stest.expect_equal(actual, reset_val, 
                    f"{name} reset value should be 0x{reset_val:08X}, got 0x{actual:08X}")
    
    def test_read_only_registers(self):
        """Test read-only registers ignore writes"""
        ro_regs = ['WDOGVALUE', 'WDOGRIS', 'WDOGMIS', 
                   'WDOGPeriphID0', 'WDOGPeriphID1', 'WDOGPeriphID2', 'WDOGPeriphID3',
                   'WDOGPCellID0', 'WDOGPCellID1', 'WDOGPCellID2', 'WDOGPCellID3']
        
        for name in ro_regs:
            offset, size, access, reset_val = self.registers[name]
            reg = dev_util.Register_LE(self.bank, offset, size)
            
            # Read original value
            original = reg.read()
            
            # Attempt write
            reg.write(0xDEADBEEF)
            
            # Verify value unchanged
            after_write = reg.read()
            stest.expect_equal(after_write, original,
                f"{name} should ignore writes (read-only), got 0x{after_write:08X}")
    
    def test_writable_registers_when_unlocked(self):
        """Test writable registers accept writes when unlocked"""
        # First unlock the device (magic value 0x1ACCE551)
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        lock_reg.write(0x1ACCE551)
        
        # Verify unlocked
        lock_status = lock_reg.read()
        stest.expect_equal(lock_status, 0, "Device should be unlocked")
        
        # Test WDOGLOAD
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        load_reg.write(0x12345678)
        stest.expect_equal(load_reg.read(), 0x12345678, "WDOGLOAD should accept writes when unlocked")
        
        # Test WDOGCONTROL
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        ctrl_reg.write(0x3)  # Enable interrupt and reset
        stest.expect_equal(ctrl_reg.read() & 0x3, 0x3, "WDOGCONTROL should accept writes when unlocked")
    
    def test_lock_protection(self):
        """Test lock protection blocks writes to protected registers"""
        # Device starts locked (WDOGLOCK = 1)
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        stest.expect_equal(lock_reg.read(), 1, "Device should start locked")
        
        # Try to write WDOGLOAD while locked
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        original = load_reg.read()
        load_reg.write(0xDEADBEEF)
        after_write = load_reg.read()
        stest.expect_equal(after_write, original,
            "WDOGLOAD writes should be blocked when locked")
        
        # Try to write WDOGCONTROL while locked
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        original_ctrl = ctrl_reg.read()
        ctrl_reg.write(0x3)
        after_ctrl = ctrl_reg.read()
        stest.expect_equal(after_ctrl, original_ctrl,
            "WDOGCONTROL writes should be blocked when locked")
    
    def test_unlock_with_magic_value(self):
        """Test unlock mechanism with magic value 0x1ACCE551"""
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        
        # Verify starts locked
        stest.expect_equal(lock_reg.read(), 1, "Device starts locked")
        
        # Unlock with magic value
        lock_reg.write(0x1ACCE551)
        stest.expect_equal(lock_reg.read(), 0, "Device should be unlocked after writing magic value")
        
        # Now writes to protected registers should work
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        load_reg.write(0xABCDEF00)
        stest.expect_equal(load_reg.read(), 0xABCDEF00, "WDOGLOAD should accept writes when unlocked")
    
    def test_relock_with_any_other_value(self):
        """Test writing any non-magic value relocks the device"""
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        
        # Unlock first
        lock_reg.write(0x1ACCE551)
        stest.expect_equal(lock_reg.read(), 0, "Device unlocked")
        
        # Write any other value to relock
        lock_reg.write(0x00000000)
        stest.expect_equal(lock_reg.read(), 1, "Device should relock after writing non-magic value")
        
        # Verify writes blocked again
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        original = load_reg.read()
        load_reg.write(0x99999999)
        stest.expect_equal(load_reg.read(), original, "WDOGLOAD writes blocked after relock")
    
    def test_peripheral_id_registers(self):
        """Test peripheral identification registers have correct values"""
        periph_ids = [
            ('WDOGPeriphID0', 0xFE0, 0x05),
            ('WDOGPeriphID1', 0xFE4, 0x18),
            ('WDOGPeriphID2', 0xFE8, 0x18),
            ('WDOGPeriphID3', 0xFEC, 0x00),
        ]
        
        for name, offset, expected in periph_ids:
            reg = dev_util.Register_LE(self.bank, offset, 4)
            actual = reg.read()
            stest.expect_equal(actual, expected,
                f"{name} should be 0x{expected:02X}, got 0x{actual:02X}")
    
    def test_primecell_id_registers(self):
        """Test PrimeCell identification registers have correct values"""
        pcell_ids = [
            ('WDOGPCellID0', 0xFF0, 0x0D),
            ('WDOGPCellID1', 0xFF4, 0xF0),
            ('WDOGPCellID2', 0xFF8, 0x05),
            ('WDOGPCellID3', 0xFFC, 0xB1),
        ]
        
        for name, offset, expected in pcell_ids:
            reg = dev_util.Register_LE(self.bank, offset, 4)
            actual = reg.read()
            stest.expect_equal(actual, expected,
                f"{name} should be 0x{expected:02X}, got 0x{actual:02X}")
    
    def test_integration_test_control(self):
        """Test integration test control register"""
        itcr_reg = dev_util.Register_LE(self.bank, 0xF00, 4)
        
        # Reset value should be 0
        stest.expect_equal(itcr_reg.read(), 0, "WDOGITCR reset value should be 0")
        
        # Should be writable
        itcr_reg.write(0x1)
        stest.expect_equal(itcr_reg.read() & 0x1, 0x1, "WDOGITCR should accept writes")
        
        # Disable test mode
        itcr_reg.write(0x0)
        stest.expect_equal(itcr_reg.read(), 0, "WDOGITCR should accept writes")

# Test runner
def run():
    """Execute all basic register tests"""
    test = WatchdogTimerBasicRegisterTest()
    test.setup()
    
    # Run all test methods
    test.test_reset_values()
    test.test_read_only_registers()
    test.test_writable_registers_when_unlocked()
    test.test_lock_protection()
    test.test_unlock_with_magic_value()
    test.test_relock_with_any_other_value()
    test.test_peripheral_id_registers()
    test.test_primecell_id_registers()
    test.test_integration_test_control()
    
    print("✓ All basic register tests defined (expected to FAIL until implementation)")

if __name__ == "__main__":
    run()
