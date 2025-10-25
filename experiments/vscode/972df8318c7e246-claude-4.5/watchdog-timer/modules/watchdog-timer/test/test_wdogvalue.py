# © 2010 Intel Corporation
# Contract test: WDOGVALUE register read
# Tests contracts from contracts/register-access.md - WDOGVALUE section

import dev_util
import stest
import simics
import watchdog_timer_common

# Create device instance
dev = watchdog_timer_common.create_watchdog_timer('wdt_test_wdogvalue')

# Register accessors
WDOGLOAD = dev_util.Register_LE(dev.bank.regs, 0x000, size=4)
WDOGVALUE = dev_util.Register_LE(dev.bank.regs, 0x004, size=4)
WDOGLOCK = dev_util.Register_LE(dev.bank.regs, 0xC00, size=4)

# Test 1: Read returns countdown value
print("Test 1: WDOGVALUE returns countdown value")
WDOGLOCK.write(0x1ACCE551)  # Unlock
WDOGLOAD.write(1000)
initial = WDOGVALUE.read()
stest.expect_equal(initial, 1000, "WDOGVALUE should be 1000 after load")

# Advance simulation by 100 cycles
simics.SIM_continue(100)
current = WDOGVALUE.read()
stest.expect_true(current < 1000, "WDOGVALUE should have decremented")
stest.expect_true(current > 0, "WDOGVALUE should still be counting down")

# Test 2: Write is ignored (read-only)
print("Test 2: Write to WDOGVALUE is ignored")
before = WDOGVALUE.read()
WDOGVALUE.write(0xDEADBEEF)
after = WDOGVALUE.read()
stest.expect_equal(before, after, "WDOGVALUE should not change on write (read-only)")

print("✓ All WDOGVALUE tests passed")
