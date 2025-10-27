# Side Effects in Simics Device Modeling

**Purpose**: Explain why side effects are critical for Simics device specifications  
**Date**: 2025-01-22  
**Context**: Simics models observable hardware behavior, which is fundamentally about side effects

---

## Key Insight

**Simics models side effects, not just register storage.**

A register in Simics is not just a memory location - it's a **behavioral model** of hardware that produces observable side effects when accessed.

---

## What Are Side Effects?

### **Definition**
Side effects are **observable changes in device state** that occur when software accesses (reads or writes) a register.

### **Examples**

#### **Write Side Effects**
- Writing to CONTROL.ENABLE triggers device initialization
- Writing to DATA register starts a DMA transfer
- Writing to STATUS.ERROR clears the error flag
- Writing to COMMAND register executes a command

#### **Read Side Effects**
- Reading STATUS register clears interrupt pending flag
- Reading DATA register advances FIFO pointer
- Reading COUNTER register captures current timer value
- Reading ERROR register acknowledges error condition

#### **Implicit Side Effects**
- Writing to one register affects another register's value
- Register access triggers state machine transitions
- Register write starts background operations
- Register read has timing implications

---

## Why Side Effects Matter for Simics

### 1. **Simics Models Observable Behavior**

Simics doesn't model the internal hardware implementation - it models what **software can observe**.

**Example: Watchdog Timer**

**Not modeled** (internal implementation):
- Clock divider circuits
- Counter flip-flops
- Reset logic gates

**Modeled** (observable behavior):
- Writing 1 to ENABLE starts countdown (side effect)
- Reading COUNTER returns current value (side effect: captures snapshot)
- COUNTER reaching 0 triggers interrupt (side effect)
- Writing to COUNTER resets timer (side effect)

### 2. **Side Effects Define Device Behavior**

The side effects **are** the device behavior from software's perspective.

**Example: FIFO Register**

```markdown
**DATA Register (0x08)**:
- **Purpose**: FIFO data access
- **Side Effects**:
  * On Write: Pushes data to FIFO, increments write pointer, sets STATUS.FULL if FIFO full
  * On Read: Pops data from FIFO, increments read pointer, clears STATUS.FULL, sets STATUS.EMPTY if FIFO empty
```

Without side effects, this is just a 32-bit storage location. With side effects, it's a FIFO.

### 3. **Side Effects Enable Correct Software Testing**

Software tests verify that side effects occur correctly.

**Example: Device Initialization Test**

```python
# Test expects these side effects:
dev.CONTROL = 0x1  # Write to ENABLE bit

# Expected side effects:
assert dev.STATUS.READY == 1    # Device becomes ready
assert dev.COUNTER == 0          # Counter resets to 0
assert dev.ERROR == 0            # Error flag clears
```

If side effects aren't modeled, tests can't verify correct behavior.

---

## Spec Template: Purpose vs Side Effects

### **Purpose** (What)
Describes **what** the register is for (high-level intent).

**Example**:
```markdown
**Purpose**: Device control and enable flags
```

### **Side Effects** (How)
Describes **how** the register behaves when accessed (observable behavior).

**Example**:
```markdown
**Side Effects**:
- On Write to DEVICE_ENABLE bit:
  * Triggers device initialization sequence
  * Resets COUNTER register to 0
  * Clears STATUS.ERROR flag
  * Sets STATUS.READY flag after initialization completes
- On Read:
  * Returns current enable state
  * No side effects
```

### **Both Are Needed**

- **Purpose**: Helps humans understand the register's role
- **Side Effects**: Tells Simics what to model

---

## Complete Example: Watchdog Timer

### **spec.md** (with side effects)

```markdown
### Hardware Specification

**Register Map**:

| Offset | Name | Size | Access | Reset | Purpose |
|--------|------|------|--------|-------|---------|
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control |
| 0x04 | STATUS | 32-bit | R/O | 0x0001 | Device status |
| 0x08 | TIMEOUT | 32-bit | R/W | 0x0000 | Timeout period |
| 0x0C | COUNTER | 32-bit | R/O | 0x0000 | Current countdown |

**CONTROL Register (0x00)** bit fields:
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupt generation
  * Side effect: When set to 1, enables interrupt generation on timeout
- Bit 0: DEVICE_ENABLE (R/W) - Enable watchdog timer
  * Side effect: 
    - Writing 1: Starts countdown from TIMEOUT value, sets STATUS.READY
    - Writing 0: Stops countdown, clears STATUS.READY

**STATUS Register (0x04)** bit fields:
- Bit 2: TIMEOUT_OCCURRED (R/O) - Timeout event occurred
  * Side effect: Reading STATUS register clears this bit
- Bit 0: READY (R/O) - Device ready and counting
  * Side effect: Automatically set when CONTROL.DEVICE_ENABLE written to 1

**TIMEOUT Register (0x08)** bit fields:
- Bits [31:0]: TIMEOUT_VALUE (R/W) - Timeout period in milliseconds
  * Side effect: Writing new value while device enabled restarts countdown with new value

**COUNTER Register (0x0C)** bit fields:
- Bits [31:0]: COUNTER_VALUE (R/O) - Current countdown value
  * Side effect: Reading captures current countdown value (snapshot)

**Operational Behavior**:
- **Initialization**:
  1. Write timeout value to TIMEOUT register
  2. Write 0x81 to CONTROL (enables device and interrupts)
  3. Side effect: Countdown starts from TIMEOUT value
  
- **Normal Operation**:
  1. Periodically write any value to COUNTER to reset timer ("pet the dog")
  2. Side effect: COUNTER resets to TIMEOUT value, countdown restarts
  
- **Timeout Event**:
  1. When COUNTER reaches 0, STATUS.TIMEOUT_OCCURRED sets to 1
  2. If CONTROL.INTERRUPT_ENABLE is 1, interrupt fires
  3. Side effect: System reset triggered (if configured)
```

### **data-model.md** (DML implementation with side effects)

```markdown
### Register: CONTROL (0x00)

- **Offset**: 0x00
- **Size**: 32-bit
- **Access**: R/W
- **Reset Value**: 0x00000000
- **Purpose**: Device control and enable flags
- **Side Effects**:
  * On Write to DEVICE_ENABLE (bit 0):
    - If value == 1: Start countdown from TIMEOUT value, set STATUS.READY
    - If value == 0: Stop countdown, clear STATUS.READY
  * On Write to INTERRUPT_ENABLE (bit 7):
    - If value == 1: Enable interrupt generation
    - If value == 0: Disable interrupt generation
  * On Read: Returns current register value, no side effects

**DML Implementation Notes**:
```dml
register CONTROL @ 0x00 size 4 {
    field INTERRUPT_ENABLE @ [7] is (simple_storage);
    field DEVICE_ENABLE @ [0] is (simple_storage) {
        method write(uint64 value) {
            default(value);
            if (value == 1) {
                // Side effect: Start countdown
                start_countdown();
                set_status_ready(true);
            } else {
                // Side effect: Stop countdown
                stop_countdown();
                set_status_ready(false);
            }
        }
    }
}
```
```

### Register: STATUS (0x04)

- **Offset**: 0x04
- **Size**: 32-bit
- **Access**: R/O
- **Reset Value**: 0x00000001
- **Purpose**: Device status indicators
- **Side Effects**:
  * On Read: Clears TIMEOUT_OCCURRED bit (bit 2) if set
  * READY bit (bit 0) automatically updated by CONTROL.DEVICE_ENABLE writes

**DML Implementation Notes**:
```dml
register STATUS @ 0x04 size 4 {
    field TIMEOUT_OCCURRED @ [2] is (read_only) {
        method read() -> (uint64) {
            local uint64 value = this.val;
            // Side effect: Clear on read
            this.val = 0;
            return value;
        }
    }
    field READY @ [0] is (read_only);
}
```
```

### Register: COUNTER (0x0C)

- **Offset**: 0x0C
- **Size**: 32-bit
- **Access**: R/O (but writing resets timer)
- **Reset Value**: 0x00000000
- **Purpose**: Current countdown value
- **Side Effects**:
  * On Read: Captures and returns current countdown value (snapshot)
  * On Write (any value): Resets countdown to TIMEOUT value ("pet the dog")

**DML Implementation Notes**:
```dml
register COUNTER @ 0x0C size 4 {
    field COUNTER_VALUE @ [31:0] is (read_only) {
        method read() -> (uint64) {
            // Side effect: Capture current countdown value
            return get_current_countdown();
        }
    }
    
    // Allow writes to reset timer (side effect)
    method write(uint64 value) {
        // Side effect: Reset countdown regardless of written value
        reset_countdown();
    }
}
```
```

---

## Template Updates

### **spec-template.md**

**Before** (purpose only):
```markdown
**CONTROL Register (0x00)** bit fields:
- Bit 0: DEVICE_ENABLE (R/W) - Master enable for device operation
```

**After** (with side effects):
```markdown
**CONTROL Register (0x00)** bit fields:
- Bit 0: DEVICE_ENABLE (R/W) - Master enable for device operation
  * Side effect: Writing 1 triggers device initialization sequence, resets COUNTER to 0, clears STATUS.ERROR
```

### **plan-template.md**

**Before** (purpose only):
```markdown
### Register: CONTROL
- **Purpose**: [copy from spec.md "Purpose" column]
```

**After** (with side effects):
```markdown
### Register: CONTROL
- **Purpose**: [copy from spec.md "Purpose" column]
- **Side Effects**: [copy from spec.md "Operational Behavior" and bit field side effects]
  * On Read: [what happens when software reads this register]
  * On Write: [what happens when software writes this register]
  * State Changes: [what device state changes occur]
  * Other Registers Affected: [which other registers are affected]
```

---

## Side Effect Categories

### 1. **Direct State Changes**
Register write directly changes device state.

**Example**:
```markdown
- Bit 0: ENABLE (R/W)
  * Side effect: Writing 1 enables device, writing 0 disables device
```

### 2. **Triggered Actions**
Register write triggers a sequence of actions.

**Example**:
```markdown
- Bit 0: START (W/O)
  * Side effect: Writing 1 triggers DMA transfer, sets STATUS.BUSY, clears when transfer completes
```

### 3. **Cross-Register Effects**
Register write affects other registers.

**Example**:
```markdown
- Bit 0: RESET (W/O)
  * Side effect: Writing 1 resets COUNTER to 0, clears STATUS.ERROR, sets STATUS.READY
```

### 4. **Read Side Effects**
Register read changes device state.

**Example**:
```markdown
- STATUS Register (R/O)
  * Side effect: Reading clears INTERRUPT_PENDING bit, acknowledges interrupt
```

### 5. **Timing Side Effects**
Register access has timing implications.

**Example**:
```markdown
- DATA Register (R/W)
  * Side effect: Writing starts 10-cycle transfer, STATUS.BUSY set until complete
```

### 6. **Conditional Side Effects**
Side effects depend on current state.

**Example**:
```markdown
- Bit 0: ENABLE (R/W)
  * Side effect: Writing 1 when STATUS.READY==0 triggers initialization; writing 1 when STATUS.READY==1 has no effect
```

---

## Best Practices

### 1. **Document All Observable Side Effects**

✅ **Good**:
```markdown
- Bit 0: ENABLE (R/W)
  * Side effect: Writing 1 starts countdown, sets STATUS.READY, clears STATUS.ERROR
```

❌ **Bad**:
```markdown
- Bit 0: ENABLE (R/W) - Enable device
```

### 2. **Distinguish Read vs Write Side Effects**

✅ **Good**:
```markdown
- STATUS Register (R/O)
  * Side effect on Read: Clears INTERRUPT_PENDING bit
  * Side effect on Write: N/A (read-only)
```

### 3. **Document Cross-Register Effects**

✅ **Good**:
```markdown
- Bit 0: RESET (W/O)
  * Side effect: Resets COUNTER to 0, clears STATUS.ERROR, sets STATUS.READY
  * Affected registers: COUNTER, STATUS
```

### 4. **Document Timing Constraints**

✅ **Good**:
```markdown
- Bit 0: START (W/O)
  * Side effect: Triggers 10-cycle operation, STATUS.BUSY set during operation
  * Timing: Must wait for STATUS.BUSY to clear before next operation
```

### 5. **Document Conditional Behavior**

✅ **Good**:
```markdown
- Bit 0: ENABLE (R/W)
  * Side effect: 
    - If currently disabled: Triggers initialization sequence (20 cycles)
    - If currently enabled: No effect
```

---

## Conclusion

**For Simics device modeling, side effects are more important than purpose because Simics models observable hardware behavior.**

Key takeaways:
1. ✅ Side effects define what Simics models
2. ✅ Purpose explains why (for humans)
3. ✅ Side effects explain how (for implementation)
4. ✅ Document all observable side effects in spec.md
5. ✅ Transform side effects into DML methods in data-model.md

**Updated templates now emphasize side effects throughout the workflow.**
