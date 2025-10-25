# Data Model: Watchdog Timer Device

## Device State Variables

### Timer State (Saved for Checkpointing)
```dml
saved cycles_t counter_start_time;      // Cycle count when counter was loaded
saved uint32 counter_start_value;       // Initial value loaded into counter
saved bool interrupt_posted;            // Interrupt event is scheduled
saved bool reset_posted;                // Reset event is scheduled
saved bool locked;                      // Lock state (true = registers protected)
saved bool integration_test_mode;       // Integration test mode enabled
```

### Derived State (Computed)
- **Current Counter Value**: Calculated from `counter_start_time`, `counter_start_value`, and current cycle count
- **Timeout Cycles**: Calculated from counter value and clock divider setting
- **Clock Divider**: Extracted from `WDOGCONTROL` register bits [1:0]

## Register Bank Structure

### Bank Configuration
```dml
bank regs {
    param register_size = 4;              // All registers are 32-bit
    param byte_order = "little-endian";   // ARM standard
    param use_io_memory = true;           // Memory-mapped device
    param overlapping = false;            // No overlapping registers
    param partial = true;                 // Allow partial access
}
```

## Register Definitions

### Core Timer Registers

#### WDOGLOAD (0x000)
**Offset**: 0x000  
**Size**: 32 bits  
**Access**: Read/Write  
**Reset Value**: 0xFFFFFFFF  
**Description**: Counter reload value register

**Behavior**:
- Write: Loads value into counter and restarts countdown
- Read: Returns the last written load value
- Side Effects: Cancels pending timeout events, recalculates and schedules new timeout

**DML Structure**:
```dml
register WDOGLOAD @ 0x000 "Counter load register" {
    param init_val = 0xFFFFFFFF;
    field value @ [31:0] "32-bit counter load value";
    
    method write(uint64 val) {
        if (!locked) {
            counter_start_value = val;
            counter_start_time = SIM_cycle_count(dev.obj);
            cancel_timeout_events();
            schedule_timeout_event();
        }
    }
}
```

#### WDOGVALUE (0x004)
**Offset**: 0x004  
**Size**: 32 bits  
**Access**: Read-only  
**Reset Value**: 0xFFFFFFFF  
**Description**: Current counter value (decrementing)

**Behavior**:
- Read: Returns current counter value calculated from elapsed cycles
- Write: Ignored (read-only register)

**DML Structure**:
```dml
register WDOGVALUE @ 0x004 is read_only "Current counter value" {
    method get() -> (uint64) {
        if (clock_divider == 0) {
            return counter_start_value;  // Counter stopped
        }
        local cycles_t now = SIM_cycle_count(dev.obj);
        local cycles_t elapsed = (now - counter_start_time) / divider_value;
        if (elapsed >= counter_start_value) {
            return 0;
        }
        return counter_start_value - elapsed;
    }
}
```

#### WDOGCONTROL (0x008)
**Offset**: 0x008  
**Size**: 32 bits  
**Access**: Read/Write  
**Reset Value**: 0x00000000  
**Description**: Control register for interrupt enable and clock divider

**Bit Fields**:
- [31:2]: Reserved (read as zero, write ignored)
- [1]: INTEN (Interrupt Enable)
  - 0 = Interrupt disabled (default)
  - 1 = Interrupt enabled on first timeout
- [0]: RESEN (Reset Enable)
  - 0 = Reset disabled (default)
  - 1 = Reset enabled on second timeout

**Behavior**:
- Protected by lock register
- Changes take effect immediately for next timeout

**DML Structure**:
```dml
register WDOGCONTROL @ 0x008 "Control register" {
    param init_val = 0x00000000;
    field RESEN @ [0] "Reset enable";
    field INTEN @ [1] "Interrupt enable";
    field reserved @ [31:2] is (read_zero, write_ignore);
    
    method write(uint64 val) {
        if (!locked) {
            default(val);
            update_timeout_behavior();
        }
    }
}
```

#### WDOGINTCLR (0x00C)
**Offset**: 0x00C  
**Size**: 32 bits  
**Access**: Write-only  
**Reset Value**: N/A  
**Description**: Interrupt clear register

**Behavior**:
- Write any value: Clears interrupt flag and cancels pending reset event
- Read: Returns undefined value (typically zero)
- Side Effects: Deasserts interrupt signal, cancels second timeout

**DML Structure**:
```dml
register WDOGINTCLR @ 0x00C is write_only "Interrupt clear" {
    method write(uint64 val) {
        // Any write clears interrupt
        clear_interrupt();
        cancel_reset_event();
        interrupt_posted = false;
    }
    
    method get() -> (uint64) {
        return 0;  // Undefined for write-only register
    }
}
```

#### WDOGRIS (0x010)
**Offset**: 0x010  
**Size**: 32 bits  
**Access**: Read-only  
**Reset Value**: 0x00000000  
**Description**: Raw interrupt status (not affected by INTEN)

**Bit Fields**:
- [31:1]: Reserved (read as zero)
- [0]: WDOGRIS
  - 0 = No interrupt pending
  - 1 = Interrupt condition occurred (first timeout reached)

**Behavior**:
- Shows raw interrupt status regardless of enable bit
- Cleared by writing to WDOGINTCLR

**DML Structure**:
```dml
register WDOGRIS @ 0x010 is read_only "Raw interrupt status" {
    method get() -> (uint64) {
        return interrupt_posted ? 1 : 0;
    }
}
```

#### WDOGMIS (0x014)
**Offset**: 0x014  
**Size**: 32 bits  
**Access**: Read-only  
**Reset Value**: 0x00000000  
**Description**: Masked interrupt status (WDOGRIS AND INTEN)

**Bit Fields**:
- [31:1]: Reserved (read as zero)
- [0]: WDOGMIS
  - 0 = No enabled interrupt pending
  - 1 = Enabled interrupt pending (first timeout and INTEN=1)

**Behavior**:
- Shows interrupt status after masking with enable bit
- Used to determine if interrupt should be signaled to CPU

**DML Structure**:
```dml
register WDOGMIS @ 0x014 is read_only "Masked interrupt status" {
    method get() -> (uint64) {
        return (interrupt_posted && WDOGCONTROL.INTEN.val) ? 1 : 0;
    }
}
```

### Lock Register

#### WDOGLOCK (0xC00)
**Offset**: 0xC00  
**Size**: 32 bits  
**Access**: Read/Write  
**Reset Value**: 0x00000000 (unlocked)  
**Magic Value**: 0x1ACCE551 (to unlock)  
**Description**: Register write protection control

**Behavior**:
- Write 0x1ACCE551: Unlocks register access (sets locked = false)
- Write any other value: Locks register access (sets locked = true)
- Read:
  - Returns 0x00000001 if locked
  - Returns 0x00000000 if unlocked

**Protected Registers**: WDOGLOAD, WDOGCONTROL

**DML Structure**:
```dml
register WDOGLOCK @ 0xC00 "Lock register" {
    param init_val = 0x00000000;
    
    method write(uint64 val) {
        if (val == 0x1ACCE551) {
            locked = false;
        } else {
            locked = true;
        }
    }
    
    method get() -> (uint64) {
        return locked ? 0x00000001 : 0x00000000;
    }
}
```

### Integration Test Registers

#### WDOGITCR (0xF00)
**Offset**: 0xF00  
**Size**: 32 bits  
**Access**: Read/Write  
**Reset Value**: 0x00000000  
**Description**: Integration test control register

**Bit Fields**:
- [31:1]: Reserved (read as zero, write ignored)
- [0]: ITCR_ENABLE
  - 0 = Normal operation (default)
  - 1 = Integration test mode (direct control of outputs)

**Behavior**:
- When enabled, interrupt and reset signals controlled by WDOGITOP
- Timeout events are ignored in test mode

**DML Structure**:
```dml
register WDOGITCR @ 0xF00 "Integration test control" {
    param init_val = 0x00000000;
    field ITCR_ENABLE @ [0] "Integration test enable";
    field reserved @ [31:1] is (read_zero, write_ignore);
    
    method write(uint64 val) {
        default(val);
        integration_test_mode = (ITCR_ENABLE.val != 0);
    }
}
```

#### WDOGITOP (0xF04)
**Offset**: 0xF04  
**Size**: 32 bits  
**Access**: Read/Write  
**Reset Value**: 0x00000000  
**Description**: Integration test output set register

**Bit Fields**:
- [31:2]: Reserved (read as zero, write ignored)
- [1]: WDOGRES_SET (Reset output test value)
- [0]: WDOGINT_SET (Interrupt output test value)

**Behavior**:
- Only effective when WDOGITCR.ITCR_ENABLE = 1
- Directly controls interrupt and reset signal levels
- Read returns last written values

**DML Structure**:
```dml
register WDOGITOP @ 0xF04 "Integration test output" {
    param init_val = 0x00000000;
    field WDOGINT_SET @ [0] "Interrupt test output";
    field WDOGRES_SET @ [1] "Reset test output";
    field reserved @ [31:2] is (read_zero, write_ignore);
    
    method write(uint64 val) {
        default(val);
        if (integration_test_mode) {
            update_test_outputs();
        }
    }
}
```

### Peripheral Identification Registers (Read-Only)

#### WDOGPeriphID0-3 (0xFE0-0xFEC)
**Offsets**: 0xFE0, 0xFE4, 0xFE8, 0xFEC  
**Size**: 32 bits each  
**Access**: Read-only  
**Description**: Peripheral identification registers

**Reset Values**:
- WDOGPeriphID0 (0xFE0): 0x00000024 (Part number [7:0])
- WDOGPeriphID1 (0xFE4): 0x000000B8 (Part number [11:8] and Designer [3:0])
- WDOGPeriphID2 (0xFE8): 0x0000001B (Designer [7:4] and Revision [3:0])
- WDOGPeriphID3 (0xFEC): 0x00000000 (Configuration)

**Peripheral ID**: 0x1B8024 (matches ARM SP805 watchdog)

**DML Structure**:
```dml
register WDOGPeriphID0 @ 0xFE0 is read_constant "Peripheral ID 0" {
    param val = 0x24;
}

register WDOGPeriphID1 @ 0xFE4 is read_constant "Peripheral ID 1" {
    param val = 0xB8;
}

register WDOGPeriphID2 @ 0xFE8 is read_constant "Peripheral ID 2" {
    param val = 0x1B;
}

register WDOGPeriphID3 @ 0xFEC is read_constant "Peripheral ID 3" {
    param val = 0x00;
}
```

#### WDOGPCellID0-3 (0xFF0-0xFFC)
**Offsets**: 0xFF0, 0xFF4, 0xFF8, 0xFFC  
**Size**: 32 bits each  
**Access**: Read-only  
**Description**: PrimeCell identification registers

**Reset Values**:
- WDOGPCellID0 (0xFF0): 0x0000000D
- WDOGPCellID1 (0xFF4): 0x000000F0
- WDOGPCellID2 (0xFF8): 0x00000005
- WDOGPCellID3 (0xFFC): 0x000000B1

**PrimeCell ID**: 0xB105F00D (standard ARM identification)

**DML Structure**:
```dml
register WDOGPCellID0 @ 0xFF0 is read_constant "PrimeCell ID 0" {
    param val = 0x0D;
}

register WDOGPCellID1 @ 0xFF4 is read_constant "PrimeCell ID 1" {
    param val = 0xF0;
}

register WDOGPCellID2 @ 0xFF8 is read_constant "PrimeCell ID 2" {
    param val = 0x05;
}

register WDOGPCellID3 @ 0xFFC is read_constant "PrimeCell ID 3" {
    param val = 0xB1;
}
```

## Register Access Summary Table

| Offset | Name | Size | Access | Reset Value | Lock Protected |
|--------|------|------|--------|-------------|----------------|
| 0x000 | WDOGLOAD | 32 | R/W | 0xFFFFFFFF | Yes |
| 0x004 | WDOGVALUE | 32 | RO | 0xFFFFFFFF | No |
| 0x008 | WDOGCONTROL | 32 | R/W | 0x00000000 | Yes |
| 0x00C | WDOGINTCLR | 32 | WO | N/A | No |
| 0x010 | WDOGRIS | 32 | RO | 0x00000000 | No |
| 0x014 | WDOGMIS | 32 | RO | 0x00000000 | No |
| 0xC00 | WDOGLOCK | 32 | R/W | 0x00000000 | No |
| 0xF00 | WDOGITCR | 32 | R/W | 0x00000000 | No |
| 0xF04 | WDOGITOP | 32 | R/W | 0x00000000 | No |
| 0xFE0 | WDOGPeriphID0 | 32 | RO | 0x00000024 | No |
| 0xFE4 | WDOGPeriphID1 | 32 | RO | 0x000000B8 | No |
| 0xFE8 | WDOGPeriphID2 | 32 | RO | 0x0000001B | No |
| 0xFEC | WDOGPeriphID3 | 32 | RO | 0x00000000 | No |
| 0xFF0 | WDOGPCellID0 | 32 | RO | 0x0000000D | No |
| 0xFF4 | WDOGPCellID1 | 32 | RO | 0x000000F0 | No |
| 0xFF8 | WDOGPCellID2 | 32 | RO | 0x00000005 | No |
| 0xFFC | WDOGPCellID3 | 32 | RO | 0x000000B1 | No |

**Note**: Reserved register space (0x018-0xBFF, 0xC04-0xEFF, 0xF08-0xFDF) returns zero on read and ignores writes.

## Clock Divider Mapping

The clock divider is encoded in WDOGCONTROL bits [1:0]:

| Bits [1:0] | Divider Value | Counter Decrement Rate |
|------------|---------------|------------------------|
| 00 | 1 | Every cycle |
| 01 | 16 | Every 16 cycles |
| 10 | 256 | Every 256 cycles |
| 11 | Reserved | Treated as divider=1 |

**Note**: Hardware spec shows 5 divider options (÷1, ÷2, ÷4, ÷8, ÷16), but ARM SP805 standard uses power-of-16 values. Implementation follows ARM standard for compatibility.

## Signal Interfaces

### Interrupt Signal
**Interface**: `signal_connect`  
**Name**: `irq_dev`  
**Direction**: Output  
**Behavior**:
- Asserted (set_level(1)) when first timeout occurs and INTEN=1
- Deasserted (set_level(0)) immediately after assertion (edge-triggered)
- Controlled by WDOGITOP.WDOGINT_SET in integration test mode

### Reset Signal
**Interface**: `signal_connect`  
**Name**: `rst_dev`  
**Direction**: Output  
**Behavior**:
- Asserted (set_level(1)) when second timeout occurs and RESEN=1
- Remains asserted until device reset
- Controlled by WDOGITOP.WDOGRES_SET in integration test mode

## Event Objects

### First Timeout Event
```dml
event first_timeout {
    param timebase = "cycles";
    
    method event(void *param) {
        interrupt_posted = true;
        if (WDOGCONTROL.INTEN.val) {
            irq_dev.set_level(1);
            irq_dev.set_level(0);  // Edge trigger
        }
        if (WDOGCONTROL.RESEN.val) {
            schedule_second_timeout();
        }
    }
}
```

### Second Timeout Event
```dml
event second_timeout {
    param timebase = "cycles";
    
    method event(void *param) {
        reset_posted = true;
        if (WDOGCONTROL.RESEN.val) {
            rst_dev.set_level(1);
        }
    }
}
```

## Memory Map

```
0x0000 +---------------------------+
       | WDOGLOAD                  |
0x0004 +---------------------------+
       | WDOGVALUE                 |
0x0008 +---------------------------+
       | WDOGCONTROL               |
0x000C +---------------------------+
       | WDOGINTCLR                |
0x0010 +---------------------------+
       | WDOGRIS                   |
0x0014 +---------------------------+
       | WDOGMIS                   |
0x0018 +---------------------------+
       |                           |
       | Reserved (RAZ/WI)         |
       |                           |
0x0C00 +---------------------------+
       | WDOGLOCK                  |
0x0C04 +---------------------------+
       |                           |
       | Reserved (RAZ/WI)         |
       |                           |
0x0F00 +---------------------------+
       | WDOGITCR                  |
0x0F04 +---------------------------+
       | WDOGITOP                  |
0x0F08 +---------------------------+
       |                           |
       | Reserved (RAZ/WI)         |
       |                           |
0x0FE0 +---------------------------+
       | WDOGPeriphID0             |
0x0FE4 +---------------------------+
       | WDOGPeriphID1             |
0x0FE8 +---------------------------+
       | WDOGPeriphID2             |
0x0FEC +---------------------------+
       | WDOGPeriphID3             |
0x0FF0 +---------------------------+
       | WDOGPCellID0              |
0x0FF4 +---------------------------+
       | WDOGPCellID1              |
0x0FF8 +---------------------------+
       | WDOGPCellID2              |
0x0FFC +---------------------------+
       | WDOGPCellID3              |
0x1000 +---------------------------+
```

**Legend**:
- RAZ/WI: Read As Zero / Write Ignore
- R/W: Read/Write
- RO: Read Only
- WO: Write Only

## State Transitions

### Normal Operation Mode
```
IDLE (counter loaded)
  ↓ (cycles elapse)
COUNTING (counter decrements)
  ↓ (counter reaches 0)
FIRST_TIMEOUT (interrupt asserted if INTEN=1)
  ↓ (interrupt cleared via WDOGINTCLR)
IDLE
  OR
  ↓ (interrupt not cleared, counter reaches 0 again)
SECOND_TIMEOUT (reset asserted if RESEN=1)
  ↓ (system reset)
RESET
```

### Integration Test Mode
```
NORMAL_MODE
  ↓ (WDOGITCR.ITCR_ENABLE = 1)
TEST_MODE (outputs controlled by WDOGITOP)
  ↓ (WDOGITCR.ITCR_ENABLE = 0)
NORMAL_MODE
```

## Checkpoint State

Variables saved across checkpoint/restore:
- `counter_start_time` (cycles_t)
- `counter_start_value` (uint32)
- `interrupt_posted` (bool)
- `reset_posted` (bool)
- `locked` (bool)
- `integration_test_mode` (bool)
- All register values (automatic via DML)

Derived state recalculated on restore:
- Current counter value (from saved start time/value)
- Pending event times (events rescheduled based on counter state)
