# Feature Specification: Simics Watchdog Timer Device Implementation

**Feature Branch**: `001-read-the-simics`
**Created**: October 25, 2025
**Status**: Draft (changes to "Ready for Planning" when all [NEEDS CLARIFICATION] markers are resolved)
**Input**: User description: "Read the Simics WDT specification from /home/hfeng1/adk-python/simics-wdt-spec.md and the hardware specifications from /home/hfeng1/adk-python/wdt.md to create a comprehensive Simics watchdog timer device implementation"

## Execution Flow (main)
```
1. Parse user description from Input
   → User requests implementation of Simics watchdog timer device based on specifications
2. Extract key concepts from description
   → Actors: Simulation platform, device drivers, system software
   → Actions: Countdown timing, interrupt generation, system reset, lock protection
   → Data: 32-bit timer values, control registers, status information
   → Constraints: ARM PrimeCell compatibility, DML 1.4 implementation
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → Defined clear testing scenarios for watchdog functionality
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

## User Scenarios & Testing

### Primary User Story
Platform developers and system engineers need a realistic watchdog timer device model in Simics to accurately simulate embedded systems that rely on watchdog protection mechanisms. The device should behave identically to the ARM PrimeCell watchdog timer hardware, allowing software drivers and applications to interact with it through memory-mapped registers and receive proper interrupt and reset signals when timeout conditions occur.

### Acceptance Scenarios
1. **Given** the watchdog device is integrated into a Simics platform, **When** system software configures the timer with a timeout value and enables it, **Then** the device counts down and generates an interrupt when reaching zero
2. **Given** an interrupt has been generated and not cleared, **When** the timer reaches zero again, **Then** the device asserts a reset signal to the system
3. **Given** the lock register is in locked state, **When** software attempts to write to control registers, **Then** the writes are ignored and register values remain unchanged
4. **Given** the device is in integration test mode, **When** test software writes to the test output register, **Then** interrupt and reset signals are directly controlled without timer countdown
5. **Given** a simulation checkpoint is taken, **When** the simulation is restored, **Then** the watchdog timer continues counting from the exact state it was in when checkpointed

### Edge Cases
- What happens when software writes to the interrupt clear register while the timer is not in timeout state?
- How does the system handle attempts to configure invalid step values in the control register?
- What occurs if the lock register receives the unlock key while the device is already unlocked?
- How does the device behave during rapid successive writes to control registers?

## Requirements

### Functional Requirements
- **FR-001**: Device MUST implement a 32-bit down-counting timer that decrements at configurable clock frequencies
- **FR-002**: Device MUST support five clock divider settings (÷1, ÷2, ÷4, ÷8, ÷16) for different timing intervals
- **FR-003**: Device MUST generate an interrupt signal when the counter reaches zero for the first time
- **FR-004**: Device MUST generate a reset signal when the counter reaches zero a second time without interrupt clearance
- **FR-005**: Device MUST implement 21 memory-mapped registers according to ARM PrimeCell specification
- **FR-006**: Device MUST provide lock protection mechanism using magic unlock value 0x1ACCE551
- **FR-007**: Device MUST support integration test mode for direct signal control during testing
- **FR-008**: Device MUST reload counter value from load register when interrupt is enabled after being disabled
- **FR-009**: Device MUST reload counter value from load register when interrupt clear register is written
- **FR-010**: Device MUST maintain persistent device identification through peripheral ID and PrimeCell ID registers
- **FR-011**: Device MUST support checkpoint and restoration of all internal state
- **FR-012**: Device MUST integrate with QSP-x86 platform at memory address 0x1000
- **FR-013**: Device MUST connect interrupt and reset outputs to platform controllers
- **FR-014**: Device MUST achieve minimal simulation performance overhead for real-time operation
- **FR-015**: Device MUST maintain compatibility with Simics 7.x and DML 1.4 standards

### Key Entities
- **Timer Counter**: 32-bit value that decrements according to configured step size and clock enable
- **Control Register**: Configuration for interrupt enable, reset enable, and clock divider settings
- **Load Register**: Initial value loaded into counter when timer is enabled or interrupt is cleared
- **Status Registers**: Raw and masked interrupt status reflecting current timer state
- **Lock Register**: Protection mechanism controlling write access to other registers
- **Identification Registers**: Fixed values identifying device type, version, and manufacturer
- **Integration Test Registers**: Special mode registers for direct signal control during testing

### Hardware Specification

**Important**: This section describes WHAT the hardware device does, not HOW to implement it in DML.

**Device Type**: Watchdog Timer - A safety device that monitors system operation and provides recovery mechanisms through interrupts and resets

**Register Map**: The device implements 21 memory-mapped registers organized in functional groups:
* **Core Timer Registers (0x00-0x14)**: Load value register for setting initial countdown value, current value register for reading real-time counter state, control register for enabling timer/interrupt/reset and setting clock divider, interrupt clear register for acknowledging timeouts, raw interrupt status register showing unmasked interrupt state, masked interrupt status register showing final interrupt output
* **Protection Register (0xC00)**: Lock register preventing unauthorized modification of timer configuration
* **Test Registers (0xF00-0xF04)**: Integration test control register for entering test mode, integration test output register for directly driving interrupt and reset signals
* **Identification Registers (0xFD0-0xFFC)**: Eight peripheral ID registers and four PrimeCell ID registers containing fixed values identifying device type, manufacturer, and version

**External Interfaces**: The device connects to the system through multiple interface types:
* **Memory Interface**: Memory-mapped register access through system bus for software control and monitoring
* **Clock Interface**: Working clock input with clock enable signal for controlling timer progression
* **Reset Interface**: Reset input for initializing device state
* **Interrupt Interface**: Interrupt output signal connecting to system interrupt controller
* **System Reset Interface**: Reset output signal connecting to system reset controller

**Software Visibility**: Software can observe and control all aspects of device operation:
* **Timer Configuration**: Set initial countdown value, enable/disable timer operation, configure clock divider ratio
* **Interrupt Management**: Enable/disable interrupt generation, read interrupt status, clear interrupt conditions
* **Reset Control**: Enable/disable reset generation on second timeout
* **Real-time Monitoring**: Read current timer value during countdown operation
* **Protection Control**: Lock/unlock register write access using magic key value
* **Device Identification**: Read fixed identification values for driver compatibility verification

**Device Behavior**: The watchdog timer operates as a safety monitoring system with multiple operational modes:
* **Normal Operation**: When enabled, timer loads initial value and counts down at configured rate; generates interrupt on first zero crossing; generates reset on second zero crossing if interrupt not cleared
* **Lock Protection**: When locked, all configuration registers ignore write attempts; only lock register accepts unlock key to restore write access
* **Integration Test Mode**: When enabled, timer counting is bypassed and interrupt/reset signals are directly controlled by test register writes
* **Idle Mode**: When disabled, timer maintains current value without counting and generates no signals

**Reset Behavior**: Device supports two independent reset domains:
* **Bus Reset**: Initializes all registers to default values and disables timer operation
* **Working Clock Reset**: Resets timer counting logic while preserving register configuration

**Interrupt Generation**: Interrupt signal activation follows specific conditions:
* **First Timeout**: Interrupt asserted when counter reaches zero and interrupt enable bit is set
* **Interrupt Persistence**: Interrupt remains active until explicitly cleared by software
* **Interrupt Clearing**: Writing any value to interrupt clear register deasserts interrupt and reloads counter
* **Masking**: Final interrupt output is logical AND of raw interrupt status and interrupt enable bit

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
- [x] Device type identified and specified
- [x] Register map described at high level (no implementation details)
- [x] External interfaces and software visibility documented

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

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

---
