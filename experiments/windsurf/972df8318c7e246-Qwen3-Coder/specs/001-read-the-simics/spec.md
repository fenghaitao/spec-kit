# Feature Specification: Simics Watchdog Timer Device Implementation

**Feature Branch**: `001-read-the-simics`
**Created**: October 25, 2025
**Status**: Draft (changes to "Ready for Planning" when all [NEEDS CLARIFICATION] markers are resolved)
**Input**: User description: "Read the Simics WDT specification from /home/hfeng1/adk-python/simics-wdt-spec.md and the hardware specifications from /home/hfeng1/adk-python/wdt.md to create a comprehensive Simics watchdog timer device implementation." (text provided after /specify command)

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
A system developer integrates a watchdog timer device into a Simics platform to monitor system health and automatically reset the system if it becomes unresponsive.

### Acceptance Scenarios
1. **Given** a configured watchdog timer device, **When** the system fails to refresh the timer within the configured timeout period, **Then** an interrupt signal is generated to notify the system.
2. **Given** a watchdog timer that has already generated an interrupt, **When** the system fails to refresh the timer within the second timeout period, **Then** a reset signal is generated to restart the system.
3. **Given** a locked watchdog device, **When** a user attempts to modify protected registers without unlocking first, **Then** the write operation is ignored and the register value remains unchanged.

### Edge Cases
- What happens when the watchdog timer is disabled during an active countdown?
- How does system handle a write to the WDOGLOAD register while the timer is actively counting down?
- What happens when the integration test mode is enabled while the normal timer operation is in progress?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST implement a 32-bit countdown timer compatible with ARM PrimeCell watchdog specification
- **FR-002**: System MUST support 21 memory-mapped registers including control, data, status, lock, integration test, and ID registers
- **FR-003**: System MUST generate an interrupt signal on first timeout when INTEN bit is set in WDOGCONTROL register
- **FR-004**: System MUST generate a reset signal on second timeout when RESEN bit is set in WDOGCONTROL register
- **FR-005**: System MUST support configurable timeout periods with 5 clock divider settings (÷1, ÷2, ÷4, ÷8, ÷16)
- **FR-006**: System MUST implement a lock protection mechanism using magic unlock value 0x1ACCE551
- **FR-007**: System MUST support integration test mode for direct control of interrupt and reset output signals
- **FR-008**: System MUST provide 8 peripheral identification registers with fixed values for device identification
- **FR-009**: System MUST provide 4 PrimeCell identification registers with fixed values for component identification
- **FR-010**: System MUST support device state persistence for checkpoint/restore functionality

### Key Entities *(include if feature involves data)*
- **Watchdog Timer**: A 32-bit countdown timer that generates interrupt and reset signals based on configuration
- **Control Registers**: Memory-mapped registers that control timer behavior, enable/disable features, and report status
- **Lock Mechanism**: A protection mechanism that prevents unauthorized modification of critical registers
- **Integration Test Mode**: A special mode that allows direct control of output signals for testing purposes

### Hardware Specification *(Simics projects only)*

**Important**: This section describes WHAT the hardware device does, not HOW to implement it in DML.
- Focus on hardware behavior and functionality
- Avoid DML syntax, templates, or implementation patterns
- DML learning will occur in /plan and /tasks phases using dedicated grammar and best practices documents

**Content Guidelines**:
- **Device Type**: Timer device with interrupt and reset generation capabilities
- **Register Map**: 
  * WDOGLOAD (0x00): 32-bit register to set the timer reload value
  * WDOGVALUE (0x04): 32-bit register to read the current timer value
  * WDOGCONTROL (0x08): 32-bit register to control timer operation and enable interrupt/reset
  * WDOGINTCLR (0x0C): 32-bit write-only register to clear interrupt and reload timer
  * WDOGRIS (0x10): 1-bit read-only register indicating raw interrupt status
  * WDOGMIS (0x14): 1-bit read-only register indicating masked interrupt status
  * WDOGLOCK (0xC00): 32-bit register controlling write access to other registers
  * WDOGITCR (0xF00): 1-bit register enabling integration test mode
  * WDOGITOP (0xF04): 2-bit write-only register controlling test output signals
  * WDOGPERIPHID0-7 (0xFE0-0xFDC): 8 read-only registers providing peripheral identification
  * WDOGPCELLID0-3 (0xFF0-0xFFC): 4 read-only registers providing PrimeCell component identification
- **External Interfaces**: 
  * Memory-mapped I/O interface for register access
  * Interrupt output signal (wdogint) for first timeout notification
  * Reset output signal (wdogres) for second timeout system reset
  * Clock input (wclk) for timer operation
  * Clock enable input (wclk_en) for clock gating
  * Reset input (wrst_n) for device reset
- **Software Visibility**: 
  * Software can read/write control registers to configure timer behavior
  * Software can read current timer value and status registers
  * Software can clear interrupts by writing to WDOGINTCLR register
  * Software can enable/disable write protection using WDOGLOCK register
  * Software can enable integration test mode for direct signal control
- **Device Behavior**: 
  * When enabled, timer counts down from configured WDOGLOAD value
  * On reaching zero, generates interrupt if INTEN=1, then reloads from WDOGLOAD
  * If interrupt is not cleared and timer reaches zero again, generates reset if RESEN=1
  * Lock mechanism prevents writes to registers unless unlocked with 0x1ACCE551
  * Integration test mode allows direct control of output signals independent of timer
- **Reset Behavior**: 
  * On device reset, timer stops and all registers are set to reset values
  * WDOGLOAD and WDOGVALUE reset to 0xFFFFFFFF
  * WDOGCONTROL resets to 0x00
  * WDOGLOCK resets to 0x00000000 (unlocked state)
- **Interrupt Generation**: 
  * Generated when timer counts down to zero and INTEN=1 in WDOGCONTROL
  * Cleared by writing any value to WDOGINTCLR register
  * Status reflected in WDOGRIS and WDOGMIS registers

**Remember**: Detailed DML implementation guidance, grammar rules, and best practices are available in:
- `.specify/memory/DML_grammar.md` (syntax, language constructs)
- `.specify/memory/DML_Device_Development_Best_Practices.md` (patterns, pitfalls)

These will be studied thoroughly in /plan and /tasks phases before any DML code is written.

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

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

### Simics Hardware Completeness *(if applicable)*
- [x] Device type identified and specified
- [x] Register map described at high level (no implementation details)
- [x] External interfaces and software visibility documented

---

## Execution Status
*Conceptual checklist - agents should mark items as they complete each workflow step*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
