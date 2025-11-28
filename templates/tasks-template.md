---

description: "Task list template for feature implementaion of a Simics DML 1.4 device model."
---

# Tasks: [DEVICE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**:
- **Required**: plan.md, spec.md, [device-name]-registers.xml
- **Optional**: research.md, data-model.md, contracts/, test-scenarios.md,
- **References**:
  - .specify/memory/DML_Device_Development_Best_Practices.md for Simics DML device modeling best practices
  - .specify/memory/DML_grammar.md for DML grammar reference
  - .specify/memory/Simics_Model_Test_Best_Practices.md for Simics model test patterns and debugging

**Tests**: Tests are REQUIRED for Simics device modeling (TDD approach).

**Organization**: Tasks are organized by feature requirements to enable proper dependency management and incremental implementation.

---

## Implementation Workflow (Applies to ALL Requirement Phases)

**⚠️ TDD Cycle** (Phase 3+):
1. **Write Tests First** → Tests define expected behavior (will fail initially)
2. **Implement DML Code** → Write code to satisfy tests
3. **Build** → `check_with_dmlc()` → `build_simics_project()` → Fix until compilation succeeds
4. **Run Tests** → `run_simics_test()` → Verify behavior
5. **Iterative Debug** → If tests fail: Fix DML code or test → Rebuild → Retest → Repeat
6. **Commit When Green** → Git commit only when ALL requirement tests pass

**⚠️ Per-Task Knowledge Check**:
- **For DML implementation**: Review research.md, data-model.md, DML_Device_Development_Best_Practices.md
- **For test implementation**: Review Simics_Model_Test_Best_Practices.md for test patterns and common issues
- RAG query if knowledge insufficient → document in research.md

---

## Format: `[ID] [P?] Description`

- **[ID]**: Sequential task ID (T001, T002, T003...)
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Path Conventions

- **Simics Project Structure**: `simics-project/modules/[device-name]/` at repository root
- **DML Files**: `[device-name].dml`, `registers.dml`(optional), `interfaces.dml`(optional) in module directory
- **Test Files**: `s-*.py` in `simics-project/modules/[device-name]/test/` directory
  - **NOTE**: Simics test scripts should start with `s-` prefix (e.g., `s-countdown-timer.py`, `s-register-access.py`)

**⚠️ CRITICAL - MCP Tool Paths (SSE Transport)**:
- **ALWAYS use ABSOLUTE paths** for MCP tools
- **NEVER use relative paths** like `"./simics-project"` or `"../project"`
- **WHY**: SSE transport MCP servers run in different process/directory context
- **HOW**: Use workspace root to construct: `"/full/path/to/workspace/simics-project"`
- **Example**: `create_simics_project(project_path="/home/user/workspace/simics-project")`

<!--
  ============================================================================
  IMPORTANT: The tasks below are EXAMPLE TASKS for illustration purposes only. The /tasks command MUST replace these with actual tasks.
  DO NOT keep these example tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Simics Project Setup

**Purpose**: Initialize Simics project structure and verify environment

- [ ] T001 Verify Simics connection: `get_simics_version()`
- [ ] T002 Create Simics project: `create_simics_project(project_path="/absolute/path/to/workspace/simics-project")` ⚠️ ABSOLUTE PATH
- [ ] T003 Generate DML register and dummy device definitions: `generate_dml_registers(project_path="/absolute/path/to/workspace/simics-project", device_name="DEVICE_NAME", reg_xml="/absolute/path/to/[device-name]-registers.xml")` ⚠️ ABSOLUTE PATH
- [ ] T004 **MANDATORY: Git commit Phase 1 completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/
  git commit -m "setup: Phase 1 complete - Simics project setup"
  git log --oneline -1
  ```

**Checkpoint**: Simics project structure ready, DML compiler available, Phase 1 committed

---

## Phase 2: Foundational (Knowledge & Base Infrastructure) ⚠️ BLOCKS ALL REQUIREMENTS

**Purpose**: Establish foundational knowledge and base test infrastructure that ALL requirements depend on

**⚠️ CRITICAL**: No requirement implementation can begin until this phase is complete

### Knowledge Acquisition

- [ ] T005 Review design documents for implementation context:
  - Read spec.md Hardware Specification (register map, external interfaces, operational model)
  - Read spec.md Functional Requirements (all requirements overview)
  - Read data-model.md (if exists): Registers, interfaces, state variables, DML patterns
  - Read test-scenarios.md (if exists): Test coverage planning
  - Read .specify/memory/DML_Device_Development_Best_Practices.md for Simics DML device modeling best practices
  - Read .specify/memory/Simics_Model_Test_Best_Practices.md for Simics model test best practices
  - Document key findings and patterns in research.md

- [ ] T006 **RAG Query** (if DML patterns needed): Execute `perform_rag_query("DML device modeling common patterns register bank interface signal event", source_type="dml", match_count=10)` → document patterns in research.md

### Base Test Infrastructure

> **NOTE**: These foundational tests validate infrastructure used by ALL requirements

- [ ] T007 [P] **Review test best practices**: Read `.specify/memory/Simics_Model_Test_Best_Practices.md` for test patterns, structure, and common issues → document in research.md

- [ ] T008 [P] Base register access test in `simics-project/modules/DEVICE_NAME/test/s-register-access.py`:
  - **Use patterns from Simics_Model_Test_Best_Practices.md**
  - Review spec.md Hardware Spec register map for ALL registers (functional + ID + configuration)
  - Review contracts/register-access.md (if exists) for test contracts
  - Test register read/write operations for all register types
  - Test reset values for all registers
  - Test access violations (RO/WO enforcement, protection mechanisms)

- [ ] T009 [P] Base memory interface test in `simics-project/modules/DEVICE_NAME/test/s-memory-interface.py`:
  - **Use patterns from Simics_Model_Test_Best_Practices.md**
  - Review spec.md Hardware Spec Memory Interface Requirements
  - Test access width validation (per spec requirements)
  - Test alignment validation (per spec requirements)
  - Test burst access handling (per spec requirements)
  - Test error responses for invalid access patterns
  - Use patterns from T007 RAG query if executed

- [ ] T010 Validate base test environment: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (device not implemented yet)
  - **If tests pass**: Tests are not correctly checking device behavior

- [ ] T011 **MANDATORY: Git commit Phase 2 completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/modules/DEVICE_NAME/test/
  git add research.md
  git commit -m "foundation: Phase 2 complete - Knowledge acquired and base tests written (TDD)"
  git log --oneline -1
  ```

**Checkpoint**: Foundation established - knowledge documented, base infrastructure tests written and failing, ready for requirement implementation

---

## Phase 3: Requirement 1 - [Requirement Name] (Priority: [P0/P1/P2])

**Goal**: [Brief description from spec.md Functional Requirements]

**Maps to**:
- spec.md: Requirement 1 section
- test-scenarios.md: Scenario(s) [X, Y, Z] (if exists)
- data-model.md: [Relevant sections] (if exists)

> **Workflow**: Follow "Implementation Workflow" section above (TDD cycle + per-task build validation)

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 3.1 Tests for Requirement 1 ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] Test for Requirement 1 in `simics-project/modules/DEVICE_NAME/test/s-[short-requirement-description].py`:
  - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and structure
  - Review spec.md Requirement 1 acceptance criteria
  - Review test-scenarios.md for relevant scenarios (if exists)
  - Review data-model.md for registers/interfaces involved (if exists)
  - **Test acceptance criterion 1**: [Describe test for criterion 1]
  - **Test acceptance criterion 2**: [Describe test for criterion 2]
  - **Test acceptance criterion 3**: [Describe test for criterion 3]
  - **RAG if needed**: `perform_rag_query("[specific test question]", source_type="python")` → document in research.md

- [ ] T014 Validate Requirement 1 tests fail: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` ⚠️ ABSOLUTE PATH
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

> **ITERATIVE DEBUGGING GUIDE**: Tests should PASS after implementation. If not, follow this cycle:

- [ ] T017 Validate Requirement 1 tests pass: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS (all acceptance criteria satisfied)
  - **If tests FAIL**: Follow iterative debugging workflow:
    1. **Analyze Failure**: Read test output → identify which acceptance criterion failed
    2. **Review Requirement**: Check spec.md Requirement 1 → verify expected behavior matches test assumptions
    3. **Determine Root Cause**: Is it DML implementation bug OR test bug?
       - **If DML is wrong**: Implementation doesn't match spec → fix DML code
       - **If Test is wrong**: Test has incorrect assumptions/assertions → fix test code
       - **If Spec is ambiguous**: Document in research.md → clarify with team
    4. **Fix Code** (DML or Test):
       - **Fix DML**: Edit `simics-project/modules/DEVICE_NAME/[file].dml`
         - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for patterns
         - Common DML issues: timing bugs, state machine errors, register side-effects, signal generation
         - RAG if needed: `perform_rag_query("[specific DML fix question]", source_type="dml")` → document in research.md
       - **Fix Test**: Edit `simics-project/modules/DEVICE_NAME/test/s-requirement_1.py`
         - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and debugging
         - Verify test logic matches spec.md acceptance criteria
         - Common test issues: incorrect assertions, wrong expected values, missing setup/teardown, timing assumptions
         - RAG if needed: `perform_rag_query("[specific test fix question]", source_type="python")` → document in research.md
    5. **Rebuild** (if DML changed): `check_with_dmlc()` → `build_simics_project()` → verify compilation
    6. **Retest**: `run_simics_test()` again → check if test passes
    7. **Repeat**: Continue cycle until ALL tests pass
  - **Success Criteria**: ALL test cases pass, no errors, no warnings

- [ ] T018 **MANDATORY: Git commit Requirement 1 completion**:
  ```bash
  cd /absolute/path/to/workspace
  git add simics-project/modules/DEVICE_NAME/
  git commit -m "implement: Requirement 1 complete - [feature name] implemented and tested"
  git log --oneline -1
  ```

**Checkpoint**: Requirement 1 complete and independently testable - can proceed to Requirement 2

---

## Phase 4+: Additional Requirements (Follow Phase 3 Pattern)

For each remaining functional requirement from spec.md, create a new phase with **identical structure to Phase 3**:
- **Phase N: Requirement X - [Name]** (Priority: [P0/P1/P2])
  - N.1 Tests ⚠️ WRITE FIRST → Validate they fail
  - N.2 Implementation → Build after each task
  - N.3 Validation & Commit → Git commit when tests pass

**Parallelization**: Requirements CAN run in parallel if they don't share registers/state/files.

---

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

**Purpose**: Connect all requirements and integrate with Simics infrastructure (after ALL requirement phases complete)

> **Workflow**: Follow "Implementation Workflow" - build after EACH task

**Integration Tasks** (in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`):

- [ ] T[N-4] **Memory interface**: io_memory methods, register bank connection, access pattern validation
- [ ] T[N-3] **Interrupt/signal connections**: signal interfaces, interrupt generation logic, timing requirements
- [ ] T[N-2] **External ports** (if needed): port interfaces, communication protocols, device integration
- [ ] T[N-1] **Checkpointing**: save/restore methods for ALL state variables

**Validation & Commit**:

- [ ] T[N] Run comprehensive tests: `run_simics_test()` → ALL tests PASS (base + requirements)
- [ ] T[N+1] **Git commit**: `"integrate: Integration complete - all tests passing"`

**Checkpoint**: Device fully integrated - all tests passing

---

## Phase N: Polish & Validation

**Purpose**: Final validation, optimization, and documentation

**Parallel Tasks** [P]:

- [ ] T[N+2] [P] **Performance**: Measure overhead, verify <1% impact, optimize hot paths
- [ ] T[N+3] [P] **Code cleanup**: DML grammar compliance, error handling, remove debug code, add comments
- [ ] T[N+4] [P] **Device docs** (`README.md`): Description, register map, interfaces, usage examples
- [ ] T[N+5] [P] **Test docs** (`test/README.md`): Test scenarios, execution instructions, coverage report

**Final Validation & Commit**:

- [ ] T[N+6] Final tests: `run_simics_test()` → Verify no regressions, all scenarios pass
- [ ] T[N+7] **Git commit**: `"polish: Device model complete - validated, optimized, documented"`

**Checkpoint**: Device model complete and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
  - T001 → T002 → T003 → T004

- **Phase 2 (Foundational)**: Depends on Phase 1 (T004) - BLOCKS all requirements
  - T005 → T006 (RAG queries)
  - T007 → T008 || T009 (parallel base tests)
  - T010 → T011 (validation + commit)

- **Phase 3 (Requirement 1)**: Depends on Phase 2 (T011) - First requirement
  - 3.1 Tests: Write tests → Validate they fail
  - 3.2 Implementation: Implement features (tasks can run parallel if different files)
  - 3.3 Validation: Tests pass → Git commit

- **Phase 4+ (Requirements 2, 3, 4, ...)**: Follow Phase 3 pattern
  - Each requirement follows: Tests → Implementation → Validation
  - Each requirement CAN run in parallel if independent (different registers, state, files)
  - Each requirement MUST complete 3.1 (tests) before 3.2 (implementation)

- **Phase N-1 (Integration)**: Depends on ALL requirement phases complete
  - Mostly sequential integration tasks
  - Comprehensive test validation
  - Git commit when all tests pass

- **Phase N (Polish)**: Depends on Integration complete
  - Performance, code review, documentation tasks (all parallel)
  - Final validation → Git commit

### Parallelization Opportunities

- **Phase 2**: Base tests can run parallel (different test files)
- **Requirement Phases**:
  - Within requirement: Implementation tasks parallel if different DML files
  - Across requirements: Independent requirements parallel if no shared resources
- **Integration**: Limited parallelization - mostly sequential
- **Polish**: All tasks parallel (performance, review, docs are independent)

### Critical Path

```
Phase 1 (Setup) → Phase 2 (Foundation) → [BLOCKS ALL]
  ↓
Phase 3 (Req 1): Tests → Implementation → Validation → Commit
  ↓ (OR parallel if independent)
Phase 4+ (Req 2, 3, 4, ...): Tests → Implementation → Validation → Commit
  ↓ (ALL requirements complete)
Phase N-1 (Integration): Connect all → Comprehensive tests → Commit
  ↓
Phase N (Polish): Optimize, document, validate → Commit
```

**Key Principle**: Requirements are independent units that can be developed in parallel if they don't share state/resources.

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
