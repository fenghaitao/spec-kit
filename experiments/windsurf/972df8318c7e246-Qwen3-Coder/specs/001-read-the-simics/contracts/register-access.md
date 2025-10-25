# Register Access Contracts: Watchdog Timer Device

## Overview
This document specifies the expected behavior of all register accesses for the watchdog timer device. These contracts define the functional requirements that must be verified through testing.

## Register Access Behavior

### WDOGLOAD (0x00) - Watchdog Load Register
**Access Type**: Read/Write
**Expected Behavior**:
- Reading returns the current timer reload value
- Writing updates the timer reload value
- When locked, writes are ignored
- In integration test mode, normal operation continues

### WDOGVALUE (0x04) - Watchdog Value Register
**Access Type**: Read Only
**Expected Behavior**:
- Reading returns the current timer counter value
- Writing is not allowed and should be ignored
- Value decreases from WDOGLOAD value to 0

### WDOGCONTROL (0x08) - Watchdog Control Register
**Access Type**: Read/Write
**Expected Behavior**:
- Reading returns current control settings
- Writing updates control settings
- When locked, writes are ignored
- step_value field controls clock divider (000=÷1, 001=÷2, 010=÷4, 011=÷8, 100=÷16)
- RESEN bit enables/disables reset output
- INTEN bit enables/disables interrupt output

### WDOGINTCLR (0x0C) - Watchdog Interrupt Clear Register
**Access Type**: Write Only
**Expected Behavior**:
- Writing any value clears pending interrupt
- Writing any value reloads timer from WDOGLOAD
- Reading is not allowed and should return undefined value
- When locked, writes are ignored

### WDOGRIS (0x10) - Watchdog Raw Interrupt Status Register
**Access Type**: Read Only
**Expected Behavior**:
- Reading returns 1 if interrupt is pending, 0 otherwise
- Writing is not allowed and should be ignored
- Bit is set when timer reaches zero and INTEN=1
- Bit is cleared when WDOGINTCLR is written

### WDOGMIS (0x14) - Watchdog Masked Interrupt Status Register
**Access Type**: Read Only
**Expected Behavior**:
- Reading returns 1 if (interrupt pending AND INTEN=1), 0 otherwise
- Writing is not allowed and should be ignored
- Bit reflects the actual interrupt output state

### WDOGLOCK (0xC00) - Watchdog Lock Register
**Access Type**: Read/Write
**Expected Behavior**:
- Reading returns 0 if unlocked, 1 if locked
- Writing 0x1ACCE551 unlocks registers
- Writing any other value locks registers
- This register is never locked itself

### WDOGITCR (0xF00) - Watchdog Integration Test Control Register
**Access Type**: Read/Write
**Expected Behavior**:
- Reading returns current test mode setting
- Writing 1 enables integration test mode
- Writing 0 disables integration test mode
- When locked, writes are ignored

### WDOGITOP (0xF04) - Watchdog Integration Test Output Set Register
**Access Type**: Write Only
**Expected Behavior**:
- Writing sets interrupt and reset output values directly
- Only effective when integration test mode is enabled
- Reading is not allowed and should return undefined value
- When locked, writes are ignored

### WDOGPERIPHID0-7 (0xFE0, 0xFE4, 0xFE8, 0xFEC, 0xFD0, 0xFD4, 0xFD8, 0xFDC) - Peripheral Identification Registers
**Access Type**: Read Only
**Expected Behavior**:
- Reading returns fixed identification values
- Writing is not allowed and should be ignored
- Values match ARM PrimeCell specification

### WDOGPCELLID0-3 (0xFF0, 0xFF4, 0xFF8, 0xFFC) - PrimeCell Identification Registers
**Access Type**: Read Only
**Expected Behavior**:
- Reading returns fixed identification values
- Writing is not allowed and should be ignored
- Values match ARM PrimeCell specification

## Error Conditions

### Locked Register Access
**Condition**: Attempt to write to protected register when WDOGLOCK != 0x1ACCE551
**Expected Behavior**:
- Write operation is ignored
- Register value remains unchanged
- No error reported to system
- Log message may be generated for debugging

### Invalid Register Access
**Condition**: Attempt to read from write-only register or write to read-only register
**Expected Behavior**:
- Operation is ignored
- No change to device state
- No error reported to system
- Log message may be generated for debugging

## Timing Behavior

### Timer Operation
**Condition**: Normal operation with INTEN=1
**Expected Behavior**:
- Timer counts down from WDOGLOAD value
- When timer reaches zero:
  * If interrupt not pending: Set interrupt pending, reload timer
  * If interrupt pending: Generate reset if RESEN=1
- Clock divider affects countdown rate according to step_value

### Integration Test Mode
**Condition**: WDOGITCR[0]=1 and WDOGITOP written
**Expected Behavior**:
- Interrupt and reset outputs reflect WDOGITOP values
- Normal timer operation suspended
- Timer counter stops counting

## Reset Behavior

### Device Reset
**Condition**: Reset signal asserted or device initialization
**Expected Behavior**:
- All registers set to reset values
- Timer counter set to WDOGLOAD value
- Interrupt pending flag cleared
- Registers unlocked (WDOGLOCK=0)
- Integration test mode disabled

### Timer Reset
**Condition**: WDOGINTCLR written
**Expected Behavior**:
- Timer counter reloaded from WDOGLOAD
- Interrupt pending flag cleared
- Device continues normal operation
