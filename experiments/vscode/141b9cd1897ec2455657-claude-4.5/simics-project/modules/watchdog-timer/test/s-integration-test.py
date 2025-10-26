# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Integration Test Mode Tests"""

import simics, stest, dev_util

class WatchdogTimerIntegrationTestTest(object):
    def setup(self):
        self.dev, self.clock = create_watchdog_with_clock('wdog_itest')
        self.bank = self.dev.bank.regs
        dev_util.Register_LE(self.bank, 0xC00, 4).write(0x1ACCE551)  # Unlock
    
    def test_enable_integration_test_mode(self):
        """Enable test mode via WDOGITCR"""
        itcr_reg = dev_util.Register_LE(self.bank, 0xF00, 4)
        itcr_reg.write(0x1)
        stest.expect_equal(itcr_reg.read() & 0x1, 0x1, "Test mode enabled")
    
    def test_direct_interrupt_control(self):
        """WDOGITOP directly controls wdogint in test mode"""
        itcr_reg = dev_util.Register_LE(self.bank, 0xF00, 4)
        itop_reg = dev_util.Register_LE(self.bank, 0xF04, 4)
        
        itcr_reg.write(0x1)  # Enable test mode
        itop_reg.write(0x1)  # Assert wdogint
        
        # TODO: Verify wdogint signal high
    
    def test_direct_reset_control(self):
        """WDOGITOP directly controls wdogres in test mode"""
        itcr_reg = dev_util.Register_LE(self.bank, 0xF00, 4)
        itop_reg = dev_util.Register_LE(self.bank, 0xF04, 4)
        
        itcr_reg.write(0x1)
        itop_reg.write(0x2)  # Assert wdogres
        
        # TODO: Verify wdogres signal high
    
    def test_normal_operation_bypassed(self):
        """Normal timeout logic bypassed in test mode"""
        itcr_reg = dev_util.Register_LE(self.bank, 0xF00, 4)
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        ris_reg = dev_util.Register_LE(self.bank, 0x010, 4)
        
        itcr_reg.write(0x1)  # Enable test mode
        load_reg.write(0x10)
        ctrl_reg.write(0x1)
        simics.SIM_continue(0x20)
        
        # Normal interrupt should NOT fire
        stest.expect_equal(ris_reg.read(), 0, "Normal interrupt bypassed in test mode")
    
    def test_disable_test_mode(self):
        """Disabling test mode restores normal operation"""
        itcr_reg = dev_util.Register_LE(self.bank, 0xF00, 4)
        itcr_reg.write(0x1)  # Enable
        itcr_reg.write(0x0)  # Disable
        stest.expect_equal(itcr_reg.read(), 0, "Test mode disabled")

def run():
    test = WatchdogTimerIntegrationTestTest()
    test.setup()
    test.test_enable_integration_test_mode()
    test.test_direct_interrupt_control()
    test.test_direct_reset_control()
    test.test_normal_operation_bypassed()
    test.test_disable_test_mode()
    print("✓ Integration test mode tests defined (expected to FAIL)")

if __name__ == "__main__":
    run()
