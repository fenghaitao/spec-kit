# Implementation Plan Template for Simics Device Models

**INSTRUCTIONS FOR AI AGENT**: This template has two parts:
1. **PART A: GUIDANCE SECTIONS** - Read these but DO NOT include them in the generated plan
2. **PART B: PLAN CONTENT TEMPLATE** - Fill these out and include in the generated plan

---

# PART A: GUIDANCE SECTIONS (DO NOT COPY TO GENERATED PLAN)

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
   → Extract: Functional Requirements, Register Map, Hardware Specification
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Extract DML version, Simics API, device type, hardware interfaces
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, test-scenarios.md
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Core Principles

1. **Complete Phase 0 before Phase 1** - Execute all Discovery MCP tools and resolve all NEEDS CLARIFICATION
2. **Minimal RAG queries** - Phase 0: 1-2 architectural queries; Phase 1: 1-2 pattern queries
3. **Validate each phase** - Run bash commands to verify files exist before proceeding
4. **No implementation** - Create design docs only; no MCP implementation tools (create_simics_project, etc.)

## Common Pitfalls

- Skipping Discovery MCP tools (get_simics_version, list_installed_packages, list_simics_platforms)
- Too many RAG queries (limit to 1-2 per phase)
- Leaving NEEDS CLARIFICATION unresolved
- Using MCP tool syntax in test-scenarios.md (use generic descriptions)
- Executing implementation MCP tools (create_simics_project, add_dml_device_skeleton - these belong in Phase 3)
- Not validating files exist before reporting completion

---
---

# PART B: PLAN CONTENT TEMPLATE (COPY AND FILL OUT IN GENERATED PLAN)

---

# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [Current date in YYYY-MM-DD format] | **Spec**: [link to spec.md]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

## Summary
[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context
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
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── test-scenarios.md    # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

**Project Structure** (created by MCP tools in Phase 3):
```
simics-project/modules/[device-name]/
  ├── [device-name].dml
  ├── registers.dml (optional)
  ├── interfaces.dml (optional)
  └── test/
      ├── s-[device-name].py
      └── test_[name]_common.py
```

**Note**: MCP tools auto-generate structure at repo root during Phase 3 Setup. specs/ contains only documentation.

## Phase 0: Outline & Research

### Step 0.1: Identify Research Needs
Extract unknowns from Technical Context above:
- For each NEEDS CLARIFICATION → research task
- For each hardware interface → patterns task
- For each register → implementation details task

### Step 0.2: Execute Discovery MCP Tools

**MANDATORY - Execute these tools immediately**:

1. **Environment Discovery**:
   - Execute `get_simics_version()` → resolve Simics Version NEEDS CLARIFICATION
   - Execute `list_installed_packages()` → resolve Required Packages NEEDS CLARIFICATION
   - Execute `list_simics_platforms()` → resolve Available Platforms NEEDS CLARIFICATION

2. **Architectural Context (1-2 queries MAX)**:
   
   **Purpose**: Gather high-level device category understanding to inform data-model.md design
   
   **Query Strategy**:
   - Read spec.md to identify device category (e.g., "timer", "UART", "PCI device", "DMA controller")
   - Execute 1-2 architectural overview queries (NOT detailed implementation)
   
   **Examples**:
   - Timer device: `"DML timer device architecture counter overflow interrupt concepts"`
   - UART device: `"DML UART serial device architecture transmit receive buffer concepts"`
   - PCI device: `"DML PCI device architecture configuration space BAR concepts"`
   - DMA device: `"DML DMA controller architecture memory transfer concepts"`
   
   **Execution**:
   ```python
   perform_rag_query(
       query="[device category] device architecture [key concepts] overview",
       source_type="docs",  # Use "docs" for architectural overviews
       match_count=5
   )
   ```
   
   **What to extract**:
   - High-level device architecture (components, registers, interfaces)
   - Common design patterns for this device category
   - Key concepts that should inform register/interface design
   
   **What NOT to query**:
   - ❌ Detailed register implementation patterns (save for Phase 3)
   - ❌ Specific callback implementations (save for Phase 3)
   - ❌ Test code examples (save for Phase 3)
   - ❌ Error handling details (save for Phase 3)

**CRITICAL**: DO NOT execute implementation tools (`create_simics_project()`, `add_dml_device_skeleton()`, `build_simics_project()`) - those belong in Phase 3 (Implementation).

### Step 0.3: Parse MCP Tool and RAG Query Outputs

Extract key information from MCP tool JSON and RAG query responses:
- **get_simics_version()** → Extract Simics version for Technical Context
- **list_installed_packages()** → Extract package list for Technical Context
- **list_simics_platforms()** → Extract platform list for Technical Context
- **Architectural RAG queries** → Extract high-level architecture patterns, device components, design concepts

### Step 0.4: Create research.md File

**MANDATORY**: Create `[SPECS_DIR]/research.md` with this exact structure:

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
[What Phase 1 should focus on based on research]
```

### Step 0.5: Update Technical Context in plan.md

**MANDATORY**: Replace ALL "NEEDS CLARIFICATION" placeholders in the Technical Context section with actual discovered values:

- **Simics Version**: Replace with actual version from `get_simics_version()`
- **Required Packages**: Replace with list from `list_installed_packages()`
- **Available Platforms**: Replace with list from `list_simics_platforms()`
- Any other NEEDS CLARIFICATION items resolved through research

### Step 0.6: Update Progress Tracking in plan.md

**MANDATORY**: Update the Progress Tracking section at the end of plan.md. Mark these checkboxes:

```markdown
**Phase Status**:
- [x] Phase 0: Research complete (/plan command)

**Discovery MCP Tool Status**:
- [x] `get_simics_version()` executed and documented (MANDATORY)
- [x] `list_installed_packages()` executed and documented (MANDATORY)
- [x] `list_simics_platforms()` executed and documented (MANDATORY)
- [x] MCP tool outputs incorporated into research.md

**Architectural Context**:
- [x] Device category identified from spec.md
- [x] Architectural RAG query executed (1-2 queries MAX for high-level overview)
- [x] Device architecture patterns documented in research.md
- [x] Design implications for data-model.md noted
```

### Step 0.7: Validation Checkpoint

**MANDATORY**: Before proceeding to Phase 1, verify:
- [ ] research.md file exists at `[SPECS_DIR]/research.md`
- [ ] Technical Context in plan.md has NO "NEEDS CLARIFICATION" text
- [ ] Progress Tracking shows Phase 0 marked complete

Use bash commands to verify:
```bash
ls -la [SPECS_DIR]/research.md
grep "NEEDS CLARIFICATION" [SPECS_DIR]/plan.md
```

### Step 0.8: Announce Phase Completion

Explicitly state in your response:
```
✅ Phase 0 (Research) complete. Proceeding to Phase 1 (Design).

**Phase 0 Summary**:
- MCP tools executed: [count]
- NEEDS CLARIFICATION resolved: [count]
- research.md created: ✅
- Technical Context updated: ✅
```

**Output**: research.md with all NEEDS CLARIFICATION resolved and MCP tool outputs documented

## Phase 1: Design & Contracts
*Prerequisites: research.md complete, Phase 0 validated*

### Step 1.1: Create data-model.md

**MANDATORY**: Create `[SPECS_DIR]/data-model.md` documenting the device data structures:

- Extract registers from spec.md Register Map (names, purposes, operations) and External Interfaces
- Add implementation details: offsets, sizes, access types, bit fields, reset values, side effects
- Reference spec.md for behavioral requirements
- **Execute 1-2 pattern-focused RAG queries** to gather DML implementation patterns
- Document patterns (not full code) in "Implementation Patterns" section

**RAG Query Strategy** (1-2 queries MAX):
Execute targeted queries for implementation patterns based on device capabilities:
```python
perform_rag_query(
    query="DML [device capability] implementation pattern example",
    source_type="code",  # Search code examples
    match_count=3
)
```

**Examples**:
- "DML register bank interrupt generation pattern"
- "DML memory-mapped I/O device register access pattern"
- "DML timer device event scheduling pattern"

**What to extract from RAG results**:
- High-level structural patterns (connect objects, method structure)
- Key DML constructs to use (interfaces, events, hooks)
- Common pitfalls and best practices
- Similar device references

**What NOT to extract**:
- ❌ Full method implementations (save for tasks phase)
- ❌ Detailed error handling (save for tasks phase)
- ❌ Test code (save for tasks phase)

Use this structure:
```markdown
# Data Model: [FEATURE_NAME]

## Registers

*For each register in spec.md Register Map, extract Purpose and Operations; add offsets, side effects, fields:*

### Register: [NAME from spec.md]
- **Offset**: [hex - assign by order/size] | **Size**: [bits from requirements/research.md] | **Access**: [RO/WO/RW from spec.md]
- **Reset**: [hex or 0x0000] | **Purpose**: [from spec.md "Purpose"]
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: [behavior] | Write: [behavior] | State: [changes] | Affects: [other registers]
- **Fields**: [bit fields from spec.md Required Capabilities]

*Example: spec.md "CONTROL | Device enable | Writing DEVICE_ENABLE=1 triggers init" → Register CONTROL offset 0x00, Side Effects Write: "Triggers initialization, resets COUNTER to 0"*

## Device State

### State Variable: [NAME]
- **Type**: [type]
- **Purpose**: [description]
- **Persistence**: [checkpointed/transient]

## Interfaces

### Interface: [INTERFACE_NAME]
- **Type**: [Simics interface type]
- **Methods**: [list methods]
- **Purpose**: [description]

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

### Step 1.2: Create contracts/ directory

**MANDATORY**: Create `[SPECS_DIR]/contracts/` directory with contract specifications:

- Register access contracts (read/write behavior)
- Interface behavior specifications
- Memory transaction patterns

Create files like:
- `contracts/register-access.md` - Register read/write specifications
- `contracts/interface-behavior.md` - Interface method contracts

### Step 1.3: Generate contract tests (planning only)

**Note**: Don't create test files yet - just plan them in contracts/

Document expected register read/write behavior tests based on spec.md requirements and data-model.md register definitions

### Step 1.4: Extract test scenarios from "User Scenarios & Testing" in spec.md

**MANDATORY**: Extract test scenarios from `[SPECS_DIR]/spec.md` "User Scenarios & Testing" section:

**Extract from spec.md**:
- **Primary User Story** → main integration test scenario
- **Acceptance Scenarios** (Given/When/Then) → individual test cases
- **Edge Cases** → edge case and error handling test scenarios

**Identify integration test scenarios**:
- Each Acceptance Scenario → integration test case
- Each Edge Case → boundary/error test case
- Test scenarios based on Primary User Story and Acceptance Scenarios
- Device operational workflow tests from Primary User Story
- Register behavior tests from Acceptance Scenarios
- Error condition tests from Edge Cases

### Step 1.5: Create test-scenarios.md from "User Scenarios & Testing" in spec.md

**MANDATORY**: Create `[SPECS_DIR]/test-scenarios.md` with test scenarios based on spec.md:

**Extract from spec.md "User Scenarios & Testing"**:
- **Primary User Story** → Goal section (what users accomplish)
- **Acceptance Scenarios** → Validation Steps (Given/When/Then → What to do/Expected Result/Success Criteria)
- **Edge Cases** → Troubleshooting section (boundary conditions and error scenarios)

**CRITICAL RULES for test-scenarios.md**:
- ❌ DO NOT use MCP tool syntax (no `create_simics_project()` calls)
- ❌ DO NOT assume implementation details (no specific register names until implemented)
- ✅ DO use generic descriptions ("Create Simics project", "Build device module")
- ✅ DO focus on Simics CLI commands users will actually run
- ✅ DO use placeholders: `[DEVICE_NAME]`, `[REGISTER_NAME]` for unknowns
- ✅ DO include validation criteria: "What constitutes success for each step?"
- ✅ DO map Acceptance Scenarios to validation steps directly

Use this structure:
```markdown
# Test Scenarios: [FEATURE_NAME]

## Goal
[One sentence: What will users accomplish by following this guide?]

## Prerequisites
[Environment requirements from research.md - actual versions/packages found]
- Simics Base [version from research.md]
- Required packages: [list from research.md]

## Validation Steps
[Map each "Acceptance Scenario" from spec.md to a validation step]

### Step 1: [First Acceptance Scenario - Given/When/Then]
**What to do**:
[Translate "Given" state and "When" action into conceptual steps - no specific implementation commands]

**Expected Result**:
[Translate "Then" outcome from spec.md Acceptance Scenario]

**Success Criteria**:
[How to verify it worked - observable behavior matching the "Then" clause]

### Step 2: [Second Acceptance Scenario - Given/When/Then]
**What to do**:
[Translate "Given" state and "When" action - reference that implementation will create necessary files]

**Expected Result**:
[Translate "Then" outcome from spec.md Acceptance Scenario]

**Success Criteria**:
[How to verify it worked - observable behavior matching the "Then" clause]

[Repeat for each Acceptance Scenario in spec.md]

## Troubleshooting
[Extract from spec.md "Edge Cases" - translate each edge case into failure mode and debug approach]
- **Issue**: [Edge case from spec.md] → **Solution**: [How to debug/resolve]
- **Issue**: [Another edge case] → **Solution**: [How to debug/resolve]

## Next Steps
[References to contracts/, data-model.md, and tasks.md]
```

**MANDATORY**: Update the Progress Tracking section in plan.md. Mark these checkboxes:

```markdown
**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)

**Gate Status**:
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
```

### Step 1.7: Re-evaluate Constitution Check

After completing design artifacts, re-check constitutional compliance:
- Review data-model.md against constitution principles
- Verify design doesn't introduce violations
- If new violations: Document in Complexity Tracking section
- If violations cannot be justified: Refactor design and return to Step 1.1

### Step 1.8: Validation Checkpoint

**MANDATORY**: Before proceeding, verify ALL Phase 1 deliverables exist:

```bash
ls -la [SPECS_DIR]/data-model.md
ls -la [SPECS_DIR]/test-scenarios.md
ls -la [SPECS_DIR]/contracts/
```

Checklist:
- [ ] data-model.md file exists and contains register/entity definitions
- [ ] contracts/ directory exists with contract specifications
- [ ] test-scenarios.md file exists with user validation steps
- [ ] Agent context file updated (ADK.md or equivalent)
- [ ] Progress Tracking shows Phase 1 marked complete
- [ ] Constitution check passed (no new violations)

### Step 1.9: Announce Phase Completion

**MANDATORY**: Explicitly state in your response:
```
✅ Phase 1 (Design) complete. Ready for /tasks command.

**Phase 1 Summary**:
- data-model.md created: ✅ ([register count] registers documented)
- contracts/ created: ✅ ([file count] contract files)
- test-scenarios.md created: ✅ ([scenario count] test scenarios)
- Constitutional compliance: ✅
```

**Output**: data-model.md, /contracts/*, test-scenarios.md

   **test-scenarios.md Structure**:
   ```
   # Quick Start: [FEATURE_NAME]

   ## Goal
   [One sentence: What will users accomplish by following this guide?]

   ## Prerequisites
   [Environment requirements from research.md - actual versions/packages found]

   ## Validation Steps
   ### Step 1: [First User Story Validation]
   [What to do]
   **Expected Result**: [What should happen]
   **Success Criteria**: [How to verify it worked]

   ### Step 2: [Second User Story Validation]
   [What to do - no implementation details, reference tasks that will create them]
   **Expected Result**: [What should happen]
   **Success Criteria**: [How to verify it worked]

   ## Troubleshooting
   [Common failure modes and how to debug them]

   ## Next Steps
   [References to contracts/, data-model.md, and tasks.md]
   ```

**Output**: data-model.md, /contracts/*, test-scenarios.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, test-scenarios)
- Each contract → contract test task [P]
- Each register → DML implementation task
- Each user story → integration test task
- Implementation tasks to make tests pass
- **Setup tasks**: `create_simics_project()`, `add_dml_device_skeleton()`, `checkout_and_build_dmlc()`
- **Validation tasks**: `check_with_dmlc()` (AI-enhanced diagnostics before build)
- **Build tasks**: `build_simics_project()`
- **Test tasks**: `run_simics_test()`
- **Note**: Discovery MCP tools (`get_simics_version`, `list_installed_packages`) already executed in /plan phase

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Register definitions → Device logic → Integration
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, verify test-scenarios.md, performance validation)

## Completion Validation (MANDATORY)

**CRITICAL**: Before reporting /plan command completion, the agent MUST verify ALL these conditions.

### Phase 0 Verification Checklist
Run these checks to verify Phase 0 is complete:

```bash
# Verify research.md exists
ls -la [SPECS_DIR]/research.md

# Verify no NEEDS CLARIFICATION remains
grep "NEEDS CLARIFICATION" [SPECS_DIR]/plan.md
```

**Checklist** (all must be [x]):
- [ ] research.md file exists and contains MCP tool outputs
- [ ] research.md has >= 50 lines (indicates complete research)
- [ ] Technical Context in plan.md has NO "NEEDS CLARIFICATION" text
- [ ] Progress Tracking shows "Phase 0: Research complete" checked
- [ ] All Discovery MCP Tool Status checkboxes marked [x]
- [ ] MCP tool outputs are documented in research.md with proper structure

### Phase 1 Verification Checklist

**Run these verification commands**:
```bash
# 1. Verify all Phase 1 files exist
ls -la [SPECS_DIR]/data-model.md
ls -la [SPECS_DIR]/test-scenarios.md
ls -la [SPECS_DIR]/contracts/
```

**Checklist** (all must be [x]):
- [ ] data-model.md file exists with register/entity definitions
- [ ] data-model.md has "Implementation Patterns" section
- [ ] contracts/ directory exists with >= 1 contract specification
- [ ] test-scenarios.md file exists (no MCP tool syntax)
- [ ] Progress Tracking shows "Phase 1: Design complete" checked
- [ ] Post-Design Constitution Check shows PASS

### Overall Completion Checklist

**Final verification**:
- [ ] Both Phase 0 and Phase 1 are complete
- [ ] All generated files follow their respective templates
- [ ] No ERROR states in execution flow
- [ ] All MANDATORY steps completed
- [ ] All verification commands executed successfully
- [ ] Ready for /tasks command

**IF ANY CHECKLIST ITEM FAILS**: Do NOT report completion. Fix the issue and re-verify.

## Final Report Format (MANDATORY)

After completing ALL verification checks, the agent MUST provide this exact report format:

```
✅ /plan command complete

**Branch**: [branch_name]
**Date**: [Current date in YYYY-MM-DD format]
**Feature**: [Feature name from spec.md]

**Files Created**:
- ✅ plan.md (updated with resolved Technical Context and Progress Tracking)
- ✅ research.md ([line count] lines - MCP tool outputs, architecture decisions)
- ✅ data-model.md ([register count] registers, [interface count] interfaces)
- ✅ test-scenarios.md ([scenario count] test scenarios - no MCP syntax)
- ✅ contracts/ ([file count] contract specifications)

**Phase Status**:
- ✅ Phase 0 (Research): Complete
- ✅ Phase 1 (Design): Complete
- ⏭️  Phase 2 (Task Planning): Approach described in plan.md
- 📋 Phase 2 Execution: Ready for /tasks command

**Progress Summary**:
- Constitutional checks: [PASS/ISSUES]
- MCP tools executed: [count] tools
- Architectural RAG queries: [0-2] queries
- NEEDS CLARIFICATION resolved: [count] items
- Files generated: [count] files
- Total phases completed: 2 of 2

**Generated Artifacts**:
```
[SPECS_DIR]/
├── plan.md              # ✅ Updated
├── research.md          # ✅ Created
├── data-model.md        # ✅ Created
├── test-scenarios.md    # ✅ Created
└── contracts/           # ✅ Created
    ├── register-access.md
    └── interface-behavior.md
```

**Next Steps**:
1. Review the generated artifacts in `[SPECS_DIR]/`
2. Verify all files contain expected content
3. Run `/tasks` to generate actionable task breakdown from design artifacts
4. The /tasks command will create tasks.md based on plan.md, data-model.md, and contracts/

**Ready For**: `/tasks` command execution
```

**CRITICAL**: Do NOT report completion until BOTH Phase 0 and Phase 1 are fully complete with all files created and verified.

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*AI Agent: Mark [x] as you complete each item (corresponds to Execution Flow in guidance)*

**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
  - [ ] Step 0.1: Research needs identified
  - [ ] Step 0.2: Discovery MCP tools executed (3 tools)
  - [ ] Step 0.3: MCP tool outputs parsed
  - [ ] Step 0.4: research.md created
  - [ ] Step 0.5: Technical Context updated (no NEEDS CLARIFICATION)
  - [ ] Step 0.6: Progress Tracking updated
  - [ ] Step 0.7: Validation checkpoint passed
  - [ ] Step 0.8: Phase completion announced
- [ ] Phase 1: Design complete (/plan command)
  - [ ] Step 1.1: data-model.md created
  - [ ] Step 1.2: contracts/ directory created
  - [ ] Step 1.3: Contract tests planned
  - [ ] Step 1.4: Test scenarios extracted from spec.md
  - [ ] Step 1.5: test-scenarios.md created
  - [ ] Step 1.6: Progress Tracking updated
  - [ ] Step 1.7: Constitution Check re-evaluated
  - [ ] Step 1.8: Validation checkpoint passed
  - [ ] Step 1.9: Phase completion announced
- [ ] Phase 2: Task planning approach described (/plan command - describe only, do NOT create tasks.md)
- [ ] Phase 3: Tasks generated (/tasks command - NOT part of /plan)
- [ ] Phase 4: Implementation complete (NOT part of /plan)
- [ ] Phase 5: Validation passed (NOT part of /plan)

**Gate Status**:
- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented (if any)

**Discovery MCP Tool Status** (Phase 0):
- [ ] `get_simics_version()` executed and documented (MANDATORY)
- [ ] `list_installed_packages()` executed and documented (MANDATORY)
- [ ] `list_simics_platforms()` executed and documented (MANDATORY)
- [ ] MCP tool outputs incorporated into research.md
- [ ] Architectural RAG queries executed (0-2 queries)
- [ ] Environmental constraints documented

**Design Artifact Status** (Phase 1):
- [ ] data-model.md created with registers/interfaces/state
- [ ] data-model.md has "Implementation Patterns" section
- [ ] Pattern RAG queries executed (0-2 queries)
- [ ] contracts/ directory created with >= 1 file
- [ ] test-scenarios.md created

**Critical Verification** (Before reporting completion):
- [ ] **Implementation MCP tools NOT executed** (create_simics_project, add_dml_device_skeleton, build_simics_project reserved for Phase 3)
- [ ] All verification commands executed successfully
- [ ] All checklist items marked [x]
- [ ] Final report generated with accurate counts

**COMPLETION CRITERIA**: All Phase 0 and Phase 1 items marked [x] = Plan ready for /tasks command

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
