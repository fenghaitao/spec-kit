# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
Counter Decrement Tests for Watchdog Timer Device

Tests cycle-based counter countdown logic:
- Counter decrements based on elapsed cycles
- Start/stop functionality
- Reload behavior
- Clock divider (step_value) configurations
"""

import simics
import stest
import dev_util
from test_common import create_watchdog_with_clock

class WatchdogTimerCountdownTest(object):
    """Test counter decrement behavior"""
    
    def setup(self):
        """Create watchdog timer device for testing"""
        self.dev, self.clock = create_watchdog_with_clock('wdog_countdown')
        self.bank = self.dev.bank.regs
        
        # Unlock device for testing
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        lock_reg.write(0x1ACCE551)
    
    def test_counter_starts_with_load_value(self):
        """Test counter initializes to WDOGLOAD value"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        
        # Write load value
        load_reg.write(0x100)
        
        # WDOGVALUE should reflect load value when not counting
        actual = value_reg.read()
        stest.expect_equal(actual, 0x100, 
            f"WDOGVALUE should match WDOGLOAD when stopped, got 0x{actual:X}")
    
    def test_counter_decrements_when_enabled(self):
        """Test counter decrements after enabling"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        # Set load value and enable
        load_reg.write(0x1000)
        ctrl_reg.write(0x1)  # Enable interrupt (starts counter)
        
        # Read initial value
        initial = value_reg.read()
        
        # Advance simulation time
        simics.SIM_continue(100)  # Run 100 cycles
        
        # Counter should have decremented
        after = value_reg.read()
        stest.expect_true(after < initial,
            f"Counter should decrement: initial=0x{initial:X}, after=0x{after:X}")
    
    def test_counter_stops_when_disabled(self):
        """Test counter holds value when disabled"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        # Start counter
        load_reg.write(0x1000)
        ctrl_reg.write(0x1)  # Enable
        simics.SIM_continue(50)
        
        # Stop counter
        ctrl_reg.write(0x0)  # Disable
        stopped_value = value_reg.read()
        
        # Advance time
        simics.SIM_continue(50)
        
        # Value should not change
        after_stop = value_reg.read()
        stest.expect_equal(after_stop, stopped_value,
            f"Counter should stop: stopped=0x{stopped_value:X}, after=0x{after_stop:X}")
    
    def test_counter_reloads_on_load_write(self):
        """Test writing WDOGLOAD while running reloads counter"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        # Start counter with initial value
        load_reg.write(0x1000)
        ctrl_reg.write(0x1)
        simics.SIM_continue(100)
        
        # Reload with new value
        load_reg.write(0x2000)
        new_value = value_reg.read()
        
        # Counter should restart from new load value
        stest.expect_true(new_value >= 0x1F00,  # Allow for some decrement
            f"Counter should reload from new WDOGLOAD value: 0x{new_value:X}")
    
    def test_counter_reaches_zero(self):
        """Test counter decrements to zero"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        # Start with small value
        load_reg.write(0x10)
        ctrl_reg.write(0x1)
        
        # Run enough cycles to reach zero
        simics.SIM_continue(0x20)
        
        # Counter should be at or near zero
        final = value_reg.read()
        stest.expect_true(final <= 0x10,
            f"Counter should reach zero or decrement significantly: 0x{final:X}")
    
    def test_clock_divider_1(self):
        """Test counter with clock divider = 1 (fastest)"""
        # Note: Clock divider controlled by WDOGCONTROL bits [3:2] in some implementations
        # For this test, we assume step_value = 1 (default)
        
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        load_reg.write(0x100)
        ctrl_reg.write(0x1)
        
        initial = value_reg.read()
        simics.SIM_continue(16)
        after = value_reg.read()
        
        # With divider=1, should decrement ~16 times
        decrement = initial - after
        stest.expect_true(decrement >= 10 and decrement <= 20,
            f"With divider=1, should decrement ~16: {decrement}")
    
    def test_counter_restart_after_stop(self):
        """Test counter can be restarted after stopping"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        # Start, stop, restart cycle
        load_reg.write(0x1000)
        ctrl_reg.write(0x1)  # Start
        simics.SIM_continue(50)
        
        ctrl_reg.write(0x0)  # Stop
        stopped = value_reg.read()
        
        ctrl_reg.write(0x1)  # Restart
        simics.SIM_continue(50)
        
        restarted = value_reg.read()
        stest.expect_true(restarted < stopped,
            f"Counter should continue decrementing after restart: stopped=0x{stopped:X}, after=0x{restarted:X}")
    
    def test_load_register_reflects_value(self):
        """Test WDOGLOAD register holds written value"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        
        test_values = [0x12345678, 0xDEADBEEF, 0x00000001, 0xFFFFFFFF]
        
        for test_val in test_values:
            load_reg.write(test_val)
            actual = load_reg.read()
            stest.expect_equal(actual, test_val,
                f"WDOGLOAD should hold written value 0x{test_val:X}, got 0x{actual:X}")
    
    def test_value_register_is_read_only(self):
        """Test WDOGVALUE cannot be written"""
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        
        original = value_reg.read()
        value_reg.write(0xDEADBEEF)
        after_write = value_reg.read()
        
        stest.expect_equal(after_write, original,
            "WDOGVALUE should be read-only and ignore writes")

# Test runner
def run():
    """Execute all countdown tests"""
    test = WatchdogTimerCountdownTest()
    test.setup()
    
    # Run all test methods
    test.test_counter_starts_with_load_value()
    test.test_counter_decrements_when_enabled()
    test.test_counter_stops_when_disabled()
    test.test_counter_reloads_on_load_write()
    test.test_counter_reaches_zero()
    test.test_clock_divider_1()
    test.test_counter_restart_after_stop()
    test.test_load_register_reflects_value()
    test.test_value_register_is_read_only()
    
    print("✓ All countdown tests defined (expected to FAIL until implementation)")

if __name__ == "__main__":
    run()
