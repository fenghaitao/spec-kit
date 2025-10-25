# © 2010 Intel Corporation
# Integration test: Basic watchdog operation
# Tests scenario from quickstart.md - Pattern 1: Basic Watchdog Operation

import dev_util
import stest
import simics
import watchdog_timer_common

dev = watchdog_timer_common.create_watchdog_timer('wdt_test_basic')

# Register accessors
WDOGLOAD = dev_util.Register_LE(dev.bank.regs, 0x000, size=4)
WDOGVALUE = dev_util.Register_LE(dev.bank.regs, 0x004, size=4)
WDOGCONTROL = dev_util.Register_LE(dev.bank.regs, 0x008, size=4)
WDOGINTCLR = dev_util.Register_LE(dev.bank.regs, 0x00C, size=4)
WDOGRIS = dev_util.Register_LE(dev.bank.regs, 0x010, size=4)
WDOGMIS = dev_util.Register_LE(dev.bank.regs, 0x014, size=4)
WDOGLOCK = dev_util.Register_LE(dev.bank.regs, 0xC00, size=4)

print("=== Basic Watchdog Operation Test ===")

# Step 1: Configure watchdog
print("Step 1: Configure watchdog")
WDOGLOCK.write(0x1ACCE551)  # Unlock
WDOGCONTROL.write(0x3)  # Enable interrupt and reset
WDOGLOAD.write(100)  # Load counter with 100 cycles

# Step 2: Verify counter counts down
print("Step 2: Verify counter counts down")
initial = WDOGVALUE.read()
stest.expect_equal(initial, 100, "Counter should be 100")
simics.SIM_continue(50)
after_50 = WDOGVALUE.read()
stest.expect_true(after_50 < 100 and after_50 > 0, "Counter should have decremented")

# Step 3: Wait for first timeout (interrupt)
print("Step 3: Wait for first timeout")
simics.SIM_continue(100)  # Run past timeout
ris = WDOGRIS.read()
mis = WDOGMIS.read()
stest.expect_equal(ris & 0x1, 0x1, "Raw interrupt status should be set")
stest.expect_equal(mis & 0x1, 0x1, "Masked interrupt status should be set (INTEN=1)")

# Step 4: Clear interrupt
print("Step 4: Clear interrupt")
WDOGINTCLR.write(0)  # Any value clears interrupt
ris_after = WDOGRIS.read()
mis_after = WDOGMIS.read()
stest.expect_equal(ris_after & 0x1, 0, "Interrupt should be cleared")
stest.expect_equal(mis_after & 0x1, 0, "Masked interrupt should be cleared")

print("✓ Basic watchdog operation test passed")
