# Register Access Contracts

## Contract: WDOGLOAD Register Access

### Read Contract
**Preconditions**: None  
**Action**: Read from offset 0x000  
**Postconditions**:
- Returns current value of WDOGLOAD register
- No side effects
- Value range: 0x00000000 to 0xFFFFFFFF

### Write Contract
**Preconditions**: 
- Device must be unlocked (WDOGLOCK != locked state)
**Action**: Write value to offset 0x000  
**Postconditions**:
- If unlocked: WDOGLOAD register updated with written value
- If locked: Write ignored, WDOGLOAD unchanged
- No immediate effect on counter (takes effect on next reload)
- No side effects on other registers

## Contract: WDOGVALUE Register Access

### Read Contract
**Preconditions**: None  
**Action**: Read from offset 0x004  
**Postconditions**:
- Returns calculated current counter value
- Calculation: If counter enabled, value = (current_cycles - start_cycles) / step_divider + start_value
- If counter disabled (INTEN=0), returns last counter value
- No side effects
- Value range: 0x00000000 to 0xFFFFFFFF

### Write Contract
**Preconditions**: N/A (register is read-only)  
**Action**: Write to offset 0x004  
**Postconditions**:
- Write ignored
- No state changes
- No error signaled

## Contract: WDOGCONTROL Register Access

### Read Contract
**Preconditions**: None  
**Action**: Read from offset 0x008  
**Postconditions**:
- Returns current value of WDOGCONTROL register
- Bits [31:5] always read as 0
- Bits [4:0] reflect current control settings
- No side effects

### Write Contract
**Preconditions**:
- Device must be unlocked (WDOGLOCK != locked state)
**Action**: Write value to offset 0x008  
**Postconditions**:
- If unlocked: WDOGCONTROL updated with written value (bits [4:0] only)
- If locked: Write ignored, WDOGCONTROL unchanged
- If INTEN transitions 0→1: Counter reloads from WDOGLOAD and starts
- If INTEN transitions 1→0: Counter stops
- If step_value changes while running: Counter behavior updates immediately
- Bits [31:5] always written as 0

## Contract: WDOGINTCLR Register Access

### Read Contract
**Preconditions**: N/A (register is write-only)  
**Action**: Read from offset 0x00C  
**Postconditions**:
- Returns undefined value (implementation may return 0)
- No side effects

### Write Contract
**Preconditions**: None  
**Action**: Write any value to offset 0x00C  
**Postconditions**:
- Interrupt cleared: WDOGRIS[0] = 0
- wdogint signal deasserted (if it was asserted)
- Counter reloaded from WDOGLOAD
- counter_start_time = current simulation cycle
- counter_start_value = WDOGLOAD value
- Written value is ignored (only write action matters)
- Not affected by lock state

## Contract: WDOGRIS Register Access

### Read Contract
**Preconditions**: None  
**Action**: Read from offset 0x010  
**Postconditions**:
- Bit [0] returns raw interrupt status (1 if timeout occurred, 0 otherwise)
- Bits [31:1] always read as 0
- No side effects
- Status reflects whether counter has reached zero since last clear

### Write Contract
**Preconditions**: N/A (register is read-only)  
**Action**: Write to offset 0x010  
**Postconditions**:
- Write ignored
- No state changes
- No error signaled

## Contract: WDOGMIS Register Access

### Read Contract
**Preconditions**: None  
**Action**: Read from offset 0x014  
**Postconditions**:
- Bit [0] returns masked interrupt status (WDOGRIS[0] AND WDOGCONTROL.INTEN)
- Bits [31:1] always read as 0
- No side effects
- Reflects whether interrupt is both pending and enabled

### Write Contract
**Preconditions**: N/A (register is read-only)  
**Action**: Write to offset 0x014  
**Postconditions**:
- Write ignored
- No state changes
- No error signaled

## Contract: WDOGLOCK Register Access

### Read Contract
**Preconditions**: None  
**Action**: Read from offset 0xC00  
**Postconditions**:
- Returns 0x00000000 if device is unlocked
- Returns 0x00000001 if device is locked
- No side effects

### Write Contract
**Preconditions**: None  
**Action**: Write value to offset 0xC00  
**Postconditions**:
- If value == 0x1ACCE551: Device unlocked (lock_state = false)
- If value != 0x1ACCE551: Device locked (lock_state = true)
- Lock state change takes effect immediately
- Not affected by current lock state (can always write to unlock)

## Contract: WDOGITCR Register Access

### Read Contract
**Preconditions**: None  
**Action**: Read from offset 0xF00  
**Postconditions**:
- Bit [0] returns integration test mode enable status
- Bits [31:1] always read as 0
- No side effects

### Write Contract
**Preconditions**: None  
**Action**: Write value to offset 0xF00  
**Postconditions**:
- Bit [0] written to integration_test_mode state
- Bits [31:1] ignored
- If mode transitions 0→1: Normal counter operation disabled
- If mode transitions 1→0: Normal counter operation re-enabled
- Not affected by lock state

## Contract: WDOGITOP Register Access

### Read Contract
**Preconditions**: N/A (register is write-only)  
**Action**: Read from offset 0xF04  
**Postconditions**:
- Returns undefined value (implementation may return 0)
- No side effects

### Write Contract
**Preconditions**: 
- Integration test mode must be enabled (WDOGITCR[0] = 1)
**Action**: Write value to offset 0xF04  
**Postconditions**:
- If integration test mode enabled:
  * wdogres signal set to bit [0] value
  * wdogint signal set to bit [1] value
  * Bits [31:2] ignored
- If integration test mode disabled:
  * Write ignored
  * No signal changes
- Not affected by lock state

## Contract: Identification Registers (WDOGPERIPHID*, WDOGPCELLID*)

### Read Contract
**Preconditions**: None  
**Action**: Read from offsets 0xFD0-0xFDC, 0xFE0-0xFEC, 0xFF0-0xFFC  
**Postconditions**:
- Returns constant identification values per register
- No side effects
- Values match ARM PrimeCell SP805 specification

### Write Contract
**Preconditions**: N/A (registers are read-only)  
**Action**: Write to identification register offsets  
**Postconditions**:
- Write ignored
- No state changes
- No error signaled

## Contract: Unmapped Address Access

### Read Contract
**Preconditions**: None  
**Action**: Read from unmapped offset (not in register map)  
**Postconditions**:
- Returns 0x00000000
- No side effects
- No error signaled

### Write Contract
**Preconditions**: None  
**Action**: Write to unmapped offset (not in register map)  
**Postconditions**:
- Write ignored
- No state changes
- No error signaled

## Lock Protection Summary

| Register | Lock Protected | Notes |
|----------|----------------|-------|
| WDOGLOAD | Yes | Writes ignored when locked |
| WDOGVALUE | No | Read-only, no lock needed |
| WDOGCONTROL | Yes | Writes ignored when locked |
| WDOGINTCLR | No | Always writable (interrupt clear) |
| WDOGRIS | No | Read-only, no lock needed |
| WDOGMIS | No | Read-only, no lock needed |
| WDOGLOCK | No | Always writable (to allow unlocking) |
| WDOGITCR | No | Always writable (test mode control) |
| WDOGITOP | No | Always writable (test mode output) |
| Identification | No | Read-only constants |

## Transaction Size Handling

All registers support 32-bit aligned accesses. Behavior for non-aligned or partial accesses:
- **8-bit access**: Supported - reads/writes single byte of 32-bit register
- **16-bit access**: Supported - reads/writes two bytes of 32-bit register  
- **32-bit access**: Preferred - reads/writes entire register
- **Unaligned access**: Supported - handled by Simics platform bus
- **Larger than 32-bit**: Not supported - behavior undefined
