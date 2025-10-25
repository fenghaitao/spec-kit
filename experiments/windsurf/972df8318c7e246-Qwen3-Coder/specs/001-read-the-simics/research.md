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

## DML Best Practices Study Notes

### DML Compilation Setup
- Key compiler flags: `--simics-api=6`, `-I ../linux64/bin/dml/api/6/1.4`, `-I ../linux64/bin/dml/1.4`
- Environment setup: Ensure UTF-8 mode with `export PYTHONUTF8=1`

### Basic DML Syntax
- Device declaration: `dml 1.4;` followed by `device device_name;`
- Register banks: `bank bank_name { ... }` with parameters like `register_size` and `byte_order`
- Register declarations: `register reg_name size N @ offset { ... }`
- Field declarations: `field field_name @ [msb:lsb];`
- Method declarations: `method method_name(parameters) { ... }`
- Session variables: `session type var_name = initial_value;`

### Device Structure
- Device object is top-level scope
- Register banks group related registers
- Registers contain fields for bit-level access
- Methods implement custom behavior
- Session variables store device state

### Common Patterns
- Register read/write methods for custom behavior
- Event handling with `after` keyword
- Signal connections using `connect` and `implement`
- State management with session variables
- Error handling with try/catch blocks

### Best Practices
- Use descriptive names for registers, fields, and methods
- Initialize session variables in `init` method
- Handle errors gracefully with appropriate logging
- Use constants for magic numbers and offsets
- Follow consistent formatting and commenting

## DML Grammar Study Notes

### Language Characteristics
- Version: DML 1.4 for Simics simulator
- Paradigm: Declarative with imperative elements
- Type System: Static typing with C-like declarations
- Compilation: Compiles to C code interfacing with Simics API

### Key Keywords
- Device declaration: `device`, `template`, `is`
- Object types: `register`, `field`, `bank`, `attribute`, `connect`, `event`
- Control flow: `if`, `else`, `while`, `for`, `switch`, `try`, `catch`
- Variable declarations: `session`, `local`, `static`, `param`
- Methods: `method`, `inline`, `return`

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `++`, `--`
- Bitwise: `&`, `|`, `^`, `~`, `<<`, `>>`
- Logical: `&&`, `||`, `!`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`

### Register and Field Syntax
- Register declaration: `register name [size N] [@ offset] [is templates] ["description"];`
- Field declaration: `field name [@ [msb:lsb]] [is templates] ["description"];`
- Bank declaration: `bank name { parameters; registers; }`

### Method Syntax
- Method declaration: `method name(parameters) [throws] { body }`
- Method with return: `method name(parameters) -> (return_types) [throws] { body }`
- Inline methods: `inline method name(inline parameters) -> (return_types) { body }`

### Event Handling
- Event declaration: `event name { parameters; method event(void *data) { body } }`
- Posting events: `after time_expression: method_call;`
- Canceling events: `cancel_after();`

## Environment Discovery

### Simics Version
Simics Base package information:
- Package Name: Simics-Base
- Package Number: 1000
- Package Version: 7.57.0

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

### Available Platforms
Available Local Manifests:
- Name: Public Intel® Simics® Quick Start Platform (QSP-x86) - 7
- Group: qsp-x86-public-7

## Documentation Access (via RAG Queries)

### DML 1.4 Reference Manual
- **Query**: "DML 1.4 reference manual register and device modeling"
- **Source Type**: docs
- **Key Findings**:
  * DML 1.4 has significant syntax changes from DML 1.2, including method declarations, inline syntax, and object arrays
  * Register declarations use `@` before bit ranges for fields
  * Methods must explicitly return values with `return` statement
  * Session variables replace data declarations
  * Template inheritance is stricter with explicit hierarchy checking
- **References**: DML 1.4 Reference Manual, Changes from DML 1.2 to DML 1.4
- **Application**: Structure the watchdog timer with appropriate register definitions and field breakdowns following DML 1.4 syntax
- **Note**: This provides initial context; detailed grammar rules from DML_grammar.md will be studied in tasks phase

### Model Builder User Guide
- **Query**: "Simics Model Builder device creation and structure patterns"
- **Source Type**: docs
- **Key Findings**:
  * Device objects inherit `init`, `post_init`, and `destroy` templates
  * Universal templates like `name`, `desc`, `documentation` are available for all objects
  * Device lifecycle methods (`init`, `post_init`, `destroy`) are automatically called
  * Register templates provide standard implementations for behavior
- **References**: DML Built-ins, Standard Templates
- **Application**: Follow established patterns for device structure and implementation approach
- **Note**: This provides architectural context; detailed best practices from DML_Device_Development_Best_Practices.md will be studied in tasks phase

### DML Device Template
- **Query**: "DML device template base structure and skeleton"
- **Source Type**: dml
- **Key Patterns**:
  * Device declaration with `dml 1.4;` and `device device_name;`
  * Register banks with parameters (`register_size`, `byte_order`)
  * Register declarations with size, offset, and behavior templates
  * Import statements for utility functions and interfaces
- **Code Examples**:
  ```dml
  dml 1.4;
  
  device sample_device_dml;
  
  // short, one-line description
  param desc = "sample DML device";
  
  // long description
  param documentation = "This is a very simple device.";
  
  import "sample-interface.dml";
  
  // simple attribute
  attribute int_attr is int64_attr "An integer attribute" {
      method set(attr_value_t val) throws {
          default(val);
          log info: "attribute int_attr updated";
      }
  }
  
  // simple interface implementation
  implement sample {
      saved int call_count = 0;
      method simple_method(int arg) {
          log info: "sample_method() was called with arg %d", arg;
              // checkpointed variable
              call_count++;
      }
  }
  
  // example bank with a register
  bank regs {
      param desc = dev.desc + "custom desc";
      register r1 size 4 @ 0x0000 is read {
          method read() -> (uint64) {
              log info: "read from r1";
              return 42 + sample.call_count;
          }
      }
  }
  ```
- **Application**: Structure the watchdog timer device following standard DML skeleton patterns

## Device Example Analysis (via RAG Queries)

### Device-Specific Best Practices
- **Query**: "Best practices for watchdog device modeling with Simics DML 1.4"
- **Source Type**: source
- **Key Patterns Observed**:
  * Use of `bank` for register organization with `register_size` and `byte_order` parameters
  * Implementation of `read` and `write` methods for custom register behavior
  * Use of `saved` variables for state that persists across checkpoints
  * Event handling with `after` for timed operations
  * Signal connections using `connect` and `implement signal`
- **Code Examples**:
  ```dml
  bank regs {
      param register_size = 2;
      param byte_order = "big-endian";
      param use_io_memory = false;
  
      // Records the time when the counter register was started.
      saved cycles_t counter_start_time;
      // Records the start value of the counter register.
      saved cycles_t counter_start_value;
  
      register counter   @ 0x00 "Counter register";
      register reference @ 0x02 "Reference counter register";
      register step      @ 0x04
          "Counter is incremented every STEP clock cycles. 0 means stopped.";
      register config    @ 0x06 "Configuration register" {
          field clear_on_match @ [1]
              "If 1, counter is cleared when counter matches reference.";
          field interrupt_enable @ [0]
              "If 1, interrupt is enabled.";
      }
  }
  ```
- **Relevant Structures**: Timer-based devices with interrupt generation and register-based configuration
- **Application**: Apply timer device patterns to implement watchdog timeout functionality

### Simics Device Reference Example
- **Query**: "Simics device implementation example watchdog or similar peripheral"
- **Source Type**: source
- **Key Patterns Observed**:
  * Register banks with multiple registers and fields
  * Event handling for timed operations using `after` syntax
  * Interrupt generation through signal connections
  * Register read/write methods with custom behavior
  * Use of `SIM_cycle_count()` for timing
- **Code Examples**:
  ```dml
  bank regs {
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
              return (now - counter_start_time) / step.val
                  + counter_start_value;
          }
  
          method read() -> (uint64) {
              return get();
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
                  (reference.val - counter_start_value) * step.val
                  - (now - counter_start_time);
              after cycles_left cycles: on_match();
          }
      }
  }
  ```
- **Applicable Patterns**: Timer-based event handling, interrupt generation, register-based configuration
- **Application**: Adapt timer device patterns to watchdog implementation requirements

### Register Implementation Patterns
- **Query**: "DML register bank implementation patterns"
- **Source Type**: dml
- **Implementation Patterns**:
  * Register bank definition with parameters (`register_size`, `byte_order`)
  * Register access methods (`read`, `write`, `get`, `set`)
  * Register callbacks and custom behaviors
  * Field definitions and bit-level access
- **Code Examples**:
  ```dml
  bank logger {
      param desc = "bank logging all accesses without storing data";
      param documentation = "Register bank that logs all accesses but does not actually " +
                            "store any data";
      
      // Write is called for actual write operations
      method write(uint64 offset, uint64 value, uint64 enabled_bytes,void *aux) throws {
          log info, 1: "Write access to offset 0x%llx, size=0x%llx, value=0x%llx", 
                       offset, size_from_enabled(enabled_bytes), value; 
      }
  
      // Read is called for actual read operations
      method read(uint64 offset, uint64 enabled_bytes, void *aux) -> (uint64) throws {
          local uint64 value = 0xc001d00ddeadbeef & enabled_bytes;
          log info, 1: "Read access to offset 0x%llx, size=0x%llx -> read value=0x%llx", 
                       offset, size_from_enabled(enabled_bytes), value; 
          return value;
      }
  }
  ```
- **Application**: Implement watchdog register bank following standard patterns with appropriate customization

## Test Example Analysis (via RAG Queries)

### Simics Python Test Patterns
- **Query**: "Simics Python test patterns and examples"
- **Source Type**: python
- **Key Test Patterns Observed**:
  * Test suite structure with `create_device()` functions
  * Device instance creation using `simics.SIM_create_object()`
  * Register access testing using `dev_util.Register_LE()`
  * Assertions and validation using `stest.expect_equal()`
- **Code Examples**:
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
  ```
- **Test Framework**: stest, dev_util, simics modules
- **Application**: Structure tests for watchdog timer following established test patterns and conventions

### Device Testing Best Practices
- **Query**: "Simics device testing best practices"
- **Source Type**: source
- **Best Practices Identified**:
  * Test coverage strategies with register read/write validation
  * Validation approaches for device behavior verification
  * Error condition testing and edge case handling
  * Use of `stest.expect_equal()` for assertions
- **Code Examples**:
  ```python
  import stest
  import info_status
  import simics
  import sample_device_with_external_lib_common
  
  # Create an instance of each object defined in this module
  dev = sample_device_with_external_lib_common.create_sample_device_with_external_lib()
  
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
- **Applicable Practices**: Register access testing, behavior verification, error handling
- **Application**: Apply comprehensive testing practices to ensure watchdog timer correctness and reliability

## Additional Research (Requirement-Driven RAG Queries)

### Additional Query #9: Watchdog timer interrupt and reset generation
- **Query**: "Simics DML 1.4 interrupt and reset signal generation patterns"
- **Source Type**: source
- **Match Count**: 5
- **Requirement Addressed**: FR-003 (interrupt signal on first timeout) and FR-004 (reset signal on second timeout)
- **Knowledge Gap**: How to properly implement interrupt and reset signal generation in DML 1.4
- **Key Findings**:
  * Use `connect` with `signal_connect` template for interrupt/reset signal connections
  * Use `set_level(1)` and `set_level(0)` to assert and deassert signals
  * Signal connections automatically handle the interface methods
- **Code Examples**:
  ```dml
  connect irq_dev is signal_connect {
      param documentation = "Device an interrupt should be forwarded to "
                                + "(interrupt controller)";
  }
  
  // In method where interrupt should be generated:
  if (regs.config.interrupt_enable.val) {
      log info, 4: "Raising interrupt";
      irq_dev.set_level(1);
      irq_dev.set_level(0);
  }
  ```
- **Application**: Implement interrupt and reset signal generation for the watchdog timer using established patterns

### Additional Query #10: Watchdog timer lock mechanism implementation
- **Query**: "Simics DML 1.4 register protection and lock mechanisms"
- **Source Type**: source
- **Match Count**: 5
- **Requirement Addressed**: FR-006 (lock protection mechanism using magic unlock value 0x1ACCE551)
- **Knowledge Gap**: How to implement register write protection based on a lock register
- **Key Findings**:
  * Use conditional logic in register write methods to check lock status
  * Implement lock state as a session variable
  * Return early from write methods when locked
- **Code Examples**:
  ```dml
  session bool registers_locked = true;
  
  register protected_reg is write {
      method write(uint64 value) {
          if (registers_locked) {
              log info: "Write to protected register ignored - device locked";
              return;
          }
          default(value);
      }
  }
  
  register lock_reg is write {
      method write(uint64 value) {
          if (value == 0x1ACCE551) {
              registers_locked = false;
              log info: "Device unlocked";
          } else {
              registers_locked = true;
              log info: "Device locked";
          }
          default(value);
      }
  }
  ```
- **Application**: Implement the lock protection mechanism for watchdog timer registers

## Architecture Decisions

### Decision: Use timer-based event handling
- **Rationale**: The watchdog timer requires precise timing for timeout detection, which is best implemented using DML's event handling mechanisms with `after` syntax and `SIM_cycle_count()`
- **Alternatives Considered**: Polling-based approach or external timer
- **Source**: RAG query results for timer device examples
- **Impact**: Provides accurate timing behavior with minimal simulation overhead

### Decision: Implement register lock mechanism with session variable
- **Rationale**: The lock mechanism requires persistent state that can be checked during register writes, which is best implemented using a `session` variable
- **Alternatives Considered**: Attribute-based approach
- **Source**: RAG query results for register protection patterns
- **Impact**: Provides efficient lock checking with clear state management

### Decision: Use signal connections for interrupt/reset outputs
- **Rationale**: The watchdog timer needs to generate interrupt and reset signals that can be connected to other devices, which is best implemented using DML's `connect` and `signal` interface
- **Alternatives Considered**: Direct API calls
- **Source**: RAG query results for interrupt generation patterns
- **Impact**: Provides standard Simics interface compatibility and flexible connection options

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
| 9 | Interrupt/Reset Generation | source | 5 | ✅ | Additional Research |
| 10 | Lock Mechanism Implementation | source | 5 | ✅ | Additional Research |

**Note**: Queries 9+ are requirement-driven queries executed to address specific knowledge gaps identified from the "Functional Requirements" section in spec.md. Each additional query documents which requirement it addresses and what knowledge gap it fills.

## Implementation Strategy

### Device Architecture
The watchdog timer will be implemented as a standalone DML 1.4 device with:
- Register bank containing all 21 required registers
- Timer event handling using cycle-based timing
- Interrupt and reset signal generation through signal connections
- Lock protection mechanism for register writes
- Integration test mode support

### Register Design Approach
- Implement all 21 registers as specified in the hardware documentation
- Use appropriate register templates for read/write behavior
- Implement custom read/write methods where needed for special behavior
- Use fields for bit-level access to control registers

### Test Strategy
- Create Python test scripts using `dev_util.Register_LE()` for register access testing
- Implement behavior verification tests for timer functionality
- Test interrupt and reset signal generation
- Verify lock protection mechanism
- Test integration test mode functionality

### Next Steps
- Create data-model.md with detailed register definitions
- Create contracts for register access behavior
- Create quickstart.md with user validation steps
- Generate tasks.md with implementation tasks
