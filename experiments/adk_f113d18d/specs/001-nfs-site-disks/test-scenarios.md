# Test Scenarios: Simics Watchdog Timer Device

## Overview

This document defines test scenarios for the Simics Watchdog Timer device. Each scenario is described using generic Simics CLI commands and concepts, focusing on device functionality, register access behaviors, and interface interactions. These scenarios will guide the development of automated tests to validate device implementation against specification requirements.

## Prerequisites

- Device is properly instantiated and connected to system
- Device registers are accessible at expected memory addresses
- Clock and reset signals are properly connected
- Interrupt and reset output signals are properly connected for monitoring

## Scenario S001: Basic Timer Operation Test

### Description
Verify basic timer countdown functionality using WDOGLOAD and WDOGVALUE registers.

### Setup
1. Write a small value (e.g., 0x10) to [DEVICE_NAME].WDOGLOAD register
2. Configure timer with INTEN=0 to prevent interrupt
3. Configure clock divider to a known value (e.g., step_value=000 for ÷1)
4. Enable timer by setting INTEN=1 in WDOGCONTROL

### Actions
1. Read [DEVICE_NAME].WDOGVALUE register multiple times with delays between reads
2. Observe counter decrementing from initial value in WDOGLOAD
3. Confirm counter stops at 0 when it reaches zero
4. Write new value to WDOGLOAD and verify counter reloads properly

### Expected Results
- WDOGVALUE reads return values that decrement over time
- Counter stops at 0 and remains at 0
- No interrupts are generated when INTEN=0
- Counter reloads properly from WDOGLOAD value

## Scenario S002: Interrupt Generation Test

### Description
Verify interrupt generation when timer reaches zero with INTEN=1.

### Setup
1. Write value 0x5 to [DEVICE_NAME].WDOGLOAD register
2. Set INTEN=1 in [DEVICE_NAME].WDOGCONTROL register
3. Configure clock divider appropriately (e.g., step_value=000)
4. Connect interrupt signal to monitoring mechanism

### Actions
1. Monitor wdogint signal for assertion
2. Wait for timer to count down to zero
3. Verify interrupt signal (wdogint) is asserted
4. Verify WDOGRIS[0] = 1 and WDOGMIS[0] = 1
5. Read WDOGVALUE to confirm it remains at zero

### Expected Results
- wdogint signal is asserted when counter reaches zero
- WDOGRIS register bit 0 shows interrupt status = 1
- WDOGMIS register bit 0 shows masked interrupt status = 1
- Counter remains at zero after reaching zero

## Scenario S003: Interrupt Clear Test

### Description
Verify interrupt clearing mechanism using WDOGINTCLR register.

### Setup
1. Configure timer to generate an interrupt
2. Allow timer to count to zero and generate interrupt
3. Verify interrupt is pending (WDOGRIS[0] = 1, WDOGMIS[0] = 1, wdogint asserted)

### Actions
1. Write any value to [DEVICE_NAME].WDOGINTCLR register
2. Monitor wdogint signal for deassertion
3. Read WDOGRIS and WDOGMIS registers
4. Read WDOGVALUE to confirm counter reloaded

### Expected Results
- wdogint signal is deasserted after writing to WDOGINTCLR
- WDOGRIS[0] and WDOGMIS[0] return to 0 after interrupt clear
- Counter reloads from WDOGLOAD value
- Timer restarts counting down from reloaded value

## Scenario S004: Reset Generation Test

### Description
Verify system reset generation when timer reaches zero again with RESEN=1 while interrupt is pending.

### Setup
1. Write small value to [DEVICE_NAME].WDOGLOAD register
2. Set both INTEN=1 and RESEN=1 in [DEVICE_NAME].WDOGCONTROL register
3. Allow timer to count to zero and generate interrupt
4. Do not clear the interrupt (do not write to WDOGINTCLR)

### Actions
1. Wait for timer to reach zero again after interrupt is generated
2. Monitor wdogres signal for assertion
3. Verify both wdogint and wdogres are asserted
4. Attempt to clear interrupt via WDOGINTCLR

### Expected Results
- wdogres signal is asserted when counter reaches zero again
- wdogres remains asserted until system reset occurs
- Clearing interrupt does not clear reset signal
- Reset signal is only cleared by system reset

## Scenario S005: Lock Protection Test

### Description
Verify lock protection mechanism prevents unauthorized register writes.

### Setup
1. Verify device is in unlocked state initially
2. Prepare values to write to protected registers

### Actions - Unlock Sequence
1. Write unlock value 0x1ACCE551 to [DEVICE_NAME].WDOGLOCK register
2. Verify WDOGLOCK read returns 0x0 (unlocked)
3. Write to WDOGLOAD register (should succeed)
4. Verify WDOGLOAD contains the written value

### Actions - Lock Sequence
1. Write any value other than unlock value to [DEVICE_NAME].WDOGLOCK register
2. Verify WDOGLOCK read returns 0x1 (locked)
3. Attempt to write to WDOGLOAD register
4. Read back WDOGLOAD register to check if value changed

### Expected Results
- Writing 0x1ACCE551 to WDOGLOCK unlocks write access to other registers
- Writing other values to WDOGLOCK locks write access to other registers
- When locked, writes to other registers are ignored
- WDOGLOCK register itself remains writable when locked

## Scenario S006: Clock Divider Test

### Description
Verify different clock divider settings affect timer decrement rate.

### Setup
1. Write same initial value to WDOGLOAD register
2. Set INTEN=0 to prevent interrupts during measurement
3. Configure timer with step_value=000 (÷1 divider)

### Actions - Divider 000
1. Start timer with divider ÷1
2. Measure time to reach zero from same starting value
3. Record time to completion

### Actions - Divider 001
1. Reset timer with same starting value
2. Configure with step_value=001 (÷2 divider)
3. Measure time to reach zero
4. Compare with previous measurement (should be 2x longer)

### Actions - Other Dividers
1. Test other divider values (010=÷4, 011=÷8, 100=÷16)
2. Verify timing is proportional to divider value

### Expected Results
- Higher divider values result in longer countdown times
- Timing should be approximately proportional to divider value
- All dividers work correctly without functional errors

## Scenario S007: Integration Test Mode Test

### Description
Verify integration test mode functionality for direct signal control.

### Setup
1. Ensure normal operation mode initially (WDOGITCR[0]=0)
2. Connect monitoring to wdogint and wdogres signals

### Actions - Enter Test Mode
1. Write value with bit 0 set (e.g., 0x1) to [DEVICE_NAME].WDOGITCR
2. Verify normal timer operation is suspended
3. Write value 0x1 to [DEVICE_NAME].WDOGITOP register
4. Verify wdogint signal is directly controlled by WDOGITOP[1]
5. Write value 0x2 to [DEVICE_NAME].WDOGITOP register
6. Verify wdogres signal is directly controlled by WDOGITOP[0]

### Actions - Exit Test Mode
1. Write value with bit 0 clear (e.g., 0x0) to [DEVICE_NAME].WDOGITCR
2. Verify normal timer operation resumes if enabled

### Expected Results
- Setting WDOGITCR[0]=1 enters test mode
- In test mode, WDOGITOP directly controls wdogint (bit 1) and wdogres (bit 0)
- Clearing WDOGITCR[0]=0 exits test mode
- Normal operation resumes after exiting test mode

## Scenario S008: Register Status Test

### Description
Verify register status reporting through WDOGRIS and WDOGMIS registers.

### Setup
1. Configure timer to generate interrupt
2. Allow interrupt to occur

### Actions
1. Read [DEVICE_NAME].WDOGRIS register
2. Verify bit 0 shows raw interrupt status
3. Read [DEVICE_NAME].WDOGMIS register
4. Verify bit 0 shows masked status (WDOGRIS[0] AND WDOGCONTROL[0])
5. Clear interrupt and verify both registers update
6. Disable INTEN and verify WDOGMIS updates but WDOGRIS doesn't

### Expected Results
- WDOGRIS shows raw interrupt status regardless of INTEN
- WDOGMIS shows masked interrupt status (raw AND INTEN)
- Both registers update correctly when interrupt state changes
- WDOGMIS reflects INTEN enable status

## Scenario S009: Reset Behavior Test

### Description
Verify reset behavior of all registers and internal states.

### Setup
1. Configure device with various non-reset values in registers
2. Monitor reset signals (wrst_n and prst_n)

### Actions - Work Reset (wrst_n)
1. Assert wrst_n reset signal
2. Wait for reset to propagate
3. Deassert wrst_n reset signal
4. Read all registers to verify reset to specification values

### Actions - Bus Reset (prst_n)
1. Assert prst_n reset signal
2. Wait for reset to propagate
3. Deassert prst_n reset signal
4. Read all registers to verify reset to specification values

### Expected Results
- All registers return to specification-defined reset values
- Internal timer state is reset
- Interrupt and reset output states are reset
- Device operates normally after reset

## Scenario S010: Counter Reload Test

### Description
Verify counter reload on INTEN enable and interrupt clear.

### Setup
1. Set INTEN=0 in WDOGCONTROL register
2. Write specific value to WDOGLOAD register
3. Verify counter is not running

### Actions - INTEN Reload
1. Set INTEN=1 in [DEVICE_NAME].WDOGCONTROL register
2. Verify counter reloads from WDOGLOAD value
3. Verify timer starts counting down

### Actions - WDOGINTCLR Reload
1. Configure timer to generate interrupt
2. Allow interrupt to occur
3. Write to [DEVICE_NAME].WDOGINTCLR register
4. Verify counter reloads from WDOGLOAD value
5. Verify timer restarts counting down

### Expected Results
- Counter reloads from WDOGLOAD when INTEN transitions from 0 to 1
- Counter reloads from WDOGLOAD when WDOGINTCLR is written
- Timer behavior is consistent in both reload scenarios

## Scenario S011: PrimeCell ID Registers Test

### Description
Verify all PrimeCell identification registers return correct values.

### Setup
1. Device is properly instantiated

### Actions
1. Read [DEVICE_NAME].WDOGPERIPHID0 register, verify returns 0x24
2. Read [DEVICE_NAME].WDOGPERIPHID1 register, verify returns 0xB8
3. Read [DEVICE_NAME].WDOGPERIPHID2 register, verify returns 0x1B
4. Read [DEVICE_NAME].WDOGPERIPHID3 register, verify returns 0x00
5. Read [DEVICE_NAME].WDOGPERIPHID4 register, verify returns 0x04
6. Read registers 5-7, verify return 0x00
7. Read [DEVICE_NAME].WDOGPCELLID0 register, verify returns 0x0D
8. Read [DEVICE_NAME].WDOGPCELLID1 register, verify returns 0xF0
9. Read [DEVICE_NAME].WDOGPCELLID2 register, verify returns 0x05
10. Read [DEVICE_NAME].WDOGPCELLID3 register, verify returns 0xB1

### Expected Results
- All ID registers return specification-defined constant values
- Registers are read-only and ignore write attempts
- Values match ARM PrimeCell specification for this device

## Scenario S012: Clock Enable Test

### Description
Verify wclk_en signal properly enables/disables timer decrementing.

### Setup
1. Configure timer with INTEN=1 to see decrementing
2. Set wclk_en to high (enabled state)
3. Observe counter decrementing

### Actions
1. Set wclk_en to low (disabled state)
2. Observe that counter stops decrementing
3. Set wclk_en to high (enabled state)
4. Observe that counter resumes decrementing
5. Verify that counter value reflects elapsed time when re-enabled

### Expected Results
- Timer stops decrementing when wclk_en is low
- Timer resumes decrementing when wclk_en is high
- Counter behavior is consistent with clock enable state
- No spurious interrupts occur due to clock enable changes

## Scenario S013: Reserved Bit Handling Test

### Description
Verify handling of reserved register bits.

### Setup
1. Device is properly instantiated

### Actions
1. Write values with reserved bits set to various registers
2. Read back the written values
3. Verify that reserved bits are properly handled
4. Check that functional bits still work as expected

### Expected Results
- Writing to reserved bits has no impact on functionality
- Reserved bits may read as defined in specification
- Functional bits continue to operate correctly
- No errors occur when reserved bits are accessed

## Scenario S014: Concurrent Operations Test

### Description
Verify proper behavior when multiple operations occur simultaneously.

### Setup
1. Configure timer with INTEN=1 and RESEN=1
2. Set a short countdown value
3. Enable monitoring of both interrupt and reset signals

### Actions
1. Allow timer to reach zero (first timeout)
2. Monitor interrupt generation
3. Without clearing interrupt, allow timer to reach zero again (second timeout)
4. Monitor reset signal generation
5. Verify proper sequence of events

### Expected Results
- First timeout generates interrupt
- Second timeout (without clearing first) generates reset
- Both signals behave correctly in sequence
- Internal state properly tracks both interrupt and reset pending states

## Scenario S015: Boundary Value Test

### Description
Test operation with boundary values for registers and counters.

### Setup
1. Device is properly instantiated

### Actions - Maximum Load Value
1. Write 0xFFFFFFFF to [DEVICE_NAME].WDOGLOAD register
2. Verify timer operates correctly with maximum value
3. Measure time to countdown from maximum value

### Actions - Minimum Load Value
1. Write 0x00000001 to [DEVICE_NAME].WDOGLOAD register
2. Verify timer operates correctly with minimum value
3. Verify timer stops at zero after short countdown

### Expected Results
- Timer handles maximum counter values correctly
- Timer handles minimum counter values correctly
- No overflow or underflow errors occur
- All boundary cases operate according to specification