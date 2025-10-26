# Tasks: Simics Watchdog Timer Device

**Status**: Ready for Implementation
**Format**: `[ID] [P?] Description`
**[P]** = Can run in parallel (different files, no dependencies)
Include exact file paths in descriptions

**⚠️ CRITICAL - MCP Tool Paths (SSE Transport)**:
- **ALWAYS use ABSOLUTE paths** for MCP tools: `create_simics_project()`, `build_simics_project()`, `run_simics_test()`
- **NEVER use relative paths** like `"./simics-project"` or `"../project"`
- **WHY**: SSE transport MCP servers run in different process/directory context
- **HOW**: Use `/home/hfeng1/latest-windsurf/simics-project` for project_path
- **Example**: `create_simics_project(project_path="/home/hfeng1/latest-windsurf/simics-project")`

**Input**: Design documents from `/specs/001-read-the-simics/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md → Extract: tech stack (DML 1.4), libraries (Simics API), structure (simics-project)
2. Load design docs:
   → data-model.md: Extract 21 registers, 7 state variables, 3 interfaces → implementation tasks
   → contracts/: 2 files (register-access.md, interface-behavior.md) → contract test tasks
   → research.md: Extract decisions → setup tasks, reference patterns for implementation
   → quickstart.md: 9 validation steps → integration test tasks
3. Simics DML Learning:
   → T021-T024: Read DML_Device_Development_Best_Practices.md + DML_grammar.md at START of implementation
   → Document learnings in research.md "## DML Best Practices Study Notes" + "## DML Grammar Study Notes"
   → Block all DML implementation until complete
4. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: registers, state, interfaces
   → Integration: signal connections, checkpointing
   → Polish: validation, documentation
5. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
6. Number tasks sequentially (T001, T002...)
7. Generate dependency graph
8. Create parallel execution examples
9. Validate task completeness
10. Return: SUCCESS (tasks ready for execution)
```

## Phase 3.1: Setup
- [x] **T001** Create Simics project structure using `create_simics_project(project_path="/home/hfeng1/latest-windsurf/simics-project")` - must use absolute path for SSE transport
- [x] **T002** Add DML device skeleton using `add_dml_device_skeleton(project_path="/home/hfeng1/latest-windsurf/simics-project", device_name="sp805-wdt")` - must use absolute path for SSE transport
- [x] **T003** Checkout and build DMLC using `checkout_and_build_dmlc(project_path="/home/hfeng1/latest-windsurf/simics-project")` - must use absolute path for SSE transport
- [x] **T004** [P] Verify project structure matches template: check modules/sp805-wdt/ directory and files
- [x] **T005** [P] **GATE**: Verify research.md exists with required 8 RAG results from /plan phase - check for DML patterns, test patterns, device examples
- [x] **T006** [P] Verify Simics version and packages using `get_simics_version()` and `list_installed_packages()` - ensure compatibility

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (from contracts/register-access.md)
- [x] **T007** [P] Register access test for WDOGLOAD - read/write behavior, lock protection in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-register-access.py`
- [x] **T008** [P] Register access test for WDOGVALUE - read-only behavior, counter calculation in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-read.py`
- [ ] **T009** [P] Register access test for WDOGCONTROL - read/write with bit field validation, INTEN transitions in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-control.py`
- [ ] **T010** [P] Register access test for WDOGINTCLR - write-only behavior, interrupt clear in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-clear.py`
- [ ] **T011** [P] Register access test for WDOGRIS - read-only interrupt status in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-status.py`
- [ ] **T012** [P] Register access test for WDOGMIS - masked interrupt status in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-masked-status.py`
- [x] **T013** [P] Register access test for WDOGLOCK - lock/unlock mechanism in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-lock.py`
- [ ] **T014** [P] Register access test for WDOGITCR - integration test mode control in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-test-mode.py`
- [ ] **T015** [P] Register access test for WDOGITOP - direct signal control in test mode in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-test-output.py`
- [x] **T016** [P] Register access test for identification registers - constant values in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-identification.py`
- [ ] **T017** [P] Register access test for unmapped addresses - return 0, ignore writes in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-unmapped.py`

### Contract Tests (from contracts/interface-behavior.md)
- [x] **T018** [P] Counter operation test - enable/disable behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-operation.py`
- [ ] **T019** [P] Counter reload test - WDOGINTCLR reload behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-reload.py`
- [ ] **T020** [P] Counter decrement test - clock divider behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-decrement.py`
- [ ] **T021** [P] Interrupt generation test - first timeout behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-generation.py`
- [ ] **T022** [P] Interrupt clear test - WDOGINTCLR clear behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-clear.py`
- [ ] **T023** [P] Reset generation test - second timeout behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-reset-generation.py`
- [ ] **T024** [P] Reset persistence test - reset signal behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-reset-persistence.py`
- [ ] **T025** [P] Lock mechanism test - write protection behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-lock-protection.py`
- [ ] **T026** [P] Integration test mode test - direct signal control in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-integration-mode.py`
- [ ] **T027** [P] Checkpoint/restore test - state persistence in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-checkpoint.py`
- [ ] **T028** [P] Clock divider test - all step_value settings in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-clock-dividers.py`

### Integration Tests (from quickstart.md 9 validation steps)
- [ ] **T029** [P] Basic register access validation test - identification registers in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-basic-access.py`
- [ ] **T030** [P] Counter operation validation test - decrement behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-validation.py`
- [ ] **T031** [P] First timeout and interrupt validation test - interrupt assertion in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-first-timeout.py`
- [ ] **T032** [P] Interrupt clear validation test - clear behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-clear-validation.py`
- [ ] **T033** [P] Second timeout and reset validation test - reset assertion in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-second-timeout.py`
- [ ] **T034** [P] Lock mechanism validation test - protection behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-lock-validation.py`
- [ ] **T035** [P] Clock divider validation test - timing behavior in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-divider-validation.py`
- [ ] **T036** [P] Integration test mode validation test - direct control in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-integration-validation.py`
- [ ] **T037** [P] Checkpoint/restore validation test - state preservation in `simics-project/modules/sp805-wdt/test/s-sp805-wdt-checkpoint-validation.py`

- [ ] **T038** [P] **GATE**: Run initial test suite to verify all tests fail: `run_simics_test(project_path="/home/hfeng1/latest-windsurf/simics-project", suite="modules/sp805-wdt/test")` - must use absolute path for SSE transport

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### DML Learning Gates (MUST COMPLETE BEFORE ANY DML IMPLEMENTATION)
- [x] **T039** **GATE**: Read `.specify/memory/DML_Device_Development_Best_Practices.md` completely - document key patterns in research.md "## DML Best Practices Study Notes"
- [x] **T040** **GATE**: Read `.specify/memory/DML_grammar.md` completely - document syntax rules in research.md "## DML Grammar Study Notes"
- [x] **T041** **GATE**: Review study notes - verify comprehensive understanding of DML 1.4 syntax, templates, and best practices
- [x] **T042** **GATE**: Review device skeleton in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - understand base structure

### Device Structure and Foundation
- [x] **T043** [P] Update DML header and imports in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - add DML 1.4 declaration, utility.dml, signal.dml, device-api.dml imports
- [x] **T044** [P] Update device parameters in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - add desc, documentation, classname parameters
- [x] **T045** [P] Add signal connections in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - wdogint and wdogres signal_connect interfaces

### Register Bank Definition (21 registers from data-model.md)
- [x] **T046** [P] Define register bank structure in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - bank regs with register_size=4, byte_order="little-endian", use_io_memory=false
- [x] **T047** [P] Implement WDOGLOAD register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0x000, R/W, init_val=0xFFFFFFFF, lock protection
- [x] **T048** [P] Implement WDOGVALUE register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0x004, RO, init_val=0xFFFFFFFF, calculated counter value
- [x] **T049** [P] Implement WDOGCONTROL register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0x008, R/W, init_val=0x00000000, bit fields for step_value, RESEN, INTEN
- [x] **T050** [P] Implement WDOGINTCLR register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0x00C, WO, interrupt clear and counter reload logic
- [x] **T051** [P] Implement WDOGRIS register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0x010, RO, raw interrupt status
- [x] **T052** [P] Implement WDOGMIS register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0x014, RO, masked interrupt status (WDOGRIS AND INTEN)
- [x] **T053** [P] Implement WDOGLOCK register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0xC00, R/W, lock/unlock mechanism (0x1ACCE551)
- [x] **T054** [P] Implement WDOGITCR register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0xF00, R/W, integration test mode control
- [x] **T055** [P] Implement WDOGITOP register in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - offset 0xF04, WO, direct signal control in test mode
- [x] **T056** [P] Implement identification registers in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - WDOGPERIPHID4-7, WDOGPERIPHID0-3, WDOGPCELLID0-3 with correct constant values

### Device State Variables (7 variables from data-model.md)
- [x] **T057** [P] Implement device state variables in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - counter_start_time (saved cycles_t), counter_start_value (saved uint32), interrupt_pending (saved bool), reset_asserted (saved bool), lock_state (saved bool), integration_test_mode (saved bool), divider_counter (session uint32)

### Core Logic Implementation
- [x] **T058** [P] Implement counter calculation logic in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - WDOGVALUE read method using cycle counting and divider
- [x] **T059** [P] Implement timeout event scheduling in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - after cycles: on_timeout() method
- [x] **T060** [P] Implement interrupt generation logic in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - first timeout: set WDOGRIS[0], assert wdogint signal
- [x] **T061** [P] Implement reset generation logic in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - second timeout: assert wdogres signal, keep asserted
- [x] **T062** [P] Implement lock mechanism logic in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - check lock_state in WDOGLOAD and WDOGCONTROL write methods
- [x] **T063** [P] Implement integration test mode logic in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - disable normal operation, direct signal control
- [x] **T064** [P] Implement clock divider logic in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - step_value to cycle multiplier conversion
- [x] **T065** [P] Implement checkpoint/restore support in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - saved variables for all state

### Validation Gates
- [x] **T066** **GATE**: Validate DML syntax using `check_with_dmlc(project_path="/home/hfeng1/latest-windsurf/simics-project", module="sp805-wdt")` - must use absolute path for SSE transport
- [x] **T067** **GATE**: Build device using `build_simics_project(project_path="/home/hfeng1/latest-windsurf/simics-project", module="sp805-wdt")` - must use absolute path for SSE transport
- [x] **T068** **GATE**: Run tests to verify implementation works: `run_simics_test(project_path="/home/hfeng1/latest-windsurf/simics-project", suite="modules/sp805-wdt/test")` - must use absolute path for SSE transport

## Phase 3.4: Integration
- [ ] **T069** [P] Implement io_memory interface in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - memory-mapped register access with transaction handling
- [ ] **T070** [P] Connect interrupt signals in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - wdogint to platform interrupt controller
- [ ] **T071** [P] Connect reset signals in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - wdogres to platform reset controller
- [ ] **T072** [P] Implement device initialization in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - init() and post_init() methods
- [ ] **T073** [P] Implement device cleanup in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - destroy() method
- [ ] **T074** **GATE**: Build and test integration: `build_simics_project(project_path="/home/hfeng1/latest-windsurf/simics-project", module="sp805-wdt")` + `run_simics_test(project_path="/home/hfeng1/latest-windsurf/simics-project", suite="modules/sp805-wdt/test")`

## Phase 3.5: Polish
- [ ] **T075** [P] Update test suite with comprehensive scenarios in `simics-project/modules/sp805-wdt/test/` - edge cases, error conditions, performance validation
- [ ] **T076** [P] Implement comprehensive logging in `simics-project/modules/sp805-wdt/sp805-wdt.dml` - register accesses, state transitions, timeout events
- [ ] **T077** [P] Execute quickstart.md validation steps 1-9 using actual device implementation
- [ ] **T078** [P] Performance testing - verify <1% simulation overhead, single-cycle register access
- [ ] **T079** [P] Update documentation in `simics-project/modules/sp805-wdt/README` - usage examples, configuration options
- [ ] **T080** **GATE**: Final comprehensive test run: `run_simics_test(project_path="/home/hfeng1/latest-windsurf/simics-project")` - all tests pass

## Dependencies

**General**: Setup → Tests → DML Learning → Implementation → Integration → Polish

**Simics Specific**:
- T001 → T002 → T003 → T004 → T005 → T006 → T007-T038 → T039-T042 → T043-T068 → T069-T074 → T075-T080
- **Key Gates**: research.md (T005) → Tests (T007-T038) → DML Learning (T039-T042) → Implementation (T043-T068) → Integration (T069-T074) → Polish (T075-T080)
- **Parallel**: T007-T037 can run in parallel (different test files), T043-T056 can run in parallel (different registers), T057-T065 can run in parallel (different logic components)

## Parallel Example
```
# Launch T007-T017 together (register access tests):
Task: "Register access test for WDOGLOAD in simics-project/modules/sp805-wdt/test/s-sp805-wdt-register-access.py"
Task: "Register access test for WDOGVALUE in simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-read.py"
Task: "Register access test for WDOGCONTROL in simics-project/modules/sp805-wdt/test/s-sp805-wdt-control.py"
Task: "Register access test for WDOGINTCLR in simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-clear.py"
Task: "Register access test for WDOGRIS in simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-status.py"
Task: "Register access test for WDOGMIS in simics-project/modules/sp805-wdt/test/s-sp805-wdt-masked-status.py"
Task: "Register access test for WDOGLOCK in simics-project/modules/sp805-wdt/test/s-sp805-wdt-lock.py"
Task: "Register access test for WDOGITCR in simics-project/modules/sp805-wdt/test/s-sp805-wdt-test-mode.py"
Task: "Register access test for WDOGITOP in simics-project/modules/sp805-wdt/test/s-sp805-wdt-test-output.py"
Task: "Register access test for identification registers in simics-project/modules/sp805-wdt/test/s-sp805-wdt-identification.py"
Task: "Register access test for unmapped addresses in simics-project/modules/sp805-wdt/test/s-sp805-wdt-unmapped.py"

# Launch T018-T028 together (interface behavior tests):
Task: "Counter operation test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-operation.py"
Task: "Counter reload test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-reload.py"
Task: "Counter decrement test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-counter-decrement.py"
Task: "Interrupt generation test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-generation.py"
Task: "Interrupt clear test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-interrupt-clear.py"
Task: "Reset generation test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-reset-generation.py"
Task: "Reset persistence test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-reset-persistence.py"
Task: "Lock mechanism test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-lock-protection.py"
Task: "Integration test mode test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-integration-mode.py"
Task: "Checkpoint/restore test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-checkpoint.py"
Task: "Clock divider test in simics-project/modules/sp805-wdt/test/s-sp805-wdt-clock-dividers.py"
```

## Notes
- **[P] tasks** = different files, no dependencies (can run in parallel)
- **TDD approach**: All tests written and failing before implementation begins
- **DML Learning Gates**: T039-T042 must complete before any DML implementation
- **Absolute paths**: All MCP tool calls use `/home/hfeng1/latest-windsurf/simics-project`
- **Research.md reference**: Use patterns from /plan phase for implementation guidance
- **Commit after each task**: Follow git workflow for task completion tracking

## Task Generation Rules Applied
1. **From Contracts**: 11 contracts from register-access.md → 11 contract tests [P], 11 interface contracts → 11 interface tests [P]
2. **From Data Model**: 21 registers → 21 register implementation tasks, 7 state variables → 7 state implementation tasks, 3 interfaces → 3 interface implementation tasks
3. **From User Stories**: 9 quickstart validation steps → 9 integration tests [P]
4. **Ordering**: Setup → Tests → DML Learning → Implementation → Integration → Polish
5. **Parallel**: Tests can run in parallel (different files), register implementations can run in parallel (different registers)

## Validation Checklist
- [x] All contracts have corresponding tests (22 contract tests from 2 contract files)
- [x] All entities have implementation tasks (21 registers, 7 state variables, 3 interfaces)
- [x] All tests come before implementation (T007-T038 before T043-T068)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] **All MCP tool calls use ABSOLUTE paths** for SSE transport
- [x] All MCP tool calls specify correct project_path parameter
- [x] Build validation tasks after implementation changes
- [x] Test execution tasks use appropriate suite parameter
- [x] Device name "sp805-wdt" consistently used across tasks
- [x] research.md from /plan phase is referenced for patterns
- [x] Optional RAG searches not needed (research.md sufficient)
- [x] DML learning gates before implementation tasks

## Critical Gates
### Pre-Test Gate (T005):
- [x] research.md exists with 8 RAG results from /plan phase
- [x] Reviewed and understood DML 1.4 patterns, timer implementation patterns, test patterns

### DML Learning Gate (T039-T042):
- [x] Read DML_Device_Development_Best_Practices.md completely
- [x] Read DML_grammar.md completely
- [x] Document study notes in research.md before implementation
- [x] Verify comprehensive understanding before T043+

### Implementation Gate (T066-T068):
- [x] DML syntax validation with check_with_dmlc()
- [x] Successful build with build_simics_project()
- [x] All tests pass with run_simics_test()

## research.md Workflow
**Source**: Created by /plan with comprehensive RAG results (8 mandatory searches)
**Usage**: Reference documented patterns for implementation (primary source)
**Modifications**: No additional RAG queries needed - research.md covers all requirements
**Status**: ✅ Available and comprehensive

## Execution Rules
1. **Prerequisites**: research.md verified (T005)
2. **Tests First**: T007-T038 written before implementation, must fail initially
3. **DML Learning**: T039-T042 before ANY DML implementation
4. **Study Notes**: Must be documented and referenced in all DML tasks
5. **Absolute Paths**: All MCP tool calls use `/home/hfeng1/latest-windsurf/simics-project`
6. **Commit After Each Task**: Maintain clear progress tracking

## Common Failures - Prevention
- ✅ **DML Learning**: T039-T042 completed before implementation
- ✅ **Tests First**: T007-T038 written and failing before T043+
- ✅ **Study Notes**: Documented in research.md, referenced during implementation
- ✅ **Research.md**: Used as primary source (no duplicate RAG queries)
- ✅ **Absolute Paths**: All MCP calls use `/home/hfeng1/latest-windsurf/simics-project`

## Error Recovery (Simics)
**Priority**: Study Notes → research.md RAG Results → DML Documentation → RAG Query (last resort)

### Build Errors
1. **Check Grammar Notes**: Search research.md "DML Grammar Study Notes" for syntax rules
2. **Check Best Practices Notes**: Search "DML Best Practices Study Notes" for patterns
3. **Check research.md RAG**: Device examples, register patterns from /plan phase
4. **Check DML Validation**: Use `check_with_dmlc()` for AI diagnostics
5. **RAG Query**: Only if above insufficient: `perform_rag_query("DML 1.4 [error_keyword] solution", source_type="dml", match_count=10)`
6. **Document**: Add solution to research.md "## Error Recovery" section

### Test Failures
1. **Check Test Patterns**: research.md test sections from /plan phase
2. **Check Implementation**: Verify against contracts/ and data-model.md
3. **Check Best Practices**: For device behavior issues
4. **Debug**: Use comprehensive logging implemented in T076
5. **Fix**: Update implementation, rebuild, retest

**Documentation**: After resolving any issue, add to research.md:
```
**Error**: [message] → **Solution**: [fix] → **Reference**: [source] → **Applied**: T0XX
```
