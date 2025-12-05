---
description: "Task list for Simics Watchdog Timer device implementation based on ARM PrimeCell specification."
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
---

# Tasks: Simics Watchdog Timer Device

**Input**: Design documents from `/specs/001-nfs-site-disks/`
**Prerequisites**:
- **Required**: plan.md, spec.md, simics-watchdog-timer-register.xml
- **Optional**: research.md, data-model.md, contracts/, test-scenarios.md
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

- **Simics Project Structure**: `simics-project/modules/watchdog-timer/` at repository root
- **DML Files**: `watchdog-timer.dml`, `registers.dml`(optional), `interfaces.dml`(optional) in module directory
- **Test Files**: `s-*.py` in `simics-project/modules/watchdog-timer/test/` directory
  - **NOTE**: Simics test scripts should start with `s-` prefix (e.g., `s-watchdog-timer.py`, `s-register-access.py`)

**⚠️ CRITICAL - MCP Tool Paths (SSE Transport)**:
- **ALWAYS use ABSOLUTE paths** for MCP tools
- **NEVER use relative paths** like `"./simics-project"` or `"../project"`
- **WHY**: SSE transport MCP servers run in different process/directory context
- **HOW**: Use workspace root to construct: `"/full/path/to/workspace/simics-project"`
- **Example**: `create_simics_project(project_path="/home/user/workspace/simics-project")`

## Phase 1: Simics Project Setup

**Purpose**: Initialize Simics project structure and verify environment

- [X] T001 Verify Simics connection: `get_simics_version()`
- [X] T002 Create Simics project: `create_simics_project(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project")` ⚠️ ABSOLUTE PATH
- [X] T003 Generate DML register and dummy device definitions: `generate_dml_registers(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", device_name="watchdog-timer", reg_xml="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/specs/001-nfs-site-disks/simics-watchdog-timer-register.xml")` ⚠️ ABSOLUTE PATH
- [X] T004 **MANDATORY: Git commit Phase 1 completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/
  git commit -m "setup: Phase 1 complete - Simics project setup (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Simics project structure ready, DML compiler available, Phase 1 committed

---

## Phase 2: Foundational (Knowledge & Base Infrastructure) ⚠️ BLOCKS ALL REQUIREMENTS

**Purpose**: Establish foundational knowledge and base test infrastructure that ALL requirements depend on

**⚠️ CRITICAL**: No requirement implementation can begin until this phase is complete

### Knowledge Acquisition

- [X] T005 Review design documents for implementation context:
  - Read spec.md Hardware Specification (register map, external interfaces, operational model)
  - Read spec.md Functional Requirements (all requirements overview)
  - Read data-model.md (if exists): Registers, interfaces, state variables, DML patterns
  - Read test-scenarios.md (if exists): Test coverage planning
  - Read .specify/memory/DML_Device_Development_Best_Practices.md for Simics DML device modeling best practices
  - Read .specify/memory/Simics_Model_Test_Best_Practices.md for Simics model test best practices
  - Document key findings and patterns in research.md

- [X] T006 **RAG Query** (if DML patterns needed): Execute `perform_rag_query("DML device modeling common patterns register bank interface signal event watchdog timer", source_type="dml", match_count=10)` → document patterns in research.md

### Base Test Infrastructure

> **NOTE**: These foundational tests validate infrastructure used by ALL requirements

- [X] T007 [P] **Review test best practices**: Read `.specify/memory/Simics_Model_Test_Best_Practices.md` for test patterns, structure, and common issues → document in research.md

- [X] T008 [P] Base register access test in `simics-project/modules/watchdog-timer/test/s-register-access.py`:
  - **Use patterns from Simics_Model_Test_Best_Practices.md**
  - Review spec.md Hardware Spec register map for ALL registers (functional + ID + configuration)
  - Review contracts/register-access.md (if exists) for test contracts
  - Test register read/write operations for all register types
  - Test reset values for all registers
  - Test access violations (RO/WO enforcement, protection mechanisms)

- [X] T009 [P] Base memory interface test in `simics-project/modules/watchdog-timer/test/s-memory-interface.py`:
  - **Use patterns from Simics_Model_Test_Best_Practices.md**
  - Review spec.md Hardware Spec Memory Interface Requirements
  - Test access width validation (per spec requirements)
  - Test alignment validation (per spec requirements)
  - Test burst access handling (per spec requirements)
  - Test error responses for invalid access patterns
  - Use patterns from T007 RAG query if executed

- [X] T010 Validate base test environment: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (device not implemented yet)
  - **If tests pass**: Tests are not correctly checking device behavior

- [X] T011 **MANDATORY: Git commit Phase 2 completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/modules/watchdog-timer/test/
  git add research.md
  git commit -m "foundation: Phase 2 complete - Knowledge acquired and base tests written (TDD) (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Foundation established - knowledge documented, base infrastructure tests written and failing, ready for requirement implementation

---

## Phase 3: Timer Functionality Requirements (Priority: P0)

**Goal**: Implement the core watchdog timer functionality including 32-bit decrementing counter that decrements based on clock divider setting, reload mechanisms, and counter behavior.

**Maps to**:
- spec.md: Functional Requirements (FUNC-001 to FUNC-004)
- test-scenarios.md: Scenario S001: Basic Timer Operation Test, Scenario S009: Counter Reload Test
- data-model.md: Timer State Variables, Counter State, Counter Value State

> **Workflow**: Follow "Implementation Workflow" section above (TDD cycle + per-task build validation)

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 3.1 Tests for Timer Functionality Requirements ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] Test for Timer Functionality in `simics-project/modules/watchdog-timer/test/s-timer-functionality.py`:
  - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and structure
  - Review spec.md Functional Requirements (FUNC-001 to FUNC-004) acceptance criteria
  - Review test-scenarios.md for relevant scenarios (S001, S009)
  - Review data-model.md for registers/interfaces involved (WDOGLOAD, WDOGVALUE, WDOGCONTROL)
  - **Test acceptance criterion 1**: Verify timer decrements at rate determined by step_value field in WDOGCONTROL
  - **Test acceptance criterion 2**: Verify timer reloads from WDOGLOAD when INTEN transitions from 0 to 1
  - **Test acceptance criterion 3**: Verify timer reloads from WDOGLOAD when WDOGINTCLR is written
  - **Test acceptance criterion 4**: Verify counter returns current value via WDOGVALUE register without affecting counter
  - **RAG if needed**: `perform_rag_query("DML timer counter implementation patterns", source_type="python")` → document in research.md

- [X] T013 Validate Timer Functionality tests fail: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)
  - **If tests pass**: Tests are not correctly checking requirement

---

### 3.2 Implementation for Timer Functionality Requirements

> **Goal**: Implement timer functionality to pass Timer Functionality tests (T012)

- [X] T014 [P] Implement timer counter state in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for timer details
  - Review data-model.md for timer implementation notes (counter_start_time, counter_start_value, timer_enabled)
  - **RAG if needed**: `perform_rag_query("DML timer counter lazy evaluation pattern", source_type="dml")` → document in research.md
  - Implement saved variables for timer state (counter_start_time, counter_start_value, timer_enabled)
  - Implement method to calculate current counter value based on elapsed time
  - Check_with_dmlc → build

- [X] T015 [P] Implement WDOGVALUE read behavior in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGVALUE register behavior
  - Review data-model.md for register side effects
  - **RAG if needed**: `perform_rag_query("DML register read behavior with side effects", source_type="dml")` → document in research.md
  - Implement custom read method that returns current counter value without changing counter
  - Check_with_dmlc → build

- [X] T016 [P] Implement WDOGLOAD write behavior in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGLOAD register behavior
  - Review data-model.md for register side effects
  - **RAG if needed**: `perform_rag_query("DML register write behavior with state updates", source_type="dml")` → document in research.md
  - Implement custom write method that stores reload value
  - Check_with_dmlc → build

- [X] T017 [P] Implement WDOGCONTROL INTEN side-effect in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for INTEN bit behavior
  - Review data-model.md for register side effects
  - **RAG if needed**: `perform_rag_query("DML register side effects on bit transitions", source_type="dml")` → document in research.md
  - Implement custom write method that handles INTEN transition from 0 to 1 to reload counter
  - Check_with_dmlc → build

- [X] T018 [P] Implement WDOGINTCLR reload behavior in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGINTCLR register behavior
  - Review data-model.md for register side effects
  - **RAG if needed**: `perform_rag_query("DML write-only register with side effects", source_type="dml")` → document in research.md
  - Implement custom write method that reloads counter from WDOGLOAD
  - Check_with_dmlc → build

---

### 3.3 Validation & Commit

> **ITERATIVE DEBUGGING GUIDE**: Tests should PASS after implementation. If not, follow this cycle:

- [X] T019 Validate Timer Functionality tests pass: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS (all acceptance criteria satisfied)
  - **If tests FAIL**: Follow iterative debugging workflow:
    1. **Analyze Failure**: Read test output → identify which acceptance criterion failed
    2. **Review Requirement**: Check spec.md Functional Requirements → verify expected behavior matches test assumptions
    3. **Determine Root Cause**: Is it DML implementation bug OR test bug?
       - **If DML is wrong**: Implementation doesn't match spec → fix DML code
       - **If Test is wrong**: Test has incorrect assumptions/assertions → fix test code
       - **If Spec is ambiguous**: Document in research.md → clarify with team
    4. **Fix Code** (DML or Test):
       - **Fix DML**: Edit `simics-project/modules/watchdog-timer/watchdog-timer.dml`
         - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for patterns
         - Common DML issues: timing bugs, state machine errors, register side-effects, signal generation
         - RAG if needed: `perform_rag_query("DML timer counter implementation fix", source_type="dml")` → document in research.md
       - **Fix Test**: Edit `simics-project/modules/watchdog-timer/test/s-timer-functionality.py`
         - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and debugging
         - Verify test logic matches spec.md acceptance criteria
         - Common test issues: incorrect assertions, wrong expected values, missing setup/teardown, timing assumptions
         - RAG if needed: `perform_rag_query("timer functionality test debugging", source_type="python")` → document in research.md
    5. **Rebuild** (if DML changed): `check_with_dmlc()` → `build_simics_project()` → verify compilation
    6. **Retest**: `run_simics_test()` again → check if test passes
    7. **Repeat**: Continue cycle until ALL tests pass
  - **Success Criteria**: ALL test cases pass, no errors, no warnings

- [X] T020 **MANDATORY: Git commit Timer Functionality completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/modules/watchdog-timer/
  git commit -m "implement: Timer Functionality Requirements complete - Core watchdog timer implemented and tested (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Timer Functionality Requirements complete and independently testable - can proceed to next requirement

---

## Phase 4: Interrupt and Reset Requirements (Priority: P0)

**Goal**: Implement interrupt and reset generation functionality including interrupt assertion when counter reaches zero with INTEN=1, reset assertion when counter reaches zero again with RESEN=1, interrupt clearing, and status register reporting.

**Maps to**:
- spec.md: Functional Requirements (FUNC-005 to FUNC-009)
- test-scenarios.md: Scenario S002: Interrupt Generation Test, Scenario S003: Interrupt Clear Test, Scenario S004: Reset Generation Test, Scenario S008: Register Status Test
- data-model.md: Interrupt State Variables (interrupt_pending, reset_pending)

> **Workflow**: Follow "Implementation Workflow" section above (TDD cycle + per-task build validation)

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 4.1 Tests for Interrupt and Reset Requirements ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T021 [P] Test for Interrupt and Reset in `simics-project/modules/watchdog-timer/test/s-interrupt-reset-functionality.py`:
  - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and structure
  - Review spec.md Functional Requirements (FUNC-005 to FUNC-009) acceptance criteria
  - Review test-scenarios.md for relevant scenarios (S002, S003, S004, S008)
  - Review data-model.md for registers/interfaces involved (WDOGRIS, WDOGMIS, WDOGINTCLR, signal interfaces)
  - **Test acceptance criterion 1**: Verify wdogint signal asserts when counter reaches zero and INTEN=1 in WDOGCONTROL
  - **Test acceptance criterion 2**: Verify WDOGRIS[0] sets to 1 when counter reaches zero and INTEN=1
  - **Test acceptance criterion 3**: Verify wdogres signal asserts when counter reaches zero again while interrupt asserted and RESEN=1
  - **Test acceptance criterion 4**: Verify writing to WDOGINTCLR clears wdogint signal and reloads counter
  - **Test acceptance criterion 5**: Verify WDOGMIS[0] reflects logical AND of WDOGRIS[0] and WDOGCONTROL[0]
  - **RAG if needed**: `perform_rag_query("DML interrupt and reset signal handling in tests", source_type="python")` → document in research.md

- [ ] T022 Validate Interrupt and Reset tests fail: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)
  - **If tests pass**: Tests are not correctly checking requirement

---

### 4.2 Implementation for Interrupt and Reset Requirements

> **Goal**: Implement interrupt and reset functionality to pass Interrupt and Reset tests (T021)

- [X] T023 [P] Implement interrupt state management in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for interrupt behavior
  - Review data-model.md for interrupt state variables (interrupt_pending, reset_pending)
  - **RAG if needed**: `perform_rag_query("DML signal interface implementation for interrupts", source_type="dml")` → document in research.md
  - Implement saved variables for interrupt_pending and reset_pending state
  - Implement signal interface connections for wdogint and wdogres
  - Check_with_dmlc → build

- [X] T024 [P] Implement WDOGRIS register behavior in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGRIS register behavior
  - Review data-model.md for register implementation notes
  - **RAG if needed**: `perform_rag_query("DML read-only register with dynamic value", source_type="dml")` → document in research.md
  - Implement custom read method that returns raw interrupt status
  - Check_with_dmlc → build

- [X] T025 [P] Implement WDOGMIS register behavior in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGMIS register behavior
  - Review data-model.md for register implementation notes
  - **RAG if needed**: `perform_rag_query("DML masked status register implementation", source_type="dml")` → document in research.md
  - Implement custom read method that returns logical AND of WDOGRIS[0] and WDOGCONTROL[0]
  - Check_with_dmlc → build

- [X] T026 [P] Implement timeout event and interrupt generation in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for timeout behavior
  - Review data-model.md for interrupt generation patterns
  - **RAG if needed**: `perform_rag_query("DML event-based timer timeout handling", source_type="dml")` → document in research.md
  - Implement event scheduling when timer reaches zero with INTEN=1
  - Implement interrupt signal assertion and state updates
  - Check_with_dmlc → build

- [X] T027 [P] Implement reset generation logic in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for reset behavior
  - Review data-model.md for reset state variables
  - **RAG if needed**: `perform_rag_query("DML reset signal generation for watchdog devices", source_type="dml")` → document in research.md
  - Implement logic for second timeout with RESEN=1 to generate system reset
  - Check_with_dmlc → build

- [X] T028 [P] Implement WDOGINTCLR interrupt clearing in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGINTCLR register behavior
  - Review data-model.md for interrupt clearing patterns
  - **RAG if needed**: `perform_rag_query("DML interrupt clearing implementation", source_type="dml")` → document in research.md
  - Implement custom write method that clears interrupt state and reloads counter
  - Check_with_dmlc → build

---

### 4.3 Validation & Commit

> **ITERATIVE DEBUGGING GUIDE**: Tests should PASS after implementation. If not, follow this cycle:

- [X] T029 Validate Interrupt and Reset tests pass: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS (all acceptance criteria satisfied)
  - **If tests FAIL**: Follow iterative debugging workflow:
    1. **Analyze Failure**: Read test output → identify which acceptance criterion failed
    2. **Review Requirement**: Check spec.md Functional Requirements → verify expected behavior matches test assumptions
    3. **Determine Root Cause**: Is it DML implementation bug OR test bug?
       - **If DML is wrong**: Implementation doesn't match spec → fix DML code
       - **If Test is wrong**: Test has incorrect assumptions/assertions → fix test code
       - **If Spec is ambiguous**: Document in research.md → clarify with team
    4. **Fix Code** (DML or Test):
       - **Fix DML**: Edit `simics-project/modules/watchdog-timer/watchdog-timer.dml`
         - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for patterns
         - Common DML issues: signal timing, state machine errors, register side-effects, interrupt generation
         - RAG if needed: `perform_rag_query("DML signal interface implementation debugging", source_type="dml")` → document in research.md
       - **Fix Test**: Edit `simics-project/modules/watchdog-timer/test/s-interrupt-reset-functionality.py`
         - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and debugging
         - Verify test logic matches spec.md acceptance criteria
         - Common test issues: incorrect assertions, wrong expected values, missing setup/teardown, timing assumptions
         - RAG if needed: `perform_rag_query("interrupt and reset test debugging", source_type="python")` → document in research.md
    5. **Rebuild** (if DML changed): `check_with_dmlc()` → `build_simics_project()` → verify compilation
    6. **Retest**: `run_simics_test()` again → check if test passes
    7. **Repeat**: Continue cycle until ALL tests pass
  - **Success Criteria**: ALL test cases pass, no errors, no warnings

- [X] T030 **MANDATORY: Git commit Interrupt and Reset completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/modules/watchdog-timer/
  git commit -m "implement: Interrupt and Reset Requirements complete - Interrupt and reset generation implemented and tested (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Interrupt and Reset Requirements complete and independently testable - can proceed to next requirement

---

## Phase 5: Clock Divider Requirements (Priority: P1)

**Goal**: Implement clock divider functionality that determines timer decrement rate based on step_value field in WDOGCONTROL register.

**Maps to**:
- spec.md: Functional Requirements (FUNC-015 to FUNC-020)
- test-scenarios.md: Scenario S006: Clock Divider Test
- data-model.md: Timer State Variables and clock divider implementation patterns

> **Workflow**: Follow "Implementation Workflow" section above (TDD cycle + per-task build validation)

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 5.1 Tests for Clock Divider Requirements ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T031 [P] Test for Clock Divider in `simics-project/modules/watchdog-timer/test/s-clock-divider.py`:
  - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and structure
  - Review spec.md Functional Requirements (FUNC-015 to FUNC-020) acceptance criteria
  - Review test-scenarios.md for relevant scenarios (S006)
  - Review data-model.md for registers involved (WDOGCONTROL)
  - **Test acceptance criterion 1**: Verify clock divider setting in WDOGCONTROL[4:2] determines timer decrement rate
  - **Test acceptance criterion 2**: Verify when step_value is 000, timer decrements at full clock rate (÷1)
  - **Test acceptance criterion 3**: Verify when step_value is 001, timer decrements at half clock rate (÷2)
  - **Test acceptance criterion 4**: Verify when step_value is 010, timer decrements at quarter clock rate (÷4)
  - **Test acceptance criterion 5**: Verify when step_value is 011, timer decrements at eighth clock rate (÷8)
  - **Test acceptance criterion 6**: Verify when step_value is 100, timer decrements at sixteenth clock rate (÷16)
  - **RAG if needed**: `perform_rag_query("DML clock divider implementation testing", source_type="python")` → document in research.md

- [ ] T032 Validate Clock Divider tests fail: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)
  - **If tests pass**: Tests are not correctly checking requirement

---

### 5.2 Implementation for Clock Divider Requirements

> **Goal**: Implement clock divider functionality to pass Clock Divider tests (T031)

- [X] T033 [P] Implement clock divider state in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for clock divider behavior
  - Review data-model.md for timer implementation notes
  - **RAG if needed**: `perform_rag_query("DML clock divider implementation with prescaler", source_type="dml")` → document in research.md
  - Implement state variable to track current step_value setting
  - Implement method to calculate prescaler based on step_value field
  - Check_with_dmlc → build

- [X] T034 [P] Implement WDOGCONTROL step_value field handling in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for step_value field behavior
  - Review data-model.md for register field implementation
  - **RAG if needed**: `perform_rag_query("DML multi-bit field handling in registers", source_type="dml")` → document in research.md
  - Implement custom write method for step_value field in WDOGCONTROL
  - Update timer behavior to use new prescaler value
  - Check_with_dmlc → build

- [X] T035 [P] Integrate prescaler into timer calculation in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for timer behavior with prescaler
  - Review data-model.md for timer implementation notes
  - **RAG if needed**: `perform_rag_query("DML timer calculation with prescaler factor", source_type="dml")` → document in research.md
  - Update timer calculation method to incorporate prescaler value
  - Ensure timer decrement rate matches expected division factor
  - Check_with_dmlc → build

---

### 5.3 Validation & Commit

> **ITERATIVE DEBUGGING GUIDE**: Tests should PASS after implementation. If not, follow this cycle:

- [X] T036 Validate Clock Divider tests pass: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS (all acceptance criteria satisfied)
  - **If tests FAIL**: Follow iterative debugging workflow:
    1. **Analyze Failure**: Read test output → identify which acceptance criterion failed
    2. **Review Requirement**: Check spec.md Functional Requirements → verify expected behavior matches test assumptions
    3. **Determine Root Cause**: Is it DML implementation bug OR test bug?
       - **If DML is wrong**: Implementation doesn't match spec → fix DML code
       - **If Test is wrong**: Test has incorrect assumptions/assertions → fix test code
       - **If Spec is ambiguous**: Document in research.md → clarify with team
    4. **Fix Code** (DML or Test):
       - **Fix DML**: Edit `simics-project/modules/watchdog-timer/watchdog-timer.dml`
         - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for patterns
         - Common DML issues: prescaler calculation errors, timing issues, state updates
         - RAG if needed: `perform_rag_query("DML clock divider implementation debugging", source_type="dml")` → document in research.md
       - **Fix Test**: Edit `simics-project/modules/watchdog-timer/test/s-clock-divider.py`
         - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and debugging
         - Verify test logic matches spec.md acceptance criteria
         - Common test issues: timing measurements, incorrect expected rates, setup/teardown problems
         - RAG if needed: `perform_rag_query("clock divider test debugging", source_type="python")` → document in research.md
    5. **Rebuild** (if DML changed): `check_with_dmlc()` → `build_simics_project()` → verify compilation
    6. **Retest**: `run_simics_test()` again → check if test passes
    7. **Repeat**: Continue cycle until ALL tests pass
  - **Success Criteria**: ALL test cases pass, no errors, no warnings

- [X] T037 **MANDATORY: Git commit Clock Divider completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/modules/watchdog-timer/
  git commit -m "implement: Clock Divider Requirements complete - Clock divider functionality implemented and tested (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Clock Divider Requirements complete and independently testable - can proceed to next requirement

---

## Phase 6: Lock Protection Requirements (Priority: P1)

**Goal**: Implement lock protection mechanism that enables/disables write access to registers using the magic unlock value 0x1ACCE551.

**Maps to**:
- spec.md: Functional Requirements (FUNC-021 to FUNC-024)
- test-scenarios.md: Scenario S005: Lock Protection Test
- data-model.md: Lock State Variables (locked) and protection patterns

> **Workflow**: Follow "Implementation Workflow" section above (TDD cycle + per-task build validation)

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 6.1 Tests for Lock Protection Requirements ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T038 [P] Test for Lock Protection in `simics-project/modules/watchdog-timer/test/s-lock-protection.py`:
  - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and structure
  - Review spec.md Functional Requirements (FUNC-021 to FUNC-024) acceptance criteria
  - Review test-scenarios.md for relevant scenarios (S005)
  - Review data-model.md for registers involved (WDOGLOCK)
  - **Test acceptance criterion 1**: Verify writing 0x1ACCE551 to WDOGLOCK unlocks write access to other registers
  - **Test acceptance criterion 2**: Verify writing any value other than 0x1ACCE551 to WDOGLOCK locks write access to other registers
  - **Test acceptance criterion 3**: Verify WDOGLOCK read returns 0x0 when unlocked, 0x1 when locked
  - **Test acceptance criterion 4**: Verify locked state prevents writes to all registers except WDOGLOCK itself
  - **RAG if needed**: `perform_rag_query("DML lock protection mechanism testing", source_type="python")` → document in research.md

- [X] T039 Validate Lock Protection tests fail: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)
  - **If tests pass**: Tests are not correctly checking requirement

---

### 6.2 Implementation for Lock Protection Requirements

> **Goal**: Implement lock protection functionality to pass Lock Protection tests (T038)

- [X] T040 [P] Implement lock state management in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for lock behavior
  - Review data-model.md for lock implementation notes
  - **RAG if needed**: `perform_rag_query("DML lock protection implementation patterns", source_type="dml")` → document in research.md
  - Implement saved variable for lock state (locked boolean)
  - Implement method to check if register writes are allowed
  - Check_with_dmlc → build

- [X] T041 [P] Implement WDOGLOCK register behavior in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGLOCK register behavior
  - Review data-model.md for lock register implementation
  - **RAG if needed**: `perform_rag_query("DML lock register implementation with magic number", source_type="dml")` → document in research.md
  - Implement custom read method that returns lock status (0x0 for unlocked, 0x1 for locked)
  - Implement custom write method that updates lock state based on magic number
  - Ensure WDOGLOCK register remains writable regardless of lock state
  - Check_with_dmlc → build

- [X] T042 [P] Implement write protection for all registers in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for lock protection behavior
  - Review data-model.md for lock implementation notes
  - **RAG if needed**: `perform_rag_query("DML register write protection based on lock state", source_type="dml")` → document in research.md
  - Implement write protection checks in all writable registers
  - Ensure write attempts to protected registers are silently ignored when locked
  - Keep WDOGLOCK always writable
  - Check_with_dmlc → build

---

### 6.3 Validation & Commit

> **ITERATIVE DEBUGGING GUIDE**: Tests should PASS after implementation. If not, follow this cycle:

- [X] T043 Validate Lock Protection tests pass: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS (all acceptance criteria satisfied)
  - **If tests FAIL**: Follow iterative debugging workflow:
    1. **Analyze Failure**: Read test output → identify which acceptance criterion failed
    2. **Review Requirement**: Check spec.md Functional Requirements → verify expected behavior matches test assumptions
    3. **Determine Root Cause**: Is it DML implementation bug OR test bug?
       - **If DML is wrong**: Implementation doesn't match spec → fix DML code
       - **If Test is wrong**: Test has incorrect assumptions/assertions → fix test code
       - **If Spec is ambiguous**: Document in research.md → clarify with team
    4. **Fix Code** (DML or Test):
       - **Fix DML**: Edit `simics-project/modules/watchdog-timer/watchdog-timer.dml`
         - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for patterns
         - Common DML issues: lock state not persisting, write protection not working, WDOGLOCK not always writable
         - RAG if needed: `perform_rag_query("DML lock protection implementation debugging", source_type="dml")` → document in research.md
       - **Fix Test**: Edit `simics-project/modules/watchdog-timer/test/s-lock-protection.py`
         - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and debugging
         - Verify test logic matches spec.md acceptance criteria
         - Common test issues: incorrect lock status checks, wrong unlock values, setup/teardown problems
         - RAG if needed: `perform_rag_query("lock protection test debugging", source_type="python")` → document in research.md
    5. **Rebuild** (if DML changed): `check_with_dmlc()` → `build_simics_project()` → verify compilation
    6. **Retest**: `run_simics_test()` again → check if test passes
    7. **Repeat**: Continue cycle until ALL tests pass
  - **Success Criteria**: ALL test cases pass, no errors, no warnings

- [X] T044 **MANDATORY: Git commit Lock Protection completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/modules/watchdog-timer/
  git commit -m "implement: Lock Protection Requirements complete - Lock protection mechanism implemented and tested (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Lock Protection Requirements complete and independently testable - can proceed to next requirement

---

## Phase 7: Integration Test Mode Requirements (Priority: P2)

**Goal**: Implement integration test mode that allows direct control of output signals when enabled.

**Maps to**:
- spec.md: Functional Requirements (FUNC-025 to FUNC-029)
- test-scenarios.md: Scenario S007: Integration Test Mode Test
- data-model.md: Test Mode State Variables (test_mode) and integration test patterns

> **Workflow**: Follow "Implementation Workflow" section above (TDD cycle + per-task build validation)

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 7.1 Tests for Integration Test Mode Requirements ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T045 [P] Test for Integration Test Mode in `simics-project/modules/watchdog-timer/test/s-integration-test-mode.py`:
  - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and structure
  - Review spec.md Functional Requirements (FUNC-025 to FUNC-029) acceptance criteria
  - Review test-scenarios.md for relevant scenarios (S007)
  - Review data-model.md for registers involved (WDOGITCR, WDOGITOP)
  - **Test acceptance criterion 1**: Verify when WDOGITCR[0]=1, device enters integration test mode
  - **Test acceptance criterion 2**: Verify in integration test mode, WDOGITOP register directly controls wdogint and wdogres outputs
  - **Test acceptance criterion 3**: Verify when WDOGITCR[0]=0, device operates in normal mode
  - **Test acceptance criterion 4**: Verify WDOGITOP[1] controls wdogint output in integration test mode
  - **Test acceptance criterion 5**: Verify WDOGITOP[0] controls wdogres output in integration test mode
  - **RAG if needed**: `perform_rag_query("DML integration test mode implementation testing", source_type="python")` → document in research.md

- [ ] T046 Validate Integration Test Mode tests fail: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)
  - **If tests pass**: Tests are not correctly checking requirement

---

### 7.2 Implementation for Integration Test Mode Requirements

> **Goal**: Implement integration test mode functionality to pass Integration Test Mode tests (T045)

- [ ] T047 [P] Implement test mode state management in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for test mode behavior
  - Review data-model.md for test mode implementation notes
  - **RAG if needed**: `perform_rag_query("DML test mode state management patterns", source_type="dml")` → document in research.md
  - Implement saved variable for test mode state (test_mode boolean)
  - Implement method to check current operational mode (test vs normal)
  - Check_with_dmlc → build

- [X] T048 [P] Implement WDOGITCR register behavior in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGITCR register behavior
  - Review data-model.md for integration test register implementation
  - **RAG if needed**: `perform_rag_query("DML integration test control register implementation", source_type="dml")` → document in research.md
  - Implement custom read method for integration test control register
  - Implement custom write method that updates test mode state
  - Check_with_dmlc → build

- [X] T049 [P] Implement WDOGITOP register behavior in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for WDOGITOP register behavior
  - Review data-model.md for integration test register implementation
  - **RAG if needed**: `perform_rag_query("DML integration test output register implementation", source_type="dml")` → document in research.md
  - Implement custom write method that directly controls output signals in test mode
  - Implement logic to only affect signals when in test mode
  - Check_with_dmlc → build

- [ ] T050 [P] Implement test mode behavioral changes in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for test mode operation
  - Review data-model.md for test mode implementation notes
  - **RAG if needed**: `perform_rag_query("DML test mode behavioral changes implementation", source_type="dml")` → document in research.md
  - Implement conditional logic to suspend normal timer operation when in test mode
  - Implement conditional logic for timer and interrupt operations based on test mode
  - Check_with_dmlc → build

---

### 7.3 Validation & Commit

> **ITERATIVE DEBUGGING GUIDE**: Tests should PASS after implementation. If not, follow this cycle:

- [ ] T051 Validate Integration Test Mode tests pass: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS (all acceptance criteria satisfied)
  - **If tests FAIL**: Follow iterative debugging workflow:
    1. **Analyze Failure**: Read test output → identify which acceptance criterion failed
    2. **Review Requirement**: Check spec.md Functional Requirements → verify expected behavior matches test assumptions
    3. **Determine Root Cause**: Is it DML implementation bug OR test bug?
       - **If DML is wrong**: Implementation doesn't match spec → fix DML code
       - **If Test is wrong**: Test has incorrect assumptions/assertions → fix test code
       - **If Spec is ambiguous**: Document in research.md → clarify with team
    4. **Fix Code** (DML or Test):
       - **Fix DML**: Edit `simics-project/modules/watchdog-timer/watchdog-timer.dml`
         - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for patterns
         - Common DML issues: mode switching logic, signal control, timer suspension
         - RAG if needed: `perform_rag_query("DML integration test mode implementation debugging", source_type="dml")` → document in research.md
       - **Fix Test**: Edit `simics-project/modules/watchdog-timer/test/s-integration-test-mode.py`
         - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and debugging
         - Verify test logic matches spec.md acceptance criteria
         - Common test issues: timing in test mode, signal monitoring, mode transition validation
         - RAG if needed: `perform_rag_query("integration test mode test debugging", source_type="python")` → document in research.md
    5. **Rebuild** (if DML changed): `check_with_dmlc()` → `build_simics_project()` → verify compilation
    6. **Retest**: `run_simics_test()` again → check if test passes
    7. **Repeat**: Continue cycle until ALL tests pass
  - **Success Criteria**: ALL test cases pass, no errors, no warnings

- [ ] T052 **MANDATORY: Git commit Integration Test Mode completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/modules/watchdog-timer/
  git commit -m "implement: Integration Test Mode Requirements complete - Integration test functionality implemented and tested (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Integration Test Mode Requirements complete and independently testable - can proceed to next requirement

---

## Phase 8: Identification Requirements (Priority: P2)

**Goal**: Implement PrimeCell and peripheral identification registers that return the correct constant values for device identification.

**Maps to**:
- spec.md: Functional Requirements (FUNC-030, FUNC-031) and Register Access Requirements
- test-scenarios.md: Scenario S011: PrimeCell ID Registers Test
- data-model.md: ID Registers implementation section

> **Workflow**: Follow "Implementation Workflow" section above (TDD cycle + per-task build validation)

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 8.1 Tests for Identification Requirements ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T053 [P] Test for Identification Registers in `simics-project/modules/watchdog-timer/test/s-identification-registers.py`:
  - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and structure
  - Review spec.md Functional Requirements (FUNC-030, FUNC-031) acceptance criteria
  - Review test-scenarios.md for relevant scenarios (S011)
  - Review data-model.md for registers involved (all ID registers)
  - **Test acceptance criterion 1**: Verify WDOGPERIPHID0 register returns 0x24
  - **Test acceptance criterion 2**: Verify WDOGPERIPHID1 register returns 0xB8
  - **Test acceptance criterion 3**: Verify WDOGPERIPHID2 register returns 0x1B
  - **Test acceptance criterion 4**: Verify WDOGPERIPHID3 register returns 0x00
  - **Test acceptance criterion 5**: Verify WDOGPERIPHID4 register returns 0x04
  - **Test acceptance criterion 6**: Verify WDOGPERIPHID5-7 registers return 0x00
  - **Test acceptance criterion 7**: Verify WDOGPCELLID0 register returns 0x0D
  - **Test acceptance criterion 8**: Verify WDOGPCELLID1 register returns 0xF0
  - **Test acceptance criterion 9**: Verify WDOGPCELLID2 register returns 0x05
  - **Test acceptance criterion 10**: Verify WDOGPCELLID3 register returns 0xB1
  - **Test acceptance criterion 11**: Verify ID registers are read-only and ignore write attempts
  - **RAG if needed**: `perform_rag_query("DML identification register testing", source_type="python")` → document in research.md

- [ ] T054 Validate Identification Registers tests fail: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)
  - **If tests pass**: Tests are not correctly checking requirement

---

### 8.2 Implementation for Identification Requirements

> **Goal**: Implement identification register functionality to pass Identification Registers tests (T053)

- [X] T055 [P] Implement PrimeCell ID registers in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for ID register values
  - Review data-model.md for ID register implementation notes
  - **RAG if needed**: `perform_rag_query("DML PrimeCell identification register implementation", source_type="dml")` → document in research.md
  - Implement all WDOGPCELLID0-3 registers with correct constant values
  - Ensure registers are read-only
  - Check_with_dmlc → build

- [X] T056 [P] Implement Peripheral ID registers in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for ID register values
  - Review data-model.md for ID register implementation notes
  - **RAG if needed**: `perform_rag_query("DML peripheral ID register implementation", source_type="dml")` → document in research.md
  - Implement all WDOGPERIPHID0-7 registers with correct constant values
  - Ensure registers are read-only
  - Check_with_dmlc → build

---

### 8.3 Validation & Commit

> **ITERATIVE DEBUGGING GUIDE**: Tests should PASS after implementation. If not, follow this cycle:

- [ ] T057 Validate Identification Registers tests pass: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS (all acceptance criteria satisfied)
  - **If tests FAIL**: Follow iterative debugging workflow:
    1. **Analyze Failure**: Read test output → identify which acceptance criterion failed
    2. **Review Requirement**: Check spec.md Functional Requirements → verify expected behavior matches test assumptions
    3. **Determine Root Cause**: Is it DML implementation bug OR test bug?
       - **If DML is wrong**: Implementation doesn't match spec → fix DML code
       - **If Test is wrong**: Test has incorrect assumptions/assertions → fix test code
       - **If Spec is ambiguous**: Document in research.md → clarify with team
    4. **Fix Code** (DML or Test):
       - **Fix DML**: Edit `simics-project/modules/watchdog-timer/watchdog-timer.dml`
         - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for patterns
         - Common DML issues: wrong ID values, registers not read-only, access violations
         - RAG if needed: `perform_rag_query("DML identification register implementation debugging", source_type="dml")` → document in research.md
       - **Fix Test**: Edit `simics-project/modules/watchdog-timer/test/s-identification-registers.py`
         - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and debugging
         - Verify test logic matches spec.md acceptance criteria
         - Common test issues: wrong expected values, write protection testing, address mapping
         - RAG if needed: `perform_rag_query("identification register test debugging", source_type="python")` → document in research.md
    5. **Rebuild** (if DML changed): `check_with_dmlc()` → `build_simics_project()` → verify compilation
    6. **Retest**: `run_simics_test()` again → check if test passes
    7. **Repeat**: Continue cycle until ALL tests pass
  - **Success Criteria**: ALL test cases pass, no errors, no warnings

- [ ] T058 **MANDATORY: Git commit Identification Registers completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/modules/watchdog-timer/
  git commit -m "implement: Identification Requirements complete - PrimeCell and peripheral ID registers implemented and tested (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Identification Requirements complete and independently testable - can proceed to Integration phase

---

## Phase 9: Clock Enable and Behavioral Requirements (Priority: P1)

**Goal**: Implement clock enable functionality that properly enables/disables timer decrementing when wclk_en signal changes.

**Maps to**:
- spec.md: Behavioral Requirements (BEHAV-005) and Hardware Spec (wclk_en signal)
- test-scenarios.md: Scenario S012: Clock Enable Test
- data-model.md: Timer State Variables and clock handling patterns

> **Workflow**: Follow "Implementation Workflow" section above (TDD cycle + per-task build validation)

**Note**: Basic register definitions exist from Phase 1. Focus on register side-effects, hardware behaviors, state transitions, and HW/SW interaction flows.

---

### 9.1 Tests for Clock Enable Requirements ⚠️ WRITE FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T059 [P] Test for Clock Enable Functionality in `simics-project/modules/watchdog-timer/test/s-clock-enable.py`:
  - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and structure
  - Review spec.md Behavioral Requirements (BEHAV-005) acceptance criteria
  - Review test-scenarios.md for relevant scenarios (S012)
  - Review data-model.md for clock interfaces
  - **Test acceptance criterion 1**: Verify when wclk_en is low (disabled), timer stops decrementing
  - **Test acceptance criterion 2**: Verify when wclk_en is high (enabled), timer resumes decrementing
  - **Test acceptance criterion 3**: Verify counter behavior is consistent with clock enable state
  - **Test acceptance criterion 4**: Verify no spurious interrupts occur due to clock enable changes
  - **RAG if needed**: `perform_rag_query("DML clock enable implementation testing", source_type="python")` → document in research.md

- [ ] T060 Validate Clock Enable tests fail: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should FAIL (not implemented yet)
  - **If tests pass**: Tests are not correctly checking requirement

---

### 9.2 Implementation for Clock Enable Requirements

> **Goal**: Implement clock enable functionality to pass Clock Enable tests (T059)

- [ ] T061 [P] Implement wclk_en signal handling in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for wclk_en signal behavior
  - Review data-model.md for signal interface implementation
  - **RAG if needed**: `perform_rag_query("DML signal interface implementation for clock enable", source_type="dml")` → document in research.md
  - Implement signal interface for wclk_en input
  - Implement logic to pause/resume timer based on wclk_en state
  - Check_with_dmlc → build

- [ ] T062 [P] Integrate clock enable into timer calculation in `simics-project/modules/watchdog-timer/watchdog-timer.dml`:
  - Review spec.md Hardware Spec for timer behavior with clock enable
  - Review data-model.md for timer implementation notes
  - **RAG if needed**: `perform_rag_query("DML timer calculation with clock enable condition", source_type="dml")` → document in research.md
  - Update timer calculation to account for clock enable state
  - Ensure timer only decrements when clock is enabled
  - Check_with_dmlc → build

---

### 9.3 Validation & Commit

> **ITERATIVE DEBUGGING GUIDE**: Tests should PASS after implementation. If not, follow this cycle:

- [ ] T063 Validate Clock Enable tests pass: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Tests should PASS (all acceptance criteria satisfied)
  - **If tests FAIL**: Follow iterative debugging workflow:
    1. **Analyze Failure**: Read test output → identify which acceptance criterion failed
    2. **Review Requirement**: Check spec.md Behavioral Requirements → verify expected behavior matches test assumptions
    3. **Determine Root Cause**: Is it DML implementation bug OR test bug?
       - **If DML is wrong**: Implementation doesn't match spec → fix DML code
       - **If Test is wrong**: Test has incorrect assumptions/assertions → fix test code
       - **If Spec is ambiguous**: Document in research.md → clarify with team
    4. **Fix Code** (DML or Test):
       - **Fix DML**: Edit `simics-project/modules/watchdog-timer/watchdog-timer.dml`
         - Review `.specify/memory/DML_Device_Development_Best_Practices.md` for patterns
         - Common DML issues: clock enable not properly monitored, timer not pausing correctly
         - RAG if needed: `perform_rag_query("DML clock enable implementation debugging", source_type="dml")` → document in research.md
       - **Fix Test**: Edit `simics-project/modules/watchdog-timer/test/s-clock-enable.py`
         - **Review `.specify/memory/Simics_Model_Test_Best_Practices.md`** for test patterns and debugging
         - Verify test logic matches spec.md acceptance criteria
         - Common test issues: timing measurements, signal state monitoring, setup/teardown problems
         - RAG if needed: `perform_rag_query("clock enable test debugging", source_type="python")` → document in research.md
    5. **Rebuild** (if DML changed): `check_with_dmlc()` → `build_simics_project()` → verify compilation
    6. **Retest**: `run_simics_test()` again → check if test passes
    7. **Repeat**: Continue cycle until ALL tests pass
  - **Success Criteria**: ALL test cases pass, no errors, no warnings

- [ ] T064 **MANDATORY: Git commit Clock Enable completion**:
  ```bash
  cd /nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9
  git add simics-project/modules/watchdog-timer/
  git commit -m "implement: Clock Enable Requirements complete - Clock enable functionality implemented and tested (watchdog-timer)"
  git log --oneline -1
  ```

**Checkpoint**: Clock Enable Requirements complete and independently testable - can proceed to Integration phase

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

## Phase 10: Integration & Interfaces

**Purpose**: Connect all requirements and integrate with Simics infrastructure (after ALL requirement phases complete)

> **Workflow**: Follow "Implementation Workflow" - build after EACH task

**Integration Tasks** (in `simics-project/modules/watchdog-timer/watchdog-timer.dml`):

- [ ] T065 **Memory interface**: io_memory methods, register bank connection, access pattern validation
- [ ] T066 **Interrupt/signal connections**: signal interfaces, interrupt generation logic, timing requirements
- [ ] T067 **External ports**: port interfaces for wclk, wclk_en, wrst_n, prst_n, wdogint, wdogres
- [ ] T068 **Clock and reset handling**: proper handling of wrst_n (work reset) and prst_n (APB reset)
- [ ] T069 **Checkpointing**: save/restore methods for ALL state variables

**Validation & Commit**:

- [ ] T070 Run comprehensive tests: `run_simics_test(project_path="/nfs/site/disks/ssm_lwang85_002/AI/workspace/test/f_d9/simics-project", module="watchdog-timer")` → ALL tests PASS (base + requirements)
- [ ] T071 **Git commit**: `git commit -m "integrate: Integration complete - all tests passing (watchdog-timer)"`

**Checkpoint**: Device fully integrated - all tests passing

---

## Phase 11: Polish & Validation

**Purpose**: Final validation, optimization, and documentation

**Parallel Tasks** [P]:

- [ ] T072 [P] **Performance**: Measure overhead, verify <1% impact, optimize hot paths
- [ ] T073 [P] **Code cleanup**: DML grammar compliance, error handling, remove debug code, add comments
- [ ] T074 [P] **Device docs** (`README.md`): Description, register map, interfaces, usage examples
- [ ] T075 [P] **Test docs** (`test/README.md`): Test scenarios, execution instructions, coverage report

**Final Validation & Commit**:

- [ ] T076 Final tests: `run_simics_test()` → Verify no regressions, all scenarios pass
- [ ] T077 **Git commit**: `git commit -m "polish: Device model complete - validated, optimized, documented (watchdog-timer)"`

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

- **Phase 3 (Timer Functionality)**: Depends on Phase 2 (T011) - Core requirement
  - 3.1 Tests: Write tests → Validate they fail
  - 3.2 Implementation: Implement features (tasks can run parallel if different files)
  - 3.3 Validation: Tests pass → Git commit

- **Phase 4+ (Requirements)**: Follow Phase 3 pattern
  - Each requirement follows: Tests → Implementation → Validation
  - Each requirement CAN run in parallel if independent (different registers, state, files)
  - Each requirement MUST complete 3.1 (tests) before 3.2 (implementation)

- **Phase 10 (Integration)**: Depends on ALL requirement phases complete
  - Mostly sequential integration tasks
  - Comprehensive test validation
  - Git commit when all tests pass

- **Phase 11 (Polish)**: Depends on Integration complete
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
Phase 3 (Timer Functionality): Tests → Implementation → Validation → Commit
  ↓
Phase 4 (Interrupt & Reset): Tests → Implementation → Validation → Commit
  ↓
Phase 5 (Clock Divider): Tests → Implementation → Validation → Commit
  ↓
Phase 6 (Lock Protection): Tests → Implementation → Validation → Commit
  ↓
Phase 7 (Integration Test Mode): Tests → Implementation → Validation → Commit
  ↓
Phase 8 (ID Registers): Tests → Implementation → Validation → Commit
  ↓
Phase 9 (Clock Enable): Tests → Implementation → Validation → Commit
  ↓ (ALL requirements complete)
Phase 10 (Integration): Connect all → Comprehensive tests → Commit
  ↓
Phase 11 (Polish): Optimize, document, validate → Commit
```

**Key Principle**: Requirements are independent units that can be developed in parallel if they don't share state/resources.

---

## Implementation Strategy

### Hybrid TDD Workflow

1. **Phase 1**: Setup → Simics project structure ready
2. **Phase 2**: Foundation → Knowledge + base infrastructure tests (MUST FAIL)
3. **Phase 3+**: Per-Requirement → Tests → Implementation → Validation (incremental delivery)
4. **Phase 10**: Integration → Connect all requirements together
5. **Phase 11**: Polish → Production-ready

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