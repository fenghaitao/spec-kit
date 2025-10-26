# Research Document: Simics Watchdog Timer Device Implementation

**Branch**: `001-create-a-comprehensive`
**Phase**: Phase 0 - Research
**Created**: 2025
**Status**: Complete

---

## Table of Contents

1. [MCP Tool Discovery Results](#mcp-tool-discovery-results)
2. [RAG Query Results](#rag-query-results)
3. [Architecture Decisions](#architecture-decisions)
4. [Implementation Strategy](#implementation-strategy)
5. [References](#references)

---

## MCP Tool Discovery Results

### 1. Simics Version Information

**Tool**: `get_simics_version()`

| Property | Value |
|----------|-------|
| Package Name | Simics-Base |
| Package Number | 1000 |
| Package Version | 7.57.0 |

**Decision Impact**: Target DML 1.4 syntax compatible with Simics 7.57.0. All API calls and features must be supported in this version.

---

### 2. Installed Packages

**Tool**: `list_installed_packages()`

| Package Name | Package Number | Version |
|-------------|---------------|---------|
| Simics-Base | 1000 | 7.57.0 |
| QSP-x86 | 2096 | 7.38.0 |
| Simics-Python | 1029 | 7.13.0 |
| GDB-Remote | 1027 | 7.9.0 |
| RISC-V-CPU | 8112 | 7.21.0 |
| SystemC-Library | 1031 | 7.17.0 |
| Crypto-Engine | 8133 | 7.14.0 |
| Eclipse-Support | 1025 | 7.6.0 |
| Ethernet-Link | 1002 | 7.13.0 |
| Model-Builder | 1003 | 7.44.0 |
| QSP-CPU | 2095 | 7.35.0 |
| QSP-Modern-Core | 2097 | 7.14.0 |

**Decision Impact**: 
- QSP-x86 7.38.0 available for integration testing
- Simics-Python 7.13.0 confirms Python test framework availability
- Model-Builder 7.44.0 supports full DML 1.4 device development workflow

---

### 3. Available Platforms

**Tool**: `list_simics_platforms()`

| Platform ID | Description |
|-------------|-------------|
| qsp-x86-public-7 | Public Intel® Simics® Quick Start Platform (QSP-x86) - 7 |

**Decision Impact**: Watchdog timer device will be developed for integration with QSP-x86 platform. Test scripts will target this platform configuration.

---

## RAG Query Results

### RAG Query #1: DML 1.4 Reference Manual - Register and Device Modeling

**Query**: "DML 1.4 reference manual register and device modeling"  
**Source Type**: docs  
**Results Count**: 5

**Key Findings**:

1. **DML 1.4 Syntax Differences from 1.2**:
   - Register arrays use `[i < size]` instead of `[i in 0..size-1]`
   - Field bit ranges use `@ [bits]` instead of `[bits]`
   - Return values must be explicit: `method get() -> (uint64)` instead of implicit returns
   - Session vs saved variables: `session` for non-checkpointed, `saved` for checkpointed state

2. **Register Definition Pattern**:
```dml
register r[i < 20] size 4 @ 0x0000 + i * 4 is read_register {
    field f @ [7:0];
}
```

3. **Bank Organization**:
   - `bank regs { param register_size = 4; param byte_order = "little-endian"; }`
   - Bank parameters: `register_size`, `byte_order`, `partial`, `overlapping`, `mappable`

**Architectural Decision**: Use DML 1.4 syntax throughout. Organize all 21 watchdog registers within a single `bank regs` at base offset 0x0000.

---

### RAG Query #2: Model Builder Device Creation Patterns

**Query**: "Simics Model Builder device creation and structure patterns"  
**Source Type**: docs  
**Results Count**: 5

**Key Findings**:

1. **Universal Device Templates**:
   - `init`: Device initialization (called once at object creation)
   - `post_init`: Post-initialization (called after all attributes set)
   - `destroy`: Cleanup before device deletion

2. **Device Lifecycle Methods**:
```dml
method init() {
    // Initialize device state
}

method post_init() {
    // Schedule initial events if needed
}
```

3. **Template Inheritance**:
   - Templates inherit `object`, `desc`, `documentation` parameters
   - Use `is` keyword for template application: `register r is (read, write)`

**Architectural Decision**: Implement `init()` to initialize counter state variables, `post_init()` to schedule initial countdown event if watchdog is enabled.

---

### RAG Query #3: DML Device Template Base Structure

**Query**: "DML device template base structure and skeleton"  
**Source Type**: dml  
**Results Count**: 3

**Key Findings**:

1. **Minimal Device Structure**:
```dml
dml 1.4;
device watchdog_timer;
param classname = "watchdog-timer";
param desc = "ARM PrimeCell SP805 Watchdog Timer";
param documentation = "Watchdog timer device with interrupt and reset generation";

import "utility.dml";
import "simics/devs/signal.dml";
```

2. **Standard Imports**:
   - `utility.dml`: Core DML utility functions
   - `simics/devs/signal.dml`: Signal interface for interrupt/reset outputs
   - `simics/base/types.dml`: Basic type definitions

**Architectural Decision**: Start with minimal device skeleton, add signal connections for `wdogint` and `wdogres` outputs.

---

### RAG Query #4: Watchdog Timer Best Practices

**Query**: "Best practices for watchdog timer device modeling with Simics DML 1.4"  
**Source Type**: source  
**Results Count**: 5

**Key Code Example - sample_timer_device.dml**:

```dml
dml 1.4;
device sample_timer_device;
import "utility.dml";
import "simics/devs/signal.dml";

connect irq_dev is signal_connect {
    param documentation = "Device an interrupt should be forwarded to (interrupt controller)";
}

bank regs {
    param register_size = 2;
    param byte_order = "big-endian";
    saved cycles_t counter_start_time;
    saved cycles_t counter_start_value;
    
    register counter @ 0x0 "Counter register";
    register reference @ 0x2 "Reference counter register";
    register step @ 0x4 "Counter is incremented every STEP clock cycles. 0 means stopped.";
    register config @ 0x6 "Configuration register" {
        field clear_on_match @ [1];
        field interrupt_enable @ [0];
    }
}

bank regs {
    register counter is (get, read, write) {
        method write(uint64 value) {
            counter_start_value = value;
            restart();
        }
        method get() -> (uint64) {
            if (step.val == 0) return counter_start_value;
            local cycles_t now = SIM_cycle_count(dev.obj);
            return (now - counter_start_time) / step.val + counter_start_value;
        }
        method restart() {
            counter_start_time = SIM_cycle_count(dev.obj);
            update_event();
        }
        method on_match() {
            log info, 4: "Counter matches reference";
            if (regs.config.clear_on_match.val) {
                regs.counter.write(0);
            }
            if (regs.config.interrupt_enable.val) {
                log info, 4: "Raising interrupt";
                irq_dev.set_level(1);
                irq_dev.set_level(0);
            }
        }
        method update_event() {
            cancel_after();
            if (step.val == 0) return;
            local cycles_t now = SIM_cycle_count(dev.obj);
            local cycles_t cycles_left = (reference.val - counter_start_value) * step.val - (now - counter_start_time);
            after cycles_left cycles: on_match();
        }
    }
}
```

**Critical Patterns Identified**:

1. **Cycle-Based Timing**: Use `SIM_cycle_count(dev.obj)` to track elapsed cycles
2. **Event Scheduling**: Use `after cycles_left cycles: on_match();` to schedule timeout events
3. **Event Cancellation**: Use `cancel_after();` to cancel pending events when counter is modified
4. **Saved State**: Mark timing variables as `saved cycles_t` for checkpoint persistence
5. **Interrupt Generation**: Use `signal_connect` with `set_level(1); set_level(0);` for pulse interrupts

**Architectural Decision**: 
- Adapt sample_timer_device pattern for watchdog timer
- Implement `counter_start_time` and `counter_start_value` as saved variables
- Use `after` events for countdown timeout scheduling
- Implement separate events for first timeout (interrupt) and second timeout (reset)

---

### RAG Query #5: Device Implementation Examples

**Query**: "Simics device implementation example watchdog timer or similar peripheral"  
**Source Type**: source  
**Results Count**: 5

**Relevant Examples**:
- **sample_timer_device.dml**: Counter with match event (highest relevance)
- **HPET (High Precision Event Timer)**: Multiple timers with comparators
- **DS323x RTC**: Real-time clock with alarm interrupts
- **ich-rtc**: Legacy PC RTC with periodic interrupts

**Key Pattern from HPET**:
```dml
method schedule_next_interrupt() {
    if (!enabled) return;
    local cycles_t cycles_to_interrupt = calculate_cycles();
    after cycles_to_interrupt cycles: fire_interrupt();
}

method fire_interrupt() {
    interrupt_status = 1;
    if (interrupt_enabled) {
        irq_out.raise();
    }
    if (periodic_mode) {
        schedule_next_interrupt();
    }
}
```

**Architectural Decision**: Implement two-stage timeout mechanism:
1. First timeout schedules interrupt event
2. If interrupt not cleared, second timeout schedules reset event
3. Both use `after` event scheduling with saved state for checkpoints

---

### RAG Query #6: Register Bank Implementation Patterns

**Query**: "DML register bank implementation patterns"  
**Source Type**: dml  
**Results Count**: 5

**Key Bank Template Features**:

1. **Address Calculation**:
```dml
bank regs {
    param register_size = 4;
    param byte_order = "little-endian";
    
    // Automatic address calculation
    register r1 @ 0x000 size 4;
    register r2 @ 0x004 size 4;
    register r3 @ 0x008 size 4;
}
```

2. **Register Views**:
   - `_get_register()`: Find register at offset
   - `_num_registers()`: Total register count
   - `_intersect()`: Check address overlap

3. **Transaction Handling**:
   - `io_memory` interface: Automatic transaction dispatch to registers
   - `read_access()`, `write_access()`: Per-register access control

**Architectural Decision**: 
- Single `bank regs` with all 21 watchdog registers
- Base address 0x000, 4KB address space (0x000-0xFFF)
- Use `param register_size = 4` for 32-bit registers
- Let bank template handle transaction dispatch

---

### RAG Query #7: Python Test Patterns

**Query**: "Simics Python test patterns and examples"  
**Source Type**: python  
**Results Count**: 5

**Key Test Pattern - s-toggle-i2c.py**:

```python
import stest
import pyobj
import dev_util
import conf
import simics

## Create objects
def create_python_simple_serial():
    py_dev = simics.pre_conf_object('pyart', 'python_simple_serial')
    phys_mem = simics.pre_conf_object('phys_mem', 'memory-space')
    phys_mem.attr.map = [ [0x0000, py_dev, 0, 0, 0x10] ]

    ## A clock
    clock = simics.pre_conf_object(
        'clock',
        'clock',
        freq_mhz=1000)
    py_dev.attr.queue = clock

    ## Add objects
    simics.SIM_add_configuration([clock, py_dev, phys_mem], None)

    ## Return objects in a list
    devobj = simics.SIM_get_object(py_dev.name)
    memobj = simics.SIM_get_object(phys_mem.name)
    clockobj = simics.SIM_get_object(clock.name)
    return [devobj, memobj, clockobj]
```

**Key Test Pattern - s-bug21328.py (Register Access)**:

```python
import dev_util
import simics
import stest

# Create the python device.
py_dev = simics.SIM_create_object('empty_device_confclass',
                                  'empty_dev_confclass')

# Add register definition for the device's register.
register = dev_util.Register_LE(py_dev.bank.regs, 0, size = 1)

# Test the register.
a = register.read()
register.write(a + 1)
b = register.read()
stest.expect_equal(b, a + 1)

# Also test the 'r1' attribute which backs the register.
stest.expect_equal(py_dev.r1, b)
c = b + 1
py_dev.r1 = c
stest.expect_equal(py_dev.r1, c)
stest.expect_equal(register.read(), c)
```

**Key Test Utilities**:
- `stest.expect_equal(actual, expected)`: Assert equality
- `stest.expect_true(condition)`: Assert boolean
- `dev_util.Register_LE(bank, offset, size)`: Create register accessor
- `simics.SIM_create_object(classname, name)`: Instantiate device
- `simics.pre_conf_object()`: Pre-configure before instantiation
- `simics.SIM_add_configuration()`: Add objects to simulation

**Architectural Decision**: 
- Use `dev_util.Register_LE` for register read/write in tests
- Create test fixture with memory-space, clock, and watchdog device
- Test scenarios: basic register access, counter countdown, interrupt generation, lock protection, checkpoint/restore

---

### RAG Query #8: Device Testing Best Practices

**Query**: "Simics device testing best practices"  
**Source Type**: source  
**Results Count**: 5

**Key Test Structure - s-info.py**:

```python
import stest
import info_status
import simics
import sample_device_with_external_lib_common

# Create an instance of each object defined in this module
dev = sample_device_with_external_lib_common.create_sample_device_with_external_lib()

# Verify that info/status commands have been registered for all
# classes in this module.
info_status.check_for_info_status(['sample-device-with-external-lib'])

# Run info and status on each object. It is difficult to test whether
# the output is informative, so we just check that the commands
# complete nicely.
for obj in [dev]:
    for cmd in ['info', 'status']:
        try:
            simics.SIM_run_command(obj.name + '.' + cmd)
        except simics.SimExc_General as e:
            stest.fail(cmd + ' command failed: ' + str(e))
```

**Best Practices Identified**:

1. **Test Organization**:
   - `tests.py`: Test suite registration
   - `s-*.py`: Individual test scripts
   - Common test utilities in shared modules

2. **Test Coverage Areas**:
   - Register read/write functionality
   - Interrupt generation and clearing
   - State machine transitions
   - Checkpoint/restore (save/load state)
   - Info/status command output

3. **Test Assertions**:
   - `stest.expect_equal()`: Value verification
   - `stest.expect_true()`: Boolean conditions
   - `stest.fail()`: Explicit test failure

**Architectural Decision**: 
- Create `test/` directory with multiple test scripts:
  - `s-basic-registers.py`: Register access tests
  - `s-countdown.py`: Counter decrement and timeout tests
  - `s-interrupt.py`: Interrupt generation tests
  - `s-lock.py`: Lock protection mechanism tests
  - `s-checkpoint.py`: Save/restore tests
  - `tests.py`: Test suite registration

---

### RAG Query #9: Lock Protection Patterns (Requirement-Driven)

**Query**: "DML register lock protection magic value pattern 0x1ACCE551"  
**Source Type**: dml  
**Results Count**: 3

**Finding**: No direct matches for lock protection patterns found in RAG results. This indicates lock protection must be implemented manually.

**Implementation Strategy from Specification**:
```dml
bank regs {
    saved bool lock_state = true;  // Default locked state
    
    register WDOGLOCK @ 0xC00 size 4 is (write, read) {
        param init_val = 0x00000001;  // Locked on reset
        
        method write(uint64 value) {
            if (value == 0x1ACCE551) {
                lock_state = false;
                this.val = 0;  // Read back as 0 when unlocked
                log info, 2: "Watchdog unlocked";
            } else {
                lock_state = true;
                this.val = 1;  // Read back as 1 when locked
                log info, 2: "Watchdog locked";
            }
        }
        
        method read() -> (uint64) {
            return lock_state ? 1 : 0;
        }
    }
    
    register WDOGLOAD @ 0x000 size 4 is (write, read) {
        method write(uint64 value) {
            if (lock_state) {
                log info, 2: "Write to WDOGLOAD blocked by lock";
                return;  // Ignore write when locked
            }
            this.val = value;
            // Update counter logic here
        }
    }
}
```

**Architectural Decision**: 
- Implement `saved bool lock_state` variable in bank
- WDOGLOCK register checks for magic value 0x1ACCE551
- All writable registers (except WDOGLOCK itself) check `lock_state` before accepting writes
- Lock state persists across checkpoints (saved variable)

---

### RAG Query #10: Checkpoint State Persistence (Requirement-Driven)

**Query**: "Simics device checkpoint state persistence saved session variable"  
**Source Type**: dml  
**Results Count**: 3

**Key Example from TSB12LV26.dml**:

```dml
session uint64 vect pkgs;
session uint64 num_accesses;

attribute caps_accesses is (uint64_attr, pseudo_attr) {
    param documentation = "Number of accesses to capabilities data";
    param writable = false;
    method get() -> (attr_value_t) {
        return SIM_make_attr_uint64(num_accesses);
    }
}

attribute selected_boot_option {
    param documentation = "Boot device that shall get maximum priority";
    param type = "s|n";

    session char* val = NULL;

    method set(attr_value_t value) throws {
        if (val != NULL)
            MM_FREE(val);
        if (SIM_attr_is_nil(value))
            val = NULL;
        else {
            if (strlen(SIM_attr_string(value)) > 255) {
                log error: "Selected boot option string must not have more" +
                           " than 255 characters.";
                throw;
            }
            val = MM_STRDUP(SIM_attr_string(value));
        }
    }

    method get() -> (attr_value_t) {
        return SIM_make_attr_string(val);
    }
}

saved uint16 mode_data[64*4];
saved uint16 last_mode_data_index = 0;
```

**Key Pattern from generic-rtc.dml**:

```dml
attribute cpus {
    param documentation = "CPUs receiving direct pin connections for SMI";
    param type = "[o*]";
    param configuration = "required";

    session int len;
    session conf_object_t **o;
    session const x86_interface_t **x86;
    saved uint1 smi_state;

    method set(attr_value_t val) throws {
        // Set logic
    }
    method get() -> (attr_value_t) {
        // Get logic
    }
}
```

**Saved vs Session Variables**:
- `saved`: Persisted in checkpoints (counter state, lock state, register values)
- `session`: Not persisted (transient runtime state, object pointers, computed values)

**Architectural Decision**: 
- Mark all register values as `saved` (automatic for register fields)
- Mark `counter_start_time` as `saved cycles_t`
- Mark `counter_start_value` as `saved uint32`
- Mark `lock_state` as `saved bool`
- Mark `interrupt_pending` as `saved bool`
- Mark event handles as `session` (events are automatically rescheduled on checkpoint restore)

---

### RAG Query #11: Integration Test Mode (Requirement-Driven)

**Query**: "DML integration test mode direct signal control bypass"  
**Source Type**: source  
**Results Count**: 3

**Finding**: No direct integration test mode examples found. Must implement based on specification.

**Implementation Strategy from Specification**:

```dml
bank regs {
    saved bool integration_test_mode = false;
    
    register WDOGITCR @ 0xF00 size 4 is (write, read) {
        param documentation = "Integration Test Control Register";
        field INTEGRATION_TEST_MODE_ENABLE @ [0];
        
        method write(uint64 value) {
            this.val = value;
            integration_test_mode = (value & 0x1) != 0;
            if (integration_test_mode) {
                log info, 2: "Integration test mode ENABLED";
            } else {
                log info, 2: "Integration test mode DISABLED";
            }
        }
    }
    
    register WDOGITOP @ 0xF04 size 4 is (write) {
        param documentation = "Integration Test Output Set Register";
        field WDOGRES @ [1];
        field WDOGINT @ [0];
        
        method write(uint64 value) {
            if (!integration_test_mode) {
                log info, 2: "WDOGITOP write ignored - integration test mode disabled";
                return;
            }
            
            // Direct signal control
            local bool wdogint_val = (value & 0x1) != 0;
            local bool wdogres_val = (value & 0x2) != 0;
            
            wdogint_signal.set_level(wdogint_val ? 1 : 0);
            wdogres_signal.set_level(wdogres_val ? 1 : 0);
            
            log info, 2: "Integration test: WDOGINT=%d, WDOGRES=%d", wdogint_val, wdogres_val;
        }
    }
}
```

**Architectural Decision**: 
- Implement `saved bool integration_test_mode` flag
- WDOGITCR register controls test mode enable
- WDOGITOP register directly controls output signals when test mode enabled
- Normal interrupt/reset generation bypassed when in test mode
- Regular interrupt clearing (WDOGINTCLR) should be suppressed in test mode

---

## Architecture Decisions

### 1. Counter Implementation Strategy

**Decision**: Use cycle-based timing with saved state variables

**Rationale**:
- `sample_timer_device.dml` demonstrates robust pattern for countdown timers
- Cycle-based approach ensures accurate timing across checkpoint/restore
- Saved variables (`counter_start_time`, `counter_start_value`) enable checkpoint persistence

**Implementation**:
```dml
bank regs {
    saved cycles_t counter_start_time;
    saved uint32 counter_start_value;
    saved uint32 step_value;  // Clock divider (1, 16, 256)
    
    method get_current_counter() -> (uint32) {
        if (!counter_enabled) return counter_start_value;
        local cycles_t now = SIM_cycle_count(dev.obj);
        local cycles_t elapsed = now - counter_start_time;
        local uint32 decrements = cast(elapsed / step_value, uint32);
        if (decrements >= counter_start_value) return 0;
        return counter_start_value - decrements;
    }
}
```

---

### 2. Two-Stage Timeout Mechanism

**Decision**: Implement separate events for interrupt timeout and reset timeout

**Rationale**:
- Specification requires first timeout to trigger interrupt, second timeout to trigger reset
- Two separate `after` events allow independent timing control
- Interrupt clearing cancels reset event

**Implementation**:
```dml
method schedule_interrupt_timeout() {
    cancel interrupt_event;
    cancel reset_event;
    
    local cycles_t cycles_to_interrupt = counter_start_value * step_value;
    after cycles_to_interrupt cycles: fire_interrupt();
}

method fire_interrupt() {
    interrupt_pending = true;
    if (interrupt_enabled && !integration_test_mode) {
        wdogint_signal.set_level(1);
    }
    
    // Schedule reset timeout
    local cycles_t cycles_to_reset = counter_start_value * step_value;
    after cycles_to_reset cycles: fire_reset();
}

method fire_reset() {
    if (reset_enabled && !integration_test_mode) {
        wdogres_signal.set_level(1);
    }
}
```

---

### 3. Lock Protection Mechanism

**Decision**: Implement `saved bool lock_state` with magic value check

**Rationale**:
- No existing DML pattern found in RAG results - must implement from specification
- Saved variable ensures lock state persists across checkpoints
- All writable registers check lock state before accepting writes

**Implementation**: See RAG Query #9 details above

---

### 4. Register Organization

**Decision**: Single `bank regs` with all 21 registers at specified offsets

**Register Map**:
| Offset | Name | Size | Access | Description |
|--------|------|------|--------|-------------|
| 0x000 | WDOGLOAD | 4 | RW | Load register |
| 0x004 | WDOGVALUE | 4 | RO | Current counter value |
| 0x008 | WDOGCONTROL | 4 | RW | Control register |
| 0x00C | WDOGINTCLR | 4 | WO | Interrupt clear register |
| 0x010 | WDOGRIS | 4 | RO | Raw interrupt status |
| 0x014 | WDOGMIS | 4 | RO | Masked interrupt status |
| 0xC00-0xCFC | Reserved | - | - | 256 bytes reserved |
| 0xD00 | WDOGLOCK | 4 | RW | Lock register |
| 0xF00 | WDOGITCR | 4 | RW | Integration test control |
| 0xF04 | WDOGITOP | 4 | WO | Integration test output set |
| 0xFE0-0xFFC | Peripheral ID | 4 each | RO | Identification registers |

---

### 5. Signal Interface Design

**Decision**: Use two `signal_connect` interfaces for interrupt and reset outputs

**Rationale**:
- `sample_timer_device.dml` demonstrates signal interface for interrupts
- Two independent signals required: `wdogint` and `wdogres`
- Signal interface supports pulse (edge-triggered) and level interrupts

**Implementation**:
```dml
connect wdogint_signal is signal_connect {
    param documentation = "Watchdog interrupt output";
}

connect wdogres_signal is signal_connect {
    param documentation = "Watchdog reset output";
}
```

---

## Implementation Strategy

### Phase 3: Implementation Approach

**File Structure**:
```
simics-project/modules/watchdog-timer/
├── watchdog-timer.dml         # Main device implementation
├── registers.dml              # Register bank definitions
├── module_load.py             # Python module loading
├── CMakeLists.txt             # Build configuration
└── test/
    ├── tests.py               # Test suite registration
    ├── s-basic-registers.py   # Register access tests
    ├── s-countdown.py         # Counter and timing tests
    ├── s-interrupt.py         # Interrupt generation tests
    ├── s-lock.py              # Lock protection tests
    └── s-checkpoint.py        # Checkpoint/restore tests
```

**Development Order**:
1. Create minimal device skeleton (watchdog-timer.dml)
2. Implement register bank with all 21 registers (registers.dml)
3. Implement counter logic with cycle-based timing
4. Implement interrupt generation (first timeout)
5. Implement reset generation (second timeout)
6. Implement lock protection mechanism
7. Implement integration test mode
8. Add signal interfaces for wdogint and wdogres
9. Implement checkpoint persistence (saved variables)
10. Create Python test suite

**Critical Implementation Details**:

1. **WDOGVALUE Register** (Read-Only, Dynamic):
```dml
register WDOGVALUE @ 0x004 size 4 is (read, read_only) {
    method read() -> (uint64) {
        return get_current_counter();
    }
}
```

2. **WDOGINTCLR Register** (Write-Only):
```dml
register WDOGINTCLR @ 0x00C size 4 is (write) {
    method write(uint64 value) {
        if (lock_state) return;  // Blocked by lock
        if (integration_test_mode) return;  // Blocked in test mode
        
        interrupt_pending = false;
        wdogint_signal.set_level(0);  // Clear interrupt
        
        // Reload counter
        counter_start_value = WDOGLOAD.val;
        counter_start_time = SIM_cycle_count(dev.obj);
        
        // Cancel pending reset event
        cancel reset_event;
    }
}
```

3. **WDOGCONTROL Register** (Control Logic):
```dml
register WDOGCONTROL @ 0x008 size 4 is (write, read) {
    field INTEN @ [0];
    field RESEN @ [1];
    
    method write(uint64 value) {
        if (lock_state) return;  // Blocked by lock
        
        local bool was_enabled = (this.val & 0x1) != 0;
        this.val = value;
        local bool now_enabled = (value & 0x1) != 0;
        
        if (!was_enabled && now_enabled) {
            // Start counter
            counter_start_value = WDOGLOAD.val;
            counter_start_time = SIM_cycle_count(dev.obj);
            schedule_interrupt_timeout();
        } else if (was_enabled && !now_enabled) {
            // Stop counter
            cancel interrupt_event;
            cancel reset_event;
        }
    }
}
```

---

## References

### DML Documentation
- DML 1.4 Reference Manual (Simics 7.57.0)
- Model Builder User Guide (Model-Builder 7.44.0)
- Simics API Reference (7.57.0)

### Code Examples
- `sample_timer_device.dml`: Counter with match event
- `TSB12LV26.dml`: Checkpoint state persistence patterns
- `generic-rtc.dml`: Saved vs session variable usage
- `ieee_mii_regs.dml`: Register bank organization

### Test Examples
- `s-toggle-i2c.py`: Device creation and object setup
- `s-bug21328.py`: Register access with dev_util.Register_LE
- `s-info.py`: Info/status command testing

### Hardware Specification
- ARM PrimeCell SP805 Watchdog Timer Technical Reference Manual
- spec.md: 34 functional requirements, 21 register definitions

---

## Appendix: RAG Search Results Summary

| Query # | Query Topic | Source Type | Results | Key Artifacts Found |
|---------|-------------|-------------|---------|---------------------|
| 1 | DML 1.4 reference manual | docs | 5 | Register syntax, field definitions, saved vs session |
| 2 | Model Builder patterns | docs | 5 | Device lifecycle methods, template inheritance |
| 3 | DML device template | dml | 3 | Minimal device structure, standard imports |
| 4 | Watchdog timer best practices | source | 5 | **sample_timer_device.dml** (complete counter example) |
| 5 | Device implementation examples | source | 5 | HPET, DS323x, sample_timer_device (repeated) |
| 6 | Register bank patterns | dml | 5 | Bank template, address calculation, transaction handling |
| 7 | Python test patterns | python | 5 | dev_util.Register_LE, stest assertions, object creation |
| 8 | Device testing best practices | source | 5 | Test suite organization, info/status commands |
| 9 | Lock protection patterns | dml | 3 | No direct match - manual implementation required |
| 10 | Checkpoint state persistence | dml | 3 | Saved vs session variables, attribute get/set |
| 11 | Integration test mode | source | 3 | No direct match - manual implementation required |

**Total RAG Queries Executed**: 11 (8 mandatory + 3 requirement-driven)

---

**Document Status**: Complete  
**Next Phase**: Phase 1 - Design (data-model.md, contracts/, quickstart.md)
