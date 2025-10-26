# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Lock Protection Tests"""

import simics, stest, dev_util

class WatchdogTimerLockTest(object):
    def setup(self):
        self.dev = simics.SIM_create_object('watchdog_timer', 'wdog_lock', [])
        self.bank = self.dev.bank.regs
    
    def test_starts_locked(self):
        """Device starts in locked state"""
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        stest.expect_equal(lock_reg.read(), 1, "Device starts locked")
    
    def test_protected_registers_blocked_when_locked(self):
        """Protected register writes blocked when locked"""
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        original = load_reg.read()
        load_reg.write(0xDEADBEEF)
        stest.expect_equal(load_reg.read(), original, "WDOGLOAD blocked when locked")
    
    def test_unlock_with_magic_value(self):
        """Magic value 0x1ACCE551 unlocks device"""
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        lock_reg.write(0x1ACCE551)
        stest.expect_equal(lock_reg.read(), 0, "Device unlocked")
    
    def test_writes_accepted_when_unlocked(self):
        """Protected registers writable when unlocked"""
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        lock_reg.write(0x1ACCE551)
        
        load_reg = dev_util.Register_LE(self.bank, 0x000, 4)
        load_reg.write(0x12345678)
        stest.expect_equal(load_reg.read(), 0x12345678, "WDOGLOAD writable when unlocked")
    
    def test_relock_with_any_other_value(self):
        """Any non-magic value relocks device"""
        lock_reg = dev_util.Register_LE(self.bank, 0xC00, 4)
        lock_reg.write(0x1ACCE551)  # Unlock
        lock_reg.write(0x00000000)  # Relock
        stest.expect_equal(lock_reg.read(), 1, "Device relocked")

def run():
    test = WatchdogTimerLockTest()
    test.setup()
    test.test_starts_locked()
    test.test_protected_registers_blocked_when_locked()
    test.test_unlock_with_magic_value()
    test.test_writes_accepted_when_unlocked()
    test.test_relock_with_any_other_value()
    print("✓ Lock tests defined (expected to FAIL)")

if __name__ == "__main__":
    run()
