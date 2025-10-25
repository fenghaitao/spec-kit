# Contract: Register Access Behavior

## Purpose
Define the expected behavior for all register read and write operations in the watchdog timer device.

## Scope
All 21 registers in the watchdog timer device (offsets 0x000 - 0xFFC).

## Register Access Contracts

### WDOGLOAD (0x000) - Counter Load Register

**Write Contract**:
```
GIVEN: Device in unlocked state (WDOGLOCK written with 0x1ACCE551)
WHEN: Software writes value V to WDOGLOAD
THEN:
  - Counter start value is set to V
  - Counter start time is set to current cycle count
  - Any pending first timeout event is cancelled
  - Any pending second timeout event is cancelled
  - New first timeout event is scheduled for V * divider cycles in future
  - WDOGVALUE returns V immediately after write
  - Interrupt flag (interrupt_posted) is cleared

GIVEN: Device in locked state
WHEN: Software writes value V to WDOGLOAD
THEN:
  - Write is ignored
  - Counter state remains unchanged
  - No events are cancelled or scheduled
```

**Read Contract**:
```
GIVEN: Any device state
WHEN: Software reads WDOGLOAD
THEN:
  - Returns the last value written to WDOGLOAD
  - Does not modify any device state
```

---

### WDOGVALUE (0x004) - Current Counter Value

**Read Contract**:
```
GIVEN: Counter is running (divider > 0)
WHEN: Software reads WDOGVALUE
THEN:
  - Calculate: elapsed_counts = (current_cycles - counter_start_time) / divider
  - IF elapsed_counts >= counter_start_value:
      RETURN 0
  - ELSE:
      RETURN counter_start_value - elapsed_counts
  - Does not modify any device state

GIVEN: Counter is stopped (divider = 0)
WHEN: Software reads WDOGVALUE
THEN:
  - Returns counter_start_value (no counting occurs)
```

**Write Contract**:
```
GIVEN: Any device state
WHEN: Software writes to WDOGVALUE
THEN:
  - Write is ignored (read-only register)
  - No device state is modified
```

---

### WDOGCONTROL (0x008) - Control Register

**Write Contract**:
```
GIVEN: Device in unlocked state
WHEN: Software writes value V to WDOGCONTROL
THEN:
  - RESEN field is set to V[0]
  - INTEN field is set to V[1]
  - Bits [31:2] are ignored
  - IF counter is currently counting AND timeout events exist:
      - Timeout behavior is updated to reflect new INTEN/RESEN settings
      - Events remain scheduled but effect changes
  - No events are cancelled or rescheduled

GIVEN: Device in locked state
WHEN: Software writes to WDOGCONTROL
THEN:
  - Write is ignored
  - Control fields remain unchanged
```

**Read Contract**:
```
GIVEN: Any device state
WHEN: Software reads WDOGCONTROL
THEN:
  - Returns current control register value
  - Bit [0] contains RESEN
  - Bit [1] contains INTEN
  - Bits [31:2] return 0
```

---

### WDOGINTCLR (0x00C) - Interrupt Clear Register

**Write Contract**:
```
GIVEN: Interrupt is pending (interrupt_posted = true)
WHEN: Software writes any value to WDOGINTCLR
THEN:
  - Interrupt flag (interrupt_posted) is cleared to false
  - Any pending second timeout event is cancelled
  - Interrupt signal is deasserted (if it was asserted)
  - Counter continues running from current value
  - First timeout event (if still in future) remains scheduled

GIVEN: No interrupt pending (interrupt_posted = false)
WHEN: Software writes to WDOGINTCLR
THEN:
  - No state change occurs
  - Operation is idempotent
```

**Read Contract**:
```
GIVEN: Any device state
WHEN: Software reads WDOGINTCLR
THEN:
  - Returns 0 (write-only register, read value is undefined)
```

---

### WDOGRIS (0x010) - Raw Interrupt Status

**Read Contract**:
```
GIVEN: First timeout has occurred (interrupt_posted = true)
WHEN: Software reads WDOGRIS
THEN:
  - Returns 0x00000001 (bit 0 set)

GIVEN: No timeout has occurred (interrupt_posted = false)
WHEN: Software reads WDOGRIS
THEN:
  - Returns 0x00000000 (bit 0 clear)

POSTCONDITION: Read does not modify interrupt_posted state
```

**Write Contract**:
```
GIVEN: Any device state
WHEN: Software writes to WDOGRIS
THEN:
  - Write is ignored (read-only register)
```

---

### WDOGMIS (0x014) - Masked Interrupt Status

**Read Contract**:
```
GIVEN: interrupt_posted = true AND WDOGCONTROL.INTEN = 1
WHEN: Software reads WDOGMIS
THEN:
  - Returns 0x00000001 (bit 0 set)

GIVEN: interrupt_posted = false OR WDOGCONTROL.INTEN = 0
WHEN: Software reads WDOGMIS
THEN:
  - Returns 0x00000000 (bit 0 clear)

POSTCONDITION: Read does not modify any device state
```

**Write Contract**:
```
GIVEN: Any device state
WHEN: Software writes to WDOGMIS
THEN:
  - Write is ignored (read-only register)
```

---

### WDOGLOCK (0xC00) - Lock Register

**Write Contract**:
```
GIVEN: Any device state
WHEN: Software writes 0x1ACCE551 (magic unlock value) to WDOGLOCK
THEN:
  - locked state is set to false
  - WDOGLOAD and WDOGCONTROL become writable

GIVEN: Any device state
WHEN: Software writes any other value to WDOGLOCK
THEN:
  - locked state is set to true
  - WDOGLOAD and WDOGCONTROL become read-only
```

**Read Contract**:
```
GIVEN: locked = true
WHEN: Software reads WDOGLOCK
THEN:
  - Returns 0x00000001

GIVEN: locked = false
WHEN: Software reads WDOGLOCK
THEN:
  - Returns 0x00000000
```

---

### WDOGITCR (0xF00) - Integration Test Control

**Write Contract**:
```
GIVEN: Any device state
WHEN: Software writes value V to WDOGITCR
THEN:
  - ITCR_ENABLE field is set to V[0]
  - Bits [31:1] are ignored
  - IF V[0] = 1 (test mode enabled):
      - integration_test_mode is set to true
      - Timeout events are ignored (no interrupt/reset from timer)
      - Signal outputs controlled by WDOGITOP
  - IF V[0] = 0 (normal mode):
      - integration_test_mode is set to false
      - Normal timeout behavior resumes
```

**Read Contract**:
```
GIVEN: Any device state
WHEN: Software reads WDOGITCR
THEN:
  - Returns current ITCR value
  - Bit [0] contains ITCR_ENABLE
  - Bits [31:1] return 0
```

---

### WDOGITOP (0xF04) - Integration Test Output

**Write Contract**:
```
GIVEN: integration_test_mode = true
WHEN: Software writes value V to WDOGITOP
THEN:
  - WDOGINT_SET field is set to V[0]
  - WDOGRES_SET field is set to V[1]
  - Bits [31:2] are ignored
  - Interrupt signal is set to level V[0]
  - Reset signal is set to level V[1]

GIVEN: integration_test_mode = false
WHEN: Software writes value V to WDOGITOP
THEN:
  - Fields are updated but have no effect on signal outputs
  - Normal timeout logic controls signals
```

**Read Contract**:
```
GIVEN: Any device state
WHEN: Software reads WDOGITOP
THEN:
  - Returns current ITOP value
  - Bit [0] contains WDOGINT_SET
  - Bit [1] contains WDOGRES_SET
  - Bits [31:2] return 0
```

---

### Peripheral ID Registers (0xFE0-0xFEC)

**Read Contract**:
```
GIVEN: Any device state
WHEN: Software reads WDOGPeriphIDx (x = 0, 1, 2, 3)
THEN:
  - WDOGPeriphID0 returns 0x00000024
  - WDOGPeriphID1 returns 0x000000B8
  - WDOGPeriphID2 returns 0x0000001B
  - WDOGPeriphID3 returns 0x00000000
  - No device state is modified
```

**Write Contract**:
```
GIVEN: Any device state
WHEN: Software writes to WDOGPeriphIDx
THEN:
  - Write is ignored (read-only register)
```

---

### PrimeCell ID Registers (0xFF0-0xFFC)

**Read Contract**:
```
GIVEN: Any device state
WHEN: Software reads WDOGPCellIDx (x = 0, 1, 2, 3)
THEN:
  - WDOGPCellID0 returns 0x0000000D
  - WDOGPCellID1 returns 0x000000F0
  - WDOGPCellID2 returns 0x00000005
  - WDOGPCellID3 returns 0x000000B1
  - No device state is modified
```

**Write Contract**:
```
GIVEN: Any device state
WHEN: Software writes to WDOGPCellIDx
THEN:
  - Write is ignored (read-only register)
```

---

## Reserved Register Space

**Read Contract**:
```
GIVEN: Any device state
WHEN: Software reads from reserved offset (0x018-0xBFF, 0xC04-0xEFF, 0xF08-0xFDF)
THEN:
  - Returns 0x00000000 (RAZ - Read As Zero)
```

**Write Contract**:
```
GIVEN: Any device state
WHEN: Software writes to reserved offset
THEN:
  - Write is ignored (WI - Write Ignore)
  - No device state is modified
```

---

## Atomic Access Requirements

### Single Register Access
```
GIVEN: Software performs 32-bit aligned read or write
WHEN: Access is to any register
THEN:
  - Access completes atomically
  - No partial updates occur
```

### Unaligned Access
```
GIVEN: Software performs unaligned access (offset not multiple of 4)
WHEN: Access spans register boundary
THEN:
  - Behavior is IMPLEMENTATION-DEFINED
  - Recommended: Support byte-level access with little-endian byte order
```

### Concurrent Access
```
GIVEN: Multiple accesses occur in same cycle
WHEN: Accesses target different registers
THEN:
  - All accesses complete with defined ordering
  - No data corruption occurs

GIVEN: Multiple accesses occur in same cycle
WHEN: Accesses target same register
THEN:
  - Last write wins (write ordering is deterministic)
  - Reads return consistent value
```

---

## Lock Protection Enforcement

**Protected Register List**:
- WDOGLOAD (0x000)
- WDOGCONTROL (0x008)

**Unprotected Registers** (always writable):
- WDOGINTCLR (0x00C)
- WDOGLOCK (0xC00)
- WDOGITCR (0xF00)
- WDOGITOP (0xF04)

**Lock Enforcement Contract**:
```
GIVEN: locked = true
WHEN: Software writes to protected register
THEN:
  - Write is silently ignored
  - No error is signaled
  - Register value remains unchanged
  - No side effects occur

GIVEN: locked = false
WHEN: Software writes to protected register
THEN:
  - Write succeeds with full side effects
```

---

## Test Verification

Each contract must be verified with a dedicated test case:

1. **Register Read/Write Tests**: Verify basic read/write behavior for all registers
2. **Lock Protection Tests**: Verify lock mechanism blocks writes to protected registers
3. **Timeout Event Tests**: Verify counter reload cancels/reschedules events correctly
4. **Interrupt Clear Tests**: Verify WDOGINTCLR clears interrupt and cancels reset
5. **Integration Test Tests**: Verify test mode overrides normal behavior
6. **Reserved Space Tests**: Verify RAZ/WI behavior for unmapped offsets
7. **Unaligned Access Tests**: Verify byte-level access handling
8. **Reset State Tests**: Verify all registers return to correct reset values

---

## Error Conditions

### Invalid Access Patterns

**Write to Read-Only Register**:
- Silently ignored
- No error signaled
- Device state unchanged

**Read from Write-Only Register**:
- Returns implementation-defined value (typically 0)
- No error signaled

**Access to Reserved Space**:
- Read returns 0
- Write ignored
- No error signaled

**Out-of-Range Access** (offset >= 0x1000):
- Handled by memory bus
- Device not responsible for range checking
