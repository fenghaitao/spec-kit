# Contract: Interface Behavior

**Branch**: `001-create-a-comprehensive`
**Phase**: Phase 1 - Design
**Created**: 2025
**Status**: Complete

---

## Overview

This contract defines the expected behavior for all external interfaces of the Simics Watchdog Timer device, including memory-mapped I/O, signal outputs, event scheduling, and checkpoint operations.

---

## io_memory Interface

### Purpose
Handles memory-mapped register access from CPU and bus masters.

### Method: operation(generic_transaction_t *trans)

#### Preconditions
- Transaction object contains valid address, size, and operation type
- Address within device's mapped range (configurable base + 0x000 to 0xFFF)

#### Read Transaction Behavior

**Inputs**:
- `trans->physical_address`: Target register offset
- `trans->size`: Number of bytes to read (typically 1, 2, or 4)
- `trans->inquiry`: Whether this is a speculative/inquiry read

**Expected Processing**:
1. Calculate register offset: `offset = trans->physical_address - base_address`
2. Validate offset within 4KB range (0x000-0xFFF)
3. Check if offset maps to valid register
4. **If valid register**:
   - Call register's `read()` method
   - Return register value in `trans->value`
   - Set `trans->exception = Sim_PE_No_Exception`
5. **If reserved/invalid offset**:
   - Log warning: "Read from invalid/reserved address [offset]"
   - Return 0 in `trans->value`
   - Set `trans->exception = Sim_PE_No_Exception` (no bus error)
6. Handle partial/unaligned access if supported

**Outputs**:
- `trans->value`: Read data
- `trans->exception`: Exception type (typically Sim_PE_No_Exception)

**Postconditions**:
- Transaction completed with appropriate data/exception
- Device state unchanged for inquiry reads
- Device state unchanged for normal reads (except FIFO/status registers - N/A for watchdog)

**Test Verification**:
```python
# Valid register read
phys_mem = dev.iface.io_memory
value = phys_mem.read(dev, None, 0x000, 4, 0)  # Read WDOGLOAD
assert value is not None

# Invalid address read
value = phys_mem.read(dev, None, 0x100, 4, 0)  # Reserved region
assert value == 0  # Returns 0, no exception
```

---

#### Write Transaction Behavior

**Inputs**:
- `trans->physical_address`: Target register offset
- `trans->size`: Number of bytes to write
- `trans->value`: Data to write
- `trans->inquiry`: Whether this is a speculative/inquiry write

**Expected Processing**:
1. Calculate register offset: `offset = trans->physical_address - base_address`
2. Validate offset within 4KB range
3. Check if offset maps to valid register
4. **If valid register**:
   - Check if register is writable (not read-only)
   - If writable: Call register's `write(value)` method
   - If read-only: Log warning, ignore write
   - Set `trans->exception = Sim_PE_No_Exception`
5. **If reserved/invalid offset**:
   - Log warning: "Write to invalid/reserved address [offset] ignored"
   - Set `trans->exception = Sim_PE_No_Exception`
6. Ignore inquiry writes (no state change)

**Outputs**:
- `trans->exception`: Exception type
- Device state updated (if non-inquiry write to valid writable register)

**Postconditions**:
- Register value updated (if valid write)
- Side effects executed (counter start/stop, interrupt clear, etc.)
- Inquiry writes leave state unchanged

**Test Verification**:
```python
# Valid register write
phys_mem = dev.iface.io_memory
phys_mem.write(dev, None, 0x000, 0x1234, 4, 0)  # Write WDOGLOAD
assert dev.bank.regs.WDOGLOAD.val == 0x1234

# Read-only register write
old_value = dev.bank.regs.WDOGVALUE.val
phys_mem.write(dev, None, 0x004, 0x5678, 4, 0)  # Write WDOGVALUE (RO)
assert dev.bank.regs.WDOGVALUE.val == old_value  # Unchanged
```

---

### Address Decoding

**Contract**: Device implements standard io_memory interface with bank template auto-dispatch

```
Base Address (configured): 0x[BASE]
Address Calculation: register_offset = transaction_address - BASE

Register Mapping:
  0x000: WDOGLOAD
  0x004: WDOGVALUE
  0x008: WDOGCONTROL
  0x00C: WDOGINTCLR
  0x010: WDOGRIS
  0x014: WDOGMIS
  0xC00: WDOGLOCK
  0xF00: WDOGITCR
  0xF04: WDOGITOP
  0xFE0-0xFEC: WDOGPeriphID[0-3]
  0xFF0-0xFFC: WDOGPCellID[0-3]
  
Reserved/Invalid: All other offsets in 0x000-0xFFF range
```

---

## signal Interface - wdogint_signal

### Purpose
Provides interrupt output to system interrupt controller.

### Connection Type
`connect wdogint_signal is signal_connect`

### Signal Protocol
**Type**: Level-sensitive signal  
**Active Level**: High (1 = interrupt asserted, 0 = interrupt deasserted)  
**Polarity**: Active-high

---

### Method: set_level(int level)

#### Assert Interrupt (level=1)

**Preconditions**:
- Counter has reached zero (first timeout)
- WDOGCONTROL.INTEN = 1 (interrupt enabled)
- Integration test mode disabled (WDOGITCR.ITEN = 0)
  OR
- Integration test mode enabled (WDOGITCR.ITEN = 1)
- WDOGITOP.WDOGINT = 1 (direct control)

**Expected Behavior**:
1. Set internal `interrupt_pending` flag = true
2. Call `wdogint_signal.set_level(1)`
3. Update WDOGRIS.RAWINT = 1
4. If WDOGCONTROL.INTEN=1: WDOGMIS.MASKINT = 1
5. Log: "Watchdog interrupt asserted"
6. If WDOGCONTROL.RESEN=1: Schedule reset event for second timeout

**Postconditions**:
- wdogint signal driven high
- Interrupt controller receives interrupt notification
- WDOGRIS.RAWINT = 1
- Reset event scheduled (if RESEN=1)

**Test Verification**:
```python
# Setup watchdog for interrupt
dev.bank.regs.WDOGLOCK.val = 0x1ACCE551  # Unlock
dev.bank.regs.WDOGLOAD.val = 0x10
dev.bank.regs.WDOGCONTROL.val = 0x1  # INTEN=1

# Run until timeout
simics.SIM_run_command("run-cycles 20")

# Verify interrupt asserted
assert dev.bank.regs.WDOGRIS.val & 0x1 == 1
assert dev.wdogint_signal.level == 1  # Signal high
```

---

#### Deassert Interrupt (level=0)

**Preconditions**:
- WDOGINTCLR register written
- Integration test mode enabled AND WDOGITOP.WDOGINT = 0

**Expected Behavior**:
1. Clear internal `interrupt_pending` flag = false
2. Call `wdogint_signal.set_level(0)`
3. Update WDOGRIS.RAWINT = 0
4. Update WDOGMIS.MASKINT = 0
5. Log: "Watchdog interrupt cleared"
6. Cancel pending reset event (interrupt cleared in time)

**Postconditions**:
- wdogint signal driven low
- Interrupt controller receives interrupt clear notification
- WDOGRIS.RAWINT = 0
- WDOGMIS.MASKINT = 0
- Reset event canceled

**Test Verification**:
```python
# After interrupt triggered (from previous test)
assert dev.bank.regs.WDOGRIS.val & 0x1 == 1

# Clear interrupt
dev.bank.regs.WDOGINTCLR.val = 0x0  # Any value clears

# Verify interrupt deasserted
assert dev.bank.regs.WDOGRIS.val & 0x1 == 0
assert dev.wdogint_signal.level == 0  # Signal low
```

---

### Integration Test Mode Behavior

**When WDOGITCR.ITEN = 1**:

**Contract**: Normal interrupt generation BYPASSED

```python
# Normal mode: Counter controls signal
if (counter_timeout AND INTEN AND NOT integration_test_mode):
    wdogint_signal.set_level(1)

# Test mode: WDOGITOP controls signal
if (integration_test_mode):
    if (WDOGITOP written):
        wdogint_signal.set_level(WDOGITOP.WDOGINT ? 1 : 0)
```

**Test Verification**:
```python
# Enable integration test mode
dev.bank.regs.WDOGITCR.val = 0x1

# Directly assert interrupt via WDOGITOP
dev.bank.regs.WDOGITOP.val = 0x1  # WDOGINT=1
assert dev.wdogint_signal.level == 1

# Directly deassert
dev.bank.regs.WDOGITOP.val = 0x0  # WDOGINT=0
assert dev.wdogint_signal.level == 0

# Verify normal timeout does NOT trigger interrupt in test mode
dev.bank.regs.WDOGITCR.val = 0x0  # Disable test mode
dev.bank.regs.WDOGITCR.val = 0x1  # Re-enable test mode
dev.bank.regs.WDOGCONTROL.val = 0x1  # INTEN=1
simics.SIM_run_command("run-cycles 20")  # Wait for timeout
assert dev.wdogint_signal.level == 0  # Signal NOT asserted (test mode active)
```

---

## signal Interface - wdogres_signal

### Purpose
Provides reset output to system reset controller.

### Connection Type
`connect wdogres_signal is signal_connect`

### Signal Protocol
**Type**: Pulse signal (typically)  
**Active Level**: High (1 = reset requested, 0 = no reset)  
**Polarity**: Active-high

---

### Method: set_level(int level)

#### Assert Reset (level=1)

**Preconditions**:
- Counter has reached zero for SECOND time (after interrupt not cleared)
- WDOGCONTROL.RESEN = 1 (reset enabled)
- Integration test mode disabled (WDOGITCR.ITEN = 0)
  OR
- Integration test mode enabled (WDOGITCR.ITEN = 1)
- WDOGITOP.WDOGRES = 1 (direct control)

**Expected Behavior**:
1. Set internal `reset_pending` flag = true
2. Call `wdogres_signal.set_level(1)`
3. Log: "Watchdog reset asserted - system reset triggered"
4. Reset signal typically held high until system reset completes

**Postconditions**:
- wdogres signal driven high
- System reset controller receives reset request
- Target system typically resets (watchdog device state preserved until system init)

**Test Verification**:
```python
# Setup watchdog for reset
dev.bank.regs.WDOGLOCK.val = 0x1ACCE551
dev.bank.regs.WDOGLOAD.val = 0x10
dev.bank.regs.WDOGCONTROL.val = 0x3  # INTEN=1, RESEN=1

# Run until first timeout (interrupt)
simics.SIM_run_command("run-cycles 20")
assert dev.bank.regs.WDOGRIS.val & 0x1 == 1

# Continue running without clearing interrupt (second timeout)
simics.SIM_run_command("run-cycles 20")

# Verify reset asserted
assert dev.wdogres_signal.level == 1  # Reset signal high
```

---

#### Deassert Reset (level=0)

**Preconditions**:
- Reset pulse completed (implementation-specific timing)
- Integration test mode enabled AND WDOGITOP.WDOGRES = 0

**Expected Behavior**:
1. Clear internal `reset_pending` flag = false
2. Call `wdogres_signal.set_level(0)`
3. Log: "Watchdog reset deasserted"

**Postconditions**:
- wdogres signal driven low
- Reset request cleared

**Note**: In typical usage, system reset occurs before reset deassert, so this transition is primarily for integration testing.

---

### Reset Prevention Contract

**Contract**: Writing WDOGINTCLR BEFORE second timeout PREVENTS reset assertion

```
Timeline:
  T=0:    Counter starts (WDOGLOAD=100, INTEN=1, RESEN=1)
  T=100:  First timeout → Interrupt asserted (wdogint=1)
          Counter reloads, reset event scheduled for T=200
  
  Scenario A: Reset Triggered
    T=200: Second timeout → Reset asserted (wdogres=1)
  
  Scenario B: Reset Prevented
    T=150: Write WDOGINTCLR → Interrupt cleared, reset event CANCELED
    T=200: No reset (event was canceled)
```

**Test Verification**:
```python
# Scenario A: Reset triggered
dev.bank.regs.WDOGLOCK.val = 0x1ACCE551
dev.bank.regs.WDOGLOAD.val = 0x10
dev.bank.regs.WDOGCONTROL.val = 0x3  # INTEN=1, RESEN=1
simics.SIM_run_command("run-cycles 40")  # Wait for both timeouts
assert dev.wdogres_signal.level == 1  # Reset asserted

# Scenario B: Reset prevented
dev2 = create_watchdog_device()
dev2.bank.regs.WDOGLOCK.val = 0x1ACCE551
dev2.bank.regs.WDOGLOAD.val = 0x10
dev2.bank.regs.WDOGCONTROL.val = 0x3
simics.SIM_run_command("run-cycles 20")  # First timeout
assert dev2.bank.regs.WDOGRIS.val & 0x1 == 1  # Interrupt set
dev2.bank.regs.WDOGINTCLR.val = 0x0  # Clear interrupt
simics.SIM_run_command("run-cycles 20")  # Would be second timeout
assert dev2.wdogres_signal.level == 0  # Reset NOT asserted
```

---

## Event Scheduling Interface

### Purpose
Schedule cycle-accurate countdown events for interrupt and reset timeouts.

### DML after Statement

```dml
after <cycles> cycles: <method_call>;
```

---

### Interrupt Timeout Event

#### Scheduling Contract

**Trigger**: Counter enabled (WDOGCONTROL.INTEN transitions 0→1) OR counter reloaded

**Calculation**:
```dml
local cycles_t cycles_to_interrupt = counter_start_value * step_value;
after cycles_to_interrupt cycles: fire_interrupt();
```

**Variables**:
- `counter_start_value`: Value from WDOGLOAD register
- `step_value`: Clock divider (1, 16, or 256 based on reserved bits, default 1)

**Preconditions**:
- WDOGCONTROL.INTEN = 1 (interrupt enabled)
- Counter loaded with non-zero value

**Expected Behavior**:
1. Cancel any pending interrupt event
2. Calculate cycles until timeout
3. Schedule `fire_interrupt()` method call
4. Store event handle in `session event_handle_t interrupt_event`

**Postconditions**:
- Event scheduled in Simics event queue
- Will execute exactly at `current_cycle + cycles_to_interrupt`

**Test Verification**:
```python
# Schedule interrupt with known timing
dev.bank.regs.WDOGLOCK.val = 0x1ACCE551
dev.bank.regs.WDOGLOAD.val = 0x100  # 256 cycles (step_value=1)
dev.bank.regs.WDOGCONTROL.val = 0x1

# Verify interrupt NOT triggered before timeout
simics.SIM_run_command("run-cycles 255")
assert dev.bank.regs.WDOGRIS.val & 0x1 == 0  # Not yet

# Verify interrupt triggered AT timeout
simics.SIM_run_command("run-cycles 1")  # Cycle 256
assert dev.bank.regs.WDOGRIS.val & 0x1 == 1  # Triggered
```

---

#### Event Cancellation Contract

**Triggers**:
- Counter disabled (WDOGCONTROL.INTEN transitions 1→0)
- Counter value modified (write to WDOGLOAD)
- Interrupt cleared (write to WDOGINTCLR)

**Expected Behavior**:
```dml
method cancel_interrupt_event() {
    if (interrupt_event != NULL) {
        cancel_after();  // Cancel pending event
        interrupt_event = NULL;
    }
}
```

**Postconditions**:
- Pending interrupt event removed from Simics event queue
- `fire_interrupt()` will NOT execute

---

### Reset Timeout Event

#### Scheduling Contract

**Trigger**: Interrupt timeout reached (first timeout)

**Calculation**:
```dml
method fire_interrupt() {
    // ... assert interrupt ...
    
    if (WDOGCONTROL.RESEN == 1) {
        // Schedule reset for second timeout
        local cycles_t cycles_to_reset = counter_start_value * step_value;
        after cycles_to_reset cycles: fire_reset();
    }
}
```

**Preconditions**:
- WDOGCONTROL.RESEN = 1 (reset enabled)
- Interrupt event just fired

**Expected Behavior**:
1. Calculate cycles until second timeout (same duration as first)
2. Schedule `fire_reset()` method call
3. Store event handle in `session event_handle_t reset_event`

**Postconditions**:
- Reset event scheduled
- Will execute IF interrupt not cleared before timeout

---

#### Event Cancellation Contract

**Triggers**:
- Interrupt cleared (write to WDOGINTCLR) BEFORE second timeout
- Counter disabled

**Expected Behavior**:
```dml
method cancel_reset_event() {
    if (reset_event != NULL) {
        cancel_after();  // Cancel pending reset
        reset_event = NULL;
        log info, 2: "Reset event canceled - interrupt cleared in time";
    }
}
```

**Postconditions**:
- Pending reset event removed
- `fire_reset()` will NOT execute
- System reset prevented

**Test Verification**:
```python
# Trigger interrupt, then clear before reset
dev.bank.regs.WDOGLOCK.val = 0x1ACCE551
dev.bank.regs.WDOGLOAD.val = 0x20
dev.bank.regs.WDOGCONTROL.val = 0x3  # INTEN=1, RESEN=1

# First timeout
simics.SIM_run_command("run-cycles 32")
assert dev.bank.regs.WDOGRIS.val & 0x1 == 1

# Clear interrupt (cancels reset event)
dev.bank.regs.WDOGINTCLR.val = 0x0

# Run past second timeout
simics.SIM_run_command("run-cycles 32")
assert dev.wdogres_signal.level == 0  # Reset NOT triggered
```

---

## Checkpoint/Restore Interface

### Purpose
Enable simulation checkpoint (save) and restore (load) operations.

### Saved State Variables

**Contract**: Variables marked as `saved` must persist across checkpoint/restore

```dml
bank regs {
    saved cycles_t counter_start_time;      // Checkpoint persistent
    saved uint32 counter_start_value;       // Checkpoint persistent
    saved uint32 step_value;                // Checkpoint persistent
    saved bool interrupt_pending;           // Checkpoint persistent
    saved bool reset_pending;               // Checkpoint persistent
    saved bool lock_state;                  // Checkpoint persistent
    saved bool integration_test_mode;       // Checkpoint persistent
}
```

---

### Checkpoint Save Contract

**Preconditions**:
- Device in any valid state (idle, counting, interrupt pending)
- Events may be scheduled

**Expected Behavior**:
1. DML framework automatically saves all `saved` variables to checkpoint
2. All register values (stored in register fields) automatically saved
3. Event handles (`session` variables) NOT saved (will be rescheduled)

**Postconditions**:
- Checkpoint file contains all device state
- Device continues operating normally (non-destructive operation)

**Test Verification**:
```python
# Setup device in active state
dev.bank.regs.WDOGLOCK.val = 0x1ACCE551
dev.bank.regs.WDOGLOAD.val = 0x1000
dev.bank.regs.WDOGCONTROL.val = 0x1

# Run for some time
simics.SIM_run_command("run-cycles 500")
value_before = dev.bank.regs.WDOGVALUE.val

# Save checkpoint
simics.SIM_run_command("write-configuration checkpoint1.ckpt")

# Continue running
simics.SIM_run_command("run-cycles 100")
assert dev.bank.regs.WDOGVALUE.val != value_before  # State changed
```

---

### Checkpoint Restore Contract

**Preconditions**:
- Valid checkpoint file exists
- Checkpoint created with compatible device version

**Expected Behavior**:
1. DML framework restores all `saved` variables from checkpoint
2. All register values restored to checkpoint state
3. Events rescheduled based on restored state:
   - If counter was running: Calculate remaining cycles, reschedule interrupt event
   - If interrupt pending: Calculate remaining cycles, reschedule reset event

**Event Rescheduling Logic**:
```dml
method post_init() {
    if (WDOGCONTROL.INTEN == 1) {
        // Restore interrupt event
        local cycles_t now = SIM_cycle_count(dev.obj);
        local cycles_t elapsed = now - counter_start_time;
        local cycles_t total_duration = counter_start_value * step_value;
        
        if (elapsed < total_duration) {
            local cycles_t remaining = total_duration - elapsed;
            after remaining cycles: fire_interrupt();
        } else if (interrupt_pending && WDOGCONTROL.RESEN == 1) {
            // Restore reset event
            local cycles_t remaining_to_reset = ...; // Calculate
            after remaining_to_reset cycles: fire_reset();
        }
    }
}
```

**Postconditions**:
- Device state identical to checkpoint save point
- Counter resumes counting from exact checkpoint value
- Interrupt/reset events fire at correct times

**Test Verification**:
```python
# Restore checkpoint from previous test
simics.SIM_run_command("read-configuration checkpoint1.ckpt")

# Verify state restored
assert dev.bank.regs.WDOGVALUE.val == value_before  # Exact restoration

# Verify counter resumes correctly
simics.SIM_run_command("run-cycles 100")
expected_value = value_before - 100  # Assuming step_value=1
assert dev.bank.regs.WDOGVALUE.val == expected_value
```

---

### Checkpoint Compatibility Contract

**Version Compatibility**:
- Device model version recorded in checkpoint
- Restore validates compatible version
- Incompatible versions rejected with error message

**State Consistency**:
- Lock state preserved
- Integration test mode preserved
- Interrupt/reset pending state preserved
- Counter timing precisely restored

---

## Reset Interface (Hard/Soft Reset)

### Hard Reset (System Reset)

**Triggers**:
- System power-on
- External reset signal (prst_n, wrst_n)

**Expected Behavior**:
1. Reset ALL registers to init_val
2. Clear all state variables:
   ```
   counter_start_time = 0
   counter_start_value = 0xFFFFFFFF
   step_value = 1
   interrupt_pending = false
   reset_pending = false
   lock_state = true  // Device starts locked
   integration_test_mode = false
   ```
3. Cancel all pending events
4. Deassert all output signals (wdogint=0, wdogres=0)
5. Log: "Watchdog hard reset"

**Postconditions**:
- Device in initial state (as if freshly instantiated)
- WDOGLOCK = 1 (locked)
- WDOGLOAD = 0xFFFFFFFF
- WDOGCONTROL = 0x00000000
- All other registers at reset values

---

### Soft Reset (Software Reset)

**Triggers**:
- Software writes to reset control register (if implemented)
- Not typically used for watchdog timers

**Expected Behavior**:
- Similar to hard reset, but may preserve certain configuration
- Implementation-specific

---

## Summary of Interface Contracts

| Interface | Purpose | Key Contracts |
|-----------|---------|---------------|
| io_memory | Register access | Address decode, read/write dispatch, lock protection |
| wdogint_signal | Interrupt output | Assert on first timeout, clear on WDOGINTCLR, test mode bypass |
| wdogres_signal | Reset output | Assert on second timeout, prevent via interrupt clear |
| Event scheduling | Timeout events | Cycle-accurate scheduling, cancellation, rescheduling |
| Checkpoint | State persistence | Save/restore all `saved` variables, event rescheduling |
| Hard reset | Initialization | Reset to known state, clear all pending operations |

---

**Document Status**: Complete  
**Next Artifact**: quickstart.md
