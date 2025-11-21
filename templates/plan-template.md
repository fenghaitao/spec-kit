# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Inputs**:
- Feature specification: `/specs/[###-feature-name]/spec.md`
- Register definitions: `/specs/[###-feature-name]/[device-name]-register.xml`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [DML 1.4 or NEEDS CLARIFICATION]
**Simics Version**: [e.g., Simics Base 7.57.0 or use MCP `get_simics_version()` or NEEDS CLARIFICATION]
**Required Packages**: [e.g., simics-base, simics-qsp-x86 or use MCP `list_installed_packages()` or NEEDS CLARIFICATION]
**Available Platforms**: [use MCP `list_simics_platforms()` to discover available simulation targets or NEEDS CLARIFICATION]
**MCP Server**: [simics-mcp-server integration available with 22+ tools for project automation, device modeling and documentation access]
**Device Type**: [e.g., PCI device, memory controller, peripheral, timer, UART or NEEDS CLARIFICATION]
**Hardware Interfaces**: [e.g., memory-mapped registers, DMA, interrupts, signal ports or NEEDS CLARIFICATION]
**Performance Goals**: [e.g., <1% simulation overhead, cycle-accurate timing, functional accuracy or NEEDS CLARIFICATION]
**Constraints**: [e.g., software-visible behavior, register access patterns, state persistence or NEEDS CLARIFICATION]
**Scale/Scope**: [e.g., register count, interface complexity, state variables or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── spec.md              # Feature specification (input)
├── [device-name]-register.xml  # Register definitions (input)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── test-scenarios.md    # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->
**Simics Project Structure** (created by MCP tools in Phase 3):

```text
simics-project/modules/[device-name]/
  ├── [device-name].dml
  ├── registers.dml (optional)
  ├── interfaces.dml (optional)
  └── test/
      ├── s-[device-name].py
      └── test_[name]_common.py
```

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## Plan Completion Checklist

Use this checklist to verify all /plan command steps have been completed:

### Step 1: Setup & Context Loading
- [ ] Executed setup script (`setup-plan.sh` or `setup-plan.ps1`) and parsed JSON output
- [ ] Read feature specification (`spec.md`)
- [ ] Read register definitions XML file (`[device-name]-register.xml`)
- [ ] Read constitution file (`/memory/constitution.md`)
- [ ] Loaded plan template (`plan.md`)

### Step 2: Technical Context & Constitution Check
- [ ] **Technical Context filled**:
  - [ ] Language/Version specified (no NEEDS CLARIFICATION)
  - [ ] Simics Version marked (will be resolved in Phase 0)
  - [ ] Required Packages marked (will be resolved in Phase 0)
  - [ ] Available Platforms marked (will be resolved in Phase 0)
  - [ ] Device Type identified
  - [ ] Hardware Interfaces defined
  - [ ] Performance Goals specified
  - [ ] Constraints documented
  - [ ] Scale/Scope defined
- [ ] **Constitution Check completed**:
  - [ ] Constitution gates evaluated
  - [ ] Gate results documented (PASS/FAIL)
  - [ ] Violations justified in Complexity Tracking (if any)

### Step 3: Phase 0 - Outline & Research
- [ ] Identified all unknowns from Technical Context
- [ ] **Discovery MCP Tools executed**:
  - [ ] `get_simics_version()` → Simics Version
  - [ ] `list_installed_packages()` → Required Packages
  - [ ] `list_simics_platforms()` → Available Platforms
- [ ] **Architectural RAG queries executed (3-4 MAX)**:
  - [ ] Query 1: Architectural Overview (device category, architecture)
  - [ ] Query 2: Key Design Concepts (core concepts, state management)
  - [ ] Query 3: Common Patterns (DML patterns, code snippets)
  - [ ] Query 4: Device-specific patterns (if needed)
- [ ] **research.md created** with:
  - [ ] DML Learning Prerequisites section
  - [ ] Environment Discovery (Simics version, packages, platforms)
  - [ ] Device Architecture Context (overview, concepts, patterns)
  - [ ] Example Code References (snippets from RAG)
  - [ ] Architecture Decisions (resolved NEEDS CLARIFICATION)
  - [ ] Implementation Strategy
- [ ] **plan.md updated**: All "NEEDS CLARIFICATION" replaced with discovered values
- [ ] **Validated**: `research.md` exists and contains >= 50 lines
- [ ] **Validated**: No "NEEDS CLARIFICATION" in `plan.md`
- [ ] **Git commit**: Phase 0 Research committed

### Step 4: Phase 1 - Design & Contracts
- [ ] **data-model.md created** with:
  - [ ] Registers section (extracted from XML + spec.md)
  - [ ] Internal State Variables section
  - [ ] Interfaces section
  - [ ] DML Implementation Notes section
  - [ ] Implementation Patterns section (from 1-2 RAG queries)
- [ ] **contracts/ directory created** with:
  - [ ] `register-access.md` (read/write behavior)
  - [ ] `interface-behavior.md` (interface contracts)
- [ ] **test-scenarios.md created** with:
  - [ ] Scenarios from spec.md "User Scenarios & Testing"
  - [ ] Generic Simics CLI descriptions (no MCP syntax)
  - [ ] Validation steps mapped
  - [ ] Edge cases documented
  - [ ] Optional: Test patterns from 1-2 RAG queries
- [ ] **Agent context updated** (executed agent script)
- [ ] **Constitution Check re-evaluated** after design
- [ ] **Validated**: `data-model.md` exists with patterns section
- [ ] **Validated**: `test-scenarios.md` exists with generic CLI
- [ ] **Validated**: `contracts/` directory has >= 1 file
- [ ] **Git commit**: Phase 1 Design committed

### Step 5: Completion Validation & Report
- [ ] All files exist in correct locations
- [ ] No implementation MCP tools were used during planning
- [ ] Constitution Check shows PASS (or violations justified)
- [ ] Completion report generated with all file details
- [ ] Ready to proceed to `/tasks` command

---

# research.md Structure Template

Use this structure when creating research.md in Phase 0:

```markdown
# Research: [FEATURE_NAME]

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
[Document output from get_simics_version() - include version number]

### Installed Packages
[Document output from list_installed_packages() - format as table with package details]

| Package Name | Package Number | Package Version |
|-------------|----------------|-----------------|
| [package-1-name] | [package-1-number] | [package-1-version] |
| [package-2-name] | [package-2-number] | [package-2-version] |
| [additional packages...] | [...] | [...] |

### Available Platforms
[Document output from list_simics_platforms() - list available simulation platforms]

## Device Architecture Context

[If architectural RAG queries were executed, document findings here]

### Device Category: [Timer/UART/PCI/DMA/etc.]

**Architectural Overview**:
[High-level description of device architecture from RAG results - components, typical registers, interfaces]

**Key Design Concepts**:
- [Concept 1: e.g., "Counter register with overflow interrupt"]
- [Concept 2: e.g., "Control register for enable/disable"]
- [Concept 3: e.g., "Status register for device state"]

**Common Patterns for This Device Type**:
- [Pattern 1: e.g., "Use io_memory interface for register bank"]
- [Pattern 2: e.g., "Implement signal interface for interrupt output"]
- [Pattern 3: e.g., "Use events for periodic/timed operations"]

**Implications for data-model.md**:
[How these architectural insights should inform register/interface design]

**Note**: Detailed implementation patterns (callbacks, error handling, test code) will be gathered via RAG queries during Phase 3 (tasks/implementation).

## Example Code References

[Code snippets from architectural RAG queries for implementation reference]

### Example 1: [Brief Description]
**Source**: [RAG query or documentation source]
**Applicability**: [What aspect of implementation this helps with]

```dml
[Code snippet showing relevant pattern or concept]
```

**Key Points**:
- [Important detail 1]
- [Important detail 2]

### Example 2: [Brief Description]
**Source**: [RAG query or documentation source]
**Applicability**: [What aspect of implementation this helps with]

```dml
[Code snippet showing relevant pattern or concept]
```

**Key Points**:
- [Important detail 1]
- [Important detail 2]

[Add additional examples as needed - focus on architectural patterns, not detailed implementations]

## Architecture Decisions

[For each NEEDS CLARIFICATION in Technical Context, create an entry:]

### Decision: [What was decided - e.g., "Use [technology/pattern]"]
- **Rationale**: [Why this choice - based on spec.md and MCP tool findings]
- **Alternatives Considered**: [What else was evaluated]
- **Source**: [Which MCP tool or spec section informed this decision]
- **Impact**: [How this affects implementation]

## Implementation Strategy

[Document overall approach based on spec.md requirements]

### Architecture Overview
[High-level architecture based on functional requirements]

### Key Design Patterns
[Patterns to apply based on spec.md and research]

### Testing Approach
[Testing strategy based on spec.md user scenarios]

### Next Steps
[Outline what will happen in Phase 1 (data-model, contracts, test-scenarios)]

---

# data-model.md Structure Template

Use this structure when creating data-model.md in Phase 1:

```markdown
# Data Model: [FEATURE_NAME]

## Summary

## Registers

*For each register that has side-effect in [device-name]-registers.xml, extract Purpose and Operations; add offsets, side effects, fields:*

### Register: [NAME from spec.md]
- **Offset**: [hex - assign by order/size] | **Size**: [bits from requirements/research.md] | **Access**: [RO/WO/RW from spec.md]
- **Reset**: [hex or 0x0000] | **Purpose**: [from spec.md "Purpose"]
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: [behavior] | Write: [behavior] | State: [changes] | Affects: [other registers]
- **Fields**: [bit fields from spec.md Required Capabilities]

*Example: [device-name]-registers.xml description of "CONTROL" as "Device enable | Writing DEVICE_ENABLE=1 triggers init" → Register CONTROL offset 0x00, Side Effects Write: "Triggers initialization, resets COUNTER to 0"*

## Internal State Variables
*For each internal state variable needed to implement behavior, document here with data type and purpose, transition:*

## Interfaces
*For each interface defined in [device-name]-interfaces.xml and spec.md, extract Methods and Purpose:*

### Interface: [INTERFACE_NAME]

## DML Implementation Notes
*Document DML-specific implementation notes for registers, interfaces, state variables, side-effects, access semantics, etc.*

## Implementation Patterns
*Patterns gathered via RAG queries to inform implementation approach*

### Pattern: [PATTERN_NAME from RAG results]
**Applicable To**: [Which registers/interfaces/capabilities]
**Source**: RAG query - "[query used]"
**Key Approach**:
- [High-level pattern point 1]
- [High-level pattern point 2]
- [Key DML constructs to use]

**Example Structure** (conceptual, not full implementation):
```dml
// Conceptual pattern showing structure only
[key DML construct examples - no full method bodies]
```

**Common Pitfalls**:
- [Pitfall 1 from RAG/Best Practices]
- [Pitfall 2 from RAG/Best Practices]

**References**:
- `.specify/memory/DML_Device_Development_Best_Practices.md`: [relevant section]
- Similar devices from RAG: [device names if found]

**Note**: Detailed implementations will be developed in tasks phase with additional RAG queries.
```
