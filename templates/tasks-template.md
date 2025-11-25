---

des**Prerequisites**:
- **Required**: plan.md, spec.md, [device-name]-registers.xml
- **Optional**: research.md, data-model.md, contracts/, test-scenarios.md

**Tests**: Tests are REQUIRED for Simics device modeling (TDD approach).

**Organization**: Tasks are organized by implementation phases to enable proper dependency management and incremental implementation.

## Task Format: `- [ ] [ID] [P?] Description`

- **[ID]**: Task identifier (T001, T002, T003...)
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

--- list template for Simics DML 1.4 device model implementation"
---

# Tasks: [DEVICE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**:
- **Required**: plan.md, spec.md, [device-name]-registers.xml
- **Optional**: research.md, data-model.md, contracts/, test-scenarios.md

**Tests**: Tests are REQUIRED for Simics device modeling (TDD approach).

**Organization**: Tasks are organized by implementation phases to enable proper dependency management and incremental implementation.

## Format: `[ID] [P?] Description`

- **[ID]**: Sequential task ID (T001, T002, T003...)
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Path Conventions

- **Simics Project Structure**: `simics-project/modules/[device-name]/` at repository root
- **DML Files**: `[device-name].dml`, `registers.dml`(optional), `interfaces.dml`(optional) in module directory
- **Test Files**: `test_*.py` in `simics-project/modules/[device-name]/test/` directory

**⚠️ CRITICAL - MCP Tool Paths (SSE Transport)**:
- **ALWAYS use ABSOLUTE paths** for MCP tools
- **NEVER use relative paths** like `"./simics-project"` or `"../project"`
- **WHY**: SSE transport MCP servers run in different process/directory context
- **HOW**: Use workspace root to construct: `"/full/path/to/workspace/simics-project"`
- **Example**: `create_simics_project(project_path="/home/user/workspace/simics-project")`

<!--
  ============================================================================
  IMPORTANT: The tasks below are EXAMPLE TASKS for illustration purposes only.

  The /tasks command MUST replace these with actual tasks based on:
  - Functional requirements from spec.md (hardware behaviors, not user stories)
  - Register definitions from [device-name]-registers.xml
  - DML implementation patterns from data-model.md and research.md
  - Test scenarios from test-scenarios.md or spec.md
  - Architecture decisions from research.md

  Tasks MUST be organized by implementation phases following the Simics device modeling workflow:
  - Setup → Knowledge Acquisition → Tests First (TDD) → DML Implementation → Integration → Polish

  DO NOT keep these example tasks in the generated tasks.md file.
  ============================================================================
-->

---

## Phase 1: Setup (Simics Project Initialization)

**Purpose**: Initialize Simics project structure and verify environment

- [ ] T001 Verify Simics connection: `get_simics_version()`
- [ ] T002 Create Simics project: `create_simics_project(project_path="/absolute/path/to/workspace/simics-project")` ⚠️ ABSOLUTE PATH
- [ ] T003 Generate DML register and dummy device definitions: `generate_dml_registers(project_path="/absolute/path/to/workspace/simics-project", device_name="DEVICE_NAME", reg_xml="/absolute/path/to/[device-name]-registers.xml")` ⚠️ ABSOLUTE PATH
- [ ] T004 [P] Verify initial build: `build_simics_project(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` ⚠️ ABSOLUTE PATH
- [ ] T005 **MANDATORY: Git commit Phase 1 completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/
  git commit -m "setup: Phase 1 complete - Simics project initialized with register definitions"
  git log --oneline -1
  ```

**Checkpoint**: Simics project structure ready, DML compiler available, Phase 1 committed

---

## Phase 2: Foundational (Knowledge & Base Infrastructure) ⚠️ BLOCKS ALL REQUIREMENTS

**Purpose**: Establish foundational knowledge and base test infrastructure that ALL requirements depend on

**⚠️ CRITICAL**: No requirement implementation can begin until this phase is complete

### Knowledge Acquisition

- [ ] T006 Review design documents for implementation context:
  - Read spec.md Hardware Specification (register map, external interfaces, operational model)
  - Read spec.md Functional Requirements (all requirements overview)
  - Read data-model.md (if exists): Registers, interfaces, state variables, DML patterns
  - Read test-scenarios.md (if exists): Test coverage planning
  - Document key findings and patterns in research.md

- [ ] T007 **RAG Query** (if DML patterns needed): Execute `perform_rag_query("DML device modeling common patterns register bank interface signal event", source_type="dml", match_count=10)` → document patterns in research.md

### Base Test Infrastructure

> **NOTE**: These foundational tests validate infrastructure used by ALL requirements

- [ ] T008 [P] **RAG Query** (if test patterns needed): Execute `perform_rag_query("Simics Python device testing register read write verification patterns", source_type="python", match_count=10)` → document test patterns in research.md

- [ ] T009 [P] Base register access test in `simics-project/modules/DEVICE_NAME/test/test_register_access.py`:
  - Review spec.md Hardware Spec register map for ALL registers (functional + ID + configuration)
  - Review contracts/register-access.md (if exists) for test contracts
  - Test register read/write operations for all register types
  - Test reset values for all registers
  - Test access violations (RO/WO enforcement, protection mechanisms)
  - Use patterns from T008 RAG query if executed

- [ ] T010 [P] Base memory interface test in `simics-project/modules/DEVICE_NAME/test/test_memory_interface.py`:
  - Review spec.md Hardware Spec Memory Interface Requirements
  - Test access width validation (per spec requirements)
  - Test alignment validation (per spec requirements)
  - Test burst access handling (per spec requirements)
  - Test error responses for invalid access patterns
  - Use patterns from T008 RAG query if executed

- [ ] T011 Validate base test environment: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (device not implemented yet)
  - **If tests pass**: Tests are not correctly checking device behavior

- [ ] T012 **MANDATORY: Git commit Phase 2 completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/modules/DEVICE_NAME/test/
  git add research.md
  git commit -m "foundation: Phase 2 complete - Knowledge acquired and base tests written (TDD)"
  git log --oneline -1
  ```

**Checkpoint**: Foundation established - knowledge documented, base infrastructure tests written and failing, ready for requirement implementation

---

<!--
  ============================================================================
  REQUIREMENT-BASED PHASES (Phase 3+)

  Each requirement from spec.md Functional Requirements becomes its own phase:
  - Phase N: Requirement X
    - N.1: Tests for Requirement X (write first, must fail)
    - N.2: Implementation for Requirement X (make tests pass)
    - N.3: Validation & Commit (tests pass, git commit)

  Benefits:
  - Incremental delivery (each requirement independently testable)
  - Clear TDD workflow (test → implement → validate per requirement)
  - Better progress tracking (requirement completion vs phase percentage)
  - Parallelization opportunities (different requirements, different agents)
  - Natural mapping to spec.md structure

  The example below shows typical hardware device requirements. Replace with
  actual requirements from spec.md Functional Requirements section.
  ============================================================================
-->

## Phase 3: Requirement 1 - [Requirement Name] (Priority: [P0/P1/P2])

**Goal**: [Brief description from spec.md Functional Requirements]

**Maps to**:
- spec.md: Requirement 1 section
- test-scenarios.md: Scenario(s) [X, Y, Z] (if exists)
- data-model.md: [Relevant sections] (if exists)

**⚠️ CRITICAL BUILD REQUIREMENT** (applies to ALL implementation tasks):
Before implementing EACH task:
1. Review available knowledge: research.md, data-model.md, DML best practices, DML grammar
2. If knowledge insufficient → execute targeted `perform_rag_query()` → document in research.md
3. Implement the task

After implementing EACH task:
1. `check_with_dmlc(project_path="/absolute/path", module="DEVICE_NAME")` for diagnostics
2. `build_simics_project(project_path="/absolute/path", module="DEVICE_NAME")` to verify compilation
3. Only mark done when build succeeds

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 3.1 Tests for Requirement 1 ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] Test for Requirement 1 in `simics-project/modules/DEVICE_NAME/test/test_requirement_1.py`:
  - Review spec.md Requirement 1 acceptance criteria
  - Review test-scenarios.md for relevant scenarios (if exists)
  - Review data-model.md for registers/interfaces involved (if exists)
  - **Test acceptance criterion 1**: [Describe test for criterion 1]
  - **Test acceptance criterion 2**: [Describe test for criterion 2]
  - **Test acceptance criterion 3**: [Describe test for criterion 3]
  - **RAG if needed**: `perform_rag_query("[specific test question]", source_type="python")` → document in research.md

- [ ] T014 Validate Requirement 1 tests fail: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test/test_requirement_1.py")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)
  - **If tests pass**: Tests are not correctly checking requirement

---

### 3.2 Implementation for Requirement 1

> **Goal**: Implement [specific feature/behavior] to pass Requirement 1 tests (T013)

- [ ] T015 [P] Implement [Feature A] in `simics-project/modules/DEVICE_NAME/[file].dml`:
  - Review spec.md Hardware Spec for [feature] details
  - Review data-model.md for [feature] implementation notes (if exists)
  - **RAG if needed**: `perform_rag_query("[specific DML question]", source_type="dml")` → document in research.md
  - Implement [specific functionality]
  - Check_with_dmlc → build

- [ ] T016 [P] Implement [Feature B] in `simics-project/modules/DEVICE_NAME/[file].dml`:
  - Review spec.md Hardware Spec for [feature] details
  - Review data-model.md for [feature] implementation notes (if exists)
  - **RAG if needed**: `perform_rag_query("[specific DML question]", source_type="dml")` → document in research.md
  - Implement [specific functionality]
  - Check_with_dmlc → build

---

### 3.3 Validation & Commit

- [ ] T017 Validate Requirement 1 tests pass: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test/test_requirement_1.py")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS
  - **If tests fail**: Fix implementation until tests pass

- [ ] T018 **MANDATORY: Git commit Requirement 1 completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/modules/DEVICE_NAME/
  git commit -m "implement: Requirement 1 complete - [feature name] implemented and tested"
  git log --oneline -1
  ```

**Checkpoint**: Requirement 1 complete and independently testable - can proceed to Requirement 2

---

## Phase 4: Requirement 2 - [Requirement Name] (Priority: [P0/P1/P2])

**Goal**: [Brief description from spec.md Functional Requirements]

**Maps to**:
- spec.md: Requirement 2 section
- test-scenarios.md: Scenario(s) [A, B] (if exists)
- data-model.md: [Relevant sections] (if exists)

---

### 4.1 Tests for Requirement 2 ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [P] Test for Requirement 2 in `simics-project/modules/DEVICE_NAME/test/test_requirement_2.py`:
  - Review spec.md Requirement 2 acceptance criteria
  - Review test-scenarios.md for relevant scenarios (if exists)
  - Review data-model.md for registers/interfaces involved (if exists)
  - **Test acceptance criterion 1**: [Describe test for criterion 1]
  - **Test acceptance criterion 2**: [Describe test for criterion 2]
  - **RAG if needed**: `perform_rag_query("[specific test question]", source_type="python")` → document in research.md

- [ ] T020 Validate Requirement 2 tests fail: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test/test_requirement_2.py")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)

---

### 4.2 Implementation for Requirement 2

> **Goal**: Implement [specific feature/behavior] to pass Requirement 2 tests (T019)

- [ ] T021 [P] Implement [Feature C] in `simics-project/modules/DEVICE_NAME/[file].dml`:
  - Review spec.md Hardware Spec for [feature] details
  - Review data-model.md for [feature] implementation notes (if exists)
  - **RAG if needed**: Execute targeted RAG query → document in research.md
  - Implement [specific functionality]
  - Check_with_dmlc → build

- [ ] T022 [P] Implement [Feature D] in `simics-project/modules/DEVICE_NAME/[file].dml`:
  - Review spec.md Hardware Spec for [feature] details
  - Review data-model.md for [feature] implementation notes (if exists)
  - **RAG if needed**: Execute targeted RAG query → document in research.md
  - Implement [specific functionality]
  - Check_with_dmlc → build

---

### 4.3 Validation & Commit

- [ ] T023 Validate Requirement 2 tests pass: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test/test_requirement_2.py")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS

- [ ] T024 **MANDATORY: Git commit Requirement 2 completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/modules/DEVICE_NAME/
  git commit -m "implement: Requirement 2 complete - [feature name] implemented and tested"
  git log --oneline -1
  ```

**Checkpoint**: Requirements 1 AND 2 complete - can proceed to Requirement 3

---

<!--
  ============================================================================
  REPEAT PATTERN for Requirement 3, 4, 5, etc.

  Each requirement gets its own phase with:
  - Phase N: Requirement X - [Name]
    - N.1 Tests for Requirement X
    - N.2 Implementation for Requirement X
    - N.3 Validation & Commit

  Continue until all functional requirements from spec.md are covered.
  ============================================================================
-->

## Phase 5: Requirement 3 - [Requirement Name] (Priority: [P0/P1/P2])

[Follow same pattern as Phase 3 and 4]

---

## Phase 6: Requirement 4 - [Requirement Name] (Priority: [P0/P1/P2])

[Follow same pattern as Phase 3 and 4]

---

<!--
  ============================================================================
  COVERAGE VALIDATION before Integration

  Before proceeding to Integration phase, validate ALL requirements complete:
  ============================================================================
-->

**Coverage Validation Before Integration**:
- [ ] ALL functional requirements from spec.md have dedicated phases above
- [ ] ALL registers from spec.md Hardware Spec implemented (functional + ID registers)
- [ ] ALL external signals from spec.md Hardware Spec implemented (interrupts + clocks + resets)
- [ ] ALL memory access validation from spec.md Hardware Spec implemented
- [ ] ALL device states and transitions from spec.md implemented
- [ ] ALL SW/HW interaction flows from spec.md implemented
- [ ] ALL requirement tests pass independently

---

## Phase N-1: Integration & Interfaces

**Purpose**: Connect all requirements together and integrate with Simics infrastructure

**Note**: This phase begins after ALL functional requirements (Phase 3, 4, 5...) are complete

**⚠️ CRITICAL BUILD REQUIREMENT**: Same as requirement phases - check_with_dmlc → build after EACH task

- [ ] T[N-5] Memory interface connection in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review spec.md Hardware Spec Memory Interface Requirements
  - Review research.md and data-model.md for memory mapping patterns
  - **RAG if needed**: `perform_rag_query("DML io_memory interface memory mapped registers", source_type="dml")` → document in research.md
  - Implement io_memory interface methods
  - Connect register bank to memory space
  - Validate memory access patterns (from base tests T010)
  - Check_with_dmlc → build

- [ ] T[N-4] Interrupt/signal connections in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review spec.md Hardware Spec External Interfaces for interrupt requirements
  - Review data-model.md for signal interface patterns
  - **RAG if needed**: `perform_rag_query("DML signal interface interrupt generation", source_type="dml")` → document in research.md
  - Implement signal interface for interrupt outputs
  - Add interrupt generation logic with timing requirements
  - Connect to interrupt controller
  - Check_with_dmlc → build

- [ ] T[N-3] External port communications in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review spec.md Hardware Spec for external interface requirements
  - **RAG if needed**: `perform_rag_query("DML port interface device communication", source_type="dml")` → document in research.md
  - Implement required port interfaces
  - Add communication protocols
  - Integrate with other devices if needed
  - Check_with_dmlc → build

- [ ] T[N-2] Checkpointing and state serialization in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for checkpoint patterns
  - **RAG if needed**: `perform_rag_query("DML checkpoint save restore state serialization", source_type="dml")` → document in research.md
  - Implement checkpoint save methods for ALL state variables
  - Implement checkpoint restore methods
  - Add state validation
  - Check_with_dmlc → build

- [ ] T[N-1] [P] Run comprehensive tests: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test")` ⚠️ ABSOLUTE PATH
  - **Expected**: ALL tests should PASS (base tests + all requirement tests)
  - **If tests fail**: Review failures and fix integration issues

- [ ] T[N] **MANDATORY: Git commit Integration completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/modules/DEVICE_NAME/
  git commit -m "integrate: Integration complete - Device integrated with Simics infrastructure, all tests passing"
  git log --oneline -1
  ```

**Checkpoint**: Device fully integrated with Simics - all tests passing

---

## Phase N: Polish & Validation

**Purpose**: Final validation, optimization, and documentation

- [ ] T[N+1] [P] Performance validation:
  - Measure simulation overhead
  - Verify <1% performance impact (or per requirements from spec.md)
  - Optimize hot paths if needed
  - Document performance characteristics

- [ ] T[N+2] [P] Code review and cleanup:
  - Verify DML grammar compliance
  - Check error handling completeness
  - Review logging statements
  - Remove debug code
  - Add code comments for complex logic
  - Verify coding standards compliance

- [ ] T[N+3] [P] Update device documentation in `simics-project/modules/DEVICE_NAME/README.md`:
  - Add device description and purpose
  - Document register map (ALL registers including ID registers)
  - Document external interfaces (ALL signals: interrupts, clocks, resets)
  - Add usage examples and configuration steps
  - Include integration instructions
  - Add troubleshooting guide

- [ ] T[N+4] [P] Update test documentation in `simics-project/modules/DEVICE_NAME/test/README.md`:
  - Document test scenarios (base tests + all requirement tests)
  - Add test execution instructions
  - Include test coverage report
  - Add troubleshooting guide for test failures

- [ ] T[N+5] Final validation: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project")` ⚠️ ABSOLUTE PATH
  - Run all project tests (base + all requirements + integration)
  - Verify no regressions
  - Confirm all scenarios pass
  - Generate test coverage report

- [ ] T[N+6] **MANDATORY: Git commit Polish completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/modules/DEVICE_NAME/
  git commit -m "polish: Device model complete - validated, optimized, and documented"
  git log --oneline -1
  ```

**Checkpoint**: Device model complete and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
  - T001 → T002 → T003 → T004 → T005

- **Phase 2 (Foundational)**: Depends on Phase 1 (T005) - BLOCKS all requirements
  - T006 → T007 (RAG queries)
  - T008 → T009 || T010 (parallel base tests)
  - T011 → T012 (validation + commit)

- **Phase 3 (Requirement 1)**: Depends on Phase 2 (T012) - First requirement
  - 3.1 Tests: T013 → T014 (write tests, validate they fail)
  - 3.2 Implementation: T015 || T016 (parallel if different files)
  - 3.3 Validation: T017 → T018 (tests pass, commit)

- **Phase 4 (Requirement 2)**: Depends on Phase 3 (T018) OR can run parallel if independent
  - 4.1 Tests: T019 → T020
  - 4.2 Implementation: T021 || T022
  - 4.3 Validation: T023 → T024

- **Phase 5+ (Requirements 3, 4, ...)**: Follow same pattern
  - Each requirement CAN run parallel if independent
  - Each requirement MUST complete tests before implementation

- **Phase N-1 (Integration)**: Depends on ALL requirement phases complete
  - T[N-5] → T[N-4] → T[N-3] → T[N-2] (mostly sequential integration)
  - T[N-1] → T[N] (validation + commit)

- **Phase N (Polish)**: Depends on Integration (T[N])
  - T[N+1] || T[N+2] || T[N+3] || T[N+4] (all parallel)
  - T[N+5] → T[N+6] (final validation + commit)

### Parallelization Opportunities

- **Phase 2**: T009 || T010 (base tests - different files)
- **Requirement Phases**:
  - Within requirement: Implementation tasks can run parallel if different files
  - Across requirements: Independent requirements can run parallel
- **Integration**: Limited parallelization - mostly sequential
- **Polish**: T[N+1] || T[N+2] || T[N+3] || T[N+4] (all different concerns)

### Critical Path

```
Phase 1 (Setup) → Phase 2 (Foundation) → [BLOCKS]
  ↓
Phase 3 (Req 1): Tests → Implementation → Validation
  ↓
Phase 4 (Req 2): Tests → Implementation → Validation
  ↓
Phase 5+ (Req 3, 4, ...): Tests → Implementation → Validation
  ↓
Phase N-1 (Integration): Connect all requirements
  ↓
Phase N (Polish): Final validation
```

**Note**: Requirements CAN run in parallel if independent (different registers, different state, no shared resources)

---

## Implementation Strategy

### Hybrid TDD Workflow

1. **Phase 1**: Setup → Simics project structure ready
2. **Phase 2**: Foundation → Knowledge + base infrastructure tests (MUST FAIL)
3. **Phase 3+**: Per-Requirement → Tests → Implementation → Validation (incremental delivery)
4. **Phase N-1**: Integration → Connect all requirements together
5. **Phase N**: Polish → Production-ready

### Benefits of Requirement-Based Organization

✅ **Incremental Delivery**: Each requirement independently testable and committable
✅ **Clear TDD**: Test → Implement → Validate cycle visible per requirement
✅ **Better Progress**: "Requirement 2 of 5 complete" vs "Phase 3 40% done"
✅ **Parallelization**: Independent requirements can be implemented simultaneously
✅ **Natural Mapping**: Follows spec.md Functional Requirements structure
✅ **Independent Validation**: Each requirement has its own test suite
✅ **Easier Debugging**: Failures isolated to specific requirement

### On-Demand Knowledge Acquisition

For each implementation task:
1. Review available knowledge: research.md, data-model.md, DML best practices, DML grammar
2. If sufficient → implement
3. If insufficient → execute targeted `perform_rag_query()` → document in research.md → implement
4. Validate: check_with_dmlc → build_simics_project
5. Only mark done when build succeeds
6. Git commit when requirement complete

---

## Notes

- **[P] tasks** = Can run in parallel (different files, no dependencies)
- **Verify tests fail** before implementing (TDD principle)
- **RAG queries** are on-demand - execute only when knowledge insufficient
- **check_with_dmlc + build** after EVERY implementation task (not separate tasks)
- **Document RAG results** in research.md for reuse across tasks
- **Git commit** after each requirement completion (incremental delivery)
- **Absolute paths** for MCP tools (SSE transport requirement)
- **Stop at checkpoints** to validate phases independently
- **Requirement independence**: Analyze dependencies - some can run parallel
- **Task IDs**: Use T[N] notation - actual numbers depend on number of requirements
