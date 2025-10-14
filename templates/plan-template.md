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

2. **Documentation Access** (if needed for architectural decisions):
   - Execute `get_simics_dml_1_4_reference_manual()` → get DML 1.4 language reference
   - Execute `get_simics_model_builder_user_guide()` → get device modeling patterns
   - Execute `get_simics_dml_template()` → get base device structure patterns

3. **Device Example Analysis** (if needed for implementation decisions):
   - Execute `get_simics_device_example_i2c()` → get simple I2C device patterns
   - Execute `get_simics_device_example_ds12887()` → get complex RTC device patterns

4. **RAG Documentation Search** (optional but recommended):
   - Use `perform_rag_query(query, source_type, match_count)` to search Simics documentation
   - `source_type="dml"` for DML device modeling examples
   - `source_type="python"` for Python test case patterns
   - `source_type="source"` for combined DML and test examples
   - `source_type="docs"` for general Simics documentation
   - `source_type="all"` for comprehensive search

**CRITICAL**: DO NOT execute implementation tools (`create_simics_project()`, `add_dml_device_skeleton()`, `build_simics_project()`) - those belong in Phase 3 (Implementation).

### Step 0.3: Parse MCP Tool Outputs

Extract key information from MCP tool JSON responses:
- **get_simics_version()** → Extract Simics version for Technical Context
- **list_installed_packages()** → Extract package list for Technical Context
- **list_simics_platforms()** → Extract platform list for Technical Context
- **Documentation tools** → Extract file paths for research.md references
- **Device examples** → Extract pattern insights for architecture decisions
- **RAG searches** → Extract code examples and best practices

### Step 0.4: Create research.md File

**MANDATORY**: Create `[SPECS_DIR]/research.md` with this exact structure:

```markdown
# Research: [FEATURE_NAME]

## Environment Discovery

### Simics Version
[Document output from get_simics_version() - include version number]

### Installed Packages
[Document output from list_installed_packages() - list all packages with versions]

### Available Platforms
[Document output from list_simics_platforms() - list available simulation platforms]

## Documentation Access

### DML 1.4 Reference Manual
[Document paths from get_simics_dml_1_4_reference_manual()]
- Path: [manual_root_path]
- Key files: [list important manual files]

### Model Builder User Guide
[Document paths from get_simics_model_builder_user_guide()]
- Path: [guide_root_path]
- Key sections: [list relevant guide sections]

### DML Device Template
[Document findings from get_simics_dml_template()]
- Template path: [template_path]
- Key patterns: [list important patterns observed]

## Device Example Analysis

### Simple I2C Device (button-i2c)
[Document findings from get_simics_device_example_i2c()]
- DML sample path: [dml_samples_path]
- Test sample path: [python_test_samples_path]
- Key patterns observed:
  * [Pattern 1]
  * [Pattern 2]
- Relevant code structures: [describe]

### Complex Device (DS12887 RTC)
[Document findings from get_simics_device_example_ds12887()]
- DML sample path: [dml_samples_path]
- Test sample path: [python_test_samples_path]
- Advanced patterns observed:
  * [Pattern 1]
  * [Pattern 2]
- Architectural approaches: [describe]

## Architecture Decisions

[For each NEEDS CLARIFICATION in Technical Context, create an entry:]

### Decision: [What was decided - e.g., "Use register bank template"]
- **Rationale**: [Why this choice - based on MCP tool findings and device examples]
- **Alternatives Considered**: [What else was evaluated]
- **Source**: [Which MCP tool, device example, or RAG search informed this decision]
- **Impact**: [How this affects implementation]

## RAG Search Results

[If perform_rag_query() was used, document findings:]

### Search: [Query description]
- **Query**: "[exact query string]"
- **Source Type**: [dml/python/source/docs/all]
- **Match Count**: [number of results]
- **Key Findings**:
  * [Finding 1 with code snippet or reference]
  * [Finding 2 with code snippet or reference]
- **Application**: [How findings will influence design decisions]

## Implementation Strategy

[Document overall approach based on research findings]

### Device Architecture
[High-level architecture based on examples and patterns]

### Register Design Approach
[Strategy for register implementation]

### Test Strategy
[Approach for testing based on example test patterns]

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
- [x] `list_simics_platforms()` executed and documented
- [x] `get_simics_dml_1_4_reference_manual()` executed
- [x] `get_simics_model_builder_user_guide()` executed
- [x] Device example tools executed
- [x] MCP tool outputs incorporated into research.md

**RAG Documentation Search Status** (if performed):
- [x] `perform_rag_query()` used for [purpose]
- [x] RAG search results documented in research.md
```

### Step 0.7: Validation Checkpoint

**MANDATORY**: Before proceeding to Phase 1, verify:
- [ ] research.md file exists at `[SPECS_DIR]/research.md`
- [ ] Technical Context in plan.md has NO "NEEDS CLARIFICATION" text
- [ ] Progress Tracking shows Phase 0 marked complete
- [ ] All MANDATORY MCP tool outputs are documented in research.md

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
- Register definitions (address, size, access type, reset value)
- Device state variables and attributes
- Interface specifications
- Memory-mapped regions

Use this structure:
```markdown
# Data Model: [FEATURE_NAME]

## Registers (Simics Projects)

### Register: [REGISTER_NAME]
- **Offset**: [hex address]
- **Size**: [bits]
- **Access**: [RO/WO/RW]
- **Reset Value**: [hex value]
- **Purpose**: [description]
- **Fields**: [bit fields if applicable]

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
- Reference device examples from `get_simics_device_example_i2c()` python_test_samples_path
- Reference device examples from `get_simics_device_example_ds12887()` python_test_samples_path
- Use test patterns from research.md Device Example Analysis

### Step 1.4: Extract test scenarios from user stories

Identify integration test scenarios:
- Each user story → integration test scenario
- Quickstart validation steps

**For Simics Projects**: Device operational workflow tests

### Step 1.5: Create quickstart.md

**MANDATORY**: Create `[SPECS_DIR]/quickstart.md` with user validation guide:

**CRITICAL RULES for quickstart.md**:
- ❌ DO NOT use MCP tool syntax (no `create_simics_project()` calls)
- ❌ DO NOT assume implementation details (no specific register names until implemented)
- ✅ DO use generic descriptions ("Create Simics project", "Build device module")
- ✅ DO focus on Simics CLI commands users will actually run
- ✅ DO use placeholders: `[DEVICE_NAME]`, `[REGISTER_NAME]` for unknowns
- ✅ DO include validation criteria: "What constitutes success for each step?"

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

### Step 1: [First User Story Validation]
**What to do**:
[Conceptual steps - no specific implementation commands]

**Expected Result**:
[What should happen]

**Success Criteria**:
[How to verify it worked - observable behavior]

### Step 2: [Second User Story Validation]
**What to do**:
[Reference that implementation will create the necessary files]

**Expected Result**:
[What should happen]

**Success Criteria**:
[How to verify it worked]

## Troubleshooting
[Common failure modes and how to debug them]

## Next Steps
[References to contracts/, data-model.md, and tasks.md]
```

### Step 1.6: Update agent context file

**MANDATORY**: Run the agent context update script:

```bash
.specify/scripts/bash/update-agent-context.sh adk
```

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
- [ ] `get_simics_dml_1_4_reference_manual()` executed (only if DML syntax was NEEDS CLARIFICATION)
- [ ] `get_simics_model_builder_user_guide()` executed (only if modeling approach was NEEDS CLARIFICATION)
- [ ] Device example tools executed (only if needed for architectural decisions)
- [ ] MCP tool outputs incorporated into research.md
- [ ] Environmental constraints documented for /implement phase
- [ ] **Implementation MCP tools NOT executed** (reserved for /implement phase)

**RAG Documentation Search Status** (if Project Type = simics):
- [ ] `perform_rag_query()` used for DML-specific research (source_type="dml")
- [ ] `perform_rag_query()` used for Python API research (source_type="python")
- [ ] `perform_rag_query()` used for implementation patterns (source_type="source")
- [ ] `perform_rag_query()` used for architectural guidance (source_type="docs")
- [ ] RAG search results documented in research.md
- [ ] Code examples and patterns extracted from RAG results
- [ ] Best practices identified and incorporated into design decisions

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
