---
description: Generate an actionable, dependency-ordered tasks.md for Simics DML 1.4 device model implementation based on available design artifacts.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**:
     * plan.md (DML version, Simics API, device type, tech stack, project structure)
     * spec.md (hardware specification, operational behaviors, state machines, hardware/software interactions)
     * [device-name]-register.xml (register definitions with descriptions)
   - **Optional**:
     * research.md (environment discovery, architecture decisions, device patterns)
     * data-model.md (registers, interfaces, state variables, DML implementation notes, patterns)
     * contracts/ (register-access.md, interface-behavior.md)
     * test-scenarios.md (test scenarios mapped from spec.md)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract: DML version, Simics API, device type, register map, project structure
   - Load spec.md and extract: Functional requirements, operational hardware behaviors, state machines, hardware/software interactions, register descriptions, test scenarios
   - Load [device-name]-registers.xml and extract: register names, offsets, sizes, access types, bit fields, reset values, **side-effect descriptions**
   - If research.md exists: Extract environment discovery (Simics version, packages, platforms), architecture decisions, device patterns for setup tasks
   - If data-model.md exists: Extract registers with side-effects, interfaces, state variables, DML implementation notes → map to **behavior implementation tasks** (NOT basic register definitions)
   - If contracts/ exists: Extract register access contracts, interface behavior contracts → map to test tasks
   - If test-scenarios.md exists: Extract test scenarios → map to test implementation tasks
   - Map functional requirements to implementation tasks (see Task Organization by Requirement Category)
   - **IMPORTANT**: Phase 1 creates basic register definitions - Phase 3 tasks focus on side-effects, behaviors, state transitions, HW/SW flows
   - Generate dependency graph showing phase dependencies and within-phase parallelization
   - Create parallel execution opportunities per phase
   - Validate task completeness (all side-effects, behaviors, interfaces, requirements, test scenarios covered)

4. **Generate tasks.md**: Use `.specify/templates/tasks-template.md` as structure, fill with:
   - Correct device name from plan.md
   - Phase 1: Setup tasks (Simics project creation, DML device skeleton with basic register definitions in [device-name]-registers.dml, DMLC checkout)
   - Phase 2: Tests First (TDD - optional test RAG, contract tests, workflow tests)
   - Phase 3: DML Implementation (register side-effects/behaviors, state transitions, HW/SW interaction flows with on-demand RAG - NOT basic register definitions)
   - Phase 4: Integration (memory mapping, interrupts, checkpointing with on-demand RAG)
   - Phase 5: Polish (validation, documentation, cleanup)
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Dependencies section showing phase dependencies and within-phase parallelization
   - Parallel execution examples per phase
   - Implementation strategy section (TDD, on-demand knowledge acquisition)
   - **CRITICAL BUILD REQUIREMENT** annotation for implementation tasks
   - **MCP Absolute Path** requirement for all MCP tool calls

5. **MANDATORY: Git commit tasks.md**:

   **CRITICAL**: Execute these commands using run_in_terminal tool AFTER generating tasks.md. Do NOT skip this step.

   ```bash
   cd [FEATURE_DIR]
   git add tasks.md
   git commit -m "tasks: [feature-name] - Generated implementation tasks ([X] tasks, [Y] phases)"
   ```

   **Verify commit**:
   ```bash
   git log --oneline -1
   ```

6. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per phase
   - Parallel opportunities identified
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)
   - **Git commit hash**: [commit-hash-short]

Context for task generation: {ARGS}

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by implementation phases to enable proper dependency management and incremental implementation.

**Tests are REQUIRED**: Simics device modeling follows TDD approach - tests must be written before DML implementation.

---

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **Description**: Clear action with exact file path

**Examples**:

- ✅ CORRECT: `- [ ] T001 Verify connection: get_simics_version()`
- ✅ CORRECT: `- [ ] T015 [P] Implement interrupt handling in simics-project/modules/device-name/device-name.dml`
- ✅ CORRECT: `- [ ] T011 [P] Register access test in simics-project/modules/device-name/test/test_register_access.py`
- ❌ WRONG: `- [ ] Create register tests` (missing ID and file path)
- ❌ WRONG: `T001 Verify Simics version` (missing checkbox)
- ❌ WRONG: `- [ ] [P] Create register definitions` (missing Task ID and file path)

---

### Task Organization by Requirement Category

Map functional requirements from spec.md to implementation tasks:

1. **From Functional Requirements (spec.md)**:
   - Each requirement maps to specific implementation tasks
   - Example: "Countdown Timer Logic" → counter logic + state management + behavior implementation tasks
   - Example: "Interrupt Generation" → interrupt interface + signal handling + trigger logic tasks

2. **From Register Map (spec.md + XML)**:
   - **NOTE**: Basic register definitions already exist in `[device-name]-registers.dml` from Phase 1 setup
   - **Focus on**: Register side-effects, read/write behaviors, cross-register dependencies
   - Each register with side-effects → implement read/write callback handlers
   - Each register with hardware behavior → implement state updates, triggers, or side-effects
   - Group related behaviors (e.g., control register writes trigger actions, status register reads update state)

3. **From External Interfaces (spec.md)**:
   - Each interface (interrupt, memory, signal) → interface implementation task
   - Interface contracts from contracts/ → test task before implementation

4. **From Device Operational Model (spec.md)**:
   - Each state machine → state management task
   - Each SW/HW interaction flow → workflow test task
   - State transitions → logic implementation tasks

5. **From Test Scenarios (spec.md or test-scenarios.md)**:
   - Each scenario → test implementation task [P] in Phase 3
   - Scenarios map to requirements → validate requirement coverage

---

### Phase Structure

Simics device modeling follows this 5-phase workflow:

- **Phase 1**: Setup (Simics project initialization with MCP tools, includes basic register definitions in [device-name]-registers.dml and device skeleton in [device-name].dml)
- **Phase 2**: Tests First (TDD - optional test RAG, contract tests, workflow tests - MUST FAIL before implementation)
- **Phase 3**: DML Implementation (register side-effects, hardware behaviors, state transitions, SW/HW interaction flows with on-demand RAG and CRITICAL BUILD REQUIREMENT - NOT basic register definitions)
- **Phase 4**: Integration (memory, interrupts, checkpointing with on-demand RAG and CRITICAL BUILD REQUIREMENT)
- **Phase 5**: Polish (validation, documentation, cleanup)

---

### Critical Requirements

1. **MCP Absolute Paths**: ALL MCP tool calls MUST use absolute paths (SSE transport requirement)

2. **No Separate Build Tasks**: check_with_dmlc and build_simics_project are NOT separate tasks - they are validation steps after EVERY implementation task

3. **Phase 1 Provides Base Structure**: Phase 1 setup creates `[device-name]-registers.dml` with basic register definitions and `[device-name].dml` with device skeleton. **Phase 3 tasks must focus on register side-effects, behaviors, state transitions, and HW/SW flows - NOT basic register definitions**

4. **Knowledge Check Before RAG**: Implementation tasks should check existing knowledge (research.md, data-model.md, study notes) before executing RAG queries

5. **MANDATORY Git Commit**: After generating tasks.md, MUST execute git commit using run_in_terminal tool with commit message: `"tasks: [feature-name] - Generated implementation tasks ([X] tasks, [Y] phases)"`. Verify with `git log --oneline -1`.
