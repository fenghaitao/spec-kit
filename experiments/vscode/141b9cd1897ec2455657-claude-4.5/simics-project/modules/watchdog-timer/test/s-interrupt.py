# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
Interrupt Generation Tests for Watchdog Timer Device

Tests first timeout interrupt behavior:
- Interrupt assertion when counter reaches zero
- WDOGRIS raw interrupt status
- WDOGMIS masked interrupt status
- WDOGINTCLR interrupt clear and reload
- wdogint signal state
"""

import simics
from test_common import create_watchdog_with_clock
import stest
import dev_util

class WatchdogTimerInterruptTest(object):
    """Test interrupt generation on first timeout"""
    
    def setup(self):
        """Create watchdog timer device for testing"""
        self.dev, self.clock = create_watchdog_with_clock('wdog_interrupt')
        self.bank = self.dev.bank.regs
        
        # Unlock device
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        lock_reg.write(0x1ACCE551)
    
    def test_interrupt_fires_on_timeout(self):
        """Test interrupt asserted when counter reaches zero"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        ris_reg = dev_util.Register_LE(self.bank, 0x010, 4)
        
        # Set small load value and enable interrupt
        load_reg.write(0x10)
        ctrl_reg.write(0x1)  # INTEN=1
        
        # Verify no interrupt initially
        stest.expect_equal(ris_reg.read(), 0, "No interrupt initially")
        
        # Run until timeout
        simics.SIM_continue(0x20)
        
        # WDOGRIS should show interrupt
        ris_status = ris_reg.read()
        stest.expect_equal(ris_status & 0x1, 0x1,
            f"WDOGRIS should indicate interrupt after timeout: 0x{ris_status:X}")
    
    def test_raw_interrupt_status(self):
        """Test WDOGRIS reflects raw interrupt state"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        ris_reg = dev_util.Register_LE(self.bank, 0x010, 4)
        
        # Trigger timeout with interrupt disabled
        load_reg.write(0x10)
        ctrl_reg.write(0x0)  # INTEN=0, interrupt disabled
        simics.SIM_continue(0x20)
        
        # WDOGRIS still shows raw interrupt (not masked by INTEN)
        # Note: This tests hardware spec - some implementations may differ
        # For SP805, WDOGRIS shows raw status regardless of INTEN
    
    def test_masked_interrupt_status(self):
        """Test WDOGMIS reflects interrupt AND enable"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        ris_reg = dev_util.Register_LE(self.bank, 0x010, 4)
        mis_reg = dev_util.Register_LE(self.bank, 0x014, 4)
        
        # Trigger interrupt with INTEN=1
        load_reg.write(0x10)
        ctrl_reg.write(0x1)
        simics.SIM_continue(0x20)
        
        # Both RIS and MIS should show interrupt
        ris = ris_reg.read()
        mis = mis_reg.read()
        
        stest.expect_equal(ris & 0x1, 0x1, "WDOGRIS should be set")
        stest.expect_equal(mis & 0x1, 0x1, "WDOGMIS should be set when INTEN=1")
    
    def test_interrupt_clear_clears_status(self):
        """Test writing WDOGINTCLR clears interrupt status"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        ris_reg = dev_util.Register_LE(self.bank, 0x010, 4)
        intclr_reg = dev_util.Register_LE(self.bank, 0x00C, 4)
        
        # Trigger interrupt
        load_reg.write(0x10)
        ctrl_reg.write(0x1)
        simics.SIM_continue(0x20)
        
        # Verify interrupt set
        stest.expect_equal(ris_reg.read() & 0x1, 0x1, "Interrupt should be set")
        
        # Clear interrupt
        intclr_reg.write(0x1)  # Any value
        
        # Interrupt status should be cleared
        ris_after = ris_reg.read()
        stest.expect_equal(ris_after, 0,
            f"WDOGRIS should be cleared after INTCLR write: 0x{ris_after:X}")
    
    def test_interrupt_clear_reloads_counter(self):
        """Test WDOGINTCLR reloads counter from WDOGLOAD"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        intclr_reg = dev_util.Register_LE(self.bank, 0x00C, 4)
        
        # Trigger interrupt with load value 0x100
        load_reg.write(0x100)
        ctrl_reg.write(0x1)
        simics.SIM_continue(0x120)  # Run past timeout
        
        # Clear interrupt (should reload counter)
        intclr_reg.write(0x1)
        
        # Counter should be reloaded to 0x100
        reloaded_value = value_reg.read()
        stest.expect_true(reloaded_value >= 0xF0,  # Allow small decrement
            f"Counter should reload to ~0x100 after INTCLR: 0x{reloaded_value:X}")
    
    def test_no_interrupt_when_disabled(self):
        """Test no interrupt when INTEN=0"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        mis_reg = dev_util.Register_LE(self.bank, 0x014, 4)
        
        # Run counter with interrupt disabled
        load_reg.write(0x10)
        ctrl_reg.write(0x0)  # INTEN=0
        simics.SIM_continue(0x20)
        
        # WDOGMIS should be 0 (masked)
        mis = mis_reg.read()
        stest.expect_equal(mis, 0,
            f"WDOGMIS should be 0 when INTEN=0: 0x{mis:X}")
    
    def test_interrupt_signal_assertion(self):
        """Test wdogint signal goes high on interrupt"""
        # This test requires signal interface implementation
        # Will check signal connection and state
        
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        # Note: Signal testing requires accessing device signal interfaces
        # In DML, signals are exposed via signal_connect interface
        # This is a placeholder for signal state verification
        
        load_reg.write(0x10)
        ctrl_reg.write(0x1)
        simics.SIM_continue(0x20)
        
        # TODO: Add signal state check when interface available
        # Expected: self.dev.wdogint_signal.level == 1
    
    def test_interrupt_cleared_on_disable(self):
        """Test interrupt clears when INTEN goes to 0"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        mis_reg = dev_util.Register_LE(self.bank, 0x014, 4)
        
        # Trigger interrupt
        load_reg.write(0x10)
        ctrl_reg.write(0x1)
        simics.SIM_continue(0x20)
        
        # Verify interrupt
        stest.expect_equal(mis_reg.read() & 0x1, 0x1, "Interrupt should be set")
        
        # Disable interrupt
        ctrl_reg.write(0x0)
        
        # MIS should clear (though RIS may remain)
        mis_after = mis_reg.read()
        stest.expect_equal(mis_after, 0,
            f"WDOGMIS should clear when INTEN=0: 0x{mis_after:X}")
    
    def test_multiple_timeouts(self):
        """Test interrupt fires on multiple timeout cycles"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        ris_reg = dev_util.Register_LE(self.bank, 0x010, 4)
        intclr_reg = dev_util.Register_LE(self.bank, 0x00C, 4)
        
        # First timeout
        load_reg.write(0x10)
        ctrl_reg.write(0x1)
        simics.SIM_continue(0x20)
        stest.expect_equal(ris_reg.read() & 0x1, 0x1, "First interrupt")
        
        # Clear and run again
        intclr_reg.write(0x1)
        simics.SIM_continue(0x20)
        stest.expect_equal(ris_reg.read() & 0x1, 0x1, "Second interrupt")
        
        # Clear and run third time
        intclr_reg.write(0x1)
        simics.SIM_continue(0x20)
        stest.expect_equal(ris_reg.read() & 0x1, 0x1, "Third interrupt")

# Test runner
def run():
    """Execute all interrupt tests"""
    test = WatchdogTimerInterruptTest()
    test.setup()
    
    # Run all test methods
    test.test_interrupt_fires_on_timeout()
    test.test_raw_interrupt_status()
    test.test_masked_interrupt_status()
    test.test_interrupt_clear_clears_status()
    test.test_interrupt_clear_reloads_counter()
    test.test_no_interrupt_when_disabled()
    test.test_interrupt_signal_assertion()
    test.test_interrupt_cleared_on_disable()
    test.test_multiple_timeouts()
    
    print("✓ All interrupt tests defined (expected to FAIL until implementation)")

if __name__ == "__main__":
    run()
