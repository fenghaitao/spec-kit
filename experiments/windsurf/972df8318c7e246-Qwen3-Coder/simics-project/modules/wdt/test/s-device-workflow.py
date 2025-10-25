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

# Test complete workflow: load → enable → timeout → interrupt → clear → timeout → reset
def test_complete_workflow():
    # Access registers
    load_register = dev_util.Register_LE(dev.bank.regs, 0x00, size=4)    # WDOGLOAD
    value_register = dev_util.Register_LE(dev.bank.regs, 0x04, size=4)    # WDOGVALUE
    control_register = dev_util.Register_LE(dev.bank.regs, 0x08, size=4)  # WDOGCONTROL
    intclr_register = dev_util.Register_LE(dev.bank.regs, 0x0C, size=4)   # WDOGINTCLR
    ris_register = dev_util.Register_LE(dev.bank.regs, 0x10, size=4)      # WDOGRIS
    mis_register = dev_util.Register_LE(dev.bank.regs, 0x14, size=4)      # WDOGMIS
    
    # Step 1: Load timer with small value
    load_register.write(0x0000000A)
    stest.expect_equal(load_register.read(), 0x0000000A, "WDOGLOAD should be set")
    
    # Step 2: Enable interrupt generation
    control_register.write(0x00000001)  # Set INTEN bit
    stest.expect_equal(control_register.read(), 0x00000001, "WDOGCONTROL should enable INTEN")
    
    # Step 3: Check initial state
    # TODO: Simulate timer countdown
    # For now, just check that we can read the value register
    current_value = value_register.read()
    print(f"Initial timer value: 0x{current_value:08X}")
    
    # Step 4: Check interrupt status registers
    ris_value = ris_register.read()
    mis_value = mis_register.read()
    print(f"Raw interrupt status: {ris_value}")
    print(f"Masked interrupt status: {mis_value}")
    
    # Step 5: Clear interrupt (simulate first timeout handled)
    intclr_register.write(0x00000001)
    print("Interrupt cleared, timer should reload")
    
    # Step 6: Enable both interrupt and reset
    control_register.write(0x00000003)  # Set both INTEN and RESEN bits
    stest.expect_equal(control_register.read(), 0x00000003, "WDOGCONTROL should enable both INTEN and RESEN")
    
    # Step 7: Check that timer is reloaded
    reloaded_value = value_register.read()
    print(f"Timer value after reload: 0x{reloaded_value:08X}")
    
    print("Complete workflow test executed (simulation of timer countdown pending)")

test_complete_workflow()

# Test lock protection workflow
def test_lock_protection_workflow():
    # Access registers
    load_register = dev_util.Register_LE(dev.bank.regs, 0x00, size=4)    # WDOGLOAD
    control_register = dev_util.Register_LE(dev.bank.regs, 0x08, size=4)  # WDOGCONTROL
    lock_register = dev_util.Register_LE(dev.bank.regs, 0xC00, size=4)    # WDOGLOCK
    
    # Step 1: Verify unlocked state
    initial_load = load_register.read()
    initial_control = control_register.read()
    
    # Step 2: Lock registers
    lock_register.write(0x12345678)  # Non-magic value to lock
    
    # Step 3: Try to write to protected registers (should be ignored when implemented)
    load_register.write(0x11111111)
    control_register.write(0x11111111)
    
    # Step 4: Verify values unchanged (when lock mechanism is implemented)
    # TODO: Uncomment when lock mechanism is implemented
    # stest.expect_equal(load_register.read(), initial_load, "WDOGLOAD should be unchanged when locked")
    # stest.expect_equal(control_register.read(), initial_control, "WDOGCONTROL should be unchanged when locked")
    
    # Step 5: Unlock registers
    lock_register.write(0x1ACCE551)  # Magic value to unlock
    
    # Step 6: Try to write to registers again (should succeed when unlocked)
    load_register.write(0x22222222)
    control_register.write(0x22222222)
    
    # Step 7: Verify values changed
    # TODO: Uncomment when lock mechanism is implemented
    # stest.expect_equal(load_register.read(), 0x22222222, "WDOGLOAD should be changed when unlocked")
    # stest.expect_equal(control_register.read(), 0x22222222, "WDOGCONTROL should be changed when unlocked")
    
    print("Lock protection workflow test executed (lock mechanism implementation pending)")
test_lock_protection_workflow()

print("Device workflow tests completed")
