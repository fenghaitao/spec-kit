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
