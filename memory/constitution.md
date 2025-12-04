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
