# Data Model: Simics Watchdog Timer Device

## Summary

The Simics Watchdog Timer device is a 32-bit decrementing counter compatible with ARM PrimeCell specification. It provides configurable timeout periods with interrupt generation on first timeout and system reset on second timeout if the interrupt is not cleared. The device includes lock protection mechanisms and integration test capabilities. The implementation will use lazy evaluation for the counter to maintain performance while ensuring accuracy, with proper handling of interrupts, reset signals, and register access behaviors.

## Registers

*For each register that has side-effect in simics-watchdog-timer-register.xml, extract Purpose and Operations; add offsets, side effects, fields:*

### Register: WDOGLOAD
- **Offset**: 0x00 | **Size**: 32 bits | **Access**: RW from spec.md
- **Reset**: 0xFFFFFFFF | **Purpose**: Watchdog reload value
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns stored reload value | Write: Stores value for reloading counter | State: Updates internal reload value | Affects: Counter reload behavior
- **Fields**: 
  - wdog_load[31:0]: Watchdog decrementing counter reload value

### Register: WDOGVALUE
- **Offset**: 0x04 | **Size**: 32 bits | **Access**: RO from spec.md
- **Reset**: 0xFFFFFFFF | **Purpose**: Current counter value
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns current counter value without changing the counter | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - count_read[31:0]: The current value of watchdog counter

### Register: WDOGCONTROL
- **Offset**: 0x08 | **Size**: 32 bits | **Access**: RW from spec.md
- **Reset**: 0x00 | **Purpose**: Control register for interrupt and reset enables and clock divider
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns current control register value | Write: Updates control bits and may trigger counter reload when INTEN transitions from 0 to 1 | State: Updates interrupt enable, reset enable and clock divider | Affects: Counter behavior, interrupt and reset generation
- **Fields**: 
  - INTEN[0]: Enable interrupt bit (when set to 1 after being previously disabled, reloads counter from WDOGLOAD)
  - RESEN[1]: Enable reset output bit
  - step_value[4:2]: Clock divider (000=÷1, 001=÷2, 010=÷4, 011=÷8, 100=÷16)
  - Reserved[31:5]: Reserved bits

### Register: WDOGINTCLR
- **Offset**: 0x0C | **Size**: 32 bits | **Access**: WO from spec.md
- **Reset**: 0x00 | **Purpose**: Interrupt clear register
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: N/A (write-only) | Write: Clears the interrupt signal (wdogint) and reloads counter from WDOGLOAD register. Any value written will trigger this behavior | State: Clears interrupt pending state | Affects: Interrupt signal, counter value
- **Fields**: 
  - int_clear[31:0]: Write any value to clear interrupt and reload counter

### Register: WDOGRIS
- **Offset**: 0x10 | **Size**: 32 bits | **Access**: RO from spec.md
- **Reset**: 0x00 | **Purpose**: Raw interrupt status register
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns raw interrupt status | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - raw_watchdog_interrupt[0]: Raw interrupt status from the counter
  - reserved[31:1]: Reserved bits

### Register: WDOGMIS
- **Offset**: 0x14 | **Size**: 32 bits | **Access**: RO from spec.md
- **Reset**: 0x00 | **Purpose**: Masked interrupt status register
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns WDOGRIS[0] AND WDOGCONTROL[0] | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - watchdog_interrupt[0]: Enable interrupt status from the counter (WDOGRIS[0] AND WDOGCONTROL[0])
  - reserved[31:1]: Reserved bits

### Register: WDOGLOCK
- **Offset**: 0xC00 | **Size**: 32 bits | **Access**: RW from spec.md
- **Reset**: 0x00000000 | **Purpose**: Lock register
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns lock status (0x0 for unlocked, 0x1 for locked) | Write: Writing 0x1ACCE551 enables write access to other registers; writing any other value disables write access to other registers | State: Updates lock status | Affects: Write access to other registers
- **Fields**: 
  - wdog_lock[31:0]: Enable write access to all other registers by writing 0x1ACCE551. Disable write access by writing any other value

### Register: WDOGITCR
- **Offset**: 0xF00 | **Size**: 32 bits | **Access**: RW from spec.md
- **Reset**: 0x00000000 | **Purpose**: Integration test control register
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns test control register value | Write: Controls entry/exit from integration test mode | State: Updates test mode status | Affects: Direct output control behavior
- **Fields**: 
  - integration_test_mode_enable[0]: Integration test mode enable: 1=enter test mode; 0=normal decrementing mode
  - reserved[31:1]: Reserved bits

### Register: WDOGITOP
- **Offset**: 0xF04 | **Size**: 32 bits | **Access**: WO from spec.md
- **Reset**: 0x00000000 | **Purpose**: Integration test output register
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: N/A (write-only) | Write: In test mode, directly controls wdogint (bit 1) and wdogres (bit 0) outputs | State: Updates test output values | Affects: Direct control of interrupt and reset outputs in test mode
- **Fields**: 
  - integration_test_wdogres_value[0]: Integration test mode WDOGRES value
  - integration_test_wdogint_value[1]: Integration test mode WDOGINT value
  - reserved[31:2]: Reserved bits

### Register: WDOGPERIPHID4
- **Offset**: 0xFD0 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x04 | **Purpose**: Peripheral ID register 4
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns peripheral ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PERIPH_ID4[7:0]: Peripheral ID register 4

### Register: WDOGPERIPHID5
- **Offset**: 0xFD4 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x00 | **Purpose**: Peripheral ID register 5, not used
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns peripheral ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PERIPH_ID5[7:0]: Peripheral ID register 5

### Register: WDOGPERIPHID6
- **Offset**: 0xFD8 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x00 | **Purpose**: Peripheral ID register 6, not used
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns peripheral ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PERIPH_ID6[7:0]: Peripheral ID register 6

### Register: WDOGPERIPHID7
- **Offset**: 0xFDC | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x00 | **Purpose**: Peripheral ID register 7, not used
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns peripheral ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PERIPH_ID7[7:0]: Peripheral ID register 7

### Register: WDOGPERIPHID0
- **Offset**: 0xFE0 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x24 | **Purpose**: Peripheral ID register 0. part number[7:0]
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns peripheral ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PERIPH_ID0[7:0]: Peripheral ID register 0

### Register: WDOGPERIPHID1
- **Offset**: 0xFE4 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0xB8 | **Purpose**: Peripheral ID register 1. [7:4] JEP106_id_3_0; [3:0] part number[11:8]
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns peripheral ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PERIPH_ID1[7:0]: Peripheral ID register 1

### Register: WDOGPERIPHID2
- **Offset**: 0xFE8 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x1B | **Purpose**: Peripheral ID register 2. [7:4] Revision; [3] JEDEC_used; [2:0] JEP106_id_6_4
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns peripheral ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PERIPH_ID2[7:0]: Peripheral ID register 2

### Register: WDOGPERIPHID3
- **Offset**: 0xFEC | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x00 | **Purpose**: Peripheral ID register 3. [7:4] ECO revision number; [3:0] Customer modification number
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns peripheral ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PERIPH_ID3[7:0]: Peripheral ID register 3

### Register: WDOGPCELLID0
- **Offset**: 0xFF0 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x0D | **Purpose**: PrimeCell ID register 0
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns PrimeCell ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PCELL_ID0[7:0]: Component ID register 0

### Register: WDOGPCELLID1
- **Offset**: 0xFF4 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0xF0 | **Purpose**: PrimeCell ID register 1
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns PrimeCell ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PCELL_ID1[7:0]: Component ID register 1

### Register: WDOGPCELLID2
- **Offset**: 0xFF8 | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0x05 | **Purpose**: PrimeCell ID register 2
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns PrimeCell ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PCELL_ID2[7:0]: Component ID register 2

### Register: WDOGPCELLID3
- **Offset**: 0xFFC | **Size**: 8 bits | **Access**: RO from spec.md
- **Reset**: 0xB1 | **Purpose**: PrimeCell ID register 3
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: Returns PrimeCell ID | Write: N/A (read-only) | State: No change | Affects: None
- **Fields**: 
  - WDOG_PCELL_ID3[7:0]: Component ID register 3

## Internal State Variables
*For each internal state variable needed to implement behavior, document here with data type and purpose, transition:*

### Counter State
- **Variable**: `saved cycles_t counter_start_time`
- **Type**: cycles_t (to track when counter was last set/updated)
- **Purpose**: Store the simulation time when counter was last loaded for lazy evaluation
- **Transition**: Updated when counter is reloaded (INTEN enabled, WDOGINTCLR written, etc.)

### Counter Value State
- **Variable**: `saved uint64 counter_start_value`
- **Type**: uint64 (to store the value from which counter decrements)
- **Purpose**: Store the value from which the counter should decrement
- **Transition**: Updated when WDOGLOAD is written or counter is reloaded

### Timer State Variables
- **Variable**: `saved bool timer_enabled`
- **Type**: bool
- **Purpose**: Track if timer is currently enabled (INTEN bit in WDOGCONTROL)
- **Transition**: Updated based on WDOGCONTROL.INTEN bit

- **Variable**: `saved bool interrupt_pending`
- **Type**: bool
- **Purpose**: Track if interrupt is pending (counter reached zero with INTEN=1)
- **Transition**: Set when counter reaches zero with INTEN=1, cleared by WDOGINTCLR or INTEN=0

- **Variable**: `saved bool reset_pending`
- **Type**: bool
- **Purpose**: Track if reset is pending (second timeout with RESEN=1 and interrupt pending)
- **Transition**: Set when counter reaches zero again with RESEN=1 and interrupt pending

### Lock State
- **Variable**: `saved bool locked`
- **Type**: bool
- **Purpose**: Track if registers are locked for write access
- **Transition**: Updated based on WDOGLOCK register value

### Test Mode State
- **Variable**: `saved bool test_mode`
- **Type**: bool
- **Purpose**: Track if in integration test mode
- **Transition**: Updated based on WDOGITCR[0] bit

## Interfaces
*For each interface defined in [device-name]-interfaces.xml and spec.md, extract Methods and Purpose:*

### Interface: signal (for wdogint)
- **Methods**: signal_raise(), signal_lower()
- **Purpose**: Output interface for watchdog interrupt signal
- **Implementation**: Connect for wdogint output signal

### Interface: signal (for wdogres)
- **Methods**: signal_raise(), signal_lower()
- **Purpose**: Output interface for watchdog reset signal
- **Implementation**: Connect for wdogres output signal

### Interface: io_memory
- **Methods**: read_write(), read(), write()
- **Purpose**: Memory-mapped register access via APB bus
- **Implementation**: Bank for register access

## DML Implementation Notes
*Document DML-specific implementation notes for registers, interfaces, state variables, side-effects, access semantics, etc.*

- The main counter will use lazy evaluation to avoid per-cycle overhead: calculate current value based on elapsed time from last reset/load instead of decrementing every cycle
- Register side effects must be carefully implemented using custom read/write methods where specified in the specification
- The lock mechanism will require custom write/read logic to prevent unauthorized register access
- The interrupt and reset outputs need to be implemented as signal interfaces
- Integration test mode will require conditional behavior based on test mode register
- All primecell and peripheral ID registers are read-only and return constant values
- Clock enable (wclk_en) needs to be factored into timing calculations
- Reset handling (wrst_n and prst_n) must properly reset all registers and internal state

## Implementation Patterns
*Patterns gathered via RAG queries to inform implementation approach*

### Pattern: Lazy Counter Evaluation
**Applicable To**: WDOGVALUE register, counter functionality
**Source**: DML Device Development Best Practices
**Key Approach**:
- Store start time and counter value
- Calculate current value on demand based on elapsed time
- Use saved variables for checkpoint compatibility
- Schedule timeout events using after statements

**Example Structure** (conceptual, not full implementation):
```dml
// Conceptual pattern showing structure only
register counter_reg {
    saved cycles_t start_time;
    saved uint64 start_value;
    
    method get_current_value() -> (uint64) {
        if (!timer_enabled.val) {
            return start_value;
        }
        
        local cycles_t now = SIM_cycle_count(dev.obj);
        local cycles_t elapsed = now - start_time;
        local uint64 prescaler = get_prescaler();
        local uint64 current = start_value - elapsed / prescaler;
        
        if (current > start_value) {  // Counter reached zero
            return 0;
        }
        return current;
    }
}
```

**Common Pitfalls**:
- Forgetting to account for prescaler in calculations
- Not handling counter wrap correctly when it reaches zero
- Not checking for enabled state when returning counter value

**References**:
- `.specify/memory/DML_Device_Development_Best Practices.md`: Lazy Counter Evaluation section

### Pattern: Register Lock Protection
**Applicable To**: WDOGLOCK register, write access control
**Source**: DML Device Development Best Practices and research
**Key Approach**:
- Store lock state in a saved variable
- Check lock status before allowing register writes
- Only WDOGLOCK register is writable when locked
- Magic number check for unlocking (0x1ACCE551)

**Example Structure** (conceptual, not full implementation):
```dml
// Conceptual pattern showing structure only
method is_write_allowed() -> (bool) {
    return !lock_enabled.val || lock_magic_unlocked.val;
}

register protected_reg {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        if (!is_write_allowed()) {
            log warning: "Write to register blocked due to lock";
            return;  // Ignore the write
        }
        default(value, enabled_bytes, aux);
    }
}
```

**Common Pitfalls**:
- Forgetting to allow writes to WDOGLOCK register even when locked
- Not handling partial writes correctly
- Not maintaining lock state properly during checkpoint/restore

**References**:
- `.specify/memory/DML_Device_Development_Best Practices.md`: Security and Protection section

### Pattern: Interrupt and Reset State Management
**Applicable To**: WDOGRIS, WDOGMIS, WDOGINTCLR registers and signal outputs
**Source**: DML Device Development Best Practices and research
**Key Approach**:
- Maintain internal state for interrupt pending and reset pending
- Update status registers based on internal state
- Implement proper signal interface handling
- Clear interrupt state on write to WDOGINTCLR

**Example Structure** (conceptual, not full implementation):
```dml
// Conceptual pattern showing structure only
saved bool interrupt_pending;

method update_interrupt_state() {
    raw_interrupt_status.val = interrupt_pending ? 1 : 0;
    masked_interrupt_status.val = interrupt_pending && inten_enabled ? 1 : 0;
    
    if (interrupt_enabled && interrupt_pending) {
        if (irq_connect.obj) {
            irq_connect.signal.signal_raise();
        }
    }
}

method clear_interrupt() {
    interrupt_pending = false;
    update_interrupt_state();
    if (irq_connect.obj) {
        irq_connect.signal.signal_lower();
    }
}
```

**Common Pitfalls**:
- Not properly handling the relationship between raw and masked interrupt status
- Forgetting to lower signal when clearing interrupt
- Not handling the sequence where interrupt is pending and counter reaches zero again

**References**:
- `.specify/memory/DML_Device_Development_Best Practices.md`: Signal Interface section

**Note**: Detailed implementations will be developed in tasks phase with additional RAG queries.