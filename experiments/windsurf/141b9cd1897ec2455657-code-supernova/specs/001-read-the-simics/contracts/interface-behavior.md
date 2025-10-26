# Interface Behavior Contracts

## Contract: Counter Operation

### Counter Enable
**Preconditions**:
- WDOGCONTROL.INTEN = 0 (counter currently disabled)
**Action**: Write WDOGCONTROL with INTEN = 1
**Postconditions**:
- Counter reloads from WDOGLOAD
- counter_start_time = current simulation cycle
- counter_start_value = WDOGLOAD value
- Counter begins decrementing based on clock divider
- Timeout event scheduled for (WDOGLOAD * step_divider) cycles in future

### Counter Disable
**Preconditions**:
- WDOGCONTROL.INTEN = 1 (counter currently enabled)
**Action**: Write WDOGCONTROL with INTEN = 0
**Postconditions**:
- Counter stops decrementing
- Current counter value preserved (readable via WDOGVALUE)
- Pending timeout event cancelled
- No interrupt or reset generation

### Counter Reload
**Preconditions**:
- Counter is running (INTEN = 1)
**Action**: Write any value to WDOGINTCLR
**Postconditions**:
- Counter reloads from WDOGLOAD
- counter_start_time = current simulation cycle
- counter_start_value = WDOGLOAD value
- Interrupt cleared (WDOGRIS[0] = 0, wdogint deasserted)
- New timeout event scheduled
- Reset state NOT cleared (if reset was asserted, it remains asserted)

### Counter Decrement
**Preconditions**:
- INTEN = 1 (counter enabled)
- Integration test mode disabled (WDOGITCR[0] = 0)
**Behavior**: Continuous
**Postconditions**:
- Counter decrements by 1 every (step_divider) simulation cycles
- step_divider determined by WDOGCONTROL.step_value:
  * 0b000 → 1 cycle
  * 0b001 → 2 cycles
  * 0b010 → 4 cycles
  * 0b011 → 8 cycles
  * 0b100 → 16 cycles
  * 0b101-0b111 → 1 cycle (undefined, treat as no division)
- Counter wraps from 0x00000000 to 0xFFFFFFFF if no timeout handling enabled

## Contract: Interrupt Generation

### First Timeout (Interrupt Assertion)
**Preconditions**:
- Counter enabled (INTEN = 1)
- Counter reaches 0x00000000
- Integration test mode disabled
**Action**: Counter timeout event
**Postconditions**:
- WDOGRIS[0] = 1 (raw interrupt status set)
- wdogint signal asserted (raised to high)
- interrupt_pending state = true
- Counter reloads from WDOGLOAD and continues
- New timeout event scheduled

### Interrupt Clear
**Preconditions**:
- Interrupt pending (WDOGRIS[0] = 1)
**Action**: Write to WDOGINTCLR
**Postconditions**:
- WDOGRIS[0] = 0 (raw interrupt status cleared)
- wdogint signal deasserted (lowered to low)
- interrupt_pending state = false
- Counter reloads from WDOGLOAD
- Timeout count resets (next timeout will be first timeout again)

### Interrupt Masking
**Preconditions**: None
**Behavior**: Continuous
**Postconditions**:
- WDOGMIS[0] = WDOGRIS[0] AND WDOGCONTROL.INTEN
- If INTEN = 0: WDOGMIS[0] = 0 (masked)
- If INTEN = 1: WDOGMIS[0] = WDOGRIS[0] (unmasked)
- Masking does NOT affect wdogint signal (signal follows WDOGRIS, not WDOGMIS)

## Contract: Reset Generation

### Second Timeout (Reset Assertion)
**Preconditions**:
- Counter enabled (INTEN = 1)
- Reset enabled (RESEN = 1)
- First timeout already occurred (interrupt_pending = true)
- Counter reaches 0x00000000 again
- Integration test mode disabled
**Action**: Counter second timeout event
**Postconditions**:
- wdogres signal asserted (raised to high)
- reset_asserted state = true
- wdogres signal remains asserted indefinitely
- Counter continues running (reloads and decrements)
- Interrupt continues to be asserted

### Reset Persistence
**Preconditions**:
- Reset asserted (reset_asserted = true)
**Behavior**: Persistent
**Postconditions**:
- wdogres signal cannot be cleared by software
- wdogres remains high until device reset (hard reset or soft reset)
- Writing to WDOGINTCLR does NOT clear reset
- Disabling RESEN does NOT clear reset

### Reset on Device Reset
**Preconditions**:
- Device reset occurs (hard reset or soft reset signal)
**Action**: Device reset
**Postconditions**:
- wdogres signal deasserted (lowered to low)
- reset_asserted state = false
- All registers reset to default values
- Counter reloads to 0xFFFFFFFF
- Interrupt cleared
- Lock state = unlocked

## Contract: Lock Mechanism

### Lock Protection
**Preconditions**:
- Device is locked (lock_state = true)
**Action**: Attempt to write to WDOGLOAD or WDOGCONTROL
**Postconditions**:
- Write ignored
- Register values unchanged
- No side effects
- No error signaled

### Unlock Sequence
**Preconditions**:
- Device is locked (lock_state = true)
**Action**: Write 0x1ACCE551 to WDOGLOCK
**Postconditions**:
- lock_state = false
- WDOGLOAD and WDOGCONTROL become writable
- Unlock takes effect immediately
- No other state changes

### Lock Sequence
**Preconditions**:
- Device is unlocked (lock_state = false)
**Action**: Write any value except 0x1ACCE551 to WDOGLOCK
**Postconditions**:
- lock_state = true
- WDOGLOAD and WDOGCONTROL become write-protected
- Lock takes effect immediately
- No other state changes

### Lock State Query
**Preconditions**: None
**Action**: Read WDOGLOCK
**Postconditions**:
- Returns 0x00000000 if unlocked
- Returns 0x00000001 if locked
- No side effects

## Contract: Integration Test Mode

### Enter Integration Test Mode
**Preconditions**:
- Integration test mode disabled (WDOGITCR[0] = 0)
**Action**: Write 1 to WDOGITCR[0]
**Postconditions**:
- integration_test_mode = true
- Normal counter operation disabled
- Pending timeout events cancelled
- wdogint and wdogres signals controlled by WDOGITOP writes
- Counter value frozen (WDOGVALUE returns last value)

### Exit Integration Test Mode
**Preconditions**:
- Integration test mode enabled (WDOGITCR[0] = 1)
**Action**: Write 0 to WDOGITCR[0]
**Postconditions**:
- integration_test_mode = false
- Normal counter operation re-enabled (if INTEN = 1)
- wdogint and wdogres signals revert to normal control
- Counter resumes from current state

### Direct Signal Control
**Preconditions**:
- Integration test mode enabled (WDOGITCR[0] = 1)
**Action**: Write value to WDOGITOP
**Postconditions**:
- wdogres signal = WDOGITOP[0]
- wdogint signal = WDOGITOP[1]
- Signals change immediately
- No effect on internal state (interrupt_pending, reset_asserted)
- No effect on counter

## Contract: Checkpoint/Restore

### Checkpoint Save
**Preconditions**: Device is running
**Action**: Simics checkpoint save operation
**Postconditions**:
- All saved state variables written to checkpoint:
  * counter_start_time
  * counter_start_value
  * interrupt_pending
  * reset_asserted
  * lock_state
  * integration_test_mode
  * All register values
- Pending events NOT saved (will be recalculated on restore)

### Checkpoint Restore
**Preconditions**: Valid checkpoint exists
**Action**: Simics checkpoint restore operation
**Postconditions**:
- All saved state variables restored from checkpoint
- Timeout events recalculated and rescheduled based on:
  * counter_start_time
  * counter_start_value
  * Current simulation cycle
  * WDOGCONTROL.step_value
- Signal states restored (wdogint, wdogres)
- Device resumes operation exactly as before checkpoint

## Contract: Clock Divider Behavior

### Divider Change While Running
**Preconditions**:
- Counter enabled (INTEN = 1)
- Counter currently running with step_value = X
**Action**: Write WDOGCONTROL with new step_value = Y
**Postconditions**:
- Divider change takes effect immediately
- Pending timeout event cancelled
- New timeout event scheduled with new divider
- Counter value calculation uses new divider from this point forward
- No counter reload (continues from current value)

### Divider Values
**Preconditions**: None
**Behavior**: Constant
**Postconditions**:
- step_value 0b000 → divide by 1 (no division)
- step_value 0b001 → divide by 2
- step_value 0b010 → divide by 4
- step_value 0b011 → divide by 8
- step_value 0b100 → divide by 16
- step_value 0b101-0b111 → undefined (treat as divide by 1)

## Contract: Signal Timing

### Interrupt Signal Timing
**Preconditions**: None
**Behavior**: Immediate
**Postconditions**:
- wdogint assertion occurs in same cycle as timeout event
- wdogint deassertion occurs in same cycle as WDOGINTCLR write
- No delay between register write and signal change

### Reset Signal Timing
**Preconditions**: None
**Behavior**: Immediate
**Postconditions**:
- wdogres assertion occurs in same cycle as second timeout event
- wdogres deassertion occurs in same cycle as device reset
- No delay between event and signal change

## Contract: Error Conditions

### Invalid step_value
**Preconditions**: None
**Action**: Write WDOGCONTROL with step_value > 0b100
**Postconditions**:
- Value accepted and stored
- Treated as step_value = 0b000 (divide by 1) for counter operation
- No error signaled
- Warning may be logged

### Counter Wrap Without Timeout Handling
**Preconditions**:
- INTEN = 0 and RESEN = 0
- Counter reaches 0x00000000
**Action**: Counter decrement
**Postconditions**:
- Counter wraps to 0xFFFFFFFF
- No interrupt generated
- No reset generated
- Counter continues decrementing

### Simultaneous Lock and Write
**Preconditions**: Device is unlocked
**Action**: Write to WDOGLOCK (to lock) and WDOGLOAD in same transaction
**Postconditions**:
- Lock state change and register write are independent
- Both operations complete
- Order depends on transaction processing order
- No race condition (operations are atomic)
