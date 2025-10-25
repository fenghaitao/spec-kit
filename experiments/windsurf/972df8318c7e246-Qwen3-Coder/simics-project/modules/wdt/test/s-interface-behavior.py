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

# Test interrupt signal generation
def test_interrupt_generation():
    # Configure watchdog timer with small timeout
    load_register = dev_util.Register_LE(dev.bank.regs, 0x00, size=4)  # WDOGLOAD
    control_register = dev_util.Register_LE(dev.bank.regs, 0x08, size=4)  # WDOGCONTROL
    
    # Set timeout value
    load_register.write(0x0000000A)  # Small value for testing
    
    # Enable interrupt generation
    control_register.write(0x00000001)  # Set INTEN bit
    
    # TODO: Implement interrupt signal checking
    # This would require connecting to an interrupt controller
    # and checking that the interrupt signal is asserted when timeout occurs
    print("Interrupt generation test - implementation pending")

test_interrupt_generation()

# Test reset signal generation
def test_reset_generation():
    # Configure watchdog timer with small timeout
    load_register = dev_util.Register_LE(dev.bank.regs, 0x00, size=4)  # WDOGLOAD
    control_register = dev_util.Register_LE(dev.bank.regs, 0x08, size=4)  # WDOGCONTROL
    
    # Set timeout value
    load_register.write(0x00000005)  # Small value for testing
    
    # Enable both interrupt and reset generation
    control_register.write(0x00000003)  # Set both INTEN and RESEN bits
    
    # TODO: Implement reset signal checking
    # This would require checking that the reset signal is asserted
    # when timeout occurs with interrupt already pending
    print("Reset generation test - implementation pending")

test_reset_generation()

# Test clock divider functionality
def test_clock_divider():
    control_register = dev_util.Register_LE(dev.bank.regs, 0x08, size=4)  # WDOGCONTROL
    
    # Test different step values
    step_values = [
        (0b000, "÷1"),
        (0b001, "÷2"),
        (0b010, "÷4"),
        (0b011, "÷8"),
        (0b100, "÷16")
    ]
    
    for step_value, description in step_values:
        # Set step value in bits [4:2]
        control_value = (step_value << 2)
        control_register.write(control_value)
        read_value = control_register.read()
        expected_value = control_value
        stest.expect_equal(read_value, expected_value, 
                          f"WDOGCONTROL should have step value {description} (0b{step_value:03b})")

    print("Clock divider tests completed")
test_clock_divider()

# Test integration test mode
def test_integration_test_mode():
    # Test enabling integration test mode
    itcr_register = dev_util.Register_LE(dev.bank.regs, 0xF00, size=4)  # WDOGITCR
    itop_register = dev_util.Register_LE(dev.bank.regs, 0xF04, size=4)  # WDOGITOP
    
    # Enable integration test mode
    itcr_register.write(0x00000001)
    read_value = itcr_register.read()
    stest.expect_equal(read_value, 0x00000001, "WDOGITCR should enable test mode")
    
    # Test setting output values
    itop_register.write(0x00000003)  # Set both interrupt and reset test values
    
    # Disable integration test mode
    itcr_register.write(0x00000000)
    read_value = itcr_register.read()
    stest.expect_equal(read_value, 0x00000000, "WDOGITCR should disable test mode")

    print("Integration test mode tests completed")
test_integration_test_mode()

print("Interface behavior tests completed")
