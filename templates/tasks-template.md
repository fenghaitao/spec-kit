---

des**Prerequisites**:
- **Required**: plan.md, spec.md, [device-name]-registers.xml
- **Optional**: research.md, data-model.md, contracts/, test-scenarios.md

**Tests**: Tests are REQUIRED for Simics device modeling (TDD approach)

**Organization**: Tasks are organized by implementation phases to enable proper dependency management and incremental implementation

## Task Format: `- [ ] [ID] [P?] Description`

- **[ID]**: Task identifier (T001, T002, T003...)
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

--- list template for Simics DML 1.4 device model implementation"
---

# Tasks: [DEVICE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**:
- **Required**: plan.md, spec.md, [device-name]-register.xml
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

**Checkpoint**: Simics project structure ready, DML compiler available

---

## Phase 2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE DML IMPLEMENTATION

**Purpose**: Write tests that define expected device behavior (tests must FAIL initially)

**⚠️ CRITICAL**: These tests MUST be written and MUST FAIL before ANY DML implementation

**Knowledge Acquisition**: On-demand as needed for test writing

### Test Pattern Research (On-Demand RAG)

- [ ] T005 **RAG Query** (if test patterns needed): Execute `perform_rag_query("Simics Python device testing register read write verification patterns", source_type="python", match_count=10)` → document test patterns in research.md

### Contract Tests (from contracts/ if exists)

- [ ] T006 [P] Register access test in `simics-project/modules/DEVICE_NAME/test/test_register_access.py`:
  - Review spec.md for register behaviors
  - Review contracts/register-access.md (if exists) for test contracts
  - Test register read operations
  - Test register write operations
  - Test reset values
  - Test access violations (RO/WO enforcement)
  - Use patterns from T005 RAG query if executed

### Workflow Tests (from test-scenarios.md if exists)

- [ ] T007 [P] Device workflow test in `simics-project/modules/DEVICE_NAME/test/test_device_workflow.py`:
  - Review spec.md for operational behaviors
  - Review test-scenarios.md (if exists) for test scenarios
  - Test device initialization sequence
  - Test normal operation scenarios
  - Test error conditions
  - Test state persistence
  - Use patterns from T005 RAG query if executed

### Validation

- [ ] T008 Validate test environment: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (device not implemented yet)
  - **If tests pass**: Tests are not correctly checking device behavior

**Checkpoint**: All tests written and failing - ready for DML implementation

---

## Phase 3: DML Implementation (ONLY after tests are failing)

**Purpose**: Implement DML device model to make tests pass

**Knowledge Acquisition**: On-demand as needed for each implementation task

**⚠️ CRITICAL BUILD REQUIREMENT**:
Before implementing EACH task in this phase:
1. Review available knowledge sources:
   - research.md (if exists): Architecture decisions, device patterns, example code
   - data-model.md (if exists): Registers, interfaces, DML implementation notes
   - `.specify/memory/DML_Device_Development_Best_Practices.md`: DML patterns and pitfalls
   - `.specify/memory/DML_grammar.md`: DML 1.4 language reference
   - Device skeleton in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`
2. If knowledge is insufficient for the specific task, execute `perform_rag_query()` with targeted question
3. Document RAG results in research.md for future reference
3. Then proceed with implementation

After implementing EACH task:
1. `check_with_dmlc(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` for AI-enhanced diagnostics
2. `build_simics_project(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` to verify compilation

Do NOT mark task done until build succeeds. Do NOT proceed to next task if build fails.

**Note**: Do NOT create separate tasks for check_with_dmlc/build_simics_project calls - they are mandatory validation steps after EVERY implementation task, not standalone tasks.

### Register Implementation (from data-model.md + register XML)

- [ ] T009 [P] Register definitions in `simics-project/modules/DEVICE_NAME/DEVICE_NAME-registers.dml`:
  - Review research.md and data-model.md for register patterns
  - **RAG if needed**: `perform_rag_query("DML register bank definition pattern io_memory", source_type="dml")` → document in research.md
  - Define register bank structure
  - Add register declarations with offsets, sizes, access types
  - Add bit field definitions
  - Set reset values
  - Check_with_dmlc → build

- [ ] T010 Register read/write handlers in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for side-effect patterns
  - Review data-model.md for register side-effects
  - **RAG if needed**: `perform_rag_query("DML register read write callback side effects", source_type="dml")` → document in research.md
  - Implement read callbacks for each register
  - Implement write callbacks for each register
  - Add side-effects from data-model.md
  - Check_with_dmlc → build

### Interface Implementation (from data-model.md)

- [ ] T011 [P] Interface declarations in `simics-project/modules/DEVICE_NAME/interfaces.dml`:
  - Review research.md and data-model.md for interface patterns
  - Review `.specify/memory/DML_grammar.md` for interface syntax
  - **RAG if needed**: `perform_rag_query("DML interface implementation io_memory signal", source_type="dml")` → document in research.md
  - Declare required Simics interfaces (io_memory, signal, etc.)
  - Implement interface methods
  - Add interface contracts from contracts/interface-behavior.md (if exists)
  - Check_with_dmlc → build

### Device Logic (from spec.md operational behaviors)

- [ ] T012 State management in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review spec.md for state transitions and operational behaviors
  - Review data-model.md for internal state variables
  - **RAG if needed**: `perform_rag_query("DML state machine implementation event handling", source_type="dml")` → document in research.md
  - Define internal state variables from data-model.md
  - Implement state transitions
  - Add state validation
  - Check_with_dmlc → build

- [ ] T013 Error handling and validation in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for error handling patterns
  - **RAG if needed**: `perform_rag_query("DML error handling validation logging", source_type="dml")` → document in research.md
  - Add input validation
  - Implement error detection
  - Add logging for debugging
  - Check_with_dmlc → build

**Checkpoint**: Core device functionality implemented - tests should start passing

---

## Phase 4: Integration

**Purpose**: Connect device to Simics infrastructure

**Knowledge Acquisition**: On-demand as needed for integration tasks

**⚠️ CRITICAL BUILD REQUIREMENT**: Same as Phase 3 applies to all integration tasks

- [ ] T014 Memory interface connection in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review research.md and data-model.md for memory mapping patterns
  - **RAG if needed**: `perform_rag_query("DML io_memory interface memory mapped registers", source_type="dml")` → document in research.md
  - Implement io_memory interface methods
  - Connect register bank to memory space
  - Add memory access validation
  - Check_with_dmlc → build

- [ ] T015 Interrupt/signal connections in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review spec.md for interrupt requirements
  - Review data-model.md for signal interface patterns
  - **RAG if needed**: `perform_rag_query("DML signal interface interrupt generation", source_type="dml")` → document in research.md
  - Implement signal interface for interrupt output
  - Add interrupt generation logic
  - Connect to interrupt controller
  - Check_with_dmlc → build

- [ ] T016 External port communications in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review spec.md for external interface requirements
  - **RAG if needed**: `perform_rag_query("DML port interface device communication", source_type="dml")` → document in research.md
  - Implement required port interfaces
  - Add communication protocols
  - Integrate with other devices if needed
  - Check_with_dmlc → build

- [ ] T017 Checkpointing and state serialization in `simics-project/modules/DEVICE_NAME/DEVICE_NAME.dml`:
  - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for checkpoint patterns
  - **RAG if needed**: `perform_rag_query("DML checkpoint save restore state serialization", source_type="dml")` → document in research.md
  - Implement checkpoint save methods
  - Implement checkpoint restore methods
  - Add state validation
  - Check_with_dmlc → build

- [ ] T018 [P] Run comprehensive tests: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test")` ⚠️ ABSOLUTE PATH
  - **Expected**: All tests should PASS
  - **If tests fail**: Review failures and fix implementation

**Checkpoint**: Device fully integrated with Simics - all tests passing

---

## Phase 5: Polish & Validation

**Purpose**: Final validation, optimization, and documentation

- [ ] T019 [P] Performance validation:
  - Measure simulation overhead
  - Verify <1% performance impact (or per requirements)
  - Optimize hot paths if needed

- [ ] T020 [P] Code review and cleanup:
  - Verify DML grammar compliance
  - Check error handling completeness
  - Review logging statements
  - Remove debug code
  - Add code comments

- [ ] T021 [P] Update device documentation in `simics-project/modules/DEVICE_NAME/README.md`:
  - Add device description
  - Document register map
  - Add usage examples
  - Include configuration instructions

- [ ] T022 [P] Update test documentation in `simics-project/modules/DEVICE_NAME/test/README.md`:
  - Document test scenarios
  - Add test execution instructions
  - Include troubleshooting guide

- [ ] T023 Final validation: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project")` ⚠️ ABSOLUTE PATH
  - Run all project tests
  - Verify no regressions
  - Confirm all scenarios pass

**Checkpoint**: Device model complete and validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
  - T001 → T002 → T003 → T004
- **Knowledge Acquisition (Phase 2)**: Depends on Setup (T004) completion - BLOCKS all implementation
  - T005 → T006 → T007 → T008 → T009 (sequential reading)
- **Tests First (Phase 3)**: Depends on Knowledge Acquisition (T009) completion - BLOCKS DML implementation
  - T010 → T011, T012, T013 (parallel after RAG query) → T014
- **DML Implementation (Phase 4)**: Depends on Tests (T014) completion - Core device logic
  - T015 || T017 (parallel - different files)
  - T016 (depends on T015 - same file)
  - T018 → T019 (sequential - same file, state before error handling)
- **Integration (Phase 5)**: Depends on DML Implementation (T019) completion - Simics connectivity
  - T020 → T021 → T022 → T023 → T024 (mostly sequential, building on each other)
- **Polish (Phase 6)**: Depends on Integration (T024) completion - Final validation
  - T025 || T026 || T027 || T028 (all parallel) → T029

### Within Each Phase

- **Setup (Phase 1)**:
  - T001-T003: Sequential (each step depends on previous)
  - T004: Can run after T003 completes

- **Knowledge Acquisition (Phase 2)**:
  - T005-T009: Sequential reading and note-taking
  - Must read research.md (T005) before other documents
  - Must complete all gates before proceeding to Phase 3

- **Tests (Phase 3)**:
  - T010: Must complete first (RAG query for test patterns)
  - T011, T012, T013: Can all run in parallel after T010 (different test files)
  - T014: Validation step after all tests written

- **DML Implementation (Phase 4)**:
  - T015 (registers.dml) and T017 (interfaces.dml): Can run in parallel (different files)
  - T016: Depends on T015 (modifying same file - registers.dml)
  - T018-T019: Sequential (same file - DEVICE_NAME.dml, state management before error handling)

- **Integration (Phase 5)**:
  - T020-T023: Mostly sequential (build on each other, same file)
  - T024: Validation step after all integration complete

- **Polish (Phase 6)**:
  - T025, T026, T027, T028: All can run in parallel (different concerns/files)
  - T029: Final validation after all polish tasks complete

### Parallel Opportunities

- **Setup**: Limited parallelization - mostly sequential setup steps
- **Knowledge**: No parallelization - sequential reading for comprehension
- **Tests**: T011 || T012 || T013 (after T010 completes)
- **DML Implementation**: T015 || T017 (different files: registers.dml and interfaces.dml)
- **Integration**: Limited parallelization - mostly sequential due to dependencies
- **Polish**: T025 || T026 || T027 || T028 (all different concerns)

### Critical Path

The critical path through all phases:
```
T001 → T002 → T003 → T004 (Setup)
  ↓
T005 → T006 → T007 → T008 → T009 (Knowledge - BLOCKS everything)
  ↓
T010 → T011/T012/T013 → T014 (Tests - BLOCKS implementation)
  ↓
T015 → T016 → T018 → T019 (DML Implementation)
  ↓
T020 → T021 → T022 → T023 → T024 (Integration)
  ↓
T025/T026/T027/T028 → T029 (Polish)
```

**Total Minimum Time**: 29 tasks (with some parallelization possible in Phases 3, 4, and 6)

---

## Parallel Example: Test Creation

```bash
# After T010 RAG query completes, launch all test creation together:
Task T011: "Register access test in simics-project/modules/DEVICE_NAME/test/test_register_access.py"
Task T012: "Interface behavior test in simics-project/modules/DEVICE_NAME/test/test_interface_behavior.py"
Task T013: "Device workflow test in simics-project/modules/DEVICE_NAME/test/test_device_workflow.py"
```

---

## Implementation Strategy

### TDD Workflow with On-Demand Knowledge

1. Complete Phase 1: Setup → Simics project ready
2. Complete Phase 2: Tests First → All tests written and FAILING (RAG on-demand for test patterns)
3. **VALIDATE**: Tests must fail before proceeding to implementation
4. Complete Phase 3: DML Implementation → Tests start passing (RAG on-demand per implementation need)
5. Complete Phase 4: Integration → All tests passing (RAG on-demand per integration need)
6. Complete Phase 5: Polish → Final validation

### On-Demand Knowledge Acquisition

For each implementation task (Phase 3 & 4):
1. Review available knowledge sources:
   - research.md (architecture decisions, patterns from planning phase)
   - data-model.md (registers, interfaces, implementation notes)
   - `.specify/memory/DML_Device_Development_Best_Practices.md` (patterns & pitfalls)
   - `.specify/memory/DML_grammar.md` (DML 1.4 reference)
   - Device skeleton (generated structure)
2. If knowledge is sufficient → proceed with implementation
3. If knowledge is insufficient → execute targeted RAG query → document results in research.md
4. Implement the task using available knowledge
5. Validate: check_with_dmlc → build_simics_project
6. Only mark done when build succeeds
7. Git commit the change

---

## Notes

- [P] tasks = different files, no dependencies
- Verify tests fail before implementing (TDD)
- RAG queries are on-demand - only execute when knowledge is insufficient
- Run check_with_dmlc + build after EVERY implementation task
- Document RAG results in research.md for reuse
- Commit after each task or logical group
- Always use absolute paths for MCP tools (SSE transport requirement)
- Do NOT create separate tasks for check_with_dmlc/build_simics_project (they are validation steps)
- Stop at any checkpoint to validate phase independently
