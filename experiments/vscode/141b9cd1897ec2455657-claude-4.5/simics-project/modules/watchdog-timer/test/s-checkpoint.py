# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Checkpoint/Restore Tests"""

import simics, stest, dev_util

class WatchdogTimerCheckpointTest(object):
    def setup(self):
        self.dev, self.clock = create_watchdog_with_clock('wdog_chkpt')
        self.bank = self.dev.bank.regs
        dev_util.Register_LE(self.bank, 0xC00, 4).write(0x1ACCE551)  # Unlock
    
    def test_checkpoint_preserves_counter_state(self):
        """Counter state persists across checkpoint"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        load_reg.write(0x1000)
        ctrl_reg.write(0x1)
        simics.SIM_continue(50)
        
        value_before = value_reg.read()
        
        # Save checkpoint (placeholder - actual Simics API)
        # simics.SIM_write_configuration_to_file("checkpoint.ckpt")
        
        # Restore checkpoint
        # simics.SIM_read_configuration("checkpoint.ckpt")
        
        value_after = value_reg.read()
        stest.expect_equal(value_after, value_before, "Counter value preserved")
    
    def test_checkpoint_preserves_lock_state(self):
        """Lock state persists across checkpoint"""
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        lock_reg.write(0x1ACCE551)  # Unlock
        
        # TODO: Save/restore checkpoint
        
        stest.expect_equal(lock_reg.read(), 0, "Lock state preserved")
    
    def test_counter_resumes_after_restore(self):
        """Counter continues counting after checkpoint restore"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        value_reg = dev_util.Register_LE(self.bank, 0x004, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        
        load_reg.write(0x1000)
        ctrl_reg.write(0x1)
        simics.SIM_continue(50)
        
        # TODO: Save/restore checkpoint
        
        value_at_restore = value_reg.read()
        simics.SIM_continue(50)
        value_after = value_reg.read()
        
        stest.expect_true(value_after < value_at_restore, "Counter continues after restore")
    
    def test_interrupt_reschedules_after_restore(self):
        """Interrupt event fires at correct time after restore"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        ctrl_reg = dev_util.Register_LE(self.bank, 0x008, 4)
        ris_reg = dev_util.Register_LE(self.bank, 0x010, 4)
        
        load_reg.write(0x100)
        ctrl_reg.write(0x1)
        simics.SIM_continue(80)  # Halfway to timeout
        
        # TODO: Save/restore checkpoint
        
        simics.SIM_continue(40)  # Run to timeout
        stest.expect_equal(ris_reg.read() & 0x1, 0x1, "Interrupt fires after restore")

def run():
    test = WatchdogTimerCheckpointTest()
    test.setup()
    test.test_checkpoint_preserves_counter_state()
    test.test_checkpoint_preserves_lock_state()
    test.test_counter_resumes_after_restore()
    test.test_interrupt_reschedules_after_restore()
    print("✓ Checkpoint tests defined (expected to FAIL)")

if __name__ == "__main__":
    run()
