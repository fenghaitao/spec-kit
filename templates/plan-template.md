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
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->
```
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

# [REMOVE IF UNUSED] Option 4: Simics device project (when "simics" detected)
# Use MCP tools for automated project creation AT REPO ROOT:
# 1. `create_simics_project(project_path="./simics-project")` → generates base structure at repo root
# 2. `add_dml_device_skeleton(project_path="./simics-project", device_name=DEVICE_NAME)` → adds device modeling files
# The structure shown below will be created automatically during Phase 3.1 Setup AT REPOSITORY ROOT.

## Repository Structure
repo-root/
├── simics-project/              # ← Source code (implementation)
│   └── modules/device-name/
│       ├── device-name.dml      # Main device implementation
│       ├── registers.dml        # Register definitions and mappings (optional)
│       ├── interfaces.dml       # Device interface implementations (optional)
│       ├── sub-feature.dml      # Device sub-feature modules (optional)
│       ├── module_load.py       # Simics module load action definitions
│       ├── CMakeLists.txt       # CMake file
│       └── test/
│           ├── CMakeLists.txt   # CMake file
│           ├── SUITEINFO        # Test timeout and tags
│           ├── s-device-name.py # tests implementation
│           ├── test_name_common.py # test configuration and device instance creation
│           └── README
│
└── specs/                       # ← Documentation artifacts only
    └── [###-feature-name]/
        ├── plan.md              # This file (/plan command output)
        ├── research.md          # Phase 0 output (/plan command)
        ├── data-model.md        # Phase 1 output (/plan command)
        ├── quickstart.md        # Phase 1 output (/plan command)
        ├── contracts/           # Phase 1 output (/plan command)
        └── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

**For Simics projects**: The structure above shows the template that will be generated AT REPOSITORY ROOT (not in specs/ folder). The actual project structure will be created by the simics-mcp-server's MCP tools during task execution (Phase 3.1 Setup):
- `create_simics_project(project_path="./simics-project")` creates the base project structure at repo root
- `add_dml_device_skeleton(project_path="./simics-project", device_name=DEVICE_NAME)` adds device-specific modeling files

**IMPORTANT**: Simics projects must be created at repository root to separate source code from documentation. The specs/ folder contains only documentation artifacts (plan.md, tasks.md, etc.), while the simics-project/ folder at repo root contains the actual implementation.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

   **Simics-specific research tasks**:
   ```
   If Project Type = simics:
     Task: "MANDATORY: Execute `get_simics_version()` MCP tool to resolve environment NEEDS CLARIFICATION"
     Task: "MANDATORY: Execute `list_installed_packages()` MCP tool to resolve package dependencies NEEDS CLARIFICATION"
     Task: "MANDATORY: Execute `list_simics_platforms()` MCP tool to identify available simulation targets"
     Task: "MANDATORY: Execute `get_simics_dml_1_4_reference_manual()` MCP tool to access DML language reference for architectural decisions"
     Task: "MANDATORY: Execute `get_simics_model_builder_user_guide()` MCP tool to understand device modeling patterns and best practices"
     Task: "MANDATORY: Execute `get_simics_dml_template()` MCP tool to study base device structure patterns before design"
     Task: "MANDATORY: Execute `get_simics_device_example_i2c()` MCP tool for reference implementation patterns (includes test samples via python_test_samples_path)"
     Task: "MANDATORY: Execute `get_simics_device_example_ds12887()` MCP tool for advanced device patterns (includes test samples via python_test_samples_path)"
     Task: "Analyze MCP tool outputs: Study DML template structure, device examples, and test patterns"
     Task: "Document architectural decisions: Register organization, interface choices, abstraction strategy based on examples"
     Task: "Extract test patterns: Review python_test_samples_path from device examples for TDD approach in Phase 1"
     Task: "Validate hardware specification completeness: Ensure spec.md has sufficient detail for data-model.md generation"
     Task: "Research Simics API specifics: Memory operations and interface implementations needed for this device type"
     Task: "Validate constitutional compliance: Device-first development approach alignment"
   ```

3. **Execute ALL discovery and documentation MCP tools immediately** (for Simics projects):
   - **Environment tools (MANDATORY)**:
     - `get_simics_version()` - Resolve Simics version NEEDS CLARIFICATION
     - `list_installed_packages()` - Resolve package dependencies NEEDS CLARIFICATION
     - `list_simics_platforms()` - Identify available simulation targets

   - **Documentation tools (MANDATORY for Phase 1 design)**:
     - `get_simics_dml_1_4_reference_manual()` - DML language reference for architectural decisions
     - `get_simics_model_builder_user_guide()` - Device modeling patterns and best practices
     - `get_simics_dml_template()` - Base device structure patterns
     - `get_simics_device_example_i2c()` - Reference implementation with test samples
     - `get_simics_device_example_ds12887()` - Advanced patterns with test samples

   - **DO NOT execute implementation tools**: `create_simics_project()`, `add_dml_device_skeleton()`, `build_simics_project()`, `run_simics_test()` belong in /implement phase (Phase 3)

   - **Include outputs in research.md**: Document all MCP tool findings to inform Phase 1 design decisions

   - **Extract test patterns**: Access python_test_samples_path from device examples for contract test generation in Phase 1

   - **Purpose**: Gather ALL information needed for data-model.md, contracts/, and test generation before implementation begins

4. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]
   - **Simics projects**: Include device architecture decisions, all MCP tool outputs, test pattern analysis, and abstraction strategy

   **research.md Structure for Simics Projects**:
   ```markdown
   # Research: [DEVICE_NAME]

   ## Environment Discovery
   - **Simics Version**: [output from get_simics_version()]
   - **Installed Packages**: [output from list_installed_packages()]
   - **Available Platforms**: [output from list_simics_platforms()]

   ## Documentation Analysis
   - **DML 1.4 Reference**: [key findings from get_simics_dml_1_4_reference_manual()]
   - **Model Builder Guide**: [patterns from get_simics_model_builder_user_guide()]
   - **DML Template Structure**: [analysis of get_simics_dml_template() output]

   ## Device Example Analysis
   - **I2C Device Example**: [architectural insights from get_simics_device_example_i2c()]
   - **DS12887 Device Example**: [advanced patterns from get_simics_device_example_ds12887()]
   - **Test Patterns Extracted**: [summary of python_test_samples_path contents for TDD]

   ## Architectural Decisions
   - **Register Organization**: [how registers will be structured in DML based on examples]
   - **Interface Strategy**: [which Simics interfaces needed and why]
   - **Device Abstraction**: [abstraction approach based on Model Builder guide]
   - **Test Strategy**: [TDD approach based on extracted test patterns]

   ## Validation
   - **Spec Completeness**: [verification that spec.md Hardware Specification is sufficient]
   - **Constitutional Compliance**: [alignment with device-first development]
   ```

**Output**: research.md with all NEEDS CLARIFICATION resolved, all MCP tool outputs documented, and architectural foundation for Phase 1 design

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable
   - **Simics projects**: Transform Hardware Specification from spec.md into structured register definitions, interfaces, and device state using this format:

   **data-model.md Format for Simics Projects**:
   ```markdown
   # Data Model: [DEVICE_NAME]

   ## Device State
   - **Device Type**: [from spec.md Device Overview]
   - **Base Address**: [from spec.md, or determined in research.md]
   - **Address Space**: [size from spec.md]

   ## Register Definitions

   ### [REGISTER_NAME] (Offset: 0xXX)
   - **Size**: [8/16/32/64-bit]
   - **Access Mode**: [R/W, R/O, W/O]
   - **Reset Value**: [hex value from spec.md]
   - **Purpose**: [copied from spec.md Register Map]

   **Bit Fields**:
   | Bits | Field Name | Access | Reset | Description |
   |------|------------|--------|-------|-------------|
   | [31:8] | RESERVED | - | 0x0 | Reserved, read as 0 |
   | 7 | FIELD_NAME | R/W | 0 | [Purpose from spec.md bit field details] |
   | ... | ... | ... | ... | ... |

   **Behavior**:
   - Read: [What happens on read, from spec.md Operational Behavior]
   - Write: [What happens on write, side effects]
   - State Changes: [What device state is modified]

   ### [Continue for each register...]

   ## Interfaces

   ### [INTERFACE_NAME] (e.g., io_memory, signal, etc.)
   - **Type**: [Simics interface type from research.md]
   - **Methods**: [interface methods needed]
   - **Connected To**: [what this interface connects to]
   - **Purpose**: [from spec.md External Interfaces]

   ## Device Attributes
   - **[attribute_name]**: [Type] - [Purpose, from spec.md Software Visibility]
   - [List all device configuration attributes]

   ## State Transitions
   - **Initialization**: [From spec.md Operational Behavior - Initialization]
   - **Normal Operation**: [From spec.md Operational Behavior - Normal Operation]
   - **Error States**: [From spec.md Operational Behavior - Error Handling]
   - **Reset Behavior**: [How device resets to initial state]

   ## Validation Rules
   - [Register access ordering constraints from spec.md Software Visibility]
   - [Reserved bit handling rules from spec.md]
   - [Interrupt generation conditions from spec.md Operational Behavior]
   ```

   **Mapping from spec.md to data-model.md**:
   - spec.md Register Map table → data-model.md Register Definitions (one section per register)
   - spec.md Bit field details → data-model.md Bit Fields tables
   - spec.md Operational Behavior → data-model.md Behavior and State Transitions
   - spec.md External Interfaces → data-model.md Interfaces
   - spec.md Software Visibility → data-model.md Device Attributes and Validation Rules

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`
   - **Simics projects**: Register access contracts and interface specifications using device examples from `get_simics_device_example_i2c()`, `get_simics_device_example_ds12887()`, and `get_simics_dml_template()` MCP tools

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)
   - **Simics projects**: Register read/write behavior tests using `run_simics_test` MCP tool for validation; sample test patterns available from `get_simics_dml_template()` MCP tool and `get_simics_device_example_i2c()`, `get_simics_device_example_ds12887()` MCP tools via python_test_samples_path

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps
   - **Simics projects**: Device operational workflow tests

5. **Generate quickstart.md** from user story validation:
   - **DO NOT assume implementation details**: No specific register names or commands until implemented
   - **Focus on user validation**: How will users verify the feature works?
   - **Reference tasks.md**: Steps should align with implementation tasks
   - **Use placeholders**: `[DEVICE_NAME]`, `[REGISTER_NAME]` for unknowns
   - **Include validation criteria**: What constitutes success for each step?
   - **Simics projects**: Focus on device behavior validation, not implementation commands
   
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
  - **Setup tasks**: `create_simics_project()`, `add_dml_device_skeleton()`
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

**Simics MCP Tool Status** (if Project Type = simics):

*Phase 0 - Discovery & Documentation Tools (MANDATORY - must execute during /plan):*
- [ ] `get_simics_version()` executed and documented
- [ ] `list_installed_packages()` executed and documented
- [ ] `list_simics_platforms()` executed and documented
- [ ] `get_simics_dml_1_4_reference_manual()` executed for DML language reference
- [ ] `get_simics_model_builder_user_guide()` executed for modeling patterns
- [ ] `get_simics_dml_template()` executed for base device structure
- [ ] `get_simics_device_example_i2c()` executed for reference patterns
- [ ] `get_simics_device_example_ds12887()` executed for advanced patterns
- [ ] Test patterns extracted from python_test_samples_path
- [ ] All MCP tool outputs incorporated into research.md
- [ ] Architectural decisions documented based on MCP findings

*Phase 3 - Implementation Tools (reserved for /implement phase):*
- [ ] `create_simics_project()` - NOT executed in /plan (belongs in Phase 3.1)
- [ ] `add_dml_device_skeleton()` - NOT executed in /plan (belongs in Phase 3.1)
- [ ] `build_simics_project()` - NOT executed in /plan (belongs in Phase 3.3+)
- [ ] `run_simics_test()` - NOT executed in /plan (belongs in Phase 3.2+)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
