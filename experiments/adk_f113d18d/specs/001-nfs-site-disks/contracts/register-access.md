# Register Access Contracts: Simics Watchdog Timer Device

## Overview

This document specifies the register access contracts for the Simics Watchdog Timer device. It defines the expected behavior for read and write operations to all registers, including side effects, error conditions, and special handling procedures. This contract ensures that both the device implementation and its test suite have a clear understanding of register behavior.

## Address Map

| Register | Offset | Size | Access | Reset Value |
|----------|--------|------|--------|-------------|
| WDOGLOAD | 0x00 | 32-bit | R/W | 0xFFFFFFFF |
| WDOGVALUE | 0x04 | 32-bit | R | 0xFFFFFFFF |
| WDOGCONTROL | 0x08 | 32-bit | R/W | 0x00 |
| WDOGINTCLR | 0x0C | 32-bit | W | 0x00 |
| WDOGRIS | 0x10 | 32-bit | R | 0x00 |
| WDOGMIS | 0x14 | 32-bit | R | 0x00 |
| WDOGLOCK | 0xC00 | 32-bit | R/W | 0x00000000 |
| WDOGITCR | 0xF00 | 32-bit | R/W | 0x00000000 |
| WDOGITOP | 0xF04 | 32-bit | W | 0x00000000 |
| WDOGPERIPHID4-7 | 0xFD0-0xFDC | 8-bit | R | 0x04, 0x00, 0x00, 0x00 |
| WDOGPERIPHID0-3 | 0xFE0-0xFEC | 8-bit | R | 0x24, 0xB8, 0x1B, 0x00 |
| WDOGPCELLID0-3 | 0xFF0-0xFFC | 8-bit | R | 0x0D, 0xF0, 0x05, 0xB1 |

## Register Access Specifications

### WDOGLOAD (0x00) - Watchdog Reload Value
- **Access Type**: Read/Write
- **Read Behavior**: Returns the current reload value stored in the register
- **Write Behavior**: Stores the written value as the new reload value. This value will be loaded into the counter when appropriate conditions are met (INTEN transitions from 0 to 1, WDOGINTCLR is written).
- **Side Effects**: None on read; reload value is updated on write
- **Error Conditions**: None
- **Special Handling**: This register is affected by the lock mechanism

### WDOGVALUE (0x04) - Current Counter Value
- **Access Type**: Read-Only
- **Read Behavior**: Returns the current value of the decrementing counter without affecting the counter itself. This value is calculated based on the elapsed time since the last counter load event, accounting for the clock divider specified in the control register.
- **Write Behavior**: Write operations to this register should be ignored
- **Side Effects**: None on read; counter value remains unchanged
- **Error Conditions**: None
- **Special Handling**: The value returned should reflect the current counter state considering elapsed time, prescaler, and enable state

### WDOGCONTROL (0x08) - Control Register
- **Access Type**: Read/Write
- **Read Behavior**: Returns the current control register value with all fields (INTEN, RESEN, step_value)
- **Write Behavior**: Updates the control register bits. When INTEN bit transitions from 0 to 1 (and was previously 0), the counter reloads from WDOGLOAD value.
- **Side Effects**: 
  - INTEN bit[0]: When transitioning from 0 to 1, counter reloads from WDOGLOAD
  - RESEN bit[1]: When set, enables reset output on second timeout
  - step_value bits[4:2]: Configures the clock divider (000=÷1, 001=÷2, 010=÷4, 011=÷8, 100=÷16)
- **Error Conditions**: None
- **Special Handling**: This register is affected by the lock mechanism

### WDOGINTCLR (0x0C) - Interrupt Clear Register
- **Access Type**: Write-Only
- **Read Behavior**: Read operations should return undefined value or 0
- **Write Behavior**: Writing any value clears the interrupt signal (wdogint) and reloads the counter from WDOGLOAD register value
- **Side Effects**: Clears interrupt state, resets counter to WDOGLOAD value, updates internal interrupt pending state
- **Error Conditions**: None
- **Special Handling**: This register is affected by the lock mechanism

### WDOGRIS (0x10) - Raw Interrupt Status
- **Access Type**: Read-Only
- **Read Behavior**: Returns the raw interrupt status bit. Bit 0 is 1 if interrupt is pending, 0 otherwise
- **Write Behavior**: Write operations to this register should be ignored
- **Side Effects**: None
- **Error Conditions**: None
- **Special Handling**: The value reflects the interrupt state regardless of INTEN bit in WDOGCONTROL

### WDOGMIS (0x14) - Masked Interrupt Status
- **Access Type**: Read-Only
- **Read Behavior**: Returns the masked interrupt status bit. Bit 0 is (WDOGRIS[0] AND WDOGCONTROL[0])
- **Write Behavior**: Write operations to this register should be ignored
- **Side Effects**: None
- **Error Conditions**: None
- **Special Handling**: The value represents the logical AND of raw interrupt status and INTEN enable bit

### WDOGLOCK (0xC00) - Lock Register
- **Access Type**: Read/Write
- **Read Behavior**: Returns 0x0 when unlocked, 0x1 when locked
- **Write Behavior**: Writing 0x1ACCE551 enables write access to other registers; writing any other value disables write access to other registers
- **Side Effects**: Updates the lock state for the entire device (except this register itself)
- **Error Conditions**: Writing invalid unlock value should result in locked state
- **Special Handling**: This register is always writable, regardless of lock state

### WDOGITCR (0xF00) - Integration Test Control Register
- **Access Type**: Read/Write
- **Read Behavior**: Returns current test control register value
- **Write Behavior**: Controls entry/exit from integration test mode via bit 0
- **Side Effects**: 
  - Bit 0: 1=enter test mode; 0=normal decrementing mode
  - In test mode, WDOGITOP can directly control outputs
- **Error Conditions**: None
- **Special Handling**: This register is affected by the lock mechanism

### WDOGITOP (0xF04) - Integration Test Output Register
- **Access Type**: Write-Only
- **Read Behavior**: Read operations should return undefined value or 0
- **Write Behavior**: In test mode, directly controls wdogint (bit 1) and wdogres (bit 0) outputs
- **Side Effects**: Directly controls interrupt and reset output signals in test mode
- **Error Conditions**: None
- **Special Handling**: This register is affected by the lock mechanism

### WDOGPERIPHID4-7 (0xFD0-0xFDC) - Peripheral ID Registers
- **Access Type**: Read-Only
- **Read Behavior**: Return fixed ID values as per ARM PrimeCell specification
- **Write Behavior**: Write operations to these registers should be ignored
- **Side Effects**: None
- **Error Conditions**: None
- **Special Handling**: These registers are unaffected by lock mechanism

### WDOGPERIPHID0-3 (0xFE0-0xFEC) - Peripheral ID Registers
- **Access Type**: Read-Only
- **Read Behavior**: Return fixed ID values as per ARM PrimeCell specification
- **Write Behavior**: Write operations to these registers should be ignored
- **Side Effects**: None
- **Error Conditions**: None
- **Special Handling**: These registers are unaffected by lock mechanism

### WDOGPCELLID0-3 (0xFF0-0xFFC) - PrimeCell ID Registers
- **Access Type**: Read-Only
- **Read Behavior**: Return fixed PrimeCell ID values as per ARM PrimeCell specification
- **Write Behavior**: Write operations to these registers should be ignored
- **Side Effects**: None
- **Error Conditions**: None
- **Special Handling**: These registers are unaffected by lock mechanism

## Lock Protection Behavior

The device implements a lock protection mechanism using the WDOGLOCK register:

1. When WDOGLOCK contains 0x1ACCE551, all registers except WDOGLOCK itself are writable
2. When WDOGLOCK contains any other value, all registers except WDOGLOCK are read-only
3. WDOGLOCK register itself is always writable regardless of lock state
4. Write attempts to protected registers while locked should be silently ignored
5. Read operations are allowed from all registers regardless of lock state

## Integration Test Mode Behavior

When WDOGITCR[0] is 1 (test mode):
1. Direct control of wdogint and wdogres signals via WDOGITOP register
2. Normal timer operation is suspended
3. Counter decrementing is disabled
4. Normal interrupt and reset generation is suspended

When WDOGITCR[0] is 0 (normal mode):
1. Timer operates normally according to specification
2. WDOGITOP has no effect on signals

## Reset Behavior

The device supports two reset signals:
1. wrst_n (work clock domain reset) - asynchronous, affects timer logic
2. prst_n (APB bus reset) - asynchronous, affects register interface

On reset, all registers return to their reset values as specified in the table above.