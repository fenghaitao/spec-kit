# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [Current date in YYYY-MM-DD format]
**Status**: [Update after completing spec - count [NEEDS CLARIFICATION] markers and set to "Ready for Planning" (0 markers) or "Draft (N clarifications needed)"]
**Input**: User description: "$ARGUMENTS" (text provided after /specify command)

---

## Simics DML Device Modeling Guidance

**Note**: For Simics device modeling projects, comprehensive DML learning resources are available:
- **.specify/memory/DML_grammar.md**: Complete DML 1.4 grammar reference with syntax rules and language constructs
- **.specify/memory/DML_Device_Development_Best_Practices.md**: Best practices, patterns, and common pitfalls for DML development
- **spec/[feature-name]/[device-name]-registers.xml**: IP-XACT register description XML

**Functional Modeling Defaults** (unless explicitly stated otherwise):
- **Timing**: Precise timing is NOT required for functional models - focus on functional correctness
- **Checkpoint/Restore**: Checkpoint and restore functionality is NOT required - Simics handles this automatically for register state

---

## Hardware Specification *(mandatory)*

### Register Map Overview

| Offset | Name | Size | Access | Reset | Purpose |
|--------|------|------|--------|-------|---------|
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control and enable flags |
| 0x04 | STATUS | 32-bit | R/O | 0x0001 | Device status indicators |
| 0x08 | TIMEOUT | 32-bit | R/W | 0x0000 | Timeout period configuration |
| 0x0C | COUNTER | 32-bit | R/O | 0x0000 | Current countdown value |
| 0x10 | INTCLR | 32-bit | W/O | 0x0000 | Write any value to clear interrupt |
| ... | ... | ... | ... | ... | ... |

### External Interfaces and Signals

**Interrupt Outputs**:
- **Signal Name**: [e.g., "wdogint", or NEEDS CLARIFICATION]
- **Direction**: Output
- **Type**: [e.g., "Edge-triggered", "Level-triggered", or NEEDS CLARIFICATION]
- **Assertion Condition**: [e.g., "Asserted when counter reaches zero and INTEN=1"]
- **Clear Mechanism**: [e.g., "Cleared by writing to INTCLR register"]

**Reset Inputs**:
- **Signal Name**: [e.g., "wrst_n", "prst_n", or NEEDS CLARIFICATION]
- **Direction**: Input
- **Type**: [e.g., "Active-low asynchronous reset"]
- **Effect**: [e.g., "Resets all registers to default values, stops counter"]

**Other Signals**:
- **Signal Name**: [e.g., "wdogres", "status_led", or NEEDS CLARIFICATION]
- **Direction**: [Input/Output/Bidirectional]
- **Purpose**: [e.g., "System reset output on second timeout"]
- **Behavior**: [e.g., "Asserted when counter reaches zero twice consecutively with RESEN=1"]

### Device Operational Model

**CRITICAL**: Document device states, transitions, and software/hardware interaction flows that drive test scenarios.

#### Device States and Transitions

**State Diagram Format**:
```
[STATE_1] → [STATE_2] → [STATE_3] → [STATE_4]
              ↑____________↓
```

**State Documentation Template**:
For each identified state, document:
1. **[STATE_NAME]**: Brief description
   - Entry conditions: [How device enters this state]
   - Observable indicators: [Register values, signal states that indicate this state]
   - Exit conditions: [What causes transition to other states]
   - *Test Scenario*: [Which scenario verifies this state]

**Common Device States**: RESET (initial), IDLE (configured), ACTIVE (operating), ERROR (fault detected), DISABLED (intentionally off)

**State Transition Template**: **[SOURCE] → [TARGET]**: Trigger condition, *Validate*: [Observable change]

**Example - Generic Transitions**:
- **RESET → IDLE**: Configuration write completes successfully
  - *Validate*: STATUS register shows ready flag, control register reflects configuration
- **IDLE → ACTIVE**: Enable bit set in control register
  - *Validate*: STATUS register shows active flag, output signals change state

#### Software/Hardware Interaction Flows

**Flow Documentation Template**:
```
Flow [N]: [Flow Name] (maps to Test Scenario [X])

State Transition: [INITIAL_STATE] → [INTERMEDIATE_STATE] → [FINAL_STATE]

Software Actions                    Hardware Responses                Observable State
─────────────────────────────────────────────────────────────────────────────────────
1. [Software action description]  → [Hardware response]            → [What software can observe]
2. [Next action...]               → [Response...]                  → [Observable change...]

Test Validation:
- [What to verify for step 1]
- [What to verify for step 2]
```

**Common Flow Patterns**: Device Initialization (RESET → IDLE → ACTIVE), Interrupt Handling (ACTIVE → INTERRUPT_PENDING → ACTIVE), Error Recovery (ACTIVE → ERROR → IDLE)

#### Register Access Ordering Requirements

**Critical Ordering Constraints** (enforce in tests):
[List any ordering requirements extracted from specification, e.g.:]
1. **[Operation A] before [Operation B]**: [Reason/consequence if violated]

**Common Patterns**: Configure before enable, Disable before reconfigure, Clear status before operation, Unlock before protected writes

**Observable vs. Non-Observable**:
- **Software CAN observe**: Register values, interrupt signals, output pins
- **Software CANNOT observe**: Internal clock dividers, FSM states, pipeline stages (must infer from observable behavior)

### Memory Interface Requirements

**Address Space**:
- **Base Address**: [e.g., "0x1000", or NEEDS CLARIFICATION]
- **Size**: [e.g., "4KB (0x1000 bytes)", or NEEDS CLARIFICATION]
- **Alignment**: [e.g., "4-byte aligned for 32-bit registers"]

**Access Patterns**:
- **Supported Widths**: [e.g., "32-bit only", "8/16/32-bit", or NEEDS CLARIFICATION]
- **Unaligned Access**: [e.g., "Not supported - must be aligned", or NEEDS CLARIFICATION]
- **Burst Access**: [e.g., "Not supported", "Supported for data registers", or NEEDS CLARIFICATION]

**Timing Requirements**:
- **Register Access Latency**: [e.g., "Single cycle", "2-3 cycles", or NEEDS CLARIFICATION]
- **Counter Precision**: [e.g., "Decrements once per clock cycle", or NEEDS CLARIFICATION]
- **Interrupt Latency**: [e.g., "Asserted within 1 clock cycle of timeout", or NEEDS CLARIFICATION]

---

## Functional Requirements *(mandatory)*

**Purpose**: Define testable, verifiable requirements derived from the Hardware Specification. Each requirement must be traceable to hardware behaviors and validated by test scenarios.

**CRITICAL**: Generate requirements that comprehensively cover ALL aspects of the Hardware Specification section above:
- **Register Map**: All registers, reset values, access types, and **side-effects**
- **External Interfaces and Signals**: All interrupt outputs, reset inputs, other signals (assertion/clear conditions)
- **Device States and Transitions**: All device states and all state transitions
- **Software/Hardware Interaction Flows**: All documented operational flows
- **Register Access Ordering**: Any critical ordering constraints
- **Memory Interface**: Address space, access patterns, timing requirements

---

**EXAMPLE - Watchdog Timer Device**:

### Requirement 1: Countdown Timer Logic

**User Story**: As a system developer, I want a countdown timer that decrements at a predictable rate, so that I can monitor software execution deadlines

**Acceptance Criteria**:
1. THE device SHALL count down from WDOGLOAD value to zero at system clock rate when INTEN=1
2. THE device SHALL provide WDOGVALUE register to read current counter value in real-time
3. WHEN INTEN transitions from 0→1, THE device SHALL reload counter with WDOGLOAD value and transition to COUNTING state
4. WHEN WDOGLOAD is written during counting, THE device SHALL update reload value but NOT affect current counter
5. THE device SHALL NOT decrement counter when INTEN=0 (disabled state)
6. WHILE counter is active, THE device SHALL decrement WDOGVALUE by 1 every clock cycle

### Requirement 2: Interrupt Generation and Clearing

**User Story**: As a driver developer, I want interrupt generation on timeout, so that I can respond to watchdog events in software

**Acceptance Criteria**:
1. WHEN counter reaches zero AND INTEN=1, THE device SHALL assert wdogint interrupt signal within 1 clock cycle
2. THE device SHALL transition from COUNTING to INTERRUPT_PENDING state when counter reaches zero
3. THE device SHALL reload counter with WDOGLOAD value when WDOGINTCLR register is written (register side-effect)
4. THE device SHALL clear wdogint interrupt signal when WDOGINTCLR is written (register side-effect)
5. WHILE in INTERRUPT_PENDING state, THE device SHALL keep wdogint asserted until WDOGINTCLR is written
6. WHEN WDOGINTCLR is written, THE device SHALL transition from INTERRUPT_PENDING to COUNTING state

---

*[Generate similar requirements for your device, covering all key capabilities from Hardware Specification]*

---

## Device Behavioral Model *(mandatory)*

### System Context
- **Simulation Purpose**: [e.g., Boot validation, Software development, Performance analysis]
- **Abstraction Level**: Functional (default for Simics device models)

### State Management
- **Device State Variables**: [internal state that must be maintained]
- **State Transitions**: [how device state changes based on register writes/external events]
- **Reset Behavior**: [how device state is initialized/reset]
- **Save/Restore**: Not required (Simics handles checkpoint/restore automatically for register state)

### Data Processing
- **Input Data Flow**: [how device processes input data]
- **Output Generation**: [how device generates outputs]
- **Buffer Management**: [internal buffer requirements and management]
- **Timing Behavior**: Functional timing (precise cycle-accurate timing not required)

### Error Scenarios and Recovery
- **Error Detection**: [how device detects error conditions]
- **Error Reporting**: [how errors are communicated to software]
- **Recovery Mechanisms**: [how device recovers from errors]
- **Fault Injection**: [support for testing error scenarios, or NEEDS CLARIFICATION]

---

## User Scenarios & Testing *(mandatory)*

**Purpose**: Define comprehensive, testable scenarios that drive specification clarity, state machine design, and test case development. Each scenario maps to device states, transitions, and operational flows.

### Functional Test Scenarios (Given-When-Then Format)

**CRITICAL**: Each scenario must explicitly reference device states, operational flows, and requirements for full traceability.

**Example Scenarios**:

1. **Scenario 1: Device Initialization**
   - **States**: RESET → IDLE → ACTIVE
   - **Flow**: Flow 1 (Device Initialization)
   - **Requirements**: Requirement 1, 2
   - **Given** device in RESET state
   - **When** software writes configuration and sets ENABLE=1
   - **Then** device transitions to ACTIVE, registers readable, STATUS shows ready
   - **Test Validation**: Verify register writes, state transition, STATUS flag

2. **Scenario 2: Interrupt Handling**
   - **States**: ACTIVE → INTERRUPT_PENDING → ACTIVE
   - **Flow**: Flow 2 (Interrupt Handling)
   - **Requirements**: Requirement 3
   - **Given** device in ACTIVE with interrupts enabled
   - **When** event occurs, then software acknowledges
   - **Then** interrupt asserted then cleared, STATUS updated correctly
   - **Test Validation**: Verify interrupt timing, STATUS flags, clear mechanism

---

*Mark any unclear cases with [NEEDS CLARIFICATION: specific behavior under [condition]]?*

### Test Coverage Requirements

**Traceability Matrix**:
- Each test scenario → Device states → Operational flows → Requirements
- Each device state → At least one test scenario
- Each state transition → At least one test scenario
- Each operational flow → At least one test scenario
- Each requirement → At least one test scenario

**Coverage Checklist**:
- [ ] **Register Coverage**: All registers tested (read, write, reset value verification)
- [ ] **Bit Field Coverage**: All functional bit fields tested (set, clear, combinations)
- [ ] **State Coverage**: All device states reachable and testable
- [ ] **Transition Coverage**: All state transitions exercised
- [ ] **Flow Coverage**: All operational flows validated
- [ ] **Error Coverage**: All error conditions testable (detection, reporting, recovery)
- [ ] **Protocol Coverage**: All bus protocol sequences validated (if applicable)

### Test Automation Considerations

*For later /plan and /implement phases:*
- Each scenario maps to 1+ automated test cases in Simics
- Test cases verify both register state AND device behavior/outputs
- Use Simics Python scripting for test automation
- Define explicit pass/fail criteria for each scenario
- Leverage state machine model for test case generation

---

## Clarifications Required

**INSTRUCTIONS**: After completing the specification, list all `[NEEDS CLARIFICATION: ...]` markers found in the document above (excluding this instructions section and headers).

**Format**:
1. **[Section Name]**: [NEEDS CLARIFICATION text]
2. **[Section Name]**: [NEEDS CLARIFICATION text]
...

**Status Update**:
- **Total Clarifications**: [N] items
- **Specification Status**: [If N=0: "Ready for Planning", else: "Draft (N clarifications needed)"]

*If no clarifications are needed, write:*
- **Total Clarifications**: 0 items
- **Specification Status**: Ready for Planning

---

## Review & Acceptance Checklist

### AUTOMATED CHECKS (AI Agent MUST verify)

**Content Quality** (objective - can be checked automatically):
- [ ] No implementation details (DML syntax, code structure, algorithms)
- [ ] Focused on hardware behavior and device operation
- [ ] All mandatory sections completed

**Hardware Specification Completeness** (objective):
- [ ] Register map table included (all registers with offset, name, size, access, reset, purpose)
- [ ] External interfaces documented (interrupt outputs, reset inputs, other signals with direction/type/behavior)
- [ ] Device operational model documented (states, transitions, interaction flows, ordering constraints)
- [ ] Memory interface requirements specified (address space, access patterns, timing)
- [ ] At least 5 functional requirements included (user stories with SHALL statements, testable acceptance criteria)
- [ ] At least 3 functional test scenarios included (with states, flows, requirements references, and validation steps)
- [ ] Device behavioral model documented (system context, state management, data processing, error handling)
- [ ] Requirements traceability established (each requirement mapped to test scenarios)

---

## Specification Generation Status
*AI Agent: Mark [x] as each section is completed*

### Section Completion
- [ ] **Hardware Specification**: Register map, external interfaces, operational model, memory interface documented
- [ ] **Functional Requirements**: Minimum 5 requirements with user stories and SHALL statements generated
- [ ] **Device Behavioral Model**: System context, state management, data processing, error handling documented
- [ ] **Test Scenarios**: Minimum 3 scenarios with states, flows, requirements references, and validation steps generated

### Quality Validation
- [ ] **Clarifications Listed**: All [NEEDS CLARIFICATION] markers documented in "Clarifications Required" section
- [ ] **Status Updated**: Clarification count complete, Status field at top updated
- [ ] **Traceability Verified**: All requirements mapped to test scenarios, all states/transitions covered
- [ ] **Completeness Check**: All mandatory sections complete, all checklists items verified

**COMPLETION CRITERIA**: All 8 checkboxes marked [x] = Specification ready for planning phase

**TRACEABILITY REQUIREMENTS**:
- [ ] Each test scenario references device states (from Device States and Transitions)
- [ ] Each test scenario references operational flows (from Software/Hardware Interaction Flows)
- [ ] Each test scenario references functional requirements (Requirement N)
- [ ] Each device state has at least one test scenario
- [ ] Each state transition has at least one test scenario
- [ ] Each functional requirement has at least one test scenario
