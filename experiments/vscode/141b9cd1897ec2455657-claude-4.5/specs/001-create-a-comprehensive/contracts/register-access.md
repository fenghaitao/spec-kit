# Contract: Register Access Behavior

**Branch**: `001-create-a-comprehensive`
**Phase**: Phase 1 - Design
**Created**: 2025
**Status**: Complete

---

## Overview

This contract defines the expected behavior for all register access operations in the Simics Watchdog Timer device. Each register's read and write behavior is specified with preconditions, actions, and postconditions.

---

## Register Access Contracts

### WDOGLOAD (0x000) - Load Register

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Returns the last written value to WDOGLOAD
- If never written, returns reset value (0xFFFFFFFF)

**Postconditions**:
- No side effects
- Register value unchanged

#### Write Access
**Preconditions**:
- Device must be unlocked (WDOGLOCK != 1)

**Expected Behavior**:
- If locked: Write ignored, log warning
- If unlocked:
  - Store written value in WDOGLOAD register
  - If counter is running (WDOGCONTROL.INTEN=1):
    - Update `counter_start_value` to new WDOGLOAD value
    - Update `counter_start_time` to current cycle count
    - Reschedule interrupt event based on new value

**Postconditions**:
- WDOGLOAD.val = written value (if unlocked)
- Counter restarted with new value (if running)
- Pending interrupt/reset events canceled and rescheduled

**Test Verification**:
```python
# Unlock device
dev.bank.regs.WDOGLOCK.val = 0x1ACCE551

# Write load value
load_val = 0x1000
WDOGLOAD_reg.write(load_val)
assert WDOGLOAD_reg.read() == load_val

# Verify locked behavior
dev.bank.regs.WDOGLOCK.val = 0x1  # Lock
WDOGLOAD_reg.write(0x2000)
assert WDOGLOAD_reg.read() == load_val  # Value unchanged
```

---

### WDOGVALUE (0x004) - Value Register

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Calculate current counter value dynamically:
  ```
  if (counter not running):
      return counter_start_value
  else:
      elapsed_cycles = SIM_cycle_count(dev.obj) - counter_start_time
      decrements = elapsed_cycles / step_value
      if (decrements >= counter_start_value):
          return 0
      else:
          return counter_start_value - decrements
  ```

**Postconditions**:
- No side effects
- Counter state unchanged

**Test Verification**:
```python
# Start counter with known value
WDOGLOAD_reg.write(0x1000)
WDOGCONTROL_reg.write(0x1)  # Enable interrupt

# Read immediate value (should be close to 0x1000)
value1 = WDOGVALUE_reg.read()
assert value1 <= 0x1000

# Advance simulation
simics.SIM_run_command("run-cycles 100")

# Read after delay (should be less)
value2 = WDOGVALUE_reg.read()
assert value2 < value1
```

#### Write Access
**Preconditions**:
- Not applicable (read-only register)

**Expected Behavior**:
- Write ignored
- Log warning: "Write to read-only register WDOGVALUE ignored"

**Postconditions**:
- Register value unchanged

---

### WDOGCONTROL (0x008) - Control Register

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Returns current value of WDOGCONTROL register
- Bits [31:2] read as 0 (reserved)
- Bit [1]: RESEN (reset enable)
- Bit [0]: INTEN (interrupt enable)

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- Device must be unlocked (WDOGLOCK != 1)

**Expected Behavior**:
- If locked: Write ignored, log warning
- If unlocked:
  - Store written value (mask to bits [1:0])
  - Detect INTEN transitions:
    - **0→1 transition** (start counter):
      - Load counter from WDOGLOAD
      - Record counter_start_time = SIM_cycle_count()
      - Calculate step_value from reserved bits (default to 1)
      - Schedule interrupt event: `after (counter_start_value * step_value) cycles: fire_interrupt()`
    - **1→0 transition** (stop counter):
      - Cancel pending interrupt event
      - Cancel pending reset event
      - Counter holds current value

**Postconditions**:
- WDOGCONTROL.val updated (if unlocked)
- Counter started or stopped based on INTEN transition
- Events scheduled/canceled appropriately

**Test Verification**:
```python
# Unlock and configure
WDOGLOCK_reg.write(0x1ACCE551)
WDOGLOAD_reg.write(0x100)

# Start counter
WDOGCONTROL_reg.write(0x1)  # INTEN=1
assert WDOGCONTROL_reg.read() == 0x1
assert WDOGVALUE_reg.read() <= 0x100

# Stop counter
WDOGCONTROL_reg.write(0x0)  # INTEN=0
value_stopped = WDOGVALUE_reg.read()
simics.SIM_run_command("run-cycles 100")
assert WDOGVALUE_reg.read() == value_stopped  # No change
```

---

### WDOGINTCLR (0x00C) - Interrupt Clear Register

#### Read Access
**Preconditions**:
- Not applicable (write-only register)

**Expected Behavior**:
- Read returns 0 (or undefined value)

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- Device must be unlocked (WDOGLOCK != 1)
- Integration test mode must be disabled (WDOGITCR.ITEN=0)

**Expected Behavior**:
- If locked or in test mode: Write ignored, log warning
- If unlocked and normal mode:
  - Clear interrupt pending flag: `interrupt_pending = false`
  - Deassert interrupt signal: `wdogint_signal.set_level(0)`
  - Reload counter: `counter_start_value = WDOGLOAD.val`
  - Reset counter timing: `counter_start_time = SIM_cycle_count()`
  - Cancel pending reset event
  - Reschedule interrupt event if INTEN=1

**Postconditions**:
- WDOGRIS.RAWINT = 0
- wdogint signal = 0
- Counter reloaded from WDOGLOAD
- Reset event canceled

**Test Verification**:
```python
# Setup: trigger interrupt
WDOGLOCK_reg.write(0x1ACCE551)
WDOGLOAD_reg.write(0x10)  # Small value for quick timeout
WDOGCONTROL_reg.write(0x1)  # INTEN=1
simics.SIM_run_command("run-cycles 20")  # Wait for timeout

# Verify interrupt asserted
assert WDOGRIS_reg.read() & 0x1 == 1

# Clear interrupt
WDOGINTCLR_reg.write(0x0)  # Any value clears

# Verify interrupt cleared
assert WDOGRIS_reg.read() & 0x1 == 0
assert WDOGVALUE_reg.read() <= 0x10  # Counter reloaded
```

---

### WDOGRIS (0x010) - Raw Interrupt Status Register

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Returns raw interrupt status (internal `interrupt_pending` flag)
- Bit [0]: RAWINT (1 = interrupt pending, 0 = no interrupt)
- Bits [31:1]: Read as 0 (reserved)

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- Not applicable (read-only register)

**Expected Behavior**:
- Write ignored
- Log warning: "Write to read-only register WDOGRIS ignored"

**Postconditions**:
- Register value unchanged

**Test Verification**:
```python
# Initially no interrupt
assert WDOGRIS_reg.read() == 0

# Trigger timeout
WDOGLOAD_reg.write(0x10)
WDOGCONTROL_reg.write(0x1)
simics.SIM_run_command("run-cycles 20")

# Verify interrupt asserted
assert WDOGRIS_reg.read() & 0x1 == 1
```

---

### WDOGMIS (0x014) - Masked Interrupt Status Register

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Calculate masked interrupt status:
  ```
  WDOGMIS.MASKINT = WDOGRIS.RAWINT & WDOGCONTROL.INTEN
  ```
- Returns 1 only if both interrupt pending AND interrupt enabled

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- Not applicable (read-only register)

**Expected Behavior**:
- Write ignored
- Log warning

**Test Verification**:
```python
# Setup interrupt but disabled
WDOGLOAD_reg.write(0x10)
WDOGCONTROL_reg.write(0x1)  # INTEN=1
simics.SIM_run_command("run-cycles 20")
assert WDOGRIS_reg.read() & 0x1 == 1
assert WDOGMIS_reg.read() & 0x1 == 1  # Masked status = enabled

# Disable interrupt
WDOGCONTROL_reg.write(0x0)  # INTEN=0
assert WDOGRIS_reg.read() & 0x1 == 1  # Raw still set
assert WDOGMIS_reg.read() & 0x1 == 0  # Masked cleared
```

---

### WDOGLOCK (0xC00) - Lock Register

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Returns current lock status:
  - 0x00000000: Device unlocked
  - 0x00000001: Device locked
- Only bit [0] is meaningful, bits [31:1] read as 0

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- None (can always write to lock register)

**Expected Behavior**:
- Compare written value against magic unlock value:
  - **If value == 0x1ACCE551**:
    - Unlock device: `lock_state = false`
    - Register reads back as 0x00000000
    - Log: "Watchdog unlocked"
  - **If value != 0x1ACCE551**:
    - Lock device: `lock_state = true`
    - Register reads back as 0x00000001
    - Log: "Watchdog locked"

**Postconditions**:
- lock_state updated
- Protected registers (WDOGLOAD, WDOGCONTROL, WDOGINTCLR) access controlled by new lock state

**Test Verification**:
```python
# Device starts locked
assert WDOGLOCK_reg.read() == 1

# Attempt write to protected register (should fail)
WDOGLOAD_reg.write(0x1234)
assert WDOGLOAD_reg.read() != 0x1234  # Write blocked

# Unlock device
WDOGLOCK_reg.write(0x1ACCE551)
assert WDOGLOCK_reg.read() == 0

# Write to protected register (should succeed)
WDOGLOAD_reg.write(0x5678)
assert WDOGLOAD_reg.read() == 0x5678

# Relock device
WDOGLOCK_reg.write(0x0)  # Any value except magic locks
assert WDOGLOCK_reg.read() == 1
```

---

### WDOGITCR (0xF00) - Integration Test Control Register

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Returns current integration test mode setting
- Bit [0]: ITEN (1 = test mode enabled, 0 = normal mode)
- Bits [31:1]: Read as 0

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- None (not lock protected)

**Expected Behavior**:
- Store written value (mask to bit [0])
- Update `integration_test_mode` flag
- **If ITEN transitions to 1** (enable test mode):
  - Normal interrupt/reset generation disabled
  - WDOGITOP controls output signals directly
  - Log: "Integration test mode ENABLED"
- **If ITEN transitions to 0** (disable test mode):
  - Normal interrupt/reset generation restored
  - WDOGITOP writes ignored
  - Output signals return to normal state
  - Log: "Integration test mode DISABLED"

**Postconditions**:
- integration_test_mode flag updated
- Interrupt/reset generation behavior changed

**Test Verification**:
```python
# Enable integration test mode
WDOGITCR_reg.write(0x1)
assert WDOGITCR_reg.read() == 0x1

# Verify WDOGITOP controls signals
WDOGITOP_reg.write(0x1)  # Set WDOGINT
# Check wdogint signal asserted

# Disable test mode
WDOGITCR_reg.write(0x0)
assert WDOGITCR_reg.read() == 0x0

# Verify WDOGITOP writes ignored
WDOGITOP_reg.write(0x1)
# Check wdogint signal NOT asserted
```

---

### WDOGITOP (0xF04) - Integration Test Output Set Register

#### Read Access
**Preconditions**:
- Not applicable (write-only register)

**Expected Behavior**:
- Read returns 0 (or undefined value)

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- Integration test mode must be enabled (WDOGITCR.ITEN=1)

**Expected Behavior**:
- If test mode disabled: Write ignored, log warning
- If test mode enabled:
  - Extract bit [0]: WDOGINT value
  - Extract bit [1]: WDOGRES value
  - Directly control output signals:
    - `wdogint_signal.set_level(WDOGINT ? 1 : 0)`
    - `wdogres_signal.set_level(WDOGRES ? 1 : 0)`
  - Log: "Integration test: WDOGINT=%d, WDOGRES=%d"

**Postconditions**:
- Output signals set to specified values
- Normal watchdog logic bypassed

**Test Verification**:
```python
# Enable test mode
WDOGITCR_reg.write(0x1)

# Set both signals high
WDOGITOP_reg.write(0x3)  # WDOGINT=1, WDOGRES=1
# Verify both signals asserted

# Set WDOGINT low, WDOGRES high
WDOGITOP_reg.write(0x2)  # WDOGINT=0, WDOGRES=1
# Verify only WDOGRES asserted

# Clear both
WDOGITOP_reg.write(0x0)
# Verify both signals deasserted
```

---

### Peripheral ID Registers (0xFE0-0xFEF)

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Return constant identification values:
  - WDOGPeriphID0 (0xFE0): 0x00000005
  - WDOGPeriphID1 (0xFE4): 0x00000018
  - WDOGPeriphID2 (0xFE8): 0x00000018
  - WDOGPeriphID3 (0xFEC): 0x00000000

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- Not applicable (read-only registers)

**Expected Behavior**:
- Write ignored
- Log warning

---

### PrimeCell ID Registers (0xFF0-0xFFF)

#### Read Access
**Preconditions**:
- None

**Expected Behavior**:
- Return constant PrimeCell identification pattern:
  - WDOGPCellID0 (0xFF0): 0x0000000D
  - WDOGPCellID1 (0xFF4): 0x000000F0
  - WDOGPCellID2 (0xFF8): 0x00000005
  - WDOGPCellID3 (0xFFC): 0x000000B1
- Pattern forms "0xB105F00D" when read as word sequence

**Postconditions**:
- No side effects

#### Write Access
**Preconditions**:
- Not applicable (read-only registers)

**Expected Behavior**:
- Write ignored
- Log warning

---

## Lock Protection Behavior

### Lock State Transitions

```
┌─────────────────────────────────────────┐
│         LOCKED STATE (Reset)            │
│  WDOGLOCK.read() = 1                    │
│  Protected register writes IGNORED      │
└─────────────────────────────────────────┘
                 │
                 │ Write 0x1ACCE551 to WDOGLOCK
                 ▼
┌─────────────────────────────────────────┐
│         UNLOCKED STATE                  │
│  WDOGLOCK.read() = 0                    │
│  Protected register writes ALLOWED      │
└─────────────────────────────────────────┘
                 │
                 │ Write any value != 0x1ACCE551
                 ▼
┌─────────────────────────────────────────┐
│         LOCKED STATE                    │
│  WDOGLOCK.read() = 1                    │
│  Protected register writes IGNORED      │
└─────────────────────────────────────────┘
```

### Protected Registers
- WDOGLOAD (0x000)
- WDOGCONTROL (0x008)
- WDOGINTCLR (0x00C)

### Lock Protection Contract
**For all protected registers**:

```python
def protected_register_write(value):
    if (lock_state == true):
        log warning: "Write to [REGISTER_NAME] blocked by lock"
        return  # Ignore write
    else:
        # Proceed with normal write logic
        ...
```

---

## Reserved Register Behavior

### Reserved Address Ranges
- 0x018-0x01F
- 0x020-0xBFF
- 0xC04-0xEFF
- 0xF08-0xF0F
- 0xF10-0xFDF

### Contract for Reserved Addresses

#### Read Access
**Expected Behavior**:
- Return 0
- Log warning: "Read from reserved address [ADDRESS]"

#### Write Access
**Expected Behavior**:
- Ignore write
- Log warning: "Write to reserved address [ADDRESS] ignored"

---

## Summary of Register Access Rules

| Register | Read | Write | Lock Protected | Special Behavior |
|----------|------|-------|----------------|------------------|
| WDOGLOAD | RW | RW | Yes | Reloads counter when written |
| WDOGVALUE | RO | - | No | Dynamically calculated |
| WDOGCONTROL | RW | RW | Yes | Starts/stops counter |
| WDOGINTCLR | - | WO | Yes | Clears interrupt, reloads counter |
| WDOGRIS | RO | - | No | Raw interrupt status |
| WDOGMIS | RO | - | No | Masked interrupt status (computed) |
| WDOGLOCK | RW | RW | No | Magic value 0x1ACCE551 unlocks |
| WDOGITCR | RW | RW | No | Enables test mode |
| WDOGITOP | - | WO | No | Direct signal control (test mode) |
| WDOGPeriphID* | RO | - | No | Constant identification values |
| WDOGPCellID* | RO | - | No | Constant PrimeCell pattern |

**Legend**:
- RO: Read-Only
- WO: Write-Only
- RW: Read-Write
- "-": Not applicable

---

**Document Status**: Complete  
**Next Artifact**: contracts/interface-behavior.md
