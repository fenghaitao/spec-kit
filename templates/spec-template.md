# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [DATE]
**Status**: Draft (changes to "Ready for Planning" when all [NEEDS CLARIFICATION] markers are resolved)
**Input**: User description: "$ARGUMENTS" (text provided after /specify command)

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

**Device Purpose**:
- **Device Type**: [e.g., Watchdog timer, Network controller, Storage device, Memory controller]
- **Primary Function**: [What the device does from software/user perspective]
- **Use Cases**: [When and why software would use this device]

**Register Map** *(parsed from hardware specification document)*:

| Offset | Name | Size | Access | Reset | Purpose |
|--------|------|------|--------|-------|---------|
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control and enable flags |
| 0x04 | STATUS | 32-bit | R/O | 0x0001 | Device status indicators |
| 0x08 | TIMEOUT | 32-bit | R/W | 0x0000 | Timeout period configuration |
| 0x0C | COUNTER | 32-bit | R/O | 0x0000 | Current countdown value |
| ... | ... | ... | ... | ... | ... |

*For each register with bit fields, detail the fields:*

**CONTROL Register (0x00)** bit fields:
- Bits [31:8]: Reserved (must be 0)
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupt generation
  * Side effect: When set to 1, enables interrupt generation; when cleared, disables interrupts
- Bit 6: DMA_ENABLE (R/W) - Enable DMA transfers
  * Side effect: When set to 1, enables DMA engine; when cleared, stops DMA transfers
- Bits [5:1]: Reserved
- Bit 0: DEVICE_ENABLE (R/W) - Master enable for device operation
  * Side effect: Writing 1 triggers device initialization sequence, resets COUNTER to 0, clears STATUS.ERROR

**STATUS Register (0x04)** bit fields:
- Bits [31:4]: Reserved
- Bit 3: ERROR (R/O) - Error condition detected
- Bit 2: BUSY (R/O) - Device busy processing
- Bit 1: INTERRUPT_PENDING (R/O) - Interrupt waiting to be serviced
- Bit 0: READY (R/O) - Device ready for operations

**TIMEOUT Register (0x08)** bit fields:
- Bits [31:0]: TIMEOUT_VALUE (R/W) - Timeout period in milliseconds

**COUNTER Register (0x0C)** bit fields:
- Bits [31:0]: COUNTER_VALUE (R/O) - Current countdown value in milliseconds

*Continue for all registers...*

**Operational Behavior** *(parsed from hardware specification)*:
- **Initialization**: [Sequence of register writes needed to initialize device, e.g., "Write 0x1 to CONTROL.DEVICE_ENABLE"]
- **Normal Operation**: [Key register interactions during typical use, e.g., "Write timeout to TIMEOUT register, write 1 to CONTROL.DEVICE_ENABLE, periodically write 1 to CONTROL to reset timer"]
- **Error Handling**: [How errors are signaled and cleared, e.g., "STATUS.ERROR set on failure, write 1 to CONTROL.CLEAR_ERROR to reset"]
- **Interrupts**: [When interrupts fire and how to acknowledge, e.g., "Interrupt fires when COUNTER reaches 0, clear by reading STATUS register"]

**External Interfaces**:
- **Bus Connection**: [e.g., "Memory-mapped I/O at base address 0x1000", or NEEDS CLARIFICATION]
- **Interrupt Lines**: [e.g., "IRQ 5 for timeout events", or NEEDS CLARIFICATION]
- **DMA Channels**: [e.g., "No DMA required", or NEEDS CLARIFICATION]
- **Other Connections**: [e.g., "Reset output line to system reset controller", or NEEDS CLARIFICATION]

**Software Visibility** *(what software can observe/control)*:
- [What aspects of device behavior are observable from software]
- [What internal state is NOT visible to software]
- [Ordering requirements for register access]

**Examples of marking unclear specifications**:
- **Base Address**: [NEEDS CLARIFICATION: Is this PCI BAR-based or fixed memory-mapped?]
- **CONTROL.RESERVED bits**: [NEEDS CLARIFICATION: Should writes to reserved bits be ignored or cause errors?]
- **Interrupt line**: [NEEDS CLARIFICATION: Which interrupt line number or dynamically assigned?]
- **Reset behavior**: [NEEDS CLARIFICATION: What happens to all registers on hardware reset?]

**RAG Query Guidance** *(for incomplete information)*:
If information is missing or unclear during /specify phase, use RAG to query the original hardware specification:
- **Missing register details**: `perform_rag_query("CONTROL register bit field definitions", source_type="docs", filter="hardware_spec.pdf")`
- **Unclear behavior**: `perform_rag_query("device initialization sequence and register write order", source_type="docs")`
- **Side effects**: `perform_rag_query("register side effects and state changes on write", source_type="docs")`
- **Timing constraints**: `perform_rag_query("register access timing requirements and constraints", source_type="docs")`

Mark areas that need RAG queries with: [RAG QUERY NEEDED: specific question about hardware spec]

**Note**: This section contains the complete parsed hardware specification. The /plan phase will transform this into DML-specific data-model.md format.

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
