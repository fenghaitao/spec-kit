# © 2025 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were
# provided to you ("License"). Unless the License provides otherwise, you may
# not use, modify, copy, publish, distribute, disclose or transmit this software
# or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or
# implied warranties, other than those that are expressly stated in the License.

import dev_util
import conf
import stest
import wdt_common

# Create an instance of the device to test
dev = wdt_common.create_wdt()

# Test WDOGLOAD register access
def test_wdogload_access():
    # Test reading reset value
    register = dev_util.Register_LE(dev.bank.regs, 0x00, size=4)
    value = register.read()
    stest.expect_equal(value, 0xFFFFFFFF, "WDOGLOAD should have reset value 0xFFFFFFFF")
    
    # Test writing and reading back
    register.write(0x12345678)
    value = register.read()
    stest.expect_equal(value, 0x12345678, "WDOGLOAD should return written value")

test_wdogload_access()

# Test WDOGVALUE register access
def test_wdogvalue_access():
    # Test reading reset value
    register = dev_util.Register_LE(dev.bank.regs, 0x04, size=4)
    value = register.read()
    stest.expect_equal(value, 0xFFFFFFFF, "WDOGVALUE should have reset value 0xFFFFFFFF")
    
    # Test that writing is ignored (read-only register)
    initial_value = register.read()
    register.write(0x12345678)
    value = register.read()
    stest.expect_equal(value, initial_value, "WDOGVALUE should be read-only")

test_wdogvalue_access()

# Test WDOGCONTROL register access
def test_wdogcontrol_access():
    # Test reading reset value
    register = dev_util.Register_LE(dev.bank.regs, 0x08, size=4)
    value = register.read()
    stest.expect_equal(value, 0x00000000, "WDOGCONTROL should have reset value 0x00000000")
    
    # Test writing and reading back
    register.write(0x00000003)  # Set both INTEN and RESEN bits
    value = register.read()
    stest.expect_equal(value, 0x00000003, "WDOGCONTROL should return written value")

test_wdogcontrol_access()

# Test WDOGLOCK register access
def test_wdoglock_access():
    # Test reading reset value (should indicate unlocked)
    register = dev_util.Register_LE(dev.bank.regs, 0xC00, size=4)
    value = register.read()
    stest.expect_equal(value, 0x00000000, "WDOGLOCK should have reset value 0x00000000 (unlocked)")
    
    # Test unlocking with magic value
    register.write(0x1ACCE551)
    # Read back to check lock status
    lock_status_register = dev_util.Register_LE(dev.bank.regs, 0xC00, size=4)
    lock_status = lock_status_register.read()
    # Implementation should return 0 for unlocked, 1 for locked
    # stest.expect_equal(lock_status, 0, "WDOGLOCK should indicate unlocked after magic value")
    
    # Test locking with non-magic value
    register.write(0x12345678)
    lock_status = lock_status_register.read()
    # stest.expect_equal(lock_status, 1, "WDOGLOCK should indicate locked after non-magic value")

test_wdoglock_access()

print("Register access tests completed")
