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
     * spec.md (hardware specification, operational behaviors, state machines, hardware/software interactions, functional requirements)
     * [device-name]-registers.xml (register definitions with descriptions, side-effects)
   - **Optional**:
     * research.md (environment discovery, architecture decisions, device patterns)
     * data-model.md (registers, interfaces, state variables, DML implementation notes, patterns)
     * contracts/ (register-access.md, interface-behavior.md)
     * test-scenarios.md (test scenarios mapped from spec.md)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

   **CRITICAL - Task Planning Strategy**:
   - **Hardware Spec provides WHAT**: Register map (12 ID registers missing from requirements!), signals (wclk, wclk_en, wrst_n, prst_n), memory interface, timing
   - **Functional Requirements provide WHY**: User stories, acceptance criteria, behavior validation
   - **Both are REQUIRED**: Hardware Spec has implementation details (offsets, bit fields, side-effects); Requirements have testable behaviors
   - **Coverage Check**: Verify ALL Hardware Spec elements have corresponding tasks (registers, signals, interfaces, memory access, error handling)

3. **Execute task generation workflow**:
   - Load plan.md and extract: DML version, Simics API, device type, register map, project structure
   - Load spec.md and extract from ALL sections:
     * **Hardware Specification**:
       - Register Map: ALL registers (functional + ID registers), offsets, sizes, access types, reset values, **side-effects**
       - External Interfaces: ALL signals (wdogint, wdogres, wclk, wclk_en, wrst_n, prst_n) with assertion/clear conditions
       - Device States: ALL states and state transitions
       - SW/HW Interaction Flows: ALL documented flows
       - Memory Interface: Address space, access patterns (width, alignment, burst), error handling
     * **Functional Requirements**: User stories, acceptance criteria, testable behaviors (map to test tasks)
     * **User Scenarios & Testing**: Test scenarios with states/flows/requirements traceability
   - Load [device-name]-registers.xml and extract: register names, offsets, sizes, access types, bit fields, reset values, **side-effect descriptions**
   - If research.md exists: Extract environment discovery (Simics version, packages, platforms), architecture decisions, device patterns for setup tasks
   - If data-model.md exists: Extract registers with side-effects, interfaces, state variables, DML implementation notes → map to **behavior implementation tasks** (NOT basic register definitions)
   - If contracts/ exists: Extract register access contracts, interface behavior contracts → map to test tasks
   - If test-scenarios.md exists: Extract test scenarios → map to test implementation tasks

   **CRITICAL - Coverage Validation** (MUST verify before generating tasks.md):
   1. **Register Coverage**:
      - [ ] ALL registers from Hardware Spec register map have corresponding tasks (functional + configuration registers)
      - [ ] Each register with side-effects has read/write callback implementation task
   2. **Signal Coverage**:
      - [ ] ALL external signals from Hardware Spec have corresponding tasks
      - [ ] Each interrupt output has generation + assertion/clearing logic task
      - [ ] Each reset input has reset handling task (specify reset scope per signal)
   3. **State Machine Coverage**:
      - [ ] ALL device states have state variable definition task
      - [ ] ALL state transitions have transition logic implementation task
      - [ ] Each SW/HW interaction flow has workflow implementation task
   4. **Memory Interface Coverage**:
      - [ ] Access width validation task (per spec requirements)
      - [ ] Alignment validation task (per spec requirements)
      - [ ] Burst access handling task (per spec requirements)
      - [ ] Error response task (invalid access handling per spec)
   5. **Requirement Coverage**:
      - [ ] Each functional requirement maps to 1+ implementation tasks
      - [ ] Each test scenario maps to 1+ test implementation tasks
      - [ ] Each requirement has corresponding test validation task

   - **IMPORTANT**: Phase 1 creates basic register definitions - Phase 3 tasks focus on side-effects, behaviors, state transitions, HW/SW flows
   - Generate dependency graph showing phase dependencies and within-phase parallelization
   - Create parallel execution opportunities per phase
   - Validate task completeness using coverage checklist above

4. **Generate tasks.md**: Use `.specify/templates/tasks-template.md` as structure, fill with:
   - Correct device name from plan.md
   - **Phase 1: Setup** - Simics project creation, DML device skeleton with basic register definitions, DMLC checkout
   - **Phase 2: Foundational (Knowledge & Base Infrastructure)** - BLOCKS all requirements:
     * Knowledge Acquisition (read docs, RAG if needed, document patterns)
     * Base Test Infrastructure (base register tests, base memory tests - NOT requirement-specific)
     * Test Validation (ensure base tests fail)
   - **Phase 3-N: Requirement-Based Phases** - Each functional requirement becomes a phase:
     * For EACH functional requirement from spec.md:
       - **Phase X: Requirement Y - [Name]** (e.g., "Phase 3: Requirement 1 - Register Behaviors")
       - Goal statement mapping to spec.md
       - **X.1 Tests for Requirement Y**: Write requirement-specific tests FIRST (must fail)
       - **X.2 Implementation for Requirement Y**: Implement features to pass tests
       - **X.3 Validation & Commit**: Verify tests pass, git commit
     * Continue for Requirements 2, 3, 4, etc.
   - **Phase N-1: Integration & Interfaces** - AFTER all requirements complete:
     * Memory interface connection
     * Interrupt/signal connections
     * External port communications
     * Checkpointing and state serialization
     * Comprehensive test run
     * Git commit
   - **Phase N: Polish & Validation** - Final phase:
     * Performance validation
     * Code review and cleanup
     * Documentation updates
     * Final validation
     * Git commit

   **CRITICAL - Phase Organization**:
   - Phase 2 contains FOUNDATIONAL tests (base infrastructure used by ALL requirements)
   - Phases 3+ are REQUIREMENT-BASED (each requirement = separate phase with tests + implementation)
   - Each requirement phase is INDEPENDENTLY TESTABLE and COMMITTABLE
   - Integration only begins AFTER all requirement phases complete

   **CRITICAL - Task Structure**:
   - All tasks must follow strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Each requirement phase has subsections: Tests → Implementation → Validation
   - Dependencies section showing phase dependencies and parallelization opportunities
   - **CRITICAL BUILD REQUIREMENT** annotation for implementation tasks
   - **MCP Absolute Path** requirement for all MCP tool calls
   - **NOTE**: Template includes mandatory git commit tasks at end of each requirement phase

   **CRITICAL - Final Coverage Validation** (before completing tasks.md generation):
   Run through the coverage checklist one more time to ensure ALL Hardware Spec elements are covered:
   ```
   Coverage Checklist:
   [ ] ALL registers from Hardware Spec register map (functional + ID/configuration registers)
   [ ] Each register with side-effects has read/write callback implementation task
   [ ] ALL external signals from Hardware Spec (interrupts, resets, control signals)
   [ ] ALL device states have state variable definition + transition logic tasks
   [ ] ALL SW/HW interaction flows have implementation tasks
   [ ] Memory interface validation (access width, alignment, burst handling, error responses)
   [ ] ALL functional requirements from spec.md mapped to implementation tasks
   [ ] ALL test scenarios from spec.md/test-scenarios.md mapped to test tasks
   [ ] Each requirement has corresponding test validation task
   ```

   **Gap Analysis**: For each unchecked item, identify specific missing elements:
   - Missing registers: [List register names]
   - Missing signals: [List signal names]
   - Missing states: [List state names]
   - Missing flows: [List flow names]
   - Missing requirements: [List requirement IDs]

   If ANY gaps identified, ADD the missing tasks before finalizing tasks.md

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
   - **Coverage Report**: Summarize what's covered vs spec.md:
     * Register coverage: [X] functional + [Y] ID registers = [Z] total
     * Signal coverage: [A] interrupts + [B] resets = [C] total
     * State machine coverage: [D] states, [E] transitions
     * Memory interface coverage: width/alignment/burst/error validation
     * Requirement coverage: [F] requirements → [G] implementation tasks
     * Test coverage: [H] test scenarios → [I] test tasks
   - **Gap Report** (if any): List any spec.md elements without corresponding tasks
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

Map functional requirements AND hardware specification to implementation tasks:

**CRITICAL**: Tasks MUST cover BOTH Hardware Specification AND Functional Requirements

1. **From Hardware Specification Register Map (spec.md + XML)**:
   - **Functional Registers**: Already have basic definitions from Phase 1
     * Focus on: Register side-effects, read/write behaviors, cross-register dependencies
     * Each register with side-effects → implement read/write callback handlers
     * Each register with hardware behavior → implement state updates, triggers
   - **Identification Registers** (Peripheral ID, PrimeCell ID): OFTEN MISSING from requirements
     * Create task: Implement ALL ID registers with correct reset values
     * Create task: Enforce read-only access (reject writes)
     * Create task: Test ID register access (read, write rejection, reset values)

2. **From Hardware Specification External Interfaces (spec.md)**:
   - **Interrupt Outputs** (wdogint, wdogres):
     * Create task: Implement signal interface declarations
     * Create task: Implement assertion logic with timing requirements
     * Create task: Implement clear mechanisms
     * Create task: Test interrupt generation and clearing
   - **Reset Inputs** (wrst_n, prst_n): OFTEN MISSING from requirements
     * Create task: Implement wrst_n (full device reset)
     * Create task: Implement prst_n (APB interface reset)
     * Create task: Test reset behaviors (separate tests for each reset type)

3. **From Hardware Specification Memory Interface (spec.md)**:
   - OFTEN MISSING from requirements - MUST create tasks:
     * Create task: Implement access width validation (32-bit only)
     * Create task: Implement alignment validation (4-byte aligned)
     * Create task: Implement burst access rejection
     * Create task: Implement error responses for invalid access
     * Create task: Test all access violation scenarios

4. **From Functional Requirements (spec.md)**:
   - Each requirement maps to specific implementation tasks
   - Example: "Countdown Timer Logic" → counter logic + state management + behavior implementation tasks
   - Example: "Interrupt Generation" → interrupt interface + signal handling + trigger logic tasks
   - Each requirement → 1+ test scenarios → test implementation tasks

5. **From Device Operational Model (spec.md)**:
   - Each state machine → state management task
   - Each SW/HW interaction flow → workflow implementation task + workflow test task
   - State transitions → logic implementation tasks

6. **From Test Scenarios (spec.md or test-scenarios.md)**:
   - Each scenario → test implementation task [P] in Phase 2
   - Scenarios map to requirements → validate requirement coverage

**Coverage Validation Checklist** (use before generating tasks.md):
- [ ] ALL registers from register map have tasks (functional + ID registers)
- [ ] ALL external signals have tasks (interrupt outputs + reset inputs)
- [ ] ALL memory interface requirements have tasks (width, alignment, burst, error handling)
- [ ] ALL functional requirements have implementation + test tasks
- [ ] ALL device states and transitions have tasks
- [ ] ALL SW/HW interaction flows have tasks

---

### Phase Structure

Simics device modeling follows this hybrid requirement-based workflow:

- **Phase 1**: Setup (Simics project initialization with MCP tools, includes basic register definitions in [device-name]-registers.dml and device skeleton in [device-name].dml)
- **Phase 2**: Foundational (Knowledge acquisition + base test infrastructure - BLOCKS all requirements)
- **Phase 3-N**: Requirement-Based Phases (each functional requirement from spec.md becomes a phase):
  * Phase 3: Requirement 1 - [Name]
    - 3.1 Tests for Requirement 1 (write first, must fail)
    - 3.2 Implementation for Requirement 1 (make tests pass)
    - 3.3 Validation & Commit (tests pass, git commit)
  * Phase 4: Requirement 2 - [Name]
    - 4.1 Tests for Requirement 2
    - 4.2 Implementation for Requirement 2
    - 4.3 Validation & Commit
  * ... Continue for all requirements
- **Phase N-1**: Integration & Interfaces (memory, interrupts, checkpointing - AFTER all requirements)
- **Phase N**: Polish & Validation (performance, documentation, final validation)

**Benefits of Requirement-Based Organization**:
- ✅ **Incremental delivery**: Each requirement independently testable and committable
- ✅ **Clear TDD**: Test → Implement → Validate cycle per requirement
- ✅ **Better progress**: "Requirement 2 of 5 complete" vs "Phase 3 40% done"
- ✅ **Parallelization**: Independent requirements can run simultaneously
- ✅ **Natural mapping**: Follows spec.md Functional Requirements structure
- ✅ **Independent validation**: Each requirement has its own test suite
- ✅ **Easier debugging**: Failures isolated to specific requirement

**⚠️ Phase Completion Git Commits**: Each requirement phase ends with mandatory git commit for audit trail and rollback capability.

---

### Critical Requirements

1. **MCP Absolute Paths**: ALL MCP tool calls MUST use absolute paths (SSE transport requirement)

2. **No Separate Build Tasks**: check_with_dmlc and build_simics_project are NOT separate tasks - they are validation steps after EVERY implementation task

3. **Phase 1 Provides Base Structure**: Phase 1 setup creates `[device-name]-registers.dml` with basic register definitions and `[device-name].dml` with device skeleton. **Phase 3 tasks must focus on register side-effects, behaviors, state transitions, and HW/SW flows - NOT basic register definitions**

4. **Knowledge Check Before RAG**: Implementation tasks should check existing knowledge (research.md, data-model.md, study notes) before executing RAG queries

5. **MANDATORY Git Commit**: After generating tasks.md, MUST execute git commit using run_in_terminal tool with commit message: `"tasks: [feature-name] - Generated implementation tasks ([X] tasks, [Y] phases)"`. Verify with `git log --oneline -1`.
