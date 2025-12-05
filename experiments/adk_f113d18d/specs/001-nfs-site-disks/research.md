# Research: Simics Watchdog Timer Device

## DML Learning Prerequisites

**⚠️ CRITICAL**: Two comprehensive DML learning documents must be studied in the tasks phase before writing any DML code:

1. `.specify/memory/DML_Device_Development_Best_Practices.md` - Patterns and pitfalls
2. `.specify/memory/DML_grammar.md` - Complete DML 1.4 language specification

**During /plan Phase**:
- ✅ Identify unknowns from Technical Context
- ✅ Document environment discovery (Simics version, packages, platforms)
- ❌ DO NOT read the DML learning documents yet (they will be studied in tasks phase)

**In Tasks Phase**: Mandatory tasks will require complete study of these documents with comprehensive note-taking in research.md before any implementation

## Environment Discovery

### Simics Version
Simics Base 7.57.0

### Installed Packages
[Document output from list_installed_packages() - format as table with package details]

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
QSP-x86 (Quick Start Platform)

## Device Architecture Context

### Device Category: Timer/Counter

**Architectural Overview**:
The ARM PrimeCell Watchdog Timer is a 32-bit decrementing counter device that provides configurable timeout periods with interrupt generation on first timeout and system reset on second timeout if the interrupt is not cleared. The device includes lock protection mechanisms and integration test capabilities.

**Key Design Concepts**:
- Counter register with auto-reload functionality on INTEN enable or interrupt clear
- Interrupt and reset generation with state management (INTERRUPT_PENDING, RESET_PENDING)
- Lock protection mechanism using magic number (0x1ACCE551)
- Integration test mode for direct output control

**Common Patterns for This Device Type**:
- Use io_memory interface for register bank with APB bus protocol
- Implement signal interfaces for interrupt (wdogint) and reset (wdogres) outputs
- Use events for periodic/timed operations and countdown timers
- Register field handling with bit-level access patterns

**Implications for data-model.md**:
The timer will require counter state tracking, interrupt state management, and integration with the clock enable signal (wclk_en) to control decrement behavior.

**Note**: Detailed implementation patterns (callbacks, error handling, test code) will be gathered via RAG queries during Phase 3 (tasks/implementation).

## Example Code References

### Example 1: Timer Device Pattern
**Source**: DML Device Development Best Practices
**Applicability**: Countdown timer functionality

```dml
register countdown {
    saved cycles_t start_time;
    saved uint64 start_value;

    method get() -> (uint64) {
        if (!enabled.val)
            return start_value;

        local cycles_t elapsed = SIM_cycle_count(dev.obj) - start_time;
        local uint64 decremented = elapsed / prescaler.val;

        if (decremented >= start_value)
            return 0;  // Expired
        return start_value - decremented;
    }

    method write(uint64 value) {
        start_value = value;
        start_time = SIM_cycle_count(dev.obj);
        schedule_expiry();
    }

    method schedule_expiry() {
        cancel_after();
        if (enabled.val && start_value > 0) {
            local cycles_t cycles_to_zero = start_value * prescaler.val;
            after cycles_to_zero cycles: on_expired();
        }
    }

    method on_expired() {
        log info: "Countdown timer expired!";
        // Trigger interrupt, reset, etc.
        if (auto_reload.val) {
            start_value = reload_value.val;
            start_time = SIM_cycle_count(dev.obj);
            schedule_expiry();
        }
    }
}
```

**Key Points**:
- Use lazy evaluation for counters to avoid per-cycle overhead
- Store start time and value, calculate on demand
- Use after statements for scheduling timeout events
- Handle timer state properly across simulation checkpoints

### Example 2: Watchdog Timer Pattern
**Source**: DML Device Development Best Practices
**Applicability**: Interrupt and reset generation

```dml
event watchdog_event is simple_time_event {
    method event() {
        log error: "Watchdog timeout! System reset triggered.";
        // Trigger system reset
        reset_signal.signal.signal_raise();
    }
}

register watchdog_ctrl {
    field enable @ [0];
    field kick @ [1] is (write_1_clears);

    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);

        if (kick.val) {
            // Kick the watchdog - restart timeout
            kick.val = 0;
            restart_watchdog();
        }
    }
}

method restart_watchdog() {
    if (watchdog_event.posted())
        watchdog_event.remove();

    if (watchdog_ctrl.enable.val) {
        local double timeout = cast(timeout_value.val, double) / clock_freq;
        watchdog_event.post(timeout);
        log info, 4: "Watchdog restarted, timeout in %f seconds", timeout;
    }
}
```

**Key Points**:
- Use events for watchdog timeout handling
- Implement proper event cancellation and rescheduling
- Use signal interfaces for interrupt/reset outputs
- Handle timer restart on write operations

[Add additional examples as needed - focus on architectural patterns, not detailed implementations]

## Architecture Decisions

### Decision: Use lazy evaluation for watchdog counter
- **Rationale**: Calculating counter value on-demand rather than decrementing every cycle reduces simulation overhead while maintaining accuracy
- **Alternatives Considered**: Per-cycle decrementing, which would be less efficient
- **Source**: DML Device Development Best Practices guide which recommends lazy evaluation for counters
- **Impact**: Counter value will be calculated based on elapsed time relative to last update, requiring saved start time and value

### Decision: Use after statements for timeout scheduling
- **Rationale**: The after statement is the recommended way to schedule future events in DML rather than complex event objects
- **Alternatives Considered**: Using event objects with time/cycle events
- **Source**: DML Device Development Best Practices guide
- **Impact**: Will use after cycles: syntax for scheduling timeout events

### Decision: Implement lock protection with saved state
- **Rationale**: The lock register requires persistent state to track lock status across operations
- **Alternatives Considered**: Computed lock status, which wouldn't persist properly
- **Source**: Hardware specification requiring persistent lock state
- **Impact**: Will use saved variable to track lock status

## Implementation Strategy

### Architecture Overview
The watchdog timer will be implemented as a DML device with a register bank containing all the specified registers. The core functionality will include a decrementing counter that can be configured with different divider values, interrupt generation capabilities, and lock protection. The device will interface with the system via APB bus and provide interrupt and reset outputs via signal interfaces.

### Key Design Patterns
- Lazy counter evaluation: Calculate counter value on read rather than decrementing each cycle
- Register side-effect handling: Implement custom read/write methods for registers with special behavior
- Signal interface for outputs: Use connect declarations for interrupt and reset signals
- Event-based timeout: Schedule timeout events using after statements
- Lock protection: Implement lock mechanism using magic number comparison

### Testing Approach
Based on the test scenarios in the specification, the implementation will be validated through:
- Basic timer operation: Verify countdown functionality
- Interrupt and reset generation: Test sequence of events
- Lock protection: Verify register access control
- Clock divider settings: Test different decrement rates
- Integration test mode: Verify direct output control

### Next Steps
Phase 1 will create the data-model.md that defines register structure, internal state variables, interfaces and implementation patterns. Then contracts and test scenarios will be documented to complete the design phase before implementation.