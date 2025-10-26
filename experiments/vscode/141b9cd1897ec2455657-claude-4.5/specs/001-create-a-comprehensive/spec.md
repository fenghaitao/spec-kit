# Feature Specification: Simics Watchdog Timer Device Implementation

**Feature Branch**: `001-create-a-comprehensive`
**Created**: October 26, 2025
**Status**: Draft
**Input**: User description: "Create a comprehensive Simics watchdog timer device implementation"

---

## User Scenarios & Testing

### Primary User Story

As a firmware engineer developing embedded software in Simics, I need a fully functional watchdog timer device model that accurately simulates the ARM PrimeCell SP805 watchdog hardware behavior. This allows me to:

1. Develop and test watchdog driver code in simulation before hardware availability
2. Verify timeout handling and system recovery mechanisms
3. Validate interrupt and reset generation sequences
4. Test lock protection mechanisms against software failures
5. Debug timing-critical watchdog refresh sequences

### Acceptance Scenarios

1. **Given** the watchdog device is integrated into QSP-x86 platform at address 0x1000, **When** firmware writes a timeout value to WDOGLOAD register and enables the timer via WDOGCONTROL, **Then** the counter decrements on each clock cycle and generates an interrupt when reaching zero

2. **Given** the watchdog has generated an interrupt (wdogint asserted), **When** the interrupt is not cleared before the counter reaches zero again, **Then** the watchdog asserts the reset signal (wdogres) to trigger system reset

3. **Given** the WDOGLOCK register is in locked state, **When** software attempts to write to control registers without first unlocking with magic value 0x1ACCE551, **Then** the write operations are ignored and register values remain unchanged

4. **Given** the watchdog is running with a specific clock divider (step_value), **When** firmware reads WDOGVALUE register, **Then** the returned value accurately reflects the current countdown value

5. **Given** the watchdog interrupt has been triggered, **When** firmware writes any value to WDOGINTCLR register, **Then** the interrupt is cleared and the counter reloads from WDOGLOAD value

6. **Given** integration test mode is enabled via WDOGITCR register, **When** firmware writes to WDOGITOP register, **Then** interrupt and reset signals are directly controlled for testing purposes

7. **Given** a simulation checkpoint is created while the watchdog is actively counting, **When** the checkpoint is restored, **Then** the watchdog resumes counting from the correct value with proper timing

### Edge Cases

- What happens when WDOGLOAD is set to 0? The counter should immediately reach zero and trigger appropriate interrupt/reset based on control settings
- What happens when INTEN is disabled after interrupt generation? The interrupt signal should be masked but raw interrupt status should remain
- What happens when both INTEN and RESEN are enabled simultaneously? First timeout triggers interrupt, second timeout triggers reset
- What happens when WDOGINTCLR is written during integration test mode? Normal interrupt clearing should be suppressed
- What happens when step_value is set to an invalid value (0b101-0b111)? Device behavior is undefined per specification
- What happens when multiple registers are accessed in rapid succession? Each access should be handled atomically with proper ordering
- What happens during reset (prst_n or wrst_n)? All registers return to their reset values and counting stops
- What happens when reading write-only registers (WDOGINTCLR, WDOGITOP)? Reads should return undefined or zero values

---

## Requirements

### Functional Requirements

**Core Timer Functionality:**

- **FR-001**: System MUST implement a 32-bit down-counter that decrements by a configurable step value on each enabled clock cycle
- **FR-002**: System MUST support five clock divider settings: ÷1 (1GHz), ÷2 (500MHz), ÷4 (250MHz), ÷8 (125MHz), ÷16 (62.5MHz) controlled via step_value field in WDOGCONTROL register
- **FR-003**: System MUST reload the counter from WDOGLOAD register value when INTEN bit transitions from 0 to 1 or when interrupt is cleared via WDOGINTCLR
- **FR-004**: System MUST support reading current counter value through WDOGVALUE register without affecting countdown operation

**Interrupt Generation:**

- **FR-005**: System MUST assert wdogint interrupt signal when counter reaches zero and INTEN bit is set to 1
- **FR-006**: System MUST maintain wdogint signal asserted until cleared by writing to WDOGINTCLR register
- **FR-007**: System MUST provide raw interrupt status via WDOGRIS register (unmasked) and masked status via WDOGMIS register (WDOGRIS & INTEN)
- **FR-008**: System MUST clear raw interrupt status and reload counter when any value is written to WDOGINTCLR register

**Reset Generation:**

- **FR-009**: System MUST assert wdogres reset signal when counter reaches zero again after a previous timeout that was not cleared and RESEN bit is set to 1
- **FR-010**: System MUST maintain wdogres signal asserted until system reset is applied via wrst_n or prst_n signals
- **FR-011**: System MUST NOT generate reset signal on first timeout, only on second consecutive timeout

**Lock Protection:**

- **FR-012**: System MUST protect all writable registers (except WDOGLOCK itself) from modification when in locked state
- **FR-013**: System MUST unlock register write access when magic value 0x1ACCE551 is written to WDOGLOCK register
- **FR-014**: System MUST lock register write access when any value other than 0x1ACCE551 is written to WDOGLOCK register
- **FR-015**: System MUST return 0x0 when reading WDOGLOCK in unlocked state and 0x1 when reading in locked state

**Integration Test Mode:**

- **FR-016**: System MUST enter integration test mode when bit 0 of WDOGITCR register is set to 1
- **FR-017**: System MUST allow direct control of wdogint and wdogres signals via WDOGITOP register when in integration test mode
- **FR-018**: System MUST resume normal countdown operation when WDOGITCR bit 0 is cleared to 0

**Register Implementation:**

- **FR-019**: System MUST implement all 21 registers with correct offsets, widths, and reset values as specified in hardware documentation
- **FR-020**: System MUST implement read-only identification registers (WDOGPERIPHID0-7, WDOGPCELLID0-3) with fixed values matching ARM PrimeCell specification
- **FR-021**: System MUST properly handle write-only registers (WDOGINTCLR, WDOGITOP) by ignoring read operations or returning zero
- **FR-022**: System MUST enforce read-only behavior for WDOGVALUE, WDOGRIS, WDOGMIS registers

**Clock and Reset:**

- **FR-023**: System MUST operate on wclk clock domain with synchronous behavior on wclk rising edges when wclk_en is asserted
- **FR-024**: System MUST support asynchronous reset on both APB domain (prst_n) and working clock domain (wrst_n)
- **FR-025**: System MUST stop counter operation when wclk_en is de-asserted

**Simics Integration:**

- **FR-026**: Device MUST be memory-mapped to QSP-x86 platform address space at base address 0x1000
- **FR-027**: Device MUST provide wdogint signal output connectable to platform interrupt controller
- **FR-028**: Device MUST provide wdogres signal output connectable to platform reset controller
- **FR-029**: Device MUST support checkpoint save and restore operations preserving all counter and register states
- **FR-030**: Device MUST maintain deterministic timing behavior using Simics cycle-based timing APIs
- **FR-031**: Device MUST be implemented using DML 1.4 syntax and follow Simics device modeling best practices

**Observability and Debugging:**

- **FR-032**: Device MUST provide logging for register accesses, counter events, interrupt generation, and reset generation
- **FR-033**: Device MUST support Simics CLI commands for device state inspection
- **FR-034**: Device MUST validate register access addresses and log warnings for invalid accesses

### Key Entities

- **Watchdog Timer Device**: The hardware device model implemented in DML that simulates ARM PrimeCell SP805 watchdog functionality
- **Down-Counter**: 32-bit register that decrements at configurable rate, core timing mechanism
- **Control Registers**: Configuration registers (WDOGLOAD, WDOGCONTROL, WDOGLOCK) that determine device behavior
- **Status Registers**: Read-only registers (WDOGVALUE, WDOGRIS, WDOGMIS) providing visibility into device state
- **Interrupt Signal (wdogint)**: Output signal asserted on first timeout when INTEN enabled
- **Reset Signal (wdogres)**: Output signal asserted on second consecutive timeout when RESEN enabled
- **Clock Domain**: Working clock (wclk) with enable signal (wclk_en) controlling counter operation
- **Reset Domains**: APB reset (prst_n) and working clock reset (wrst_n) for device initialization
- **Lock State**: Security mechanism protecting registers from unauthorized modification
- **Integration Test Mode**: Special mode allowing direct signal control for validation

### Hardware Specification

**Device Type**: ARM PrimeCell SP805 compatible Watchdog Timer

**Register Map**:

The device implements 21 memory-mapped registers organized as follows:

- **Timer Registers (0x00-0x14)**:
  - WDOGLOAD (0x00): 32-bit load value for counter initialization, R/W, reset=0xFFFFFFFF
  - WDOGVALUE (0x04): 32-bit current counter value, Read-only, reset=0xFFFFFFFF
  - WDOGCONTROL (0x08): Control register with step_value[4:2], RESEN[1], INTEN[0], R/W, reset=0x00
  - WDOGINTCLR (0x0C): Write-any-value to clear interrupt and reload counter, Write-only
  - WDOGRIS (0x10): Raw interrupt status bit, Read-only, reset=0
  - WDOGMIS (0x14): Masked interrupt status (WDOGRIS & INTEN), Read-only, reset=0

- **Lock Register (0xC00)**:
  - WDOGLOCK (0xC00): Lock control, write 0x1ACCE551 to unlock, R/W, reset=0x00000000

- **Integration Test Registers (0xF00-0xF04)**:
  - WDOGITCR (0xF00): Integration test mode enable bit, R/W, reset=0
  - WDOGITOP (0xF04): Direct control of wdogint[1] and wdogres[0] in test mode, Write-only, reset=0

- **Peripheral ID Registers (0xFD0-0xFEC)**:
  - WDOGPERIPHID4-7 (0xFD0-0xFDC): Identification values 0x04, 0x00, 0x00, 0x00
  - WDOGPERIPHID0-3 (0xFE0-0xFEC): Identification values 0x24, 0xB8, 0x1B, 0x00

- **PrimeCell ID Registers (0xFF0-0xFFC)**:
  - WDOGPCELLID0-3 (0xFF0-0xFFC): Component ID values 0x0D, 0xF0, 0x05, 0xB1

**External Interfaces**:

- **Memory-Mapped I/O Interface**: Device connects to system bus at base address 0x1000 with 4KB address space
- **Interrupt Output (wdogint)**: Single-bit signal to platform interrupt controller, active high, maintained until cleared
- **Reset Output (wdogres)**: Single-bit signal to platform reset controller, active high, maintained until system reset
- **Clock Input (wclk)**: Working clock for counter operation with clock enable signal (wclk_en)
- **Reset Inputs**: APB reset (prst_n) and working clock reset (wrst_n), both active low, asynchronous

**Software Visibility**:

- Software can read and write configuration registers when lock is disabled
- Software can read current counter value at any time without affecting operation
- Software can observe raw and masked interrupt status
- Software can clear interrupts by writing to dedicated clear register
- Software can enable/disable interrupt and reset generation independently
- Software can configure counter decrement rate through clock divider settings
- Software can read device identification through peripheral ID and component ID registers

**Device Behavior**:

- **Normal Operation Flow**:
  1. Software unlocks device by writing 0x1ACCE551 to WDOGLOCK
  2. Software configures timeout period in WDOGLOAD register
  3. Software sets step_value for clock division and enables INTEN in WDOGCONTROL
  4. Counter begins decrementing from WDOGLOAD value by step_value each enabled clock
  5. When counter reaches zero, wdogint signal asserts if INTEN=1
  6. If software clears interrupt via WDOGINTCLR, counter reloads and continues
  7. If interrupt not cleared and counter reaches zero again, wdogres asserts if RESEN=1

- **State Machine**: Counter operates in three states:
  1. Idle: INTEN=0, counter not running
  2. Counting: INTEN=1, counter decrementing, no timeout yet
  3. Interrupt Pending: Counter reached zero once, wdogint asserted, awaiting clear or second timeout

**Reset Behavior**:

- On prst_n assertion: All registers reset to default values, outputs de-asserted
- On wrst_n assertion: Counter domain resets, WDOGVALUE returns to 0xFFFFFFFF
- WDOGLOCK initializes to unlocked state (0x00000000)
- WDOGLOAD initializes to maximum value (0xFFFFFFFF)
- WDOGCONTROL initializes to all zeros (timer disabled)

**Interrupt Generation**:

- First timeout (counter reaches zero with INTEN=1): Assert wdogint, continue counting from WDOGLOAD
- Interrupt remains asserted until WDOGINTCLR written
- Writing WDOGINTCLR clears wdogint and reloads counter from WDOGLOAD
- WDOGRIS shows raw interrupt status, WDOGMIS shows masked status (WDOGRIS & INTEN)

**Timing Characteristics**:

- Counter decrement occurs on rising edge of wclk when wclk_en is high
- Step value determines decrement amount: 1, 2, 4, 8, or 16 per clock cycle
- Timeout period = WDOGLOAD / (step_value × wclk_frequency)
- Signal outputs (wdogint, wdogres) change synchronously with wclk domain

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

### Simics Hardware Completeness
- [x] Device type identified and specified (ARM PrimeCell SP805 Watchdog Timer)
- [x] Register map described at high level with all 21 registers documented
- [x] External interfaces and software visibility documented
- [x] Timing behavior, state machine, and operational modes specified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted from hardware specifications
- [x] Ambiguities marked (none found - specifications are comprehensive)
- [x] User scenarios defined with firmware engineer perspective
- [x] Requirements generated covering all hardware aspects
- [x] Entities identified (device, registers, signals, clock domains)
- [x] Review checklist passed

---

## Git Version Control

**Next Step**: Commit this specification with:

```bash
cd /home/hfeng1/latest-vscode
git add specs/001-create-a-comprehensive/spec.md
git commit -m "specify: simics-watchdog-timer - initial specification created"
```


## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements with [NEEDS CLARIFICATION: ...]
6. Identify Key Entities (if data involved)
7. Run Review Checklist and Update Status
   → Search entire spec for [NEEDS CLARIFICATION] markers
   → If found: WARN "Spec has uncertainties - this is EXPECTED for Draft status", keep "No [NEEDS CLARIFICATION] markers remain" box UNCHECKED
   → If NOT found: Mark [x] "No [NEEDS CLARIFICATION] markers remain"
   → For objective items (no implementation details, mandatory sections completed): Mark [x] if passing
   → For subjective items (testable requirements, measurable criteria): Leave unchecked for human review
8. Return: SUCCESS (spec ready for planning) with all applicable checklist items marked
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- **Simics sections**: Include "Hardware Specification" section only for hardware device modeling projects
- **Simics project detection**: Look for keywords in feature description:
  * "device modeling", "DML device", or "DML 1.4"
  * "hardware simulation" or "Simics platform"
  * "register map" or "memory-mapped registers"
  * "device model" with hardware context
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### Simics DML Device Modeling Guidance
**Note**: For Simics device modeling projects, comprehensive DML learning resources are available:
- **.specify/memory/DML_grammar.md**: Complete DML 1.4 grammar reference with syntax rules and language constructs
- **.specify/memory/DML_Device_Development_Best_Practices.md**: Best practices, patterns, and common pitfalls for DML development

**During /specify phase**: Focus on WHAT the device does (hardware behavior specification)
- Describe device functionality from hardware perspective
- Specify register behaviors without DML implementation details
- Define interfaces and protocols the device supports
- Document timing and state machine behaviors

**In later phases**: The /plan and /tasks phases will require reading and studying the DML documents before implementation. This specification should remain focused on hardware behavior, not DML syntax or coding patterns.

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

### Best Practices for Marking Uncertainties
- **Be specific**: Not "auth method unclear" but "[NEEDS CLARIFICATION: authentication method - email/password, SSO, OAuth, or other?]"
- **Don't over-mark**: If requirement is clear from context, don't mark it
- **Test mindset**: If you can't write a test case without guessing, mark it
- **Common areas to check**: User types, retention policies, performance targets, error handling, integration points

---

## 📝 Example Feature Descriptions

### Example 1: Simple Feature
"Add a dark mode toggle to the application settings that persists user preference across sessions."

### Example 2: Data-Heavy Feature
"Create a product inventory system where users can add products with name, SKU, price, and quantity. Support bulk import from CSV and export to Excel. Send email alerts when stock falls below reorder threshold."

### Example 3: Simics Hardware Feature
"Implement a DML 1.4 watchdog timer device model for Simics with configurable timeout, hardware reset capability, and memory-mapped control registers. The device should support interrupt generation and integration with QSP-x86 platform."

**Note**: When writing the specification for this, describe the watchdog timer's hardware behavior (countdown mechanism, reset conditions, interrupt generation) without DML implementation details. DML syntax and best practices will be learned in subsequent /plan and /tasks phases using dedicated study documents.

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
[Describe the main user journey in plain language]

### Acceptance Scenarios
1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

### Edge Cases
- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*
- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*
- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

### Hardware Specification *(Simics projects only)*

**Important**: This section describes WHAT the hardware device does, not HOW to implement it in DML.
- Focus on hardware behavior and functionality
- Avoid DML syntax, templates, or implementation patterns
- DML learning will occur in /plan and /tasks phases using dedicated grammar and best practices documents

**Content Guidelines**:
- **Device Type**: [e.g., Network controller, Storage device, Memory controller, Timer device, Interrupt controller]
- **Register Map**: [High-level register categories and their purposes - describe register functions, not DML declarations]
  * Example: "Control register enables/disables timer and sets mode"
  * Not: "register control size 4 @ 0x00 { ... }" (this is DML syntax)
- **External Interfaces**: [Ports, connections, and protocols the device supports - describe connections, not DML interface declarations]
  * Example: "Device connects to system bus via memory-mapped I/O"
  * Not: "port bank { implement io_memory; ... }" (this is DML syntax)
- **Software Visibility**: [What aspects of the device software can observe/control]
  * Example: "Software can read timer value, configure timeout, and enable interrupts"
- **Device Behavior**: [State machines, timing, events, and operational modes]
  * Example: "When enabled, timer counts down from configured value and triggers interrupt on zero"
- **Reset Behavior**: [What happens when device is reset]
- **Interrupt Generation**: [Conditions that trigger interrupts]

**Remember**: Detailed DML implementation guidance, grammar rules, and best practices are available in:
- `.specify/memory/DML_grammar.md` (syntax, language constructs)
- `.specify/memory/DML_Device_Development_Best_Practices.md` (patterns, pitfalls)

These will be studied thoroughly in /plan and /tasks phases before any DML code is written.

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

### Simics Hardware Completeness *(if applicable)*
- [ ] Device type identified and specified
- [ ] Register map described at high level (no implementation details)
- [ ] External interfaces and software visibility documented

---

## Execution Status
*Conceptual checklist - agents should mark items as they complete each workflow step*

- [ ] User description parsed
- [ ] Key concepts extracted
- [ ] Ambiguities marked
- [ ] User scenarios defined
- [ ] Requirements generated
- [ ] Entities identified
- [ ] Review checklist passed

## Git Version Control

**MANDATORY: Commit After Each Major Update**

- **WHEN**: After completing the specification or making significant updates
- **WHAT**: Stage and commit the spec file and any related changes
- **HOW**: Use these exact commands:
  ```bash
  git add -A
  git commit -m "specify: <feature-name> - <section/update-description>"
  ```
- **EXAMPLES**:
  - Initial spec: `git commit -m "specify: device-name - initial specification created"`
  - Updated requirements: `git commit -m "specify: device-name - updated functional requirements"`
  - Added clarifications: `git commit -m "specify: device-name - added clarifications section"`
- **WHY**: This creates a clear audit trail of specification evolution, making it easy to:
  - Track how requirements evolved
  - Understand decision rationale
  - Review specification history
  - Revert to previous specification versions if needed
- **CRITICAL**: Always commit specification changes to maintain project history

---
