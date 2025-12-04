<<<<<<< HEAD
# Simics Model Development Constitution

## Core Principles

### I. Device-First Development
Every hardware component starts as a standalone device model—no exceptions. This forces modular design from the start:

- Device models must be self-contained DML modules
- Each device model is independently testable in isolation
- Clear hardware abstraction boundaries with well-defined interfaces
- Device models expose functionality through standardized Simics interfaces
- No monolithic system models - compose from discrete device components

### II. Interface-First Architecture
All device components communicate through well-defined, testable hardware interfaces:

- DML Interface: Registers, ports, and connections defined before logic implementation
- Hardware interfaces specified before behavioral modeling
- Memory-mapped interfaces with clear address space definitions
- Inter-device communication through standardized Simics interfaces
- Register maps documented before register implementation
- Signal and bus protocols defined before device logic

### III. Test-First Development (NON-NEGOTIABLE)
TDD mandatory for all Simics device development:

- Specification tests written → Hardware behavior verified → Tests fail → Then implement DML
- Register access tests, device behavior tests, integration tests with other devices
- Functional simulation validation against hardware specification
- Test vectors derived from hardware specification documents
- Red-Green-Refactor cycle: Test → Fail → Implement → Pass → Refactor
- Behavior verification before implementation complexity

### IV. Specification-Driven Implementation
Base all implementation decisions strictly on provided hardware specifications:

- Hardware specifications drive register definitions and device behavior
- Software-visible behavior must match specification exactly
- Internal implementation may be simplified if not software-visible
- Mark unclear hardware behaviors with [NEEDS CLARIFICATION] and implement as TODO
- No assumptions beyond documented hardware specification
- Reference specification sections in DML comments

### V. Integration Testing Focus
Focus on real-world hardware integration scenarios:

- Device-to-device communication testing
- Software driver compatibility testing
- Platform integration validation
- Memory subsystem interaction testing
- Bus protocol compliance verification
- Interrupt handling and timing validation

### VI. Observability and Transparency
Everything must be inspectable and debuggable in simulation:

- Register states must be inspectable at runtime
- Device state changes must be traceable
- Simulation events must be observable
- Debug interfaces for device inspection
- Comprehensive logging of device operations
- State visibility through Simics CLI and debugging tools

### VII. Versioning and Evolution
MAJOR.MINOR.BUILD format with clear compatibility contracts:

- Device model versioning aligned with hardware specification versions
- Register interface changes require version increment
- Simulation compatibility maintained across device model versions
- Backward compatibility for simulation checkpoints
- Clear migration paths for specification updates

### VIII. Simplicity and Incremental Development
Start simple, add complexity only when proven necessary:

- Model only software-visible behaviors initially
- Add internal complexity only when required for accuracy
- Prefer functional correctness over implementation detail accuracy
- Implement clear abstractions before detailed behaviors
- YAGNI principles for device features - implement what's specified
- Single responsibility per device model and register

### IX. Simics Excellence
Leverage Simics domain expertise and best practices:

- Follow DML coding standards and patterns
- Use Simics templates and utility functions
- Implement proper state management for checkpointing
- Ensure timing and event handling accuracy
- Optimize for simulation performance while maintaining accuracy
- Leverage Simics debugging and inspection capabilities

## Technical Implementation Rules

### File System Organization

#### Editable Files (Permitted Modifications)

✅ **DML Device Implementation**
- Location: `simics-project/modules/<device_name>/<device_name>.dml`
- Purpose: Device behavior, register side-effects, timer logic
- Rule: This is the PRIMARY implementation file for device logic

✅ **Python Unit Tests**
- Location: `simics-project/modules/<device_name>/test/*.py`
- Pattern: `s-<feature>.py` (one test function per file)
- Purpose: Functional validation of device behavior

#### Protected Files (DO NOT MODIFY)

❌ **Auto-Generated DML Files**
- `<device_name>-glue.dml` - Generated from IP-XACT during build
- `<device_name>-dia.dml` - Defines register interface from IP-XACT
- `<device_name>-registers.dml` - Defines register skeleton from IP-XACT
- **Reason**: These files are regenerated on every build. Manual changes will be lost.

❌ **Build Configuration Files**
- `Makefile`, `CMakeLists.txt`, `MODULEINFO`, `MODULEDEPS`
- **Reason**: Build system is pre-configured for Simics project structure

❌ **IP-XACT XML Files**
- `<device_name>.xml` and other register specification files
- **Reason**: These are specification artifacts from the specify phase

### DML Import Statements (CRITICAL)

**ABSOLUTE REQUIREMENT**: Keep ALL import statements intact - NEVER remove or comment out:

```dml
import "<device_name>-glue.dml"; // Auto-generated - register association
import "<device_name>-dia.dml";  // Defines register interface from IP-XACT
import "simics/devs/signal.dml"; // Defines signal interfaces (interrupts)
```
or
```
import "<device_name>-registers.dml"; // Defines register skeleton from IP-XACT
import "simics/devs/signal.dml";      // Defines signal interfaces (interrupts)
```

**Why This Matters**:
- Register map: Without <device_name>-glue.dml, register interface/storage association are not resolved
- Register Interface: Without <device_name>-dia.dml, register template won't be available
- Register Skeleton: Without <device_name>-registers.dml, register skeleton won't be available
- Signal Interfaces: Without signal.dml, interrupt handling won't compile

### Timer Device Implementation Pattern

**REQUIRED**: Use DML `event` objects with explicit timestamp management

```dml
// ✅ CORRECT: Event-based timer
event timeout_event;

method schedule_timeout() {
    local double seconds = calculate_timeout_seconds();
    after (seconds) call timeout_event;
}
```

**REQUIRED**: Use `SIM_time()` for elapsed time calculations

```dml
// ✅ CORRECT: Timestamp-based calculation
method read_remaining_value() -> (uint32) {
    local double elapsed = SIM_time() - timer_start_time;
    return convert_to_ticks(timeout_duration - elapsed);
}
```

**FORBIDDEN**: Storing counter values in `saved uint32` variables
```dml
// ❌ WRONG: Breaks on checkpoint restore
saved uint32 current_counter;  // Don't do this!
```

### Python Test File Structure

**Pattern**: `s-<feature>.py` (one test function per file)

**Required Structure**:
```python
# Device instantiation
device = SIM_create_object("test_dev", "dev0", [])

# Configure clock queue (REQUIRED for time-based tests)
device.queue = conf.sim.queue

# Test with assertions
SIM_write_phys_memory(device, ADDR, value, 4)
result = SIM_read_phys_memory(device, ADDR, 4)
assert result == expected, f"Expected {expected}, got {result}"
```

### Forbidden Actions (Complete List)

#### ❌ File System Violations
- Removing or commenting out ANY import statements
- Creating new `.dml` files without explicit approval
- Modifying auto-generated files (`-registers.dml`, `-dia.dml`, `-glue.dml`)
- Editing build configuration files
- Modifying IP-XACT XML during implementation

#### ❌ Implementation Anti-Patterns
- Storing counter/timer values in `saved uint32` variables
- Using polling loops or busy-wait patterns
- Implementing cycle-accurate timing (use functional model)
- Adding checkpoint/restore logic (Simics handles automatically)
- Making assumptions beyond hardware specification

#### ❌ Test Anti-Patterns
- Multiple test functions in one file
- Tests without clock queue configuration
- Tests without clear assertions
- Tests that don't validate time-based behavior

### Build and Validation Commands

**Building**:
```bash
cd simics-project
make <device_name>
```

**Testing**:
```bash
cd simics-project/
./bin/test-runner --suite modules/<device_name>/test
```

### Compliance Checklist

Before submitting any implementation, verify:

- [ ] ✅ All import statements present and intact
- [ ] ✅ Only permitted files modified (`.dml` implementation, `.py` tests)
- [ ] ✅ No auto-generated files edited
- [ ] ✅ Timer uses `event` objects with timestamps
- [ ] ✅ No `saved uint32` for counter/timer state
- [ ] ✅ Tests follow `s-<feature>.py` pattern
- [ ] ✅ Tests configure clock queue
- [ ] ✅ Device builds successfully
- [ ] ✅ All tests pass

## Constitutional Compliance Framework

### Specification Phase
- All device projects begin with hardware specification templates
- Device specifications include register maps, interface definitions, and behavioral requirements
- Mark ambiguities with [NEEDS CLARIFICATION] for hardware specification gaps

### Planning Phase
- Constitutional compliance verification for Simics device development
- Technical translation from hardware specifications to DML implementation plans
- Behavioral testing strategy focused on software-visible device functionality
- **Mandatory**: Reference technical rules and forbidden actions in proposals

### Implementation Phase
- Simics-specific task generation following device modeling best practices
- Adherence to DML standards while maintaining constitutional principles
- Consistent documentation and validation approaches across all device models
- **Mandatory**: Verify compliance checklist before archiving

## Amendment Process

Modifications to this constitution require:
- Explicit documentation of the rationale for change
- Review and approval by Simics development team
- Backwards compatibility assessment with existing device models
- Update of all dependent templates and documentation

## Governance

This constitution supersedes all other Simics device development practices. All specification, planning, task generation, and implementation must verify constitutional compliance. When specific device requirements conflict with constitutional principles, the constitution takes precedence unless explicitly documented and justified.

**Version**: 5.0.0 | **Ratified**: 2025-12-03 | **Last Amended**: 2025-12-03

*Major version increment adds comprehensive technical implementation rules extracted from prompt templates for agent autonomy.*
||||||| parent of 28c80a59 (Minor fix and update for task done and refer to best practice)
# Simics Model Development Constitution

## Core Principles

### I. Device-First Development
Every hardware component starts as a standalone device model—no exceptions. This forces modular design from the start:

- Device models must be self-contained DML modules
- Each device model is independently testable in isolation
- Clear hardware abstraction boundaries with well-defined interfaces
- Device models expose functionality through standardized Simics interfaces
- No monolithic system models - compose from discrete device components

### II. Interface-First Architecture
All device components communicate through well-defined, testable hardware interfaces:

- DML Interface: Registers, ports, and connections defined before logic implementation
- Hardware interfaces specified before behavioral modeling
- Memory-mapped interfaces with clear address space definitions
- Inter-device communication through standardized Simics interfaces
- Register maps documented before register implementation
- Signal and bus protocols defined before device logic

### III. Test-First Development (NON-NEGOTIABLE)
TDD mandatory for all Simics device development:

- Specification tests written → Hardware behavior verified → Tests fail → Then implement DML
- Register access tests, device behavior tests, integration tests with other devices
- Functional simulation validation against hardware specification
- Test vectors derived from hardware specification documents
- Red-Green-Refactor cycle: Test → Fail → Implement → Pass → Refactor
- Behavior verification before implementation complexity

### IV. Specification-Driven Implementation
Base all implementation decisions strictly on provided hardware specifications:

- Hardware specifications drive register definitions and device behavior
- Software-visible behavior must match specification exactly
- Internal implementation may be simplified if not software-visible
- Mark unclear hardware behaviors with [NEEDS CLARIFICATION] and implement as TODO
- No assumptions beyond documented hardware specification
- Reference specification sections in DML comments

### V. Integration Testing Focus
Focus on real-world hardware integration scenarios:

- Device-to-device communication testing
- Software driver compatibility testing
- Platform integration validation
- Memory subsystem interaction testing
- Bus protocol compliance verification
- Interrupt handling and timing validation

### VI. Observability and Transparency
Everything must be inspectable and debuggable in simulation:

- Register states must be inspectable at runtime
- Device state changes must be traceable
- Simulation events must be observable
- Debug interfaces for device inspection
- Comprehensive logging of device operations
- State visibility through Simics CLI and debugging tools

### VII. Versioning and Evolution
MAJOR.MINOR.BUILD format with clear compatibility contracts:

- Device model versioning aligned with hardware specification versions
- Register interface changes require version increment
- Simulation compatibility maintained across device model versions
- Backward compatibility for simulation checkpoints
- Clear migration paths for specification updates

### VIII. Simplicity and Incremental Development
Start simple, add complexity only when proven necessary:

- Model only software-visible behaviors initially
- Add internal complexity only when required for accuracy
- Prefer functional correctness over implementation detail accuracy
- Implement clear abstractions before detailed behaviors
- YAGNI principles for device features - implement what's specified
- Single responsibility per device model and register

### IX. Simics Excellence
Leverage Simics domain expertise and best practices:

- Follow DML coding standards and patterns
- Use Simics templates and utility functions
- Implement proper state management for checkpointing
- Ensure timing and event handling accuracy
- Optimize for simulation performance while maintaining accuracy
- Leverage Simics debugging and inspection capabilities

## Technical Implementation Rules

### File System Organization

#### Editable Files (Permitted Modifications)

✅ **DML Device Implementation**
- Location: `simics-project/modules/<device_name>/<device_name>.dml`
- Purpose: Device behavior, register side-effects, timer logic
- Rule: This is the PRIMARY implementation file for device logic

✅ **Python Unit Tests**
- Location: `simics-project/modules/<device_name>/test/*.py`
- Pattern: `s-<feature>.py` (one test function per file)
- Purpose: Functional validation of device behavior

#### Protected Files (DO NOT MODIFY)

❌ **Auto-Generated DML Files**
- `<device_name>-glue.dml` - Generated from IP-XACT during build
- `<device_name>-dia.dml` - Defines register interface from IP-XACT
- `<device_name>-registers.dml` - Defines register skeleton from IP-XACT
- **Reason**: These files are regenerated on every build. Manual changes will be lost.

❌ **Build Configuration Files**
- `Makefile`, `CMakeLists.txt`, `MODULEINFO`, `MODULEDEPS`
- **Reason**: Build system is pre-configured for Simics project structure

❌ **IP-XACT XML Files**
- `<device_name>.xml` and other register specification files
- **Reason**: These are specification artifacts from the specify phase

### DML Import Statements (CRITICAL)

**ABSOLUTE REQUIREMENT**: Keep ALL import statements intact - NEVER remove or comment out:

```dml
import "<device_name>-glue.dml"; // Auto-generated - register association
import "<device_name>-dia.dml";  // Defines register interface from IP-XACT
import "simics/devs/signal.dml"; // Defines signal interfaces (interrupts)
```
or
```
import "<device_name>-registers.dml"; // Defines register skeleton from IP-XACT
import "simics/devs/signal.dml";      // Defines signal interfaces (interrupts)
```

**Why This Matters**:
- Register map: Without <device_name>-glue.dml, register interface/storage association are not resolved
- Register Interface: Without <device_name>-dia.dml, register template won't be available
- Register Skeleton: Without <device_name>-registers.dml, register skeleton won't be available
- Signal Interfaces: Without signal.dml, interrupt handling won't compile

### Timer Device Implementation Pattern

**REQUIRED**: Use DML `event` objects with explicit timestamp management

```dml
// ✅ CORRECT: Event-based timer
event timeout_event;

method schedule_timeout() {
    local double seconds = calculate_timeout_seconds();
    after (seconds) call timeout_event;
}
```

**REQUIRED**: Use `SIM_time()` for elapsed time calculations

```dml
// ✅ CORRECT: Timestamp-based calculation
method read_remaining_value() -> (uint32) {
    local double elapsed = SIM_time() - timer_start_time;
    return convert_to_ticks(timeout_duration - elapsed);
}
```

**FORBIDDEN**: Storing counter values in `saved uint32` variables
```dml
// ❌ WRONG: Breaks on checkpoint restore
saved uint32 current_counter;  // Don't do this!
```

### Python Test File Structure

**Pattern**: `s-<feature>.py` (one test function per file)

**Required Structure**:
```python
# Device instantiation
device = SIM_create_object("test_dev", "dev0", [])

# Configure clock queue (REQUIRED for time-based tests)
device.queue = conf.sim.queue

# Test with assertions
SIM_write_phys_memory(device, ADDR, value, 4)
result = SIM_read_phys_memory(device, ADDR, 4)
assert result == expected, f"Expected {expected}, got {result}"
```

### Forbidden Actions (Complete List)

#### ❌ File System Violations
- Removing or commenting out ANY import statements
- Creating new `.dml` files without explicit approval
- Modifying auto-generated files (`-registers.dml`, `-dia.dml`, `-glue.dml`)
- Editing build configuration files
- Modifying IP-XACT XML during implementation

#### ❌ Implementation Anti-Patterns
- Storing counter/timer values in `saved uint32` variables
- Using polling loops or busy-wait patterns
- Implementing cycle-accurate timing (use functional model)
- Adding checkpoint/restore logic (Simics handles automatically)
- Making assumptions beyond hardware specification

#### ❌ Test Anti-Patterns
- Multiple test functions in one file
- Tests without clock queue configuration
- Tests without clear assertions
- Tests that don't validate time-based behavior

### Build and Validation Commands

**Building**:
```bash
cd simics-project
make <device_name>
```

**Testing**:
```bash
cd simics-project/
./bin/test-runner --suite modules/<device_name>/test
```

### Compliance Checklist

Before submitting any implementation, verify:

- [ ] ✅ All import statements present and intact
- [ ] ✅ Only permitted files modified (`.dml` implementation, `.py` tests)
- [ ] ✅ No auto-generated files edited
- [ ] ✅ Timer uses `event` objects with timestamps
- [ ] ✅ No `saved uint32` for counter/timer state
- [ ] ✅ Tests follow `s-<feature>.py` pattern
- [ ] ✅ Tests configure clock queue
- [ ] ✅ Device builds successfully
- [ ] ✅ All tests pass

## Constitutional Compliance Framework

### Specification Phase
- All device projects begin with hardware specification templates
- Device specifications include register maps, interface definitions, and behavioral requirements
- Mark ambiguities with [NEEDS CLARIFICATION] for hardware specification gaps

### Planning Phase
- Constitutional compliance verification for Simics device development
- Technical translation from hardware specifications to DML implementation plans
- Behavioral testing strategy focused on software-visible device functionality
- **Mandatory**: Reference technical rules and forbidden actions in proposals

### Implementation Phase
- Simics-specific task generation following device modeling best practices
- Adherence to DML standards while maintaining constitutional principles
- Consistent documentation and validation approaches across all device models
- **Mandatory**: Verify compliance checklist before archiving

## Amendment Process

Modifications to this constitution require:
- Explicit documentation of the rationale for change
- Review and approval by Simics development team
- Backwards compatibility assessment with existing device models
- Update of all dependent templates and documentation

## Governance

This constitution supersedes all other Simics device development practices. All specification, planning, task generation, and implementation must verify constitutional compliance. When specific device requirements conflict with constitutional principles, the constitution takes precedence unless explicitly documented and justified.

**Version**: 5.0.0 | **Ratified**: 2025-12-03 | **Last Amended**: 2025-12-03

*Major version increment adds comprehensive technical implementation rules extracted from prompt templates for agent autonomy.*
=======
# Simics Model Development Constitution

## Core Principles

### I. Device-First Development
Every hardware component starts as a standalone device model—no exceptions. This forces modular design from the start:

- Device models must be self-contained DML modules
- Each device model is independently testable in isolation
- Clear hardware abstraction boundaries with well-defined interfaces
- Device models expose functionality through standardized Simics interfaces
- No monolithic system models - compose from discrete device components

### II. Interface-First Architecture
All device components communicate through well-defined, testable hardware interfaces:

- DML Interface: Registers, ports, and connections defined before logic implementation
- Hardware interfaces specified before behavioral modeling
- Memory-mapped interfaces with clear address space definitions
- Inter-device communication through standardized Simics interfaces
- Register maps documented before register implementation
- Signal and bus protocols defined before device logic

### III. Test-First Development (NON-NEGOTIABLE)
TDD mandatory for all Simics device development:

- Specification tests written → Hardware behavior verified → Tests fail → Then implement DML
- Register access tests, device behavior tests, integration tests with other devices
- Functional simulation validation against hardware specification
- Test vectors derived from hardware specification documents
- Red-Green-Refactor cycle: Test → Fail → Implement → Pass → Refactor
- Behavior verification before implementation complexity

### IV. Specification-Driven Implementation
Base all implementation decisions strictly on provided hardware specifications:

- Hardware specifications drive register definitions and device behavior
- Software-visible behavior must match specification exactly
- Internal implementation may be simplified if not software-visible
- Mark unclear hardware behaviors with [NEEDS CLARIFICATION] and implement as TODO
- No assumptions beyond documented hardware specification
- Reference specification sections in DML comments

### V. Integration Testing Focus
Focus on real-world hardware integration scenarios:

- Device-to-device communication testing
- Software driver compatibility testing
- Platform integration validation
- Memory subsystem interaction testing
- Bus protocol compliance verification
- Interrupt handling and timing validation

### VI. Observability and Transparency
Everything must be inspectable and debuggable in simulation:

- Register states must be inspectable at runtime
- Device state changes must be traceable
- Simulation events must be observable
- Debug interfaces for device inspection
- Comprehensive logging of device operations
- State visibility through Simics CLI and debugging tools

### VII. Versioning and Evolution
MAJOR.MINOR.BUILD format with clear compatibility contracts:

- Device model versioning aligned with hardware specification versions
- Register interface changes require version increment
- Simulation compatibility maintained across device model versions
- Backward compatibility for simulation checkpoints
- Clear migration paths for specification updates

### VIII. Simplicity and Incremental Development
Start simple, add complexity only when proven necessary:

- Model only software-visible behaviors initially
- Add internal complexity only when required for accuracy
- Prefer functional correctness over implementation detail accuracy
- Implement clear abstractions before detailed behaviors
- YAGNI principles for device features - implement what's specified
- Single responsibility per device model and register

### IX. Simics Excellence
Leverage Simics domain expertise and best practices:

- Follow DML coding standards and patterns
- Use Simics templates and utility functions
- Implement proper state management for checkpointing
- Ensure timing and event handling accuracy
- Optimize for simulation performance while maintaining accuracy
- Leverage Simics debugging and inspection capabilities

## Technical Implementation Rules

### File System Organization

#### Editable Files (Permitted Modifications)

✅ **DML Device Implementation**
- Location: `simics-project/modules/<device_name>/<device_name>.dml`
- Purpose: Device behavior, register side-effects, timer logic
- Rule: This is the PRIMARY implementation file for device logic

✅ **Python Unit Tests**
- Location: `simics-project/modules/<device_name>/test/*.py`
- Pattern: `s-<feature>.py` (one test function per file)
- Purpose: Functional validation of device behavior

#### Protected Files (DO NOT MODIFY)

❌ **Auto-Generated DML Files**
- `<device_name>-glue.dml` - Generated from IP-XACT during build
- `<device_name>-dia.dml` - Defines register interface from IP-XACT
- `<device_name>-registers.dml` - Defines register skeleton from IP-XACT
- **Reason**: These files are regenerated on every build. Manual changes will be lost.

❌ **Build Configuration Files**
- `Makefile`, `CMakeLists.txt`, `MODULEINFO`, `MODULEDEPS`
- **Reason**: Build system is pre-configured for Simics project structure

❌ **IP-XACT XML Files**
- `<device_name>.xml` and other register specification files
- **Reason**: These are specification artifacts from the specify phase

### DML Import Statements (CRITICAL)

**ABSOLUTE REQUIREMENT**: Keep ALL import statements intact - NEVER remove or comment out:

```dml
import "<device_name>-glue.dml"; // Auto-generated - register association
import "<device_name>-dia.dml";  // Defines register interface from IP-XACT
import "simics/devs/signal.dml"; // Defines signal interfaces (interrupts)
```
or
```
import "<device_name>-registers.dml"; // Defines register skeleton from IP-XACT
import "simics/devs/signal.dml";      // Defines signal interfaces (interrupts)
```

**Why This Matters**:
- Register map: Without <device_name>-glue.dml, register interface/storage association are not resolved
- Register Interface: Without <device_name>-dia.dml, register template won't be available
- Register Skeleton: Without <device_name>-registers.dml, register skeleton won't be available
- Signal Interfaces: Without signal.dml, interrupt handling won't compile

### Timer Device Implementation Pattern

**CRITICAL PERFORMANCE RULE**: Simics is EVENT-DRIVEN, not cycle-accurate!

**REQUIRED**: Use timestamp-based single event pattern
```dml
// ✅ EFFICIENT: Post ONE event for final timeout
event timer_event is (simple_time_event) {
    method event() {
        // Timer expired - handle timeout
    }

    method arm(double timeout_seconds) {
        if (posted()) remove();  // Remove old event if exists
        post(timeout_seconds);   // Post ONE event
    }
}

saved double timer_start_simtime = 0.0;

method start_timer(uint64 timeout_cycles) {
    timer_start_simtime = SIM_time(dev.obj);  // Record start time
    local double timeout_seconds = cycles_to_simtime(timeout_cycles);
    timer_event.arm(timeout_seconds);  // Post single event
}

method read_current_value() -> (uint64) {
    local double elapsed = SIM_time(dev.obj) - timer_start_simtime;
    local uint64 elapsed_cycles = simtime_to_cycles(elapsed);
    return calculate_remaining(elapsed_cycles);  // Dynamic calculation
}
```

**For complete timer implementation details**, including:
- Full code examples with `simple_time_event` template
- Event remove/posted/post methods
- Frequency conversion helpers
- Relative vs absolute timer patterns

→ **See `.specify/memory/DML_Device_Development_Best_Practices.md` Section: "Timer Device"**

**Timer Implementation Checklist**:
- [ ] ✅ Use `saved double timer_start_simtime` to record when timer started
- [ ] ✅ Use `event ... is (simple_time_event)` with arm/cancel methods
- [ ] ✅ Post exactly ONE event for when counter reaches zero
- [ ] ✅ Calculate current counter value from `SIM_time()` - timer_start_simtime

### Python Test File Structure

**CRITICAL**: See `.specify/memory/DML_Device_Development_Best_Practices.md` for complete test examples and patterns.

**Pattern**: `s-<feature>.py` (one test function per file)

**Required Imports**:
```python
#!/usr/bin/env python3
import simics      # REQUIRED - Simics API
import stest       # REQUIRED - Test assertions
import dev_util    # REQUIRED - Register access utilities
```

**Essential Test Structure** (simplified - see best practices doc for details):
```python
def test_feature_name():
    # 1. Create device and clock (MANDATORY for time-based tests)
    device = simics.SIM_create_object('<device_name>', 'dev0')
    clk = simics.SIM_create_object('clock', 'clk', freq_mhz=1)
    device.queue = clk
    
    # 2. Access registers via bank
    bank = dev_util.bank_regs(device.bank.<Bank_Name>)
    
    # 3. Test and validate
    bank.<REGISTER_NAME>.write(<value>)
    result = bank.<REGISTER_NAME>.read()
    stest.expect_equal(result, <expected>, "message")

# Run test when executed
if __name__ == '__main__':
    test_feature_name()
```

**For complete examples including**:
- Clock queue configuration details
- Register access patterns (bank vs attribute)
- Time advancement with `simics.SIM_continue()`
- Signal interface mocking
- Troubleshooting common test errors

→ **Refer to `.specify/memory/DML_Device_Development_Best_Practices.md` Section: "Testing Best Practices"**

### Forbidden Actions (Complete List)

#### ❌ File System Violations
- Removing or commenting out ANY import statements
- Creating new `.dml` files without explicit approval
- Modifying auto-generated files (`-registers.dml`, `-dia.dml`, `-glue.dml`)
- Editing build configuration files
- Modifying IP-XACT XML during implementation

#### ❌ Implementation Anti-Patterns
- Decrementing counters in event handlers instead of calculating from `SIM_time()`
- Using polling loops or busy-wait patterns
- Implementing cycle-accurate timing (use functional, event-driven model)
- Adding checkpoint/restore logic (Simics handles automatically)
- Making assumptions beyond hardware specification

#### ❌ Test Anti-Patterns
- Multiple test functions in one file
- Tests without clock queue configuration
- Tests without clear assertions
- Tests that don't validate time-based behavior
- **Using pytest-style fixtures** (e.g., `def test(conf, SIM_create_object)`)
- **Missing required imports** (`simics`, `stest`, `dev_util`)
- **Using undefined functions** (e.g., `SIM_write_phys_memory` doesn't exist)
- **Wrong function signatures** - test functions take no parameters

**Correct vs Incorrect Test Patterns**:

❌ **WRONG - Pytest-style**:
```python
def test_device(conf, SIM_create_object, SIM_write_phys_memory):
    dev = SIM_create_object("<device_name>", "dev0", [])
    dev.queue = conf.sim.queue  # conf doesn't exist
    SIM_write_phys_memory(dev, 0x0, 0x10, 4)  # function doesn't exist
```

✅ **CORRECT - Simics style**:
```python
import simics
import stest
import dev_util

def test_device():
    dev = simics.SIM_create_object('<device_name>', 'dev0')
    clk = simics.SIM_create_object('clock', 'clk', freq_mhz=1)
    dev.queue = clk
    bank = dev_util.bank_regs(dev.bank.<BankName>)
    bank.<REGISTER_NAME>.write(0x10)
```

### Build and Validation Commands

**Building**:
```bash
cd simics-project
make <device_name>
```

**Testing**:
```bash
cd simics-project/
./bin/test-runner --suite modules/<device_name>/test
```

### Task Marking Requirements (MANDATORY)

**CRITICAL**: Mark tasks in `tasks.md` IMMEDIATELY after completing each step.

#### Preparation Tasks (Section 1) - Mark AFTER Reading
```bash
# After reading constitution.md
read_file(".specify/memory/constitution.md")
→ IMMEDIATELY mark: "- [x] Read project constitution"

# After reading spec.md
read_file("specs/<change-id>/spec.md")
→ IMMEDIATELY mark: "- [x] Review device spec"

# After reading best practices
read_file(".specify/memory/DML_Device_Development_Best_Practices.md")
→ IMMEDIATELY mark: "- [x] Review best practices"
```

**Why this matters**: Preparation tasks have NO artifacts (no files created), but they ARE required work. You must explicitly mark them to show transparency and progress tracking.

#### Actionable Tasks (Sections 2-5) - Mark AFTER Creating/Validating
```bash
# Tests: Mark after test file created
write_file("test/s-<feature>.py")
→ IMMEDIATELY mark: "- [x] Add Python test"

# Implementation: Mark after DML file created
write_file("<device>.dml")
→ IMMEDIATELY mark: "- [x] Implement <behavior>"

# Validation: Mark after build succeeds
bash "make <device>" (success)
→ IMMEDIATELY mark: "- [x] Build passes"

# Archive: Mark after archiving completes
bash "openspec archive" (success)
→ IMMEDIATELY mark: "- [x] Move to archive"
```

**Pattern**:
- Preparation = Read → Mark
- Other tasks = Create/Validate → Mark

### Compliance Checklist

Before submitting any implementation, verify:

- [ ] ✅ **ALL preparation tasks marked** (constitution, spec, best practices)
- [ ] ✅ All import statements present and intact
- [ ] ✅ Only permitted files modified (`.dml` implementation, `.py` tests)
- [ ] ✅ No auto-generated files edited
- [ ] ✅ Timer uses `event` objects with timestamps
- [ ] ✅ No `saved uint32` for counter/timer state
- [ ] ✅ Tests follow `s-<feature>.py` pattern
- [ ] ✅ Tests configure clock queue
- [ ] ✅ **Build validation executed** (make succeeded at least once)
- [ ] ✅ **Test validation executed** (test-runner ran at least once)
- [ ] ✅ Device builds successfully (final state - may require iteration)
- [ ] ✅ All tests pass (final state - may require iteration)
- [ ] ✅ **ALL tasks in tasks.md marked complete**

### Archive Readiness Criteria

**Minimum criteria for archiving** (ALL required):
1. ✅ All preparation tasks marked [x]
2. ✅ All test files created
3. ✅ All implementation code written (no TODO comments)
4. ✅ Build succeeds at least once
5. ✅ Test suite executed at least once
6. ✅ All import statements intact
7. ✅ No auto-generated files modified
8. ✅ All tasks in tasks.md marked [x]

**Optional criteria** (can defer to follow-up changes):
- ❓ All tests pass 100% (can document failures and fix later)
- ❓ Perfect code quality (can refactor later)
- ❓ Full feature parity with spec (can implement remaining features later)
- ❓ Optimal performance (can optimize later)

**Archive with known issues** (acceptable pattern):
- If tests fail: Add "## Known Issues" section to proposal.md
- If partial implementation: Add "## Future Work" section to proposal.md
- If performance issues: Add "## Performance Notes" section to proposal.md
- Archive anyway, create follow-up change for fixes

**Rationale**:
- OpenSpec is iterative - changes build on changes
- Perfect implementation blocks progress
- Known issues documented are better than incomplete workflows
- Git history shows evolution of implementation
- Follow-up changes can address issues incrementally

## Constitutional Compliance Framework

### Specification Phase
- All device projects begin with hardware specification templates
- Device specifications include register maps, interface definitions, and behavioral requirements
- Mark ambiguities with [NEEDS CLARIFICATION] for hardware specification gaps

### Planning Phase
- Constitutional compliance verification for Simics device development
- Technical translation from hardware specifications to DML implementation plans
- Behavioral testing strategy focused on software-visible device functionality
- **Mandatory**: Reference technical rules and forbidden actions in proposals

### Implementation Phase
- Simics-specific task generation following device modeling best practices
- Adherence to DML standards while maintaining constitutional principles
- Consistent documentation and validation approaches across all device models
- **Mandatory**: Verify compliance checklist before archiving
- **CRITICAL**: "Implementation" means complete functional code:
  - Replace ALL TODO comments with actual working DML code
  - Implement ALL register side-effects (write_register, read_register)
  - Implement ALL device behavior (timers, events, state management)
  - Implement ALL signal handling (connect blocks)
  - Tests are created FIRST (TDD), but implementation MUST follow
  - Do NOT stop after creating tests - that's only the preparation step

### Completion Phase
- **Mandatory**: After archiving, provide clear status report
- **Success case**: Report all tests passing, implementation complete
- **Partial success case**: Report which tests failed, provide next prompt
- **Failure case**: Report build errors, provide fix prompt
- **Iterative workflow**: Each change builds on previous archived changes
- **Next steps guidance**: Provide specific, actionable prompts for follow-up changes

## Amendment Process

Modifications to this constitution require:
- Explicit documentation of the rationale for change
- Review and approval by Simics development team
- Backwards compatibility assessment with existing device models
- Update of all dependent templates and documentation

## Governance

This constitution supersedes all other Simics device development practices. All specification, planning, task generation, and implementation must verify constitutional compliance. When specific device requirements conflict with constitutional principles, the constitution takes precedence unless explicitly documented and justified.

**Version**: 5.0.0 | **Ratified**: 2025-12-03 | **Last Amended**: 2025-12-03

*Major version increment adds comprehensive technical implementation rules extracted from prompt templates for agent autonomy.*
>>>>>>> 28c80a59 (Minor fix and update for task done and refer to best practice)
