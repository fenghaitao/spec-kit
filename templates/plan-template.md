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
├── quickstart.md        # Phase 1 output (/speckit.plan command)
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

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

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
```
