# © 2010 Intel Corporation
# Contract test: WDOGCONTROL register
# Tests contracts from contracts/register-access.md - WDOGCONTROL section

import dev_util
import stest
import watchdog_timer_common

dev = watchdog_timer_common.create_watchdog_timer('wdt_test_wdogcontrol')

WDOGCONTROL = dev_util.Register_LE(dev.bank.regs, 0x008, size=4)
WDOGLOCK = dev_util.Register_LE(dev.bank.regs, 0xC00, size=4)

# Test 1: Write sets INTEN/RESEN bits when unlocked
print("Test 1: Write WDOGCONTROL when unlocked")
WDOGLOCK.write(0x1ACCE551)  # Unlock
WDOGCONTROL.write(0x3)  # INTEN=1, RESEN=1
value = WDOGCONTROL.read()
stest.expect_equal(value & 0x3, 0x3, "INTEN and RESEN should be set")

# Test 2: Write ignored when locked
print("Test 2: Write WDOGCONTROL when locked")
WDOGLOCK.write(0x0)  # Lock
WDOGCONTROL.write(0x0)
value = WDOGCONTROL.read()
stest.expect_equal(value & 0x3, 0x3, "Write should be ignored when locked")

# Test 3: Bits [31:2] read as zero
print("Test 3: Reserved bits read as zero")
WDOGLOCK.write(0x1ACCE551)  # Unlock
WDOGCONTROL.write(0xFFFFFFFF)
value = WDOGCONTROL.read()
stest.expect_equal(value & 0xFFFFFFFC, 0, "Bits [31:2] should read as zero")

print("✓ All WDOGCONTROL tests passed")
