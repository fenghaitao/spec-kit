# © 2010 Intel Corporation
# Contract test: WDOGLOAD register access
# Tests contracts from contracts/register-access.md - WDOGLOAD section

import dev_util
import stest
import watchdog_timer_common

# Create device instance
dev = watchdog_timer_common.create_watchdog_timer('wdt_test_wdogload')

# Register accessors
WDOGLOAD = dev_util.Register_LE(dev.bank.regs, 0x000, size=4)
WDOGVALUE = dev_util.Register_LE(dev.bank.regs, 0x004, size=4)
WDOGLOCK = dev_util.Register_LE(dev.bank.regs, 0xC00, size=4)

# Test 1: Write to WDOGLOAD when unlocked
print("Test 1: Write WDOGLOAD when unlocked")
WDOGLOCK.write(0x1ACCE551)  # Unlock
WDOGLOAD.write(0x12345678)
value = WDOGLOAD.read()
stest.expect_equal(value, 0x12345678, "WDOGLOAD should return last written value")
stest.expect_equal(WDOGVALUE.read(), 0x12345678, "WDOGVALUE should match WDOGLOAD immediately after write")

# Test 2: Write ignored when locked
print("Test 2: Write WDOGLOAD when locked")
WDOGLOCK.write(0x0)  # Lock
WDOGLOAD.write(0xAAAAAAAA)
value = WDOGLOAD.read()
stest.expect_equal(value, 0x12345678, "WDOGLOAD write should be ignored when locked")

# Test 3: Read returns last written value
print("Test 3: Read returns last written value")
WDOGLOCK.write(0x1ACCE551)  # Unlock
WDOGLOAD.write(0xFFFFFFFF)
value = WDOGLOAD.read()
stest.expect_equal(value, 0xFFFFFFFF, "WDOGLOAD read should return 0xFFFFFFFF")

print("✓ All WDOGLOAD tests passed")
