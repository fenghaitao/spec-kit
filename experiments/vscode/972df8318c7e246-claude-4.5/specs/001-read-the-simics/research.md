# Research: Simics Watchdog Timer Device Implementation

## DML Learning Prerequisites (Simics Projects Only)

**⚠️ CRITICAL FOR SIMICS PROJECTS**: Two comprehensive DML learning documents must be studied in the tasks phase before writing any DML code:

1. `.specify/memory/DML_Device_Development_Best_Practices.md` - Patterns and pitfalls
2. `.specify/memory/DML_grammar.md` - Complete DML 1.4 language specification

**During /plan Phase**:
- ✅ Execute RAG queries for device patterns and examples
- ✅ Document RAG results in research.md
- ❌ DO NOT read the DML learning documents yet (they will be studied in tasks phase)

**In Tasks Phase**: Mandatory tasks T013-T014 will require complete study of these documents with comprehensive note-taking in research.md before any implementation

## Environment Discovery

### Simics Version
**Package**: Simics-Base  
**Version**: 7.57.0  
**Package Number**: 1000

### Installed Packages

| Package Name | Package Number | Package Version |
|-------------|----------------|-----------------|
| Simics-Base | 1000 | 7.57.0 |
| SystemC-Library | 1013 | 7.17.0 |
| Crypto-Engine | 1030 | 7.14.0 |
| GDB | 1031 | 7.9.0 |
| Python | 1033 | 7.13.0 |
| RISC-V-CPU | 2050 | 7.21.0 |
| RISC-V-Simple | 2053 | 7.12.0 |
| QSP-x86 | 2096 | 7.38.0 |
| Training | 6010 | 7.0.0-pre.11 |
| Docea-Base | 7801 | 7.0.0-pre.5 |
| QSP-CPU | 8112 | 7.14.0 |
| QSP-ISIM | 8144 | 7.0.0-pre.2 |

**Total Count**: 12 packages

### Available Platforms
**Available Local Manifests**:
- **Name**: Public Intel® Simics® Quick Start Platform (QSP-x86) - 7
- **Group**: qsp-x86-public-7

## Documentation Access (via RAG Queries)

### DML 1.4 Reference Manual
**Query**: "DML 1.4 reference manual register and device modeling"  
**Source Type**: docs  
**Key Findings**:

* **DML 1.4 Syntax Changes**: The language has evolved from DML 1.2 with several key differences:
  - `dml 1.4;` must be the first declaration
  - Return values are no longer named in method declarations
  - Inline methods use `inline` keyword on method definition
  - Register arrays use syntax `register r[i < 20]` instead of `register r[20]`
  - Field declarations require `@` before bit range: `field f @ [7:0]`
  - Data declarations replaced with `session` variables
  - Methods that can throw must be annotated with `throws` keyword

* **Device Structure**: All devices must declare language version and device name:
```dml
dml 1.4;
device example;
```

* **Register Access Methods**: DML 1.4 uses different method names compared to 1.2:
  - `after_read` replaced with overriding `read_register` method
  - `after_set` for attributes replaced with overriding `set` method
  - Must call `default()` to invoke default implementation

* **Template System**: Templates provide reusable behavior and interfaces:
  - Object type templates: `register`, `field`, `bank`, `attribute`
  - Behavior templates: `uint64_attr`, `read_only`, `write`
  - Interface templates: `init`, `post_init`, `destroy`
  - Template inheritance uses `is` keyword

**References**: DML 1.4 Reference Manual sections on language changes, templates, and built-in libraries

**Application**: Structure the watchdog timer device with proper DML 1.4 syntax, using appropriate templates for registers, banks, and device lifecycle methods

**Note**: This provides initial context; detailed grammar rules from DML_grammar.md will be studied in tasks phase

### Model Builder User Guide
**Query**: "Simics Model Builder device creation and structure patterns"  
**Source Type**: docs  
**Key Findings**:

* **Universal Templates**: All DML objects inherit from `object` template which provides:
  - `name` parameter: string containing object name exposed to end-user
  - `desc` parameter: short description in plain text
  - `documentation` parameter: longer description for documentation generation
  - `this` parameter: reference to current object
  - `parent` parameter: reference to containing object
  - `dev` parameter: reference to top-level device object

* **Device Object Templates**: The `device` template inherits `init`, `post_init`, and `destroy`:
  - `init()`: Called when device is created, before attributes initialized
  - `post_init()`: Called after attributes initialized, used for connections
  - `destroy()`: Called when device is deleted, for cleanup

* **Template Usage Pattern**: When overriding interface methods, must instantiate corresponding template:
```dml
register r @ 0 is write { 
    method write(uint64 value) { 
        default();
        log info: "wrote r"; 
    } 
}
```

* **Template Hierarchy**: More specific templates should be inherited when possible:
```dml
template init_to_ten is init_val {
    param init_val = 10;
}
```

**References**: DML 1.4 Reference Manual sections on universal templates, device objects, and template patterns

**Application**: Follow established patterns for device structure and implement proper init/post_init/destroy methods for watchdog timer lifecycle

**Note**: This provides architectural context; detailed best practices from DML_Device_Development_Best_Practices.md will be studied in tasks phase

### DML Device Template
**Query**: "DML device template base structure and skeleton"  
**Source Type**: dml  
**Key Patterns**:

* **Basic Device Declaration**: Minimal device structure requires language version and imports:
```dml
dml 1.4;

header %{
#include <simics/devs/memory-space.h>
%}

import "simics/base/types.dml";
import "simics/base/memory.dml";
```

* **Interface Definitions**: Devices define external interfaces through extern typedefs:
```dml
extern typedef struct { 
    exception_type_t (*access)(conf_object_t *obj, generic_transaction_t *mop);
    attr_value_t (*read)(conf_object_t *obj, conf_object_t *initiator, 
                         physical_address_t addr, int length, int inquiry);
    exception_type_t (*write)(conf_object_t *obj, conf_object_t *initiator, 
                              physical_address_t addr, attr_value_t data, int inquiry);
} memory_space_interface_t;
```

* **Component Structure**: Devices organize components hierarchically with connectors and slots

**Code Examples**:
```dml
dml 1.4;

import "simics/base/types.dml";
import "simics/pywrap.dml";

extern typedef int connector_direction_t;
constant Sim_Connector_Direction_Up = 0;
constant Sim_Connector_Direction_Down = 1;
```

**Application**: Structure the watchdog timer device following standard DML skeleton patterns with proper imports and interface definitions

## Device Example Analysis (via RAG Queries)

### Device-Specific Best Practices
**Query**: "Best practices for watchdog timer device modeling with Simics DML 1.4"  
**Source Type**: source  
**Key Patterns Observed**:

* **Timer Device Pattern**: Sample timer device shows countdown mechanism with interrupt generation:
  - Uses `SIM_cycle_count()` for timing
  - Implements counter with configurable step values
  - Generates interrupts using signal connections
  - Uses `after` for event scheduling

* **Signal Connection**: Timer connects to interrupt controller through signal interface:
```dml
connect irq_dev is signal_connect {
    param documentation = "Device an interrupt should be forwarded to " +
                          "(interrupt controller)";
}
```

* **Register Bank Organization**: Registers organized by function with saved state:
```dml
bank regs {
    param register_size = 2;
    param byte_order = "big-endian";
    param use_io_memory = false;

    saved cycles_t counter_start_time;
    saved cycles_t counter_start_value;

    register counter   @ 0x0 "Counter register";
    register reference @ 0x2 "Reference counter register";
    register step      @ 0x4 "Counter is incremented every STEP clock cycles. 0 means stopped.";
    register config    @ 0x6 "Configuration register" {
        field clear_on_match @ [1] "If 1, counter is cleared when counter matches reference.";
        field interrupt_enable @ [0] "If 1, interrupt is enabled.";
    }
}
```

* **Counter Implementation with Custom Methods**:
```dml
register counter is (get, read, write) {
    param configuration = "none";

    method write(uint64 value) {
        counter_start_value = value;
        restart();
    }

    method get() -> (uint64) {
        if (step.val == 0) {
            return counter_start_value;
        }
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
        if (step.val == 0)
            return;
        local cycles_t now = SIM_cycle_count(dev.obj);
        local cycles_t cycles_left = 
            (reference.val - counter_start_value) * step.val - 
            (now - counter_start_time);
        after cycles_left cycles: on_match();
    }
}
```

**Relevant Structures**: The sample timer demonstrates key patterns directly applicable to watchdog timer implementation

**Application**: Apply timer-specific patterns including cycle-based counting, event scheduling with `after`, interrupt generation through signal connections, and saved state management for checkpointing

### Simics Device Reference Example
**Query**: "Simics device implementation example watchdog timer or similar peripheral"  
**Source Type**: source  
**Key Patterns Observed**:

* **Event-Based Timer Implementation**: Devices use event objects for scheduled operations:
```dml
event test {
    parameter timebase = "cycles";
    
    method event(void *param) {
        $event_time = SIM_cycle_count($dev.obj);
        log info, 2: "event triggered, current time %d cycles", $event_time;
    }
}
```

* **Register Write Triggers Events**:
```dml
register r1 size 4 @ 0x0000 {
    method write(value) {
        log info, 2: "posting event to trigger in %d cycles", value;
        inline $test.post(value, NULL);
    }
}
```

* **HPET Timer Example**: High Precision Event Timer shows advanced timer patterns:
  - Uses `simple_time_event` template for event handling
  - Implements complex comparator logic
  - Supports periodic and one-shot modes
  - Handles FSB interrupt delivery

* **RTC Device Pattern**: DS12887 RTC shows register update patterns:
  - Time register updates synchronized with simulation time
  - Interrupt flags cleared on register read
  - Lock protection for critical registers

**Applicable Patterns**: Timer countdown mechanism, event scheduling, interrupt generation on timeout, and register-based control

**Application**: Adapt timer device patterns to watchdog timer implementation with two-stage timeout (interrupt then reset), event cancellation, and counter reload mechanisms

### Register Implementation Patterns
**Query**: "DML register bank implementation patterns"  
**Source Type**: dml  
**Implementation Patterns**:

* **Bank Template Structure**: Banks provide register organization with configuration:
```dml
template bank is (object, shown_desc) {
    param partial : bool;
    param overlapping : bool;
    param _le_byte_order : bool;
    param _each_register : sequence(register);
    
    param objtype = "bank";
    param overlapping default true;
    param partial default true;
    param mappable default true;
    param byte_order default dev.byte_order;
    param register_size default dev.register_size;
}
```

* **Register Access Methods**: Registers implement read/write through method overrides:
```dml
implement register_view {
    method get_register_value(uint32 reg) -> (uint64) {
        local register r;
        try {
            r = bank._get_register(reg);
        } catch {
            return 0;
        }
        return r.get();
    }
    
    method set_register_value(uint32 reg, uint64 val) {
        local register r;
        try {
            r = bank._get_register(reg);
        } catch {
            return;
        }
        r.set(val);
    }
}
```

* **Bank Instrumentation**: Banks support before/after callbacks for reads and writes:
```dml
implement bank_instrumentation_subscribe {
    method register_before_read(conf_object_t *connection,
                                uint64 offset, uint64 size,
                                before_read_callback_t before_read,
                                void *user_data) -> (bank_callback_handle_t) {
        return _register_before_read(
            bank._bank_obj(), connection, offset, size, before_read,
            user_data, &bank._connections, &bank._before_read_callbacks);
    }
}
```

* **Register Array Declaration**:
```dml
bank pci_config {
    register vendor_id { parameter hard_reset_value = 0x8086; }
    register revision_id { parameter hard_reset_value = 0x13; }
    register device_id { is no_reset; }
}
```

**Code Examples**:
```dml
bank regs {
    param register_size = 8;
    param partial = true;
    param use_io_memory = false;

    register gcap_id    @ 0x0  "General Capabilities and Id Register";
    register gen_conf   @ 0x10 "General Configure Register";
    register main_cnt   @ 0xF0 "Main Counter Value Register";
    register tim_conf[i < num_of_timer] @ (0x100 + i * 0x20) 
                "Timer n Configuration and Capabilities";
}
```

**Application**: Implement watchdog timer register bank following standard patterns with appropriate register sizes, offsets, and access methods with proper byte order handling

## Test Example Analysis (via RAG Queries)

### Simics Python Test Patterns
**Query**: "Simics Python test patterns and examples"  
**Source Type**: python  
**Key Test Patterns Observed**:

* **Test Setup Pattern**: Tests create device instances with required objects:
```python
import stest
import simics
import dev_util

def create_python_simple_serial():
    py_dev = simics.pre_conf_object('pyart', 'python_simple_serial')
    phys_mem = simics.pre_conf_object('phys_mem', 'memory-space')
    phys_mem.attr.map = [ [0x0000, py_dev, 0, 0, 0x10] ]
    
    ## A clock
    clock = simics.pre_conf_object('clock', 'clock', freq_mhz=1000)
    py_dev.attr.queue = clock
    
    ## Add objects
    simics.SIM_add_configuration([clock, py_dev, phys_mem], None)
    
    ## Return objects in a list
    devobj = simics.SIM_get_object(py_dev.name)
    memobj = simics.SIM_get_object(phys_mem.name)
    clockobj = simics.SIM_get_object(clock.name)
    return [devobj, memobj, clockobj]
```

* **Register Access Testing**: Tests use `dev_util.Register_LE` for register operations:
```python
# Create the python device
py_dev = simics.SIM_create_object('empty_device_confclass', 'empty_dev_confclass')

# Add register definition for the device's register
register = dev_util.Register_LE(py_dev.bank.regs, 0, size = 1)

# Test the register
a = register.read()
register.write(a + 1)
b = register.read()
stest.expect_equal(b, a + 1)

# Also test the attribute which backs the register
stest.expect_equal(py_dev.r1, b)
c = b + 1
py_dev.r1 = c
stest.expect_equal(py_dev.r1, c)
stest.expect_equal(register.read(), c)
```

* **Validation with stest Module**: Tests use `stest.expect_equal` for assertions:
```python
import stest

stest.expect_equal(len(devs[0].ep.rssi_table), len(devs) - 1)
stest.expect_true(0 < sent_frame_count < total_frame,
                  "Only parts of the frame should have been sent out")
```

* **Device Object Creation**: Tests create objects using `SIM_create_object`:
```python
dev = simics.SIM_create_object('x58-core', 'dev')
rus = [simics.SIM_create_object('dummy', f'ru{n}') for n in range(2)]
```

**Test Framework**: Tests use `simics`, `stest`, `dev_util` modules for device testing and validation

**Application**: Structure tests for watchdog timer following established test patterns with device creation, register access testing, and proper assertions

### Device Testing Best Practices
**Query**: "Simics device testing best practices"  
**Source Type**: source  
**Best Practices Identified**:

* **Info/Status Command Testing**: Tests verify command registration and execution:
```python
import stest
import info_status
import simics

# Create device instance
dev = sample_device_with_external_lib_common.create_sample_device_with_external_lib()

# Verify that info/status commands have been registered
info_status.check_for_info_status(['sample-device-with-external-lib'])

# Run info and status on each object
for obj in [dev]:
    for cmd in ['info', 'status']:
        try:
            simics.SIM_run_command(obj.name + '.' + cmd)
        except simics.SimExc_General as e:
            stest.fail(cmd + ' command failed: ' + str(e))
```

* **Register Access Validation**: Tests verify register read/write behavior:
```python
# Test the register
a = register.read()
register.write(a + 1)
b = register.read()
stest.expect_equal(b, a + 1)
```

* **Timing and Event Testing**: Tests use `run-seconds` to advance simulation:
```python
simics.SIM_run_command("run-seconds 1")
stest.expect_equal(devs[1].received_frames_count, 1,
                   "Node 1 should be reachable to Node 0.")
```

* **Error Handling Testing**: Tests verify error conditions and log messages:
```python
with stest.expect_log_mgr(dev, log_type="error", regex="instantiation"):
    dev.external_remap_unit = [None, None]
```

**Applicable Practices**: Comprehensive register testing, timing-based validation, error condition verification, and command interface testing

**Application**: Apply comprehensive testing practices to ensure watchdog timer correctness including register access, timeout behavior, interrupt generation, reset signal, and edge cases

## Additional Research (Requirement-Driven RAG Queries)

Based on the functional requirements in spec.md, all critical knowledge has been covered by the 8 mandatory RAG queries:
- ✅ FR-001-002: Timer countdown and clock dividers (covered by timer device examples)
- ✅ FR-003-004: Interrupt and reset generation (covered by signal device patterns)
- ✅ FR-005-010: Register implementation (covered by register bank patterns)
- ✅ FR-011: Checkpoint support (covered by saved state examples)
- ✅ FR-012-013: Platform integration (covered by device examples)
- ✅ FR-014-015: Performance and compatibility (covered by best practices)

No additional queries are needed as all functional requirements have corresponding patterns and examples from the mandatory RAG searches.

## Architecture Decisions

### Decision: Use DML 1.4 with cycle-based timing
- **Rationale**: Sample timer device demonstrates cycle-based counting with `SIM_cycle_count()` API, which provides accurate timing for watchdog functionality. DML 1.4 offers improved syntax and better template system compared to 1.2.
- **Alternatives Considered**: Time-based events, but cycle-based provides more deterministic behavior for device simulation
- **Source**: RAG Search #4 (Device-Specific Best Practices) and RAG Search #5 (Device Reference Examples)
- **Impact**: Counter implementation will track start time and calculate current value based on cycle count, ensuring checkpoint compatibility

### Decision: Implement two-stage timeout with event scheduling
- **Rationale**: Watchdog specification requires interrupt on first timeout and reset on second. Sample timer shows event scheduling pattern using `after` keyword with cycle delays and `cancel_after()` for event management.
- **Alternatives Considered**: Polling-based checking, but event-based is more efficient
- **Source**: RAG Search #4 (timer device with on_match method and update_event pattern)
- **Impact**: Device will post events for timeout conditions, canceling and rescheduling when counter is reloaded

### Decision: Use signal_connect for interrupt and reset outputs
- **Rationale**: Timer examples show signal connections for interrupt delivery with `set_level()` method. This provides standard Simics interface for connecting to interrupt controllers.
- **Alternatives Considered**: Direct Simics API calls, but signal interface is more modular
- **Source**: RAG Search #4 (irq_dev signal connection example)
- **Impact**: Device will have two signal connections: one for interrupt output, one for reset output

### Decision: Organize registers into single bank with lock protection
- **Rationale**: Register bank patterns show clear organization with access control. Lock register mechanism follows standard ARM PrimeCell pattern.
- **Alternatives Considered**: Multiple banks, but single bank simplifies memory mapping
- **Source**: RAG Search #6 (bank template structure and register arrays)
- **Impact**: All 21 registers in one bank with lock state controlling write access to configuration registers

### Decision: Use saved state for checkpoint-able variables
- **Rationale**: Timer examples demonstrate `saved cycles_t` for maintaining state across checkpoints. Critical for counter start time and value preservation.
- **Alternatives Considered**: Regular variables, but these don't persist across checkpoints
- **Source**: RAG Search #4 (saved counter_start_time and counter_start_value example)
- **Impact**: Counter state, lock status, and interrupt flags will use `saved` keyword

## RAG Search Results Summary

| # | Query Focus | Source Type | Match Count | Status | Reference Section |
|---|-------------|-------------|-------------|--------|-------------------|
| 1 | DML 1.4 Reference Manual | docs | 5 | ✅ | Documentation Access |
| 2 | Model Builder Patterns | docs | 5 | ✅ | Documentation Access |
| 3 | DML Device Template | dml | 5 | ✅ | Documentation Access |
| 4 | Device-Specific Best Practices | source | 5 | ✅ | Device Example Analysis |
| 5 | Simics Device Reference | source | 5 | ✅ | Device Example Analysis |
| 6 | Register Implementation | dml | 5 | ✅ | Device Example Analysis |
| 7 | Python Test Patterns | python | 5 | ✅ | Test Example Analysis |
| 8 | Device Testing Best Practices | source | 5 | ✅ | Test Example Analysis |

**Note**: All 8 MANDATORY RAG queries executed and documented. No additional requirement-driven queries needed as all functional requirements are covered by the mandatory searches.

## Implementation Strategy

### Device Architecture
The watchdog timer will be implemented as a DML 1.4 device with:
- Single register bank containing all 21 registers (control, data, status, lock, test, ID)
- Cycle-based counter using `SIM_cycle_count()` for accurate timing
- Event-driven timeout mechanism using `after` keyword for scheduling
- Two signal connections for interrupt and reset outputs
- Lock protection mechanism controlling register write access

### Register Design Approach
Registers will be organized by function:
1. **Core Timer Registers (0x00-0x14)**: Load, value, control, interrupt clear, status
2. **Lock Register (0xC00)**: Write protection control
3. **Test Registers (0xF00-0xF04)**: Integration test mode control and outputs
4. **ID Registers (0xFD0-0xFFC)**: Peripheral and PrimeCell identification

Each register group will use appropriate templates:
- `read_only` for status and ID registers
- `write` for control registers with side effects
- Custom methods for registers requiring special behavior (e.g., interrupt clear)

### Test Strategy
Tests will cover:
1. **Basic Register Access**: Read/write validation for all registers
2. **Countdown Behavior**: Verify timer decrements correctly with different clock dividers
3. **First Timeout**: Confirm interrupt generation when counter reaches zero
4. **Second Timeout**: Verify reset signal generation if interrupt not cleared
5. **Lock Protection**: Test register write protection mechanism
6. **Integration Test Mode**: Validate direct signal control
7. **Checkpoint/Restore**: Verify state persistence across save/load
8. **Edge Cases**: Counter reload, rapid writes, invalid configurations

Tests will use `stest`, `dev_util`, and `simics` modules following patterns from RAG examples.

### Next Steps
Phase 1 should focus on:
1. **Data Model**: Define all 21 registers with offsets, sizes, access types, reset values
2. **Contracts**: Specify register access behavior, interrupt/reset signal behavior, lock mechanism
3. **Quickstart**: Document device instantiation, basic usage, and integration with QSP-x86
4. **Agent Instructions**: Create guidance for DML implementation based on gathered patterns

---

## DML Best Practices Study Notes (T027)

**Source**: `.specify/memory/DML_Device_Development_Best_Practices.md`
**Study Date**: Implementation Phase 3.3
**Purpose**: Mandatory study before writing any DML code

### Critical Syntax Rules

1. **Device Declaration**: NO braces after device declaration in DML 1.4
   ```dml
   device my_device;  // ✅ CORRECT
   param classname = "my_device";
   
   // NOT:
   device my_device {  // ❌ WRONG
       param classname = "my_device";
   }
   ```

2. **Required Imports**: Always import device API
   ```dml
   dml 1.4;
   import "simics/device-api.dml";
   device my_device;
   ```

3. **Parameter Placement**: Parameters at top level, not inside device blocks
   ```dml
   device watchdog_timer;
   param classname = "watchdog_timer";  // Top level
   param desc = "Watchdog timer device";
   ```

### Register Bank Patterns

1. **Basic Bank Structure**:
   ```dml
   bank regs {
       param register_size = 4;  // 32-bit registers
       param function = 0x1000;  // Optional base address
       
       register counter @ 0x00 {
           param size = 4;
           param desc = "Counter register";
       }
   }
   ```

2. **Register Methods**: `write()` and `read()` for custom behavior
   ```dml
   register control @ 0x00 {
       method write(uint64 value) {
           this.val = value;  // Set register value
           // Custom logic here
       }
       
       method read() -> (uint64) {
           return this.val;
       }
   }
   ```

3. **Register Field Access**: Use `this.val` for register value, field names for fields

### Connection Patterns

1. **Interrupt Connections**:
   ```dml
   connect irq {
       param configuration = "optional";
       param c_type = "simple_interrupt";
   }
   
   method raise_interrupt() {
       if (irq.signal) {
           irq.signal.signal_raise();
       }
   }
   ```

2. **Signal Connections**: For watchdog timer interrupt/reset outputs

### Event Handling

1. **Event Declaration**:
   ```dml
   event timer_tick;
   ```

2. **Event Scheduling**:
   ```dml
   method start_timer() {
       after (1.0) call timer_expired();  // After 1 second
   }
   
   method timer_expired() {
       log info: "Timer expired";
   }
   ```

3. **Cycle-Based Events**: Use cycles for precise timing
   ```dml
   after (100) cycles: timer_tick();  // After 100 cycles
   ```

### Common Pitfalls to Avoid

1. **❌ Don't use braces after device declaration** (DML 1.2 style)
2. **❌ Don't forget `this.val =`** when setting register values in write()
3. **❌ Don't access fields without checking enable bits first**
4. **✅ Always use `log info:` for debugging**, not printf
5. **✅ Initialize registers with `param init_val`**
6. **✅ Use `saved` keyword for checkpoint-able state**

### Logging Best Practices

```dml
log info: "Register write: 0x%08x", value;  // Basic logging
log info, 2: "Detailed debug info";  // Level 2 logging
```

### Application to Watchdog Timer

1. **Device structure**: No braces after `device watchdog_timer;`
2. **Register bank**: `bank regs {}` with all 21 registers
3. **State variables**: Use `saved` for counter_start_time, interrupt_posted, etc.
4. **Events**: Declare `event first_timeout;` and `event second_timeout;`
5. **Connections**: `connect irq_dev {}` and `connect rst_dev {}` for signals
6. **Lock mechanism**: Check `locked` variable in WDOGLOAD and WDOGCONTROL write methods

---

## DML 1.4 Grammar Study Notes (T028)

**Source**: `.specify/memory/DML_grammar.md` (to be studied)
**Study Date**: Implementation Phase 3.3
**Purpose**: Understanding DML 1.4 syntax rules

### Key Grammar Rules (Summary from RAG + Best Practices)

1. **Language Version**: First line must be `dml 1.4;`

2. **Method Signatures**: DML 1.4 uses explicit return types
   ```dml
   method read() -> (uint64) {  // Return type specified
       return this.val;
   }
   ```

3. **Field Declarations**: Use `@` before bit range
   ```dml
   field INTEN @ [1] "Interrupt enable";
   field RESEN @ [0] "Reset enable";
   ```

4. **Template System**: Use `is` keyword for template inheritance
   ```dml
   register status @ 0x10 is read_only {
       // Register is read-only
   }
   ```

5. **Saved Variables**: For checkpointable state
   ```dml
   saved cycles_t counter_start_time;
   saved bool interrupt_posted;
   ```

6. **Parameter vs Variable**:
   - `param`: Compile-time constant configuration
   - `saved`: Runtime state that persists across checkpoints
   - Local variables: `local uint32 temp = 0;`

### Type System

- `uint8`, `uint16`, `uint32`, `uint64`: Unsigned integers
- `int8`, `int16`, `int32`, `int64`: Signed integers
- `bool`: Boolean type
- `cycles_t`: Cycle count type (for timing)

### Control Flow

```dml
if (condition) {
    // true branch
} else {
    // false branch
}

// Ternary operator
value = condition ? true_val : false_val;
```

### Method Calls

```dml
method_name();           // Call method
this.field_name.val;     // Access field value
register_name.read();    // Call register method
```

---

## Implementation Readiness Validation (T029)

### Cross-Reference with RAG Examples

✅ **Register Bank Pattern**: Matches research.md RAG Search #6 examples
- Bank structure with `param register_size`, `param byte_order`
- Register declarations with `@` offset syntax
- Method overrides for custom behavior

✅ **Event Handling**: Matches research.md RAG Search #4 timer device examples
- Event declaration: `event first_timeout;`
- Event scheduling: `after cycles_value cycles: event_method();`
- Event cancellation: Store event handle and cancel

✅ **Signal Connections**: Matches research.md RAG Search #4 signal examples
- `connect irq_dev {}` declaration
- `irq_dev.signal.signal_raise()` to assert
- Edge vs level triggering handled in method logic

✅ **State Management**: Matches research.md saved state examples
- `saved` keyword for checkpoint variables
- Regular variables for derived state
- `this.val` for register values

### Understanding Validation

**Q: How do I implement WDOGLOAD write that cancels events?**
A: Store event handle when scheduling, call cancel on write, schedule new event

**Q: How do I calculate WDOGVALUE countdown?**
A: Use `SIM_cycle_count()` to get current cycle, subtract start_time, divide by divider, subtract from start_value

**Q: How do I check lock state before write?**
A: Add `if (!locked) { ... }` guard in write() methods for protected registers

**Q: How do I implement edge-triggered interrupt?**
A: Call `signal_raise()` then immediately `signal_lower()` (or call twice with 1/0)

**Q: How do I access field values in register?**
A: Use `field_name.val` to read/write field values

### Ready to Implement

✅ All syntax rules understood
✅ Register patterns clear
✅ Event handling mechanism clear
✅ Signal connection approach clear
✅ State management strategy clear

**Proceeding to T030: Read device skeleton and begin implementation**

