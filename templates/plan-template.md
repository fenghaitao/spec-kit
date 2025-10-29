---
description: "Implementation plan template for feature development"
scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
   → Extract: Functional Requirements, Key Entities, Hardware Specification (if Simics project)
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api, simics=hardware device)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, `ADK.md` for adk, or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context
**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75, DML 1.4 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM, Simics API or NEEDS CLARIFICATION]
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
**Testing**: [e.g., pytest, XCTest, cargo test, Simics test scripts or NEEDS CLARIFICATION]
**Target Platform**: [e.g., Linux server, iOS 15+, WASM, Simics 6.x or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile/simics - determines source structure]
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps, functional accuracy or NEEDS CLARIFICATION]
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable, software-visible behavior or NEEDS CLARIFICATION]
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens, register count/complexity or NEEDS CLARIFICATION]

**Simics-Specific Context** (if Project Type = simics):
**Simics Version**: [e.g., Simics Base 7.57.0 or use MCP `get_simics_version()` or NEEDS CLARIFICATION]
**Required Packages**: [e.g., simics-base, simics-qsp-x86 or use MCP `list_installed_packages()` or NEEDS CLARIFICATION]
**Available Platforms**: [use MCP `list_simics_platforms()` to discover available simulation targets or NEEDS CLARIFICATION]
**MCP Server**: [simics-mcp-server integration available with 22+ tools for project automation, device modeling and documentation access]
**Device Type**: [e.g., PCI device, memory controller, peripheral or NEEDS CLARIFICATION]
**Hardware Interfaces**: [e.g., memory-mapped registers, DMA, interrupts or NEEDS CLARIFICATION]

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
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

**Select ONE structure based on Project Type. Delete unused options and customize with real paths.**

```
# Single project (DEFAULT)
src/[models|services|cli|lib]/
tests/[contract|integration|unit]/

# Web application (frontend + backend)
backend/src/[models|services|api]/
frontend/src/[components|pages|services]/

# Mobile + API (iOS/Android)
api/src/[models|services|api]/
[ios|android]/[feature modules]/

# Simics device (created by MCP tools in Phase 3)
simics-project/modules/[device-name]/
  ├── [device-name].dml
  ├── registers.dml (optional)
  ├── interfaces.dml (optional)
  └── test/
      ├── s-[device-name].py
      └── test_[name]_common.py
```

**Structure Decision**: [Selected structure, real directories, and rationale]

**Simics Note**: MCP tools auto-generate structure at repo root during Phase 3 Setup. Specs/ contains only documentation.

## Phase 0: Outline & Research

### Step 0.1: Identify Research Needs
Extract unknowns from Technical Context above:
- For each NEEDS CLARIFICATION → research task
- For each dependency → best practices task
- For each integration → patterns task

### Step 0.2: Execute Discovery MCP Tools (Simics Projects)

**MANDATORY for Simics projects - Execute these tools immediately**:

1. **Environment Discovery** (MANDATORY):
   - Execute `get_simics_version()` → resolve Simics Version NEEDS CLARIFICATION
   - Execute `list_installed_packages()` → resolve Required Packages NEEDS CLARIFICATION
   - Execute `list_simics_platforms()` → resolve Available Platforms NEEDS CLARIFICATION

2. **Requirement-Driven RAG Documentation Search** (MANDATORY - query based on spec.md):
   
   **Process**:
   1. **Read spec.md thoroughly**: Load and analyze `specs/[###-feature-name]/spec.md`
   2. **Extract key concepts**: Identify technical concepts, features, patterns, and technologies mentioned
   3. **For EACH functional requirement**, generate targeted RAG queries to gather implementation knowledge
   
   **Query Generation Guidelines** (Simics/Hardware Projects):
   
   **A. Device Type & Architecture Queries** - For device modeling patterns:
   - Example: If spec mentions "PCI device", query: `"PCI device modeling DML configuration space BAR registers"`
   - Example: If spec mentions "UART controller", query: `"UART serial device DML transmit receive registers"`
   - Example: If spec mentions "timer device", query: `"timer counter device DML interrupt generation periodic events"`
   - Source type: `"source"` for device examples, `"dml"` for DML code patterns
   
   **B. Register Implementation Queries** - For register-specific features:
   - Example: If spec requires "control registers", query: `"DML control register implementation read write callbacks"`
   - Example: If spec requires "status registers", query: `"DML status register read-only fields state reflection"`
   - Example: If spec requires "interrupt registers", query: `"DML interrupt status enable mask registers"`
   - Source type: `"dml"` for register patterns, `"docs"` for register modeling guidance
   
   **C. Hardware Interface Queries** - For device interfaces and protocols:
   - Example: If spec mentions "memory-mapped I/O", query: `"DML io_memory interface bank register mapping"`
   - Example: If spec requires "DMA", query: `"DML DMA implementation memory transactions buffer management"`
   - Example: If spec requires "interrupts", query: `"DML interrupt signal port interface assertion deassertion"`
   - Source type: `"dml"` for interface code, `"docs"` for Simics interface documentation
   
   **D. Device Behavior Queries** - For operational behavior and state machines:
   - Example: If spec describes "state machine", query: `"DML device state machine implementation transitions"`
   - Example: If spec requires "event handling", query: `"DML event posting callback scheduling timing"`
   - Example: If spec requires "checkpointing", query: `"DML checkpointing saved variables state persistence"`
   - Source type: `"dml"` for behavior patterns, `"source"` for complex examples
   
   **E. Testing Strategy Queries** - For device testing:
   - Example: For register tests, query: `"Simics Python device testing register read write verification"`
   - Example: For functional tests, query: `"Simics Python test patterns device workflow integration"`
   - Example: For error cases, query: `"Simics device testing error conditions invalid access"`
   - Source type: `"python"` for test code, `"source"` for test frameworks
   
   **Query Construction Best Practices**:
   - ✅ Include multiple related terms: `"DML register bank io_memory interface callbacks"`
   - ✅ Specify DML version/platform: `"DML 1.4 Simics device checkpointing state"`
   - ✅ Add device context from spec: `"timer device counter register overflow interrupt"`
   - ✅ Use 5-10 words per query for precision
   - ❌ Avoid vague queries: `"how to implement device"`
   - ❌ Don't duplicate: Check if knowledge is already covered
   
   **Execution**:
   ```python
   # For each requirement in spec.md, execute 1-3 targeted queries
   perform_rag_query(
       query="[specific technical terms from requirement]",
       source_type="[docs|source|dml|python|all]",
       match_count=5  # Use 10 for complex/critical requirements
   )
   ```
   
   **Documentation**: In research.md, for each query document:
   - Which requirement(s) it addresses
   - Why this specific query was needed
   - What knowledge gap it fills
   - Key findings and code examples extracted

**CRITICAL**: DO NOT execute implementation tools (`create_simics_project()`, `add_dml_device_skeleton()`, `build_simics_project()`) - those belong in Phase 3 (Implementation).

### Step 0.3: Parse MCP Tool and RAG Query Outputs

Extract key information from MCP tool JSON and RAG query responses:
- **get_simics_version()** → Extract Simics version for Technical Context
- **list_installed_packages()** → Extract package list for Technical Context
- **list_simics_platforms()** → Extract platform list for Technical Context
- **RAG queries** → Extract patterns, best practices, code examples, and implementation guidance
  * **CRITICAL**: Extract and include actual code examples from RAG results:
    - Parse the JSON response `results[].content` field to locate code snippets
    - Look for relevant code patterns based on your query (e.g., class definitions, function signatures, configuration examples)
    - Extract complete, self-contained code examples (not just descriptions). Focus on minimal but functional snippets that demonstrate the pattern - avoid truncating mid-function or removing essential context.
    - Format as markdown code blocks with appropriate language fencing (```python, ```javascript, ```dml, etc.)
    - Example: If RAG returns code with class definitions and methods, extract and format the actual code
    - DO NOT write descriptions like "Example implementation pattern" - show the actual code

### Step 0.4: Create research.md File

**MANDATORY**: Create `[SPECS_DIR]/research.md` with this exact structure:

```markdown
# Research: [FEATURE_NAME]

## DML Learning Prerequisites (Simics Projects Only)

**⚠️ CRITICAL FOR SIMICS PROJECTS**: Two comprehensive DML learning documents must be studied in the tasks phase before writing any DML code:

1. `.specify/memory/DML_Device_Development_Best_Practices.md` - Patterns and pitfalls
2. `.specify/memory/DML_grammar.md` - Complete DML 1.4 language specification

**During /plan Phase**:
- ✅ Execute RAG queries for device patterns and examples
- ✅ Document RAG results in research.md
- ❌ DO NOT read the DML learning documents yet (they will be studied in tasks phase)

**In Tasks Phase**: Mandatory tasks T013-T014 will require complete study of these documents with comprehensive note-taking in research.md before any implementation

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

## Requirement-Driven RAG Research

[Document RAG queries executed to address functional requirements from spec.md]

### Query #1: [Query Focus - tied to specific requirement]
[Document findings from RAG query addressing a knowledge gap]
- **Query**: "[exact query string used]"
- **Source Type**: [dml/python/source/docs/all]
- **Match Count**: [number]
- **Requirement Addressed**: [Reference specific functional requirement from spec.md that necessitated this query]
- **Knowledge Gap**: [What technical knowledge was needed to implement this requirement]
- **Key Findings**:
  * [Finding 1: Specific pattern, feature, or approach discovered]
  * [Finding 2: Implementation detail or best practice]
  * [Finding 3: Integration or interface pattern]
  * [Additional findings as relevant]
- **Code Examples**:
  ```[language]
  [code example 1 - 10-20 lines of actual code extracted from RAG results]
  ```
  ```[language]
  [code example 2 - showing specific pattern or feature]
  ```
- **Application**: [How these findings will be applied to [FEATURE_NAME] implementation]

### Query #2: [Query Focus - tied to specific requirement]
[Repeat structure above for each query]
- **Query**: "[exact query string]"
- **Source Type**: [type]
- **Match Count**: [number]
- **Requirement Addressed**: [Reference specific functional requirement]
- **Knowledge Gap**: [What knowledge was needed]
- **Key Findings**: [...]
- **Code Examples**: [...]
- **Application**: [...]

[Continue with Query #3, #4, etc. as needed based on functional requirements]

## Architecture Decisions

[For each NEEDS CLARIFICATION in Technical Context, create an entry:]

### Decision: [What was decided - e.g., "Use [technology/pattern]"]
- **Rationale**: [Why this choice - based on MCP tool and RAG findings]
- **Alternatives Considered**: [What else was evaluated]
- **Source**: [Which MCP tool or RAG query informed this decision]
- **Impact**: [How this affects implementation]

## RAG Search Results Summary

[Quick reference table for all RAG queries executed]

| # | Query Focus | Source Type | Match Count | Status | Requirement Addressed |
|---|-------------|-------------|-------------|--------|-----------------------|
| 1 | [Query focus summary] | [type] | [N] | ✅ | [Requirement reference] |
| 2 | [Query focus summary] | [type] | [N] | ✅ | [Requirement reference] |
| 3+ | [Additional queries] | [type] | [N] | ✅ | [Requirement reference] |

**Note**: Each query should address a specific functional requirement or knowledge gap identified from spec.md. Document the requirement-to-query mapping clearly.

## Implementation Strategy

[Document overall approach based on research findings]

### Architecture Overview
[High-level architecture based on examples and patterns discovered]

### Key Design Patterns
[Patterns to apply based on RAG research]

### Testing Approach
[Testing strategy based on discovered test patterns]

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

**Simics Discovery MCP Tool Status** (if Project Type = simics):
- [x] `get_simics_version()` executed and documented (MANDATORY)
- [x] `list_installed_packages()` executed and documented (MANDATORY)
- [x] `list_simics_platforms()` executed and documented (MANDATORY)
- [x] MCP tool outputs incorporated into research.md

**RAG Documentation Search Status** (if Project Type = simics):
- [x] `perform_rag_query()` used for requirement-driven research
- [x] RAG search results documented in research.md

**RAG Quality Verification**:
- [x] RAG queries executed based on spec.md functional requirements
- [x] Code examples extracted and included in relevant sections
- [x] Key findings documented with excerpts and references
- [x] Application guidance provided for implementation
- [x] RAG Search Results Summary table completed with status checkmarks
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
- RAG searches performed: [count]
- NEEDS CLARIFICATION resolved: [count]
- research.md created: ✅
- Technical Context updated: ✅
```

**Output**: research.md with all NEEDS CLARIFICATION resolved, MCP tool outputs, and RAG documentation search results documented

## Phase 1: Design & Contracts
*Prerequisites: research.md complete, Phase 0 validated*

### Step 1.1: Create data-model.md

**MANDATORY**: Create `[SPECS_DIR]/data-model.md` documenting the data structures:

**For Software Projects**:
- Entity name, fields, relationships
- Validation rules from requirements
- State transitions if applicable

**For Simics Projects**:
- Extract registers from spec.md Register Map (names, purposes, operations) and External Interfaces
- Add implementation details: offsets, sizes, access types, bit fields, reset values, side effects
- Reference research.md for DML patterns

Use this structure:
```markdown
# Data Model: [FEATURE_NAME]

## Registers (Simics Projects)

*For each register in spec.md Register Map, extract Purpose and Operations; add offsets, side effects, fields:*

### Register: [NAME from spec.md]
- **Offset**: [hex - assign by order/size] | **Size**: [bits from requirements/research.md] | **Access**: [RO/WO/RW from spec.md]
- **Reset**: [hex or 0x0000] | **Purpose**: [from spec.md "Purpose"]
- **Side Effects** (from spec.md "Operational Behavior"):
  * Read: [behavior] | Write: [behavior] | State: [changes] | Affects: [other registers]
- **Fields**: [bit fields from spec.md Required Capabilities]

*Example: spec.md "CONTROL | Device enable | Writing DEVICE_ENABLE=1 triggers init" → Register CONTROL offset 0x00, Side Effects Write: "Triggers initialization, resets COUNTER to 0"*

## Device State (Simics Projects)

### State Variable: [NAME]
- **Type**: [type]
- **Purpose**: [description]
- **Persistence**: [checkpointed/transient]

## Interfaces (Simics Projects)

### Interface: [INTERFACE_NAME]
- **Type**: [Simics interface type]
- **Methods**: [list methods]
- **Purpose**: [description]
```

### Step 1.2: Create contracts/ directory

**MANDATORY**: Create `[SPECS_DIR]/contracts/` directory with contract specifications:

**For Software Projects**:
- API contracts (REST/GraphQL endpoints)
- Request/response schemas
- Error codes and messages

**For Simics Projects**:
- Register access contracts (read/write behavior)
- Interface behavior specifications
- Memory transaction patterns

Create files like:
- `contracts/register-access.md` - Register read/write specifications
- `contracts/interface-behavior.md` - Interface method contracts

### Step 1.3: Generate contract tests (planning only)

**Note**: Don't create test files yet - just plan them in contracts/

**For Simics Projects**: Document expected register read/write behavior tests:
- Reference device test patterns from research.md Device Example Analysis section
- Use test patterns discovered via `perform_rag_query()` for [DEVICE_NAME] and similar devices
- Extract test structure patterns from RAG search results (simple and complex device references)

### Step 1.4: Extract test scenarios from "User Scenarios & Testing" in spec.md

**MANDATORY**: Extract test scenarios from `[SPECS_DIR]/spec.md` "User Scenarios & Testing" section:

**Extract from spec.md**:
- **Primary User Story** → main integration test scenario
- **Acceptance Scenarios** (Given/When/Then) → individual test cases
- **Edge Cases** → edge case and error handling test scenarios

**Identify integration test scenarios**:
- Each Acceptance Scenario → integration test case
- Each Edge Case → boundary/error test case
- Quickstart validation steps based on Primary User Story

**For Simics Projects**: 
- Device operational workflow tests from Primary User Story
- Register behavior tests from Acceptance Scenarios
- Error condition tests from Edge Cases

### Step 1.5: Create quickstart.md from "User Scenarios & Testing" in spec.md

**MANDATORY**: Create `[SPECS_DIR]/quickstart.md` with user validation guide based on spec.md:

**Extract from spec.md "User Scenarios & Testing"**:
- **Primary User Story** → Goal section (what users accomplish)
- **Acceptance Scenarios** → Validation Steps (Given/When/Then → What to do/Expected Result/Success Criteria)
- **Edge Cases** → Troubleshooting section (boundary conditions and error scenarios)

**CRITICAL RULES for quickstart.md**:
- ❌ DO NOT use MCP tool syntax (no `create_simics_project()` calls)
- ❌ DO NOT assume implementation details (no specific register names until implemented)
- ✅ DO use generic descriptions ("Create Simics project", "Build device module")
- ✅ DO focus on Simics CLI commands users will actually run
- ✅ DO use placeholders: `[DEVICE_NAME]`, `[REGISTER_NAME]` for unknowns
- ✅ DO include validation criteria: "What constitutes success for each step?"
- ✅ DO map Acceptance Scenarios to validation steps directly

Use this structure:
```markdown
# Quick Start: [FEATURE_NAME]

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

### Step 1.6: Update agent context file

**MANDATORY**: Run `{SCRIPT}`

**IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.

This updates the agent-specific file (e.g., `ADK.md` for ADK agent) with:
- New technologies from current plan
- Preserved manual additions between markers
- Updated recent changes (keep last 3)
- Kept under 150 lines for token efficiency

### Step 1.7: Update Progress Tracking in plan.md

**MANDATORY**: Update the Progress Tracking section in plan.md. Mark these checkboxes:

```markdown
**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)

**Gate Status**:
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
```

### Step 1.8: Re-evaluate Constitution Check

After completing design artifacts, re-check constitutional compliance:
- Review data-model.md against constitution principles
- Verify design doesn't introduce violations
- If new violations: Document in Complexity Tracking section
- If violations cannot be justified: Refactor design and return to Step 1.1

### Step 1.9: Validation Checkpoint

**MANDATORY**: Before proceeding, verify all Phase 1 deliverables exist:

```bash
ls -la [SPECS_DIR]/data-model.md
ls -la [SPECS_DIR]/quickstart.md
ls -la [SPECS_DIR]/contracts/
ls -la ADK.md  # or agent-specific file
```

Checklist:
- [ ] data-model.md file exists and contains register/entity definitions
- [ ] contracts/ directory exists with contract specifications
- [ ] quickstart.md file exists with user validation steps
- [ ] Agent context file updated (ADK.md or equivalent)
- [ ] Progress Tracking shows Phase 1 marked complete
- [ ] Constitution check passed (no new violations)

### Step 1.10: Announce Phase Completion

Explicitly state in your response:
```
✅ Phase 1 (Design) complete. Ready for /tasks command.

**Phase 1 Summary**:
- data-model.md created: ✅
- contracts/ created: ✅
- quickstart.md created: ✅
- Agent context updated: ✅
- Constitutional compliance: ✅
```

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific context file (e.g., ADK.md)

   **Quickstart.md Structure**:
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

6. **Update agent file incrementally** (O(1) operation):
   - Run `{SCRIPT}`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass
- **Simics projects**: Include implementation MCP tool tasks:
  - **Setup tasks**: `create_simics_project()`, `add_dml_device_skeleton()`, `checkout_and_build_dmlc()`
  - **Validation tasks**: `check_with_dmlc()` (before build)
  - **Build tasks**: `build_simics_project()`
  - **Test tasks**: `run_simics_test()`
  - **Note**: Discovery MCP tools (`get_simics_version`, `list_installed_packages`) already executed in /plan phase

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Completion Validation (MANDATORY)

Before reporting /plan command completion, the agent MUST verify ALL these conditions:

### Phase 0 Verification Checklist
Run these checks to verify Phase 0 is complete:

```bash
# Verify research.md exists
ls -la [SPECS_DIR]/research.md

# Verify no NEEDS CLARIFICATION remains
grep "NEEDS CLARIFICATION" [SPECS_DIR]/plan.md
```

- [ ] research.md file exists and contains MCP tool outputs
- [ ] Technical Context in plan.md has NO "NEEDS CLARIFICATION" text
- [ ] Progress Tracking shows "Phase 0: Research complete" checked
- [ ] All Simics Discovery MCP Tool Status checkboxes marked (if Simics project)
- [ ] MCP tool outputs are documented in research.md with proper structure

### Phase 1 Verification Checklist
Run these checks to verify Phase 1 is complete:

```bash
# Verify all Phase 1 files exist
ls -la [SPECS_DIR]/data-model.md
ls -la [SPECS_DIR]/quickstart.md
ls -la [SPECS_DIR]/contracts/
ls -la ADK.md  # or agent-specific file
```

- [ ] data-model.md file exists with register/entity definitions
- [ ] contracts/ directory exists with contract specifications
- [ ] quickstart.md file exists with user validation steps (NO MCP tool syntax)
- [ ] Agent context file updated (ADK.md, CLAUDE.md, or equivalent)
- [ ] Progress Tracking shows "Phase 1: Design complete" checked
- [ ] Post-Design Constitution Check shows PASS

### Overall Completion Checklist

- [ ] Both Phase 0 and Phase 1 are complete
- [ ] All generated files follow their respective templates
- [ ] No ERROR states in execution flow
- [ ] All MANDATORY steps completed
- [ ] Ready for /tasks command

## Final Report Format (MANDATORY)

After completing ALL verification checks, the agent MUST provide this exact report format:

```
✅ /plan command complete

**Branch**: [branch_name from setup script]

**Files Created**:
- ✅ plan.md (updated with resolved Technical Context and Progress Tracking)
- ✅ research.md (MCP tool outputs, device examples, architecture decisions)
- ✅ data-model.md (register definitions, device state, interfaces)
- ✅ quickstart.md (user validation guide - no MCP syntax)
- ✅ contracts/ (register access contracts, interface specifications)
- ✅ [agent-file].md (updated agent context - e.g., ADK.md, CLAUDE.md)

**Phase Status**:
- ✅ Phase 0 (Research): Complete
- ✅ Phase 1 (Design): Complete
- ⏭️  Phase 2 (Task Planning): Approach described in plan.md
- 📋 Phase 2 Execution: Ready for /tasks command

**Progress Summary**:
- Constitutional checks: [PASS/ISSUES]
- MCP tools executed: [count] tools
- RAG searches performed: [count] searches
- NEEDS CLARIFICATION resolved: [count] items
- Files generated: [count] files
- Total phases completed: 2 of 2

**Generated Artifacts**:
```
[SPECS_DIR]/
├── plan.md              # ✅ Updated
├── research.md          # ✅ Created
├── data-model.md        # ✅ Created
├── quickstart.md        # ✅ Created
└── contracts/           # ✅ Created
    ├── register-access.md
    └── interface-behavior.md
```

**Next Steps**:
1. Review the generated artifacts in `[SPECS_DIR]/`
2. Run `/tasks` to generate actionable task breakdown from design artifacts
3. The /tasks command will create tasks.md based on plan.md, data-model.md, and contracts/

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
*This checklist is updated during execution flow*

**Phase Status**:
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

**Simics Discovery MCP Tool Status** (if Project Type = simics):
- [ ] `get_simics_version()` executed and documented (MANDATORY)
- [ ] `list_installed_packages()` executed and documented (MANDATORY)
- [ ] `list_simics_platforms()` executed and documented (MANDATORY)
- [ ] MCP tool outputs incorporated into research.md
- [ ] Environmental constraints documented for /implement phase
- [ ] **Implementation MCP tools NOT executed** (reserved for /implement phase)

**RAG Documentation Search Status** (if Project Type = simics):
- [ ] `perform_rag_query()` used for requirement-driven research
- [ ] RAG search results documented in research.md
- [ ] Code examples and patterns extracted from RAG results
- [ ] Best practices identified and incorporated into design decisions

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
