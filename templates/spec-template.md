# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

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
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- **Simics sections**: Include only for hardware device modeling projects
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

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

**Device Overview**:
- **Device Type**: [e.g., PCI Network controller, I2C Storage device, Memory-mapped Memory controller]
- **Base Address**: [e.g., 0x1000, dynamically assigned, or NEEDS CLARIFICATION]
- **Address Space Size**: [e.g., 4KB, 64 registers, or NEEDS CLARIFICATION]
- **External Interfaces**: [Ports, bus connections, interrupt lines, DMA channels the device exposes]

**Register Map** *(use table format for each register)*:

| Offset | Name | Size | Access | Reset | Purpose |
|--------|------|------|--------|-------|---------|
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control and enable flags |
| 0x04 | STATUS | 32-bit | R/O | 0x0001 | Device status indicators |
| 0x08 | DATA | 32-bit | R/W | 0x0000 | Data transfer register |
| ... | ... | ... | ... | ... | ... |

*For each register with bit fields, detail the fields:*

**CONTROL Register (0x00)** bit fields:
- Bits [31:8]: Reserved (must be 0)
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupt generation
- Bit 6: DMA_ENABLE (R/W) - Enable DMA transfers
- Bits [5:1]: Reserved
- Bit 0: DEVICE_ENABLE (R/W) - Master enable for device operation

**STATUS Register (0x04)** bit fields:
- Bits [31:4]: Reserved
- Bit 3: ERROR (R/O) - Error condition detected
- Bit 2: BUSY (R/O) - Device busy processing
- Bit 1: INTERRUPT_PENDING (R/O) - Interrupt waiting to be serviced
- Bit 0: READY (R/O) - Device ready for operations

*Continue for all registers...*

**Operational Behavior**:
- **Initialization**: [Sequence of register writes needed to initialize device, e.g., "Write 0x1 to CONTROL.DEVICE_ENABLE"]
- **Normal Operation**: [Key register interactions during typical use, e.g., "Write data to DATA register, then set CONTROL.START_TRANSFER"]
- **Error Handling**: [How errors are signaled and cleared, e.g., "STATUS.ERROR set on failure, write 1 to CONTROL.CLEAR_ERROR to reset"]
- **Interrupts**: [When interrupts fire and how to acknowledge, e.g., "Interrupt fires when STATUS.INTERRUPT_PENDING=1, clear by reading STATUS"]

**Software Visibility**:
- [What aspects of device behavior are observable from software]
- [What internal state is NOT visible to software]
- [Timing constraints or ordering requirements for register access]

**Examples of marking unclear specifications**:
- **Base Address**: [NEEDS CLARIFICATION: Is this PCI BAR-based or fixed memory-mapped?]
- **CONTROL.RESERVED bits**: [NEEDS CLARIFICATION: Should writes to reserved bits be ignored or cause errors?]
- **Interrupt line**: [NEEDS CLARIFICATION: Which interrupt line number or dynamically assigned?]

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

---

## Execution Status
*Updated by main() during processing*

- [ ] User description parsed
- [ ] Key concepts extracted
- [ ] Ambiguities marked
- [ ] User scenarios defined
- [ ] Requirements generated
- [ ] Entities identified
- [ ] Review checklist passed

---
