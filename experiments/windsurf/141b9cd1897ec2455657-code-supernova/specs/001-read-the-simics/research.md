# Research: Simics Watchdog Timer Device

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
**Package Number**: 1000  
**Package Version**: 7.57.0

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

**Total Packages**: 12

### Available Platforms
**Available Local Manifests**:
- Public Intel® Simics® Quick Start Platform (QSP-x86) - 7 (Group: qsp-x86-public-7)

## Documentation Access (via RAG Queries)

### DML 1.4 Reference Manual
**Query**: "DML 1.4 reference manual register and device modeling"  
**Source Type**: docs  
**Key Findings**:
  * **DML 1.4 Syntax Changes**: Key differences from DML 1.2 including mandatory `dml 1.4;` declaration, explicit return statements, `throws` keyword for exception handling, and new array syntax `[i < size]`
  * **Register Implementation Patterns**: Override `read_register` and `write_register` methods instead of deprecated `after_read`/`after_write`; use `default()` to call base implementation
  * **Field Declaration Syntax**: Fields must use `@` prefix before bit range (e.g., `field f @ [7:0]`)
  * **Template System**: Built-in templates for registers, banks, and devices; interface templates must be explicitly instantiated to override behavior
  * **Session Variables**: Replace DML 1.2 `data` declarations with `session` keyword for device state

**References**: 
- DML 1.4 Reference Manual - Changes from DML 1.2
- Libraries and Built-ins section
- Standard Templates (utility.dml)

**Application**: Structure the watchdog timer device following DML 1.4 syntax with proper register templates, field declarations, and session state management

**Note**: This provides initial context; detailed grammar rules from DML_grammar.md will be studied in tasks phase

### Model Builder User Guide
**Query**: "Simics Model Builder device creation and structure patterns"  
**Source Type**: docs  
**Key Findings**:
  * **Universal Templates**: All objects inherit `name`, `desc`, `documentation`, `limitations` templates; provide metadata and description parameters
  * **Lifecycle Methods**: `init()` called before attribute initialization, `post_init()` after attributes set, `destroy()` for cleanup
  * **Device Object Structure**: Top-level device inherits `init`, `post_init`, `destroy` templates automatically
  * **Object Hierarchy**: All objects provide `this`, `parent`, `dev`, `qname`, `objtype` parameters for navigation
  * **Configuration Attributes**: Use `int64_attr`, `uint64_attr` templates for simple attributes with automatic get/set methods

**References**: 
- Section 4.1 Universal templates
- Section 4.2 Device objects
- Template inheritance patterns

**Application**: Follow established patterns for device structure with proper init/post_init lifecycle, attribute definitions, and object hierarchy

**Note**: This provides architectural context; detailed best practices from DML_Device_Development_Best_Practices.md will be studied in tasks phase

### DML Device Template
**Query**: "DML device template base structure and skeleton"  
**Source Type**: dml  
**Key Patterns**:
  * **Device Declaration**: Start with `dml 1.4;` followed by `device <name>;` with description parameters
  * **Import Statements**: Common imports include `utility.dml`, `simics/devs/signal.dml`, `simics/device-api.dml`
  * **Bank Structure**: Banks contain registers with parameters like `register_size`, `byte_order`, `use_io_memory`
  * **Interface Implementations**: Devices implement Simics interfaces (e.g., `io_memory`, `signal`) for platform integration

**Code Examples**:

```dml
dml 1.4;

device sample_timer_device;
param desc = "sample timer device";
param documentation = "This is the <class>sample_timer_device</class> "
                          + "class, an example of how timer devices "
                          + "can be written in Simics.";

import "utility.dml";
import "simics/devs/signal.dml";

connect irq_dev is signal_connect {
    param documentation = "Device an interrupt should be forwarded to "
                              + "(interrupt controller)";
}

bank regs {
    param register_size = 2;
    param byte_order = "big-endian";
    param use_io_memory = false;

    register counter   @ 0x0 "Counter register";
    register reference @ 0x2 "Reference counter register";
    register config    @ 0x6 "Configuration register" {
        field interrupt_enable @ [0]
            "If 1, interrupt is enabled.";
    }
}
```

**Application**: Structure the watchdog timer device following standard DML skeleton patterns with proper imports, bank definitions, and register declarations

## Device Example Analysis (via RAG Queries)

### Device-Specific Best Practices
**Query**: "Best practices for watchdog timer device modeling with Simics DML 1.4"  
**Source Type**: source  
**Key Patterns Observed**:
  * **Timer Counter Management**: Use `saved cycles_t` variables to track counter start time and value; calculate current counter based on cycle count
  * **Event-Based Timeout**: Use `after <cycles> cycles: method()` syntax to schedule timeout events; cancel with `cancel_after()`
  * **Interrupt Handling**: Connect to interrupt controller via `signal_connect` template; use `set_level(1)` to raise, `set_level(0)` to lower
  * **Register Write Side-Effects**: Override `write` method to trigger counter restart or event updates when configuration changes

**Code Examples**:

```dml
bank regs {
    // Records the time when the counter register was started.
    saved cycles_t counter_start_time;
    // Records the start value of the counter register.
    saved cycles_t counter_start_value;

    register counter is (get, read, write) {
        method write(uint64 value) {
            counter_start_value = value;
            restart();
        }

        method get() -> (uint64) {
            if (step.val == 0) {
                return counter_start_value;
            }

            local cycles_t now = SIM_cycle_count(dev.obj);
            return (now - counter_start_time) / step.val
                + counter_start_value;
        }

        method restart() {
            counter_start_time = SIM_cycle_count(dev.obj);
            update_event();
        }

        method update_event() {
            cancel_after();

            if (step.val == 0)
                return;

            local cycles_t now = SIM_cycle_count(dev.obj);
            local cycles_t cycles_left =
                (reference.val - counter_start_value) * step.val
                - (now - counter_start_time);
            after cycles_left cycles: on_match();
        }
    }
}
```

**Relevant Structures**: Timer device pattern with counter, reference, and configuration registers; event scheduling for timeout handling

**Application**: Apply timer-specific patterns to watchdog implementation with cycle-accurate counter decrement, timeout event scheduling, and interrupt generation

### Simics Device Reference Example
**Query**: "Simics device implementation example watchdog timer or similar peripheral"  
**Source Type**: source  
**Key Patterns Observed**:
  * **Bank Organization**: Separate register definitions from behavior implementation; use multiple bank blocks for clarity
  * **Saved State Variables**: Use `saved` keyword for checkpointable state (counter values, timestamps)
  * **Session State Variables**: Use `session` keyword for transient state (last initiator, temporary flags)
  * **Event Lifecycle**: Post events in `post_init()`, cancel in register write methods, update when configuration changes

**Code Examples**:

```dml
bank regs {
    session conf_object_t* last_initiator = NULL;
    
    method transaction_access(transaction_t *t, uint64 offset, void *aux)
           -> (exception_type_t) {
        last_initiator = SIM_transaction_initiator(t);
        return default(t, offset, aux);
    }
}

// Event definition
event tim_event is simple_time_event {
    method event() {
        regs.on_event();
    }
}

// Interrupt handling
if (regs.config.interrupt_enable.val) {
    log info, 4: "Raising interrupt";
    irq_dev.set_level(1);
    irq_dev.set_level(0);
}
```

**Applicable Patterns**: Transaction tracking, event-based timing, interrupt signaling, register field access

**Application**: Adapt timer/peripheral patterns to watchdog implementation with proper state management, event handling, and interrupt generation

### Register Implementation Patterns
**Query**: "DML register bank implementation patterns"  
**Source Type**: dml  
**Implementation Patterns**:
  * **Bank Parameters**: Define `register_size`, `byte_order`, `partial`, `use_io_memory` at bank level
  * **Register Arrays**: Use syntax `register name[i < size] @ (base + i * offset)` for register arrays
  * **Field Bit Ranges**: Declare fields with `@ [high:low]` syntax; access via `field.val`
  * **Template Instantiation**: Use `is (template1, template2)` to apply multiple templates to registers

**Code Examples**:

```dml
bank regs {
    param register_size = 8;
    param partial = true;
    param use_io_memory = false;

    register gcap_id    @ 0x0  "General Capabilities and Id Register";
    register gen_conf   @ 0x10 "General Configure Register";
    
    register tim_conf[i < num_of_timer] @ (0x100 + i * 0x20) 
                "Timer n Configuration and Capabilities";
    register tim_comp [i < num_of_timer] @ (0x108 + i * 0x20) 
                "Timer n Comparator Value Register";
}

bank regs {
    register config @ 0x6 "Configuration register" {
        field clear_on_match @ [1]
            "If 1, counter is cleared when counter matches reference.";
        field interrupt_enable @ [0]
            "If 1, interrupt is enabled.";
    }
}
```

**Application**: Implement watchdog register bank following standard patterns with appropriate parameters, register offsets, and field definitions

## Test Example Analysis (via RAG Queries)

### Simics Python Test Patterns
**Query**: "Simics Python test patterns and examples"  
**Source Type**: python  
**Key Test Patterns Observed**:
  * **Device Creation**: Use `simics.pre_conf_object()` to create pre-configuration objects, then `simics.SIM_add_configuration()` to instantiate
  * **Memory Mapping**: Configure `phys_mem.attr.map` with `[base_addr, device_obj, function, offset, size]` tuples
  * **Register Access**: Use `dev_util.Register_LE()` to create register accessors; call `.read()` and `.write()` methods
  * **Test Assertions**: Use `stest.expect_equal()`, `stest.expect_true()` for validation

**Code Examples**:

```python
import stest
import dev_util
import simics

# Create device
py_dev = simics.pre_conf_object('pyart', 'python_simple_serial')
phys_mem = simics.pre_conf_object('phys_mem', 'memory-space')
phys_mem.attr.map = [ [0x0000, py_dev, 0, 0, 0x10] ]

# Add clock
clock = simics.pre_conf_object('clock', 'clock', freq_mhz=1000)
py_dev.attr.queue = clock

# Instantiate
simics.SIM_add_configuration([clock, py_dev, phys_mem], None)

# Access registers
register = dev_util.Register_LE(py_dev.bank.regs, 0, size = 1)
a = register.read()
register.write(a + 1)
b = register.read()
stest.expect_equal(b, a + 1)
```

**Test Framework**: Uses `stest` module for assertions, `dev_util` for register access, `simics` for object creation

**Application**: Structure tests for watchdog timer following established test patterns with device creation, memory mapping, register access, and validation

### Device Testing Best Practices
**Query**: "Simics device testing best practices"  
**Source Type**: source  
**Best Practices Identified**:
  * **Info/Status Commands**: Verify that `info` and `status` commands are registered and execute without errors
  * **Object Lifecycle**: Test device creation, configuration, and deletion; verify cleanup in destroy methods
  * **Attribute Validation**: Test both direct attribute access and register-backed attributes for consistency
  * **Error Handling**: Use `stest.expect_log_mgr()` to verify expected error messages and log output

**Code Examples**:

```python
import stest
import info_status
import simics

# Create device
dev = create_sample_device()

# Verify info/status commands registered
info_status.check_for_info_status(['sample-device-class'])

# Test info and status commands
for obj in [dev]:
    for cmd in ['info', 'status']:
        try:
            simics.SIM_run_command(obj.name + '.' + cmd)
        except simics.SimExc_General as e:
            stest.fail(cmd + ' command failed: ' + str(e))

# Test error conditions
with stest.expect_log_mgr(dev, log_type="error", regex="expected pattern"):
    dev.some_invalid_operation()
```

**Applicable Practices**: Command registration verification, lifecycle testing, attribute consistency checks, error condition validation

**Application**: Apply comprehensive testing practices to ensure watchdog timer correctness, reliability, and proper error handling

## Additional Research (Requirement-Driven RAG Queries)

No additional RAG queries were needed beyond the 8 mandatory searches. The mandatory queries provided comprehensive coverage of:
- DML 1.4 language syntax and semantics
- Device modeling patterns and structure
- Timer/counter implementation approaches
- Register bank organization
- Interrupt handling mechanisms
- Python test frameworks and patterns
- Device testing best practices

All functional requirements from spec.md are addressed by the knowledge gathered from the mandatory queries.

## Architecture Decisions

### Decision: Use Event-Based Counter Decrement
- **Rationale**: Based on sample_timer_device example showing cycle-accurate counter management using `SIM_cycle_count()` and `after` events
- **Alternatives Considered**: Polling-based counter update (rejected - inefficient), tick-based decrement (rejected - less accurate)
- **Source**: RAG Query #4 (Device-Specific Best Practices) and #5 (Simics Device Reference)
- **Impact**: Enables accurate timeout simulation with minimal performance overhead; requires careful event management on register writes

### Decision: Separate Register Definition from Behavior
- **Rationale**: DML 1.4 best practice pattern observed in multiple device examples; improves code organization and readability
- **Alternatives Considered**: Inline all behavior in register declarations (rejected - less maintainable)
- **Source**: RAG Query #6 (Register Implementation Patterns)
- **Impact**: Cleaner code structure with register map defined first, then behavior implementations in separate bank blocks

### Decision: Use signal_connect Template for Interrupts
- **Rationale**: Standard Simics pattern for interrupt output; provides `set_level()` method for raising/lowering interrupts
- **Alternatives Considered**: Direct Simics API calls (rejected - less idiomatic), custom interface (rejected - unnecessary complexity)
- **Source**: RAG Query #4 (Device-Specific Best Practices)
- **Impact**: Simplified interrupt handling with standard Simics integration pattern

### Decision: Use saved cycles_t for Counter State
- **Rationale**: Enables checkpoint/restore support while maintaining cycle-accurate timing
- **Alternatives Considered**: Session variables (rejected - not checkpointed), tick counter (rejected - less accurate)
- **Source**: RAG Query #4 (Device-Specific Best Practices) and #5 (Simics Device Reference)
- **Impact**: Proper state persistence across checkpoints; requires calculation on each counter read

### Decision: Implement Lock Mechanism via Register Write Validation
- **Rationale**: Standard pattern for write-protected registers; check lock state in write methods
- **Alternatives Considered**: Bank-level write protection (rejected - too coarse-grained)
- **Source**: DML 1.4 Reference Manual (RAG Query #1) and register patterns (RAG Query #6)
- **Impact**: Fine-grained control over register write protection; requires lock state checks in each protected register

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

**Note**: All 8 mandatory RAG queries executed successfully. No additional requirement-driven queries were needed as the mandatory searches provided comprehensive coverage of all functional requirements.

## DML Best Practices Study Notes (T039)

**Source**: `.specify/memory/DML_Device_Development_Best_Practices.md`  
**Study Date**: Phase 3.3 - Before Implementation  
**Purpose**: Critical patterns and pitfalls to avoid in DML 1.4 device development

### Critical Syntax Rules

1. **Device Declaration** - NO BRACES:
   ```dml
   // ❌ WRONG (old DML style)
   device my_device { ... }
   
   // ✅ CORRECT (DML 1.4)
   device my_device;
   param classname = "my_device";
   ```

2. **File Structure**:
   ```dml
   dml 1.4;                           // MUST be first line
   import "simics/device-api.dml";    // Always needed
   device device_name;                 // Single line, no braces
   param classname = "device_name";    // Parameters at top level
   ```

3. **Register Declaration**:
   ```dml
   bank regs {
       param register_size = 4;        // Default register size
       param function = 0x1000;        // Base address (optional)
       
       register control @ 0x00 {       // @ for offset
           param size = 4;             // Size in bytes
           param desc = "Description"; // Always document
           param init_val = 0x0;       // Reset value
       }
   }
   ```

### Common Patterns Applied to Watchdog Timer

1. **Memory-Mapped Device Pattern**:
   - Use `bank` for register groups
   - Use `@` for register offsets
   - Use `param init_val` for reset values
   - **Application**: 21 registers in single bank at offsets 0x000-0xFFC

2. **Interrupt Device Pattern**:
   ```dml
   connect irq {
       param configuration = "optional";
       param c_type = "simple_interrupt";
   }
   
   method update_interrupt() {
       if (condition) {
           if (irq.signal) {
               irq.signal.signal_raise();
           }
       }
   }
   ```
   - **Application**: wdogint signal for first timeout

3. **Timer Device Pattern**:
   ```dml
   event timer_tick;
   
   method start_timer() {
       after (1.0) call timer_expired();
   }
   ```
   - **Application**: Counter decrement using `after` for timeout events

4. **Register Access Methods**:
   ```dml
   register data @ 0x00 {
       method write(uint64 value) {
           // Custom write logic
           this.val = value;
       }
       
       method read() -> (uint64) {
           // Custom read logic
           return this.val;
       }
   }
   ```
   - **Application**: WDOGLOAD (lock-protected), WDOGVALUE (calculated), WDOGINTCLR (write-only)

### Critical Compilation Requirements

1. **Compiler Flags** (from best practices):
   ```bash
   dmlc --simics-api=6 -I ../linux64/bin/dml/api/6/1.4 -I ../linux64/bin/dml/1.4 input.dml output
   ```

2. **UTF-8 Mode**: Set `PYTHONUTF8=1` environment variable

3. **Include Paths**: Both API and builtins paths required

### Common Pitfalls to Avoid

1. ❌ **Braces after device declaration** → Syntax error
2. ❌ **Missing include paths** → "cannot find dml-builtins.dml"
3. ❌ **Wrong UTF-8 mode** → "assert sys.flags.utf8_mode"
4. ❌ **Parameters inside device braces** → Use top-level params
5. ❌ **Forgetting `this.val =` in write methods** → Register won't update

### Best Practices for Watchdog Implementation

1. **Naming**: Use lowercase_with_underscores (sp805_wdt, wdogload, etc.)
2. **Documentation**: Every register needs `param desc`
3. **Logging**: Use appropriate levels (info, warning, error)
4. **Error Handling**: Validate values in write methods
5. **State Management**: Use `saved` for checkpointed state, `session` for transient

## DML Grammar Study Notes (T040)

**Source**: `.specify/memory/DML_grammar.md`  
**Study Date**: Phase 3.3 - Before Implementation  
**Purpose**: Complete DML 1.4 syntax specification for correct code generation

### Lexical Elements

**Keywords Used in Watchdog**:
- `device`, `param`, `bank`, `register`, `field`, `method`, `connect`, `event`
- `saved`, `session`, `local`, `if`, `return`, `log`, `after`

**Operators**:
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Bitwise: `&`, `|`, `^`, `~`, `<<`, `>>`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Assignment: `=`, `+=`, `-=`

### Grammar Rules Applied

1. **Top-Level Structure**:
   ```
   dml 1.4;
   [imports]
   device identifier;
   [device_statements]
   ```

2. **Register Declaration Syntax**:
   ```
   register identifier [array_spec] [size_spec] offset_spec [is template_list] object_body
   
   Examples:
   register control @ 0x008 { ... }
   register data size 4 @ 0x000 { ... }
   register id[i < 4] @ (0xFE0 + i * 4) { ... }
   ```

3. **Field Declaration Syntax**:
   ```
   field identifier @ [high:low] { ... }
   field identifier @ [bit] { ... }
   
   Example:
   field INTEN @ [0] { param desc = "Interrupt enable"; }
   field step_value @ [4:2] { param desc = "Clock divider"; }
   ```

4. **Method Declaration Syntax**:
   ```
   method identifier(parameters) [-> (return_type)] [throws] { statements }
   
   Examples:
   method write(uint64 value) { ... }
   method read() -> (uint64) { ... }
   method update_event() throws { ... }
   ```

5. **Event Declaration Syntax**:
   ```
   event identifier [is template_list] { method event() { ... } }
   
   Example:
   event timeout_event {
       method event() {
           log info: "Timeout occurred";
       }
   }
   ```

6. **After Statement Syntax**:
   ```
   after expression [unit]: statement
   
   Examples:
   after 100 cycles: on_timeout();
   after (cycles_left) cycles: on_match();
   ```

### Type System

**Basic Types**:
- `uint8`, `uint16`, `uint32`, `uint64` - Unsigned integers
- `int8`, `int16`, `int32`, `int64` - Signed integers
- `bool` - Boolean
- `cycles_t` - Simics cycle count type
- `conf_object_t*` - Simics object pointer

**Type Usage in Watchdog**:
- Counter values: `uint32`
- Cycle tracking: `cycles_t`
- Boolean flags: `bool`
- Register values: `uint64` (method parameters)

### Variable Declarations

1. **Saved Variables** (checkpointed):
   ```dml
   saved cycles_t counter_start_time;
   saved uint32 counter_start_value;
   saved bool interrupt_pending;
   ```

2. **Session Variables** (transient):
   ```dml
   session uint32 divider_counter;
   session conf_object_t* last_initiator;
   ```

3. **Local Variables** (method scope):
   ```dml
   method calculate() -> (uint64) {
       local cycles_t now = SIM_cycle_count(dev.obj);
       local uint32 elapsed = now - counter_start_time;
       return elapsed;
   }
   ```

### Control Flow

**If Statement**:
```dml
if (condition) {
    statement;
} else if (condition2) {
    statement;
} else {
    statement;
}
```

**Ternary Operator**:
```dml
local uint32 divider = (step_value == 0) ? 1 : (1 << step_value);
```

**Switch Statement** (not commonly used in device models)

### Logging Syntax

```dml
log info: "Message with value: 0x%x", value;
log warning: "Unusual condition";
log error: "Invalid operation";
log info, 2: "Verbose message (log level 2)";
```

### Key Syntax for Watchdog Implementation

1. **Register with Fields**:
   ```dml
   register WDOGCONTROL @ 0x008 {
       param size = 4;
       param init_val = 0x00000000;
       
       field step_value @ [4:2] "Clock divider selection";
       field RESEN @ [1] "Reset enable";
       field INTEN @ [0] "Interrupt enable";
       
       method write(uint64 value) {
           // Check lock state
           if (lock_state) {
               log warning: "Write to WDOGCONTROL ignored (locked)";
               return;
           }
           // Update fields
           default(value);
           // Handle INTEN transition
           if (value & 0x1) {
               reload_counter();
           }
       }
   }
   ```

2. **Read-Only Register**:
   ```dml
   register WDOGVALUE @ 0x004 is (read) {
       param size = 4;
       param init_val = 0xFFFFFFFF;
       
       method read() -> (uint64) {
           return calculate_counter_value();
       }
   }
   ```

3. **Constant Register**:
   ```dml
   register WDOGPERIPHID0 @ 0xFE0 is (read_only) {
       param size = 4;
       param init_val = 0x24;
   }
   ```

### Implementation Strategy

### Device Architecture
The watchdog timer will be implemented as a DML 1.4 device with:
- **Single register bank** containing all 21 registers (control, data, identification)
- **Event-based counter** using Simics cycle counting for accurate timing
- **Signal outputs** for interrupt (wdogint) and reset (wdogres) using signal_connect template
- **Lock mechanism** implemented via register write validation
- **Integration test mode** with direct signal control via WDOGITOP register

### Register Design Approach
- **Register map definition** in first bank block with offsets, sizes, and descriptions
- **Behavior implementation** in second bank block with read/write method overrides
- **Field declarations** using `@ [high:low]` syntax for bit-level access
- **Reset values** specified via `param init_val` for each register
- **Read-only registers** using `is read_only` template for identification registers

### Counter Implementation
- **Saved state**: `counter_start_time` (cycles_t) and `counter_value` (uint32)
- **Clock divider**: Internal divider counter based on step_value field
- **Counter read**: Calculate current value from start time and divider
- **Counter reload**: On INTEN transition or WDOGINTCLR write
- **Timeout detection**: Event scheduled based on counter value and divider

### Interrupt and Reset Logic
- **First timeout**: Assert wdogint if INTEN=1; set WDOGRIS flag
- **Second timeout**: Assert wdogres if RESEN=1; keep asserted until device reset
- **Interrupt clear**: Write to WDOGINTCLR clears interrupt and reloads counter
- **Masked status**: WDOGMIS = WDOGRIS AND INTEN

### Test Strategy
Based on Python test patterns discovered:
- **Unit tests**: Register read/write, field access, reset behavior
- **Functional tests**: Counter decrement, timeout generation, interrupt assertion
- **Integration tests**: Lock mechanism, integration test mode, checkpoint/restore
- **Edge case tests**: Clock divider settings, rapid lock/unlock, simultaneous timeouts

### Next Steps
Phase 1 should focus on:
1. **Data model definition**: Complete register map with all 21 registers, fields, and reset values
2. **Contract specifications**: Register access contracts, interrupt behavior contracts, timing contracts
3. **Quickstart guide**: User validation steps for basic watchdog operation and timeout testing
4. **Constitutional compliance**: Verify device-first, interface-first, test-first principles are followed
