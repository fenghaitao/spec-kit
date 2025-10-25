# Contract: Timeout and Event Behavior

## Purpose
Define the expected behavior for timeout events, interrupt generation, and reset signal generation.

## Scope
Timer countdown logic, event scheduling, and signal generation for the watchdog timer device.

## Timing Behavior Contracts

### Counter Countdown Mechanism

**Contract: Counter Value Calculation**
```
GIVEN: Counter loaded with value V at cycle C_start
  AND: Clock divider set to D (1, 16, or 256)
WHEN: Software reads WDOGVALUE at cycle C_now
THEN:
  elapsed_counts = (C_now - C_start) / D
  IF elapsed_counts >= V:
    RETURN 0
  ELSE:
    RETURN V - elapsed_counts

INVARIANT: Counter value decreases monotonically until reaching 0
INVARIANT: Counter value never goes negative
```

**Contract: Counter Stopped State**
```
GIVEN: Clock divider set to 0 (reserved encoding, treated as stopped)
WHEN: Any time passes
THEN:
  - WDOGVALUE returns last loaded value (no decrement)
  - No timeout events are scheduled
  - Interrupt and reset signals remain inactive
```

---

### First Timeout Event

**Contract: First Timeout Scheduling**
```
GIVEN: Counter loaded with value V at cycle C_start
  AND: Clock divider D is non-zero
WHEN: WDOGLOAD is written
THEN:
  - First timeout event is scheduled for cycle: C_start + (V * D)
  - Any previously scheduled first timeout is cancelled
  - interrupt_posted is cleared to false

INVARIANT: Only one first timeout event can be pending at any time
```

**Contract: First Timeout Execution**
```
GIVEN: First timeout event fires at cycle C_timeout
  AND: WDOGCONTROL.INTEN = 1 (interrupt enabled)
WHEN: Event handler executes
THEN:
  1. Set interrupt_posted = true
  2. Assert interrupt signal: irq_dev.set_level(1)
  3. Immediately deassert: irq_dev.set_level(0) [edge-triggered]
  4. IF WDOGCONTROL.RESEN = 1:
       Schedule second timeout event for cycle: C_timeout + (V * D)
     ELSE:
       No second timeout is scheduled

POSTCONDITION: WDOGRIS returns 1 after this point
POSTCONDITION: WDOGMIS returns 1 (since INTEN=1)
```

**Contract: First Timeout with Interrupt Disabled**
```
GIVEN: First timeout event fires
  AND: WDOGCONTROL.INTEN = 0 (interrupt disabled)
WHEN: Event handler executes
THEN:
  1. Set interrupt_posted = true
  2. Do NOT assert interrupt signal (remains at 0)
  3. IF WDOGCONTROL.RESEN = 1:
       Schedule second timeout event
     ELSE:
       No second timeout is scheduled

POSTCONDITION: WDOGRIS returns 1 (raw status shows timeout occurred)
POSTCONDITION: WDOGMIS returns 0 (masked status shows no interrupt)
```

---

### Second Timeout Event

**Contract: Second Timeout Scheduling**
```
GIVEN: First timeout has occurred
  AND: WDOGCONTROL.RESEN = 1 (reset enabled)
  AND: Interrupt has NOT been cleared
WHEN: Counter reaches 0 again
THEN:
  - Second timeout event is scheduled for V * D cycles after first timeout
  - Counter continues counting from V down to 0 again

INVARIANT: Second timeout only scheduled if RESEN=1 at first timeout
INVARIANT: Clearing interrupt cancels second timeout
```

**Contract: Second Timeout Execution**
```
GIVEN: Second timeout event fires at cycle C_reset
  AND: WDOGCONTROL.RESEN = 1 (reset enabled)
WHEN: Event handler executes
THEN:
  1. Set reset_posted = true
  2. Assert reset signal: rst_dev.set_level(1)
  3. Reset signal remains asserted (level-triggered, not edge)
  4. Counter stops counting (system reset expected)

POSTCONDITION: Reset signal remains high until system reset
POSTCONDITION: Device enters reset state
```

**Contract: Second Timeout with Reset Disabled**
```
GIVEN: Second timeout event fires
  AND: WDOGCONTROL.RESEN = 0 (reset disabled)
WHEN: Event handler executes
THEN:
  - No action is taken
  - Reset signal remains at 0
  - Counter continues cycling (will trigger first timeout again)

INVARIANT: If RESEN was 1 at first timeout but changed to 0 before second timeout,
           second timeout event still fires but has no effect
```

---

### Event Cancellation

**Contract: Cancellation on Counter Reload**
```
GIVEN: Timeout events are pending (first and/or second)
WHEN: Software writes to WDOGLOAD
THEN:
  - All pending first timeout events are cancelled
  - All pending second timeout events are cancelled
  - interrupt_posted is cleared to false
  - New first timeout is scheduled based on new counter value

POSTCONDITION: No orphaned events remain in event queue
```

**Contract: Cancellation on Interrupt Clear**
```
GIVEN: interrupt_posted = true
  AND: Second timeout event is pending
WHEN: Software writes to WDOGINTCLR
THEN:
  - Second timeout event is cancelled
  - First timeout event (if pending) is NOT cancelled
  - interrupt_posted is cleared to false

POSTCONDITION: If counter hasn't been reloaded, first timeout may fire again
```

---

## Signal Output Contracts

### Interrupt Signal (irq_dev)

**Contract: Edge-Triggered Interrupt**
```
GIVEN: First timeout occurs with INTEN=1
WHEN: Interrupt is generated
THEN:
  - Signal transitions 0 → 1 → 0 in same cycle (edge pulse)
  - Pulse duration is implementation-defined (typically 1 cycle)
  - Multiple timeouts generate multiple pulses

INVARIANT: Interrupt signal is never held high continuously
```

**Contract: Interrupt Signal in Test Mode**
```
GIVEN: integration_test_mode = true
WHEN: Software writes to WDOGITOP.WDOGINT_SET
THEN:
  - Interrupt signal is set to WDOGINT_SET value (0 or 1)
  - Signal remains at specified level until next write
  - Timeout events do NOT affect signal

POSTCONDITION: Test mode overrides normal interrupt behavior
```

---

### Reset Signal (rst_dev)

**Contract: Level-Triggered Reset**
```
GIVEN: Second timeout occurs with RESEN=1
WHEN: Reset is generated
THEN:
  - Signal transitions to 1 and remains high
  - Signal stays high until device is reset by system
  - No automatic deassertion occurs

INVARIANT: Reset signal is level-triggered (not edge-triggered)
INVARIANT: Once asserted, reset persists until system reset
```

**Contract: Reset Signal in Test Mode**
```
GIVEN: integration_test_mode = true
WHEN: Software writes to WDOGITOP.WDOGRES_SET
THEN:
  - Reset signal is set to WDOGRES_SET value (0 or 1)
  - Signal remains at specified level until next write
  - Timeout events do NOT affect signal

POSTCONDITION: Test mode overrides normal reset behavior
```

---

## Integration Test Mode Contracts

**Contract: Test Mode Activation**
```
GIVEN: Device in normal operation mode
WHEN: Software writes 1 to WDOGITCR.ITCR_ENABLE
THEN:
  - integration_test_mode is set to true
  - Pending timeout events are NOT cancelled
  - Timeout events continue to fire but do NOT affect signals
  - Signal outputs controlled exclusively by WDOGITOP

INVARIANT: Counter continues running in test mode
INVARIANT: Timeout events update interrupt_posted but don't assert signals
```

**Contract: Test Mode Deactivation**
```
GIVEN: Device in integration test mode
  AND: WDOGITOP has set signals to levels L_int and L_rst
WHEN: Software writes 0 to WDOGITCR.ITCR_ENABLE
THEN:
  - integration_test_mode is set to false
  - Signal outputs revert to normal timeout-driven behavior
  - Test output levels in WDOGITOP are ignored
  - Current interrupt_posted state determines interrupt signal

POSTCONDITION: Normal operation resumes immediately
```

---

## Clock Divider Behavior

**Contract: Divider Change Effect**
```
GIVEN: Counter is running with divider D1
WHEN: Software changes WDOGCONTROL divider bits to D2
THEN:
  - Divider change takes effect immediately
  - Counter calculation uses D2 for all future WDOGVALUE reads
  - Pending timeout events remain scheduled at original cycle count
  - Actual timeout may occur earlier/later due to divider change

WARNING: Changing divider while counting can cause unexpected timeout timing
RECOMMENDATION: Reload counter after changing divider for predictable behavior
```

**Contract: Divider Encoding**
```
GIVEN: WDOGCONTROL bits [1:0] set to DD
WHEN: Divider value is needed
THEN:
  DD = 00 → Divider = 1   (counter decrements every cycle)
  DD = 01 → Divider = 16  (counter decrements every 16 cycles)
  DD = 10 → Divider = 256 (counter decrements every 256 cycles)
  DD = 11 → Divider = 1   (reserved, treated as divider=1)

INVARIANT: Divider is always >= 1 (counter never stops due to divider)
```

---

## Interrupt/Reset Enable Behavior

**Contract: Enable Changes After Timeout Scheduled**
```
GIVEN: First timeout event is scheduled with INTEN=X, RESEN=Y
WHEN: Software changes INTEN or RESEN before timeout fires
THEN:
  - Timeout event still fires at scheduled time
  - Effect of timeout uses NEW values of INTEN and RESEN
  - Event is not rescheduled

EXAMPLE:
  1. Load counter with INTEN=0, RESEN=0
  2. First timeout scheduled (no effect)
  3. Set INTEN=1 before timeout fires
  4. When timeout fires: interrupt IS generated (uses new INTEN=1)
```

---

## Checkpoint/Restore Contracts

**Contract: State Preservation**
```
GIVEN: Device state at checkpoint time T_ckpt:
  - counter_start_time = C_start
  - counter_start_value = V
  - interrupt_posted = I
  - reset_posted = R
  - First timeout scheduled for cycle C_timeout1
  - Second timeout scheduled for cycle C_timeout2 (if applicable)

WHEN: Checkpoint is saved and later restored at simulation cycle C_restore

THEN:
  - Saved variables are restored exactly
  - Current counter value is recalculated: V - (C_restore - C_start) / D
  - IF C_restore < C_timeout1:
      First timeout is rescheduled for (C_timeout1 - C_restore) cycles
  - ELSE IF C_restore >= C_timeout1 AND C_restore < C_timeout2:
      First timeout has passed, second timeout rescheduled
  - ELSE:
      Both timeouts have passed, device in reset state

INVARIANT: Counter behavior after restore matches what would have happened
           if simulation had run continuously
```

**Contract: Event Rescheduling**
```
GIVEN: Checkpoint saved with pending events
WHEN: Checkpoint is restored
THEN:
  - Events are NOT restored from checkpoint directly
  - Events are recreated based on counter state:
    * If counter > 0 and not timed out: schedule first timeout
    * If interrupt_posted=true and counter would time out again: schedule second timeout
  - Event times are adjusted relative to restore cycle

INVARIANT: Event semantics are preserved, not exact event objects
```

---

## Timing Guarantees

### Accuracy Guarantees
```
GUARANTEE: Counter value is cycle-accurate
  - WDOGVALUE returns exact count based on SIM_cycle_count()
  - No drift or approximation errors

GUARANTEE: Timeout occurs at deterministic cycle
  - First timeout fires exactly at cycle: C_start + V * D
  - Second timeout fires exactly at cycle: C_start + 2 * V * D
  - No jitter or variability
```

### Performance Guarantees
```
GUARANTEE: Constant-time operations
  - WDOGVALUE read computes in O(1) time
  - Event scheduling/cancellation is O(1)
  - No performance degradation with large counter values

GUARANTEE: No missed events
  - All timeout events fire exactly once
  - No events are lost or duplicated
  - Event ordering is deterministic
```

---

## Edge Cases and Error Conditions

### Zero Counter Value
```
GIVEN: Software writes 0 to WDOGLOAD
WHEN: Counter is loaded
THEN:
  - First timeout event scheduled for cycle: C_start + (0 * D) = C_start
  - Timeout fires immediately (same cycle as load)
  - Interrupt generated immediately if INTEN=1
```

### Maximum Counter Value
```
GIVEN: Software writes 0xFFFFFFFF to WDOGLOAD
  AND: Divider = 256
WHEN: Counter is loaded
THEN:
  - First timeout scheduled for cycle: C_start + (0xFFFFFFFF * 256)
  - Timeout occurs in very distant future (> 1 trillion cycles)
  - Counter decrements normally, no overflow issues
```

### Rapid Counter Reloads
```
GIVEN: Software writes to WDOGLOAD multiple times in rapid succession
WHEN: Each write occurs before previous timeout fires
THEN:
  - Each write cancels previous timeout
  - Only last write's timeout will fire
  - No race conditions or event queue buildup

INVARIANT: Device handles rapid reloads gracefully
```

### Interrupt Clear Before Timeout
```
GIVEN: First timeout is scheduled but has not fired yet
WHEN: Software writes to WDOGINTCLR
THEN:
  - Write has no effect (interrupt not posted yet)
  - First timeout event still scheduled
  - When timeout fires, interrupt is posted normally
```

### Lock During Timeout
```
GIVEN: First timeout event is scheduled
WHEN: Device is locked (WDOGLOCK written with lock value)
THEN:
  - Timeout event still fires normally
  - Interrupt/reset signals still asserted
  - Lock only affects register writes, not timeout behavior

INVARIANT: Lock does not prevent timeout events from occurring
```

---

## Test Verification Requirements

Each contract must be verified with dedicated test cases:

1. **Basic Timeout Test**: Verify first timeout fires at correct cycle
2. **Dual Timeout Test**: Verify second timeout after first timeout
3. **Interrupt Clear Test**: Verify WDOGINTCLR prevents second timeout
4. **Counter Reload Test**: Verify reload cancels pending timeouts
5. **Divider Test**: Verify all divider values produce correct timing
6. **Enable Change Test**: Verify changing INTEN/RESEN affects behavior
7. **Test Mode Test**: Verify integration test mode overrides normal behavior
8. **Checkpoint Test**: Verify device state restores correctly
9. **Edge Case Tests**: Verify zero count, max count, rapid reloads
10. **Signal Test**: Verify interrupt edge-triggered, reset level-triggered
