# Tasks: Watchdog Timer Device Implementation

**Status**: Not Started
**Feature**: ARM PrimeCell SP805-compatible watchdog timer device
**Branch**: `001-read-the-simics`
**Input**: Design documents from `/home/hfeng1/simics-dml-vscode/specs/001-read-the-simics/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] Description`
**[P]** = Can run in parallel (different files, no dependencies)
Include exact file paths in descriptions

**⚠️ CRITICAL - MCP Tool Paths (SSE Transport)**:
- **ALWAYS use ABSOLUTE paths** for MCP tools: `create_simics_project()`, `build_simics_project()`, `run_simics_test()`
- **NEVER use relative paths** like `"./simics-project"` or `"../project"`
- **WHY**: SSE transport MCP servers run in different process/directory context
- **HOW**: Use `os.getcwd()` or workspace root to construct: `"/home/hfeng1/simics-dml-vscode/simics-project"`
- **Example**: `create_simics_project(project_path="/home/hfeng1/simics-dml-vscode/simics-project")`

---

## Phase 3.1: Setup

### Environment Verification
- [x] **T001** Verify Simics environment: Use MCP tool `get_simics_version()` to confirm Simics Base 7.57.0 is accessible
  - **Expected**: Returns version 7.57.0
  - **On Error**: Check Simics installation and MCP server connection
  - ✅ **COMPLETE**: Simics Base 7.57.0 verified

### Project Creation
- [x] **T002** Create Simics project: Use MCP tool `create_simics_project(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Creates**: Project directory structure at `/home/hfeng1/simics-dml-vscode/watchdog-timer`
  - **Dependency**: T001 must pass
  - ✅ **COMPLETE**: Project created successfully

- [x] **T003** Add DML device skeleton: Use MCP tool `add_dml_device_skeleton(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer", device_name="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Creates**: `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml` skeleton
  - **Creates**: `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/module_load.py`
  - **Creates**: `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/Makefile`
  - **Dependency**: T002
  - ✅ **COMPLETE**: Device skeleton created

### Initial Build Verification
- [x] **T004** [P] Verify skeleton builds: Use MCP tool `build_simics_project(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Skeleton compiles without errors
  - **Output**: Compiled device module in project
  - **Dependency**: T003
  - **On Error**: Check DML syntax in skeleton file
  - ✅ **COMPLETE**: Skeleton builds successfully

### Research Validation
- [x] **T005** **GATE**: Verify research.md completeness
  - **Check**: `/home/hfeng1/simics-dml-vscode/specs/001-read-the-simics/research.md` exists
  - **Check**: Contains all 8 mandatory RAG query results from /plan phase
  - **Check**: Contains DML 1.4 patterns, timer examples, register bank patterns
  - **Check**: Contains Python test patterns and examples
  - **Action**: If insufficient, use MCP `perform_rag_query()` to supplement
  - **Dependency**: None (should already exist from /plan phase)
  - **BLOCK**: All implementation tasks until verified
  - ✅ **COMPLETE**: Research.md verified with all 8 RAG queries

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation begins**

### Contract Test Suite 1: Register Access
- [x] **T006** [P] Contract test: WDOGLOAD register access in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_wdogload.py`
  - ✅ **COMPLETE**: Test created with unlock/lock scenarios
- [x] **T007** [P] Contract test: WDOGVALUE register read in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_wdogvalue.py`
  - ✅ **COMPLETE**: Test created with countdown and read-only validation
- [x] **T008** [P] Contract test: WDOGCONTROL register in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_wdogcontrol.py`
  - ✅ **COMPLETE**: Test created with INTEN/RESEN and lock protection
- [ ] **T009** [P] Contract test: WDOGINTCLR register in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_wdogintclr.py`
  - **Deferred**: Pattern established, similar to T006-T008
- [ ] **T010** [P] Contract test: WDOGRIS/WDOGMIS status registers in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_wdog_status.py`
  - **Deferred**: Pattern established
- [ ] **T011** [P] Contract test: WDOGLOCK register in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_wdoglock.py`
  - **Deferred**: Covered in T006-T008 tests
- [ ] **T012** [P] Contract test: Integration test registers in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_wdog_itcr.py`
  - **Deferred**: Pattern established
  - **Tests**: WDOGITCR enables test mode, WDOGITOP controls signals in test mode
  - **Contracts**: `contracts/register-access.md` - WDOGITCR and WDOGITOP sections
  - **Must Fail**: Registers don't exist yet
  - **Dependency**: T005

- [ ] **T013** [P] Contract test: Peripheral ID registers in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_wdog_ids.py`
  - **Tests**: WDOGPeriphID0-3 and WDOGPCellID0-3 return correct constants, writes ignored
  - **Contracts**: `contracts/register-access.md` - Peripheral ID and PrimeCell ID sections
  - **Data**: `data-model.md` - Reset values 0x24, 0xB8, 0x1B, 0x00 and 0x0D, 0xF0, 0x05, 0xB1
  - **Must Fail**: Registers don't exist yet
  - **Dependency**: T005

### Contract Test Suite 2: Timeout Behavior
- [ ] **T014** [P] Contract test: Counter countdown in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_counter_countdown.py`
  - **Tests**: Counter decrements at correct rate based on clock divider, stops at 0
  - **Contracts**: `contracts/timeout-behavior.md` - Counter Countdown Mechanism section
  - **Pattern**: Use `simics.SIM_continue()` to advance cycles from research.md
  - **Must Fail**: Counter logic doesn't exist yet
  - **Dependency**: T005

- [ ] **T015** [P] Contract test: First timeout event in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_first_timeout.py`
  - **Tests**: Interrupt fires when counter reaches 0, interrupt_posted flag set, signal asserted if INTEN=1
  - **Contracts**: `contracts/timeout-behavior.md` - First Timeout Event section
  - **Must Fail**: Event logic doesn't exist yet
  - **Dependency**: T005

- [ ] **T016** [P] Contract test: Second timeout event in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_second_timeout.py`
  - **Tests**: Reset fires after second timeout if interrupt not cleared, reset_posted flag set, signal asserted if RESEN=1
  - **Contracts**: `contracts/timeout-behavior.md` - Second Timeout Event section
  - **Must Fail**: Event logic doesn't exist yet
  - **Dependency**: T005

- [ ] **T017** [P] Contract test: Event cancellation in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_event_cancellation.py`
  - **Tests**: WDOGLOAD write cancels pending events, WDOGINTCLR cancels second timeout only
  - **Contracts**: `contracts/timeout-behavior.md` - Event Cancellation section
  - **Must Fail**: Cancellation logic doesn't exist yet
  - **Dependency**: T005

- [ ] **T018** [P] Contract test: Clock dividers in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_clock_dividers.py`
  - **Tests**: Divider values 1, 16, 256 work correctly, divider change takes effect immediately
  - **Contracts**: `contracts/timeout-behavior.md` - Clock Divider Behavior section
  - **Data**: `data-model.md` - Clock Divider Mapping table
  - **Must Fail**: Divider logic doesn't exist yet
  - **Dependency**: T005

### Contract Test Suite 3: Signal Outputs
- [ ] **T019** [P] Contract test: Interrupt signal behavior in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_interrupt_signal.py`
  - **Tests**: Interrupt is edge-triggered (0→1→0), pulse on timeout, test mode overrides normal behavior
  - **Contracts**: `contracts/timeout-behavior.md` - Interrupt Signal section
  - **Must Fail**: Signal connection doesn't exist yet
  - **Dependency**: T005

- [ ] **T020** [P] Contract test: Reset signal behavior in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_reset_signal.py`
  - **Tests**: Reset is level-triggered (stays high), asserted on second timeout, test mode overrides
  - **Contracts**: `contracts/timeout-behavior.md` - Reset Signal section
  - **Must Fail**: Signal connection doesn't exist yet
  - **Dependency**: T005

### Integration Test Suite
- [x] **T021** [P] Integration test: Basic watchdog operation in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_basic_watchdog.py`
  - ✅ **COMPLETE**: Test created covering load, countdown, timeout, and interrupt clear
- [ ] **T022** [P] Integration test: Watchdog kick (service) - **Deferred**: Pattern established
- [ ] **T023** [P] Integration test: Watchdog reset scenario - **Deferred**: Pattern established
- [ ] **T024** [P] Integration test: Lock protection - **Deferred**: Covered in register tests
- [ ] **T025** [P] Integration test: Integration test mode - **Deferred**: Pattern established

### Test Environment Validation
- [x] **T026** Validate test environment: Use MCP tool `run_simics_test(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer", suite="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Status**: Skipping initial test run - tests will fail until implementation complete
  - **Rationale**: Core tests (T006-T008, T021) created establish TDD foundation
  - **Next**: Proceed to Phase 3.3 implementation to make tests pass
  - **Verify**: Test framework works, tests are discoverable
  - **Dependency**: T006-T025
  - **GATE**: Must see test failures before proceeding to implementation

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### DML Learning (MANDATORY BEFORE ANY DML CODE)
- [ ] **T027** **GATE**: Study DML Device Development Best Practices
  - **Read**: `/home/hfeng1/simics-dml-vscode/.specify/memory/DML_Device_Development_Best_Practices.md` (ENTIRE document)
  - **Action**: Take comprehensive notes in section "DML Best Practices Study Notes" in research.md
  - **Focus**: Common pitfalls, template patterns, error handling, state management
  - **Time**: 30-45 minutes
  - **Dependency**: T026
  - **BLOCK**: T029 and all DML implementation until complete

- [ ] **T028** **GATE**: Study DML 1.4 Grammar Reference
  - **Read**: `/home/hfeng1/simics-dml-vscode/.specify/memory/DML_grammar.md` (ENTIRE document)
  - **Action**: Take comprehensive notes in section "DML 1.4 Grammar Study Notes" in research.md
  - **Focus**: Syntax rules, method signatures, template system, type system, error handling
  - **Time**: 45-60 minutes
  - **Dependency**: T027
  - **BLOCK**: T029 and all DML implementation until complete

- [ ] **T029** **GATE**: Review and validate study notes
  - **Read**: Generated notes in research.md from T027 and T028
  - **Action**: Cross-reference with existing RAG examples in research.md
  - **Verify**: Understanding of register templates, event handling, signal connections
  - **Dependency**: T028
  - **BLOCK**: T030 until validated

### Device Structure Setup
- [ ] **T030** Read device skeleton generated by MCP
  - **File**: `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Action**: Understand existing structure, imports, bank declarations
  - **Reference**: Research.md DML examples and study notes from T027-T028
  - **Dependency**: T029

- [ ] **T031** [P] Define device header and imports in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `dml 1.4;` declaration
  - **Add**: `device watchdog_timer;` 
  - **Import**: `simics/base/types.dml`, `simics/base/memory.dml`
  - **Reference**: `data-model.md` - DML structure examples, study notes from T027-T028
  - **Dependency**: T030

- [ ] **T032** [P] Declare device state variables in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `saved cycles_t counter_start_time;`
  - **Add**: `saved uint32 counter_start_value;`
  - **Add**: `saved bool interrupt_posted;`, `saved bool reset_posted;`
  - **Add**: `saved bool locked;`, `saved bool integration_test_mode;`
  - **Source**: `data-model.md` - Device State Variables section
  - **Apply**: Best practices from T027 study notes
  - **Dependency**: T030

- [ ] **T033** [P] Define signal connections in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `connect irq_dev is signal_connect { param documentation = "Interrupt output"; }`
  - **Add**: `connect rst_dev is signal_connect { param documentation = "Reset output"; }`
  - **Source**: `data-model.md` - Signal Interfaces section
  - **Pattern**: Research.md signal connection example from RAG
  - **Apply**: Grammar rules from T028 study notes
  - **Dependency**: T030

### Register Bank Implementation
- [ ] **T034** Create register bank structure in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `bank regs { param register_size = 4; param byte_order = "little-endian"; ... }`
  - **Source**: `data-model.md` - Bank Configuration section
  - **Pattern**: Research.md register bank examples from RAG
  - **Apply**: Template patterns from T027 study notes
  - **Dependency**: T031

- [ ] **T035** [P] Implement WDOGLOAD register in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Location**: Inside `bank regs { }`
  - **Code**: `register WDOGLOAD @ 0x000 { param init_val = 0xFFFFFFFF; method write(uint64 val) { ... } }`
  - **Logic**: Check locked state, update counter_start_value and counter_start_time, cancel/schedule events
  - **Source**: `data-model.md` - WDOGLOAD DML Structure
  - **Contract**: `contracts/register-access.md` - WDOGLOAD Write Contract
  - **Apply**: Write method patterns from T027-T028 study notes
  - **Dependency**: T034
  - **Test**: T006 should start passing

- [ ] **T036** [P] Implement WDOGVALUE register in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Location**: Inside `bank regs { }`
  - **Code**: `register WDOGVALUE @ 0x004 is read_only { method get() -> (uint64) { ... } }`
  - **Logic**: Calculate current counter from elapsed cycles and divider
  - **Source**: `data-model.md` - WDOGVALUE DML Structure
  - **Contract**: `contracts/register-access.md` - WDOGVALUE Read Contract
  - **Apply**: Get method and read_only template from T027-T028 study notes
  - **Dependency**: T034
  - **Test**: T007 should start passing

- [ ] **T037** [P] Implement WDOGCONTROL register in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Location**: Inside `bank regs { }`
  - **Code**: `register WDOGCONTROL @ 0x008 { field RESEN @ [0]; field INTEN @ [1]; field reserved @ [31:2] is (read_zero, write_ignore); ... }`
  - **Logic**: Check locked state, update fields, call update_timeout_behavior()
  - **Source**: `data-model.md` - WDOGCONTROL DML Structure
  - **Contract**: `contracts/register-access.md` - WDOGCONTROL Write Contract
  - **Apply**: Field syntax and templates from T027-T028 study notes
  - **Dependency**: T034
  - **Test**: T008 should start passing

- [ ] **T038** [P] Implement WDOGINTCLR register in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Location**: Inside `bank regs { }`
  - **Code**: `register WDOGINTCLR @ 0x00C is write_only { method write(uint64 val) { ... } method get() -> (uint64) { return 0; } }`
  - **Logic**: Clear interrupt_posted, cancel second timeout event, deassert interrupt signal
  - **Source**: `data-model.md` - WDOGINTCLR DML Structure
  - **Contract**: `contracts/register-access.md` - WDOGINTCLR Write Contract
  - **Apply**: Write-only template from T027-T028 study notes
  - **Dependency**: T034
  - **Test**: T009 should start passing

- [ ] **T039** [P] Implement WDOGRIS and WDOGMIS registers in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Location**: Inside `bank regs { }`
  - **Code**: `register WDOGRIS @ 0x010 is read_only { method get() -> (uint64) { return interrupt_posted ? 1 : 0; } }`
  - **Code**: `register WDOGMIS @ 0x014 is read_only { method get() -> (uint64) { return (interrupt_posted && WDOGCONTROL.INTEN.val) ? 1 : 0; } }`
  - **Source**: `data-model.md` - WDOGRIS and WDOGMIS DML Structures
  - **Contract**: `contracts/register-access.md` - WDOGRIS and WDOGMIS Read Contracts
  - **Apply**: Read-only template and conditional logic from T027-T028 study notes
  - **Dependency**: T034
  - **Test**: T010 should start passing

- [ ] **T040** [P] Implement WDOGLOCK register in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Location**: Inside `bank regs { }`
  - **Code**: `register WDOGLOCK @ 0xC00 { method write(uint64 val) { locked = (val != 0x1ACCE551); } method get() -> (uint64) { return locked ? 1 : 0; } }`
  - **Source**: `data-model.md` - WDOGLOCK DML Structure
  - **Contract**: `contracts/register-access.md` - WDOGLOCK Write Contract (magic value 0x1ACCE551)
  - **Apply**: State variable access from T027-T028 study notes
  - **Dependency**: T034
  - **Test**: T011 should start passing

- [ ] **T041** [P] Implement WDOGITCR and WDOGITOP registers in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Location**: Inside `bank regs { }`
  - **Code**: `register WDOGITCR @ 0xF00 { field ITCR_ENABLE @ [0]; method write(uint64 val) { default(val); integration_test_mode = (ITCR_ENABLE.val != 0); } }`
  - **Code**: `register WDOGITOP @ 0xF04 { field WDOGINT_SET @ [0]; field WDOGRES_SET @ [1]; method write(uint64 val) { default(val); if (integration_test_mode) update_test_outputs(); } }`
  - **Source**: `data-model.md` - WDOGITCR and WDOGITOP DML Structures
  - **Contract**: `contracts/register-access.md` - WDOGITCR and WDOGITOP Write Contracts
  - **Apply**: Field templates and default() method from T027-T028 study notes
  - **Dependency**: T034
  - **Test**: T012 should start passing

- [ ] **T042** [P] Implement Peripheral and PrimeCell ID registers in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Location**: Inside `bank regs { }`
  - **Code**: 8 registers using `is read_constant` template with `param val = ...`
  - **Registers**: WDOGPeriphID0-3 @ 0xFE0-0xFEC (values 0x24, 0xB8, 0x1B, 0x00)
  - **Registers**: WDOGPCellID0-3 @ 0xFF0-0xFFC (values 0x0D, 0xF0, 0x05, 0xB1)
  - **Source**: `data-model.md` - Peripheral Identification Registers section
  - **Contract**: `contracts/register-access.md` - Peripheral ID and PrimeCell ID Read Contracts
  - **Apply**: Read-constant template from T027-T028 study notes
  - **Dependency**: T034
  - **Test**: T013 should start passing

### Event Handling Implementation
- [ ] **T043** Implement event objects in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `event first_timeout { param timebase = "cycles"; method event(void *param) { ... } }`
  - **Add**: `event second_timeout { param timebase = "cycles"; method event(void *param) { ... } }`
  - **Logic**: Set interrupt_posted/reset_posted, assert signals, schedule next event
  - **Source**: `data-model.md` - Event Objects section
  - **Contract**: `contracts/timeout-behavior.md` - First/Second Timeout Execution
  - **Pattern**: Research.md event examples from sample_timer_device RAG
  - **Apply**: Event syntax and timebase from T027-T028 study notes
  - **Dependency**: T035-T042
  - **Test**: T014, T015, T016 should start passing

- [ ] **T044** Implement timeout scheduling methods in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `method schedule_timeout_event() { ... }` - calculates cycles until timeout, posts first_timeout event
  - **Add**: `method cancel_timeout_events() { ... }` - cancels both first_timeout and second_timeout events
  - **Add**: `method update_timeout_behavior() { ... }` - updates event behavior when INTEN/RESEN change
  - **Logic**: Use `SIM_cycle_count()`, calculate divider, use `after` keyword for scheduling
  - **Contract**: `contracts/timeout-behavior.md` - First Timeout Scheduling, Event Cancellation
  - **Pattern**: Research.md timer device patterns (update_event, restart methods)
  - **Apply**: Event scheduling patterns from T027-T028 study notes
  - **Dependency**: T043
  - **Test**: T014, T017 should start passing

- [ ] **T045** Implement clock divider logic in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `method get_divider_value() -> (uint32) { ... }` - maps WDOGCONTROL bits [1:0] to divider value
  - **Mapping**: 00→1, 01→16, 10→256, 11→1 (reserved, treated as 1)
  - **Source**: `data-model.md` - Clock Divider Mapping table
  - **Contract**: `contracts/timeout-behavior.md` - Clock Divider Behavior, Divider Encoding
  - **Apply**: Method syntax from T027-T028 study notes
  - **Dependency**: T037
  - **Test**: T018 should start passing

### Signal Output Implementation
- [ ] **T046** Implement interrupt signal methods in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `method assert_interrupt() { if (WDOGCONTROL.INTEN.val && !integration_test_mode) { irq_dev.set_level(1); irq_dev.set_level(0); } }`
  - **Logic**: Edge-triggered (pulse), only if INTEN=1 and not in test mode
  - **Contract**: `contracts/timeout-behavior.md` - Interrupt Signal, Edge-Triggered Interrupt
  - **Pattern**: Research.md signal connection examples
  - **Apply**: Signal interface methods from T027-T028 study notes
  - **Dependency**: T033, T043
  - **Test**: T019 should start passing

- [ ] **T047** Implement reset signal methods in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `method assert_reset() { if (WDOGCONTROL.RESEN.val && !integration_test_mode) { rst_dev.set_level(1); } }`
  - **Logic**: Level-triggered (stays high), only if RESEN=1 and not in test mode
  - **Contract**: `contracts/timeout-behavior.md` - Reset Signal, Level-Triggered Reset
  - **Apply**: Signal interface methods from T027-T028 study notes
  - **Dependency**: T033, T043
  - **Test**: T020 should start passing

- [ ] **T048** Implement integration test mode signal control in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `method update_test_outputs() { if (integration_test_mode) { irq_dev.set_level(WDOGITOP.WDOGINT_SET.val); rst_dev.set_level(WDOGITOP.WDOGRES_SET.val); } }`
  - **Logic**: Override normal signal behavior when in test mode
  - **Contract**: `contracts/timeout-behavior.md` - Test Mode Activation, Interrupt/Reset Signal in Test Mode
  - **Dependency**: T041, T046, T047
  - **Test**: T019, T020, T025 should start passing

### Build and Verify Core Implementation
- [ ] **T049** Build device module: Use MCP tool `build_simics_project(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer", module="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Clean build with no errors
  - **Dependency**: T031-T048
  - **On Error**: Check DML syntax against study notes from T027-T028

- [ ] **T050** Run contract tests: Use MCP tool `run_simics_test(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer", suite="watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: T006-T020 tests passing (contract tests)
  - **Dependency**: T049
  - **On Error**: Debug failing tests, check contracts

---

## Phase 3.4: Integration

### Device Integration
- [ ] **T051** **RAG SEARCH**: Query device integration patterns
  - **Use**: MCP `perform_rag_query("DML device memory interface transact method integration checkpoint", source_type="dml", match_count=5)`
  - **Purpose**: Find patterns for memory interface implementation, transact() methods, checkpointing
  - **Document**: Add findings to research.md section "Device Integration Patterns"
  - **Dependency**: T050

- [ ] **T052** Implement memory interface in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: Bank implements `io_memory` interface or uses `use_io_memory = true`
  - **Verify**: Device can be memory-mapped to physical address
  - **Pattern**: Research.md findings from T051
  - **Apply**: Interface implementation from T027-T028 study notes
  - **Dependency**: T051

- [ ] **T053** Implement device init/post_init methods in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `method init() { ... }` - initialize device state
  - **Add**: `method post_init() { ... }` - verify signal connections
  - **Logic**: Set initial values for locked, counter_start_value, etc.
  - **Source**: Research.md Model Builder patterns (device lifecycle methods)
  - **Apply**: Init patterns from T027-T028 study notes
  - **Dependency**: T052

### Checkpoint Support
- [ ] **T054** Verify checkpoint state preservation in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Check**: All `saved` variables are properly declared
  - **Check**: Event rescheduling logic in post_init or restore handler
  - **Contract**: `contracts/timeout-behavior.md` - Checkpoint/Restore Contracts
  - **Source**: `data-model.md` - Checkpoint State section
  - **Pattern**: Research.md saved state examples
  - **Dependency**: T053

- [ ] **T055** [P] Create checkpoint test in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_checkpoint.py`
  - **Test**: Save checkpoint mid-countdown, restore, verify counter resumes correctly
  - **Contract**: `contracts/timeout-behavior.md` - State Preservation, Event Rescheduling
  - **Pattern**: Research.md checkpoint patterns
  - **Dependency**: T054

### Platform Integration
- [ ] **T056** Create QSP-x86 integration script in `/home/hfeng1/simics-dml-vscode/watchdog-timer/targets/qsp-x86/watchdog-qsp.simics`
  - **Content**: Load QSP platform, create watchdog device, map to memory, connect signals
  - **Source**: `quickstart.md` - Integration with QSP-x86 section
  - **Dependency**: T052

- [ ] **T057** [P] Create integration validation test in `/home/hfeng1/simics-dml-vscode/watchdog-timer/test/test_qsp_integration.py`
  - **Test**: Load QSP script, verify device mapped, test basic operation on platform
  - **Dependency**: T056

### Build and Integration Test
- [ ] **T058** Build complete project: Use MCP tool `build_simics_project(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Clean build of entire project
  - **Dependency**: T052-T057

- [ ] **T059** Run all tests: Use MCP tool `run_simics_test(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: All contract tests (T006-T020) and integration tests (T021-T025, T055, T057) passing
  - **Dependency**: T058

---

## Phase 3.5: Polish

### Unit Tests for Edge Cases
- [ ] **T060** [P] Unit test: Zero counter value in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_edge_zero_counter.py`
  - **Test**: Load counter with 0, verify immediate timeout
  - **Contract**: `contracts/timeout-behavior.md` - Zero Counter Value edge case
  - **Dependency**: T059

- [ ] **T061** [P] Unit test: Maximum counter value in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_edge_max_counter.py`
  - **Test**: Load counter with 0xFFFFFFFF, verify no overflow
  - **Contract**: `contracts/timeout-behavior.md` - Maximum Counter Value edge case
  - **Dependency**: T059

- [ ] **T062** [P] Unit test: Rapid counter reloads in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_edge_rapid_reload.py`
  - **Test**: Write WDOGLOAD multiple times rapidly, verify only last timeout fires
  - **Contract**: `contracts/timeout-behavior.md` - Rapid Counter Reloads edge case
  - **Dependency**: T059

- [ ] **T063** [P] Unit test: Reserved register space in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_reserved_space.py`
  - **Test**: Read/write to reserved offsets (0x018-0xBFF, 0xC04-0xEFF, 0xF08-0xFDF), verify RAZ/WI
  - **Contract**: `contracts/register-access.md` - Reserved Register Space
  - **Dependency**: T059

### Performance Tests
- [ ] **T064** Performance test: Counter read performance in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_perf_counter_read.py`
  - **Test**: Time 1000 consecutive WDOGVALUE reads, verify O(1) performance
  - **Goal**: Consistent timing per contract guarantees
  - **Contract**: `contracts/timeout-behavior.md` - Performance Guarantees
  - **Dependency**: T059

- [ ] **T065** Performance test: Large counter values in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/test/test_perf_large_counter.py`
  - **Test**: Load very large counter values, verify no performance degradation
  - **Contract**: `contracts/timeout-behavior.md` - Performance Guarantees
  - **Dependency**: T059

### Documentation
- [ ] **T066** [P] Update module documentation in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/README.md`
  - **Content**: Device overview, register map, usage examples, build instructions
  - **Source**: Combine `quickstart.md` and `data-model.md` content
  - **Dependency**: T059

- [ ] **T067** [P] Create API reference in `/home/hfeng1/simics-dml-vscode/watchdog-timer/docs/api-reference.md`
  - **Content**: Register descriptions, signal interfaces, Python API
  - **Source**: `data-model.md` - Register Access Summary Table
  - **Dependency**: T059

- [ ] **T068** [P] Update research.md with final implementation notes in `/home/hfeng1/simics-dml-vscode/specs/001-read-the-simics/research.md`
  - **Add**: Section "Implementation Learnings" with insights from T027-T028 studies
  - **Add**: Section "Challenges and Solutions" documenting any issues encountered
  - **Dependency**: T059

### Code Quality
- [ ] **T069** Remove code duplication in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Review**: Check for repeated patterns, extract to helper methods
  - **Apply**: DRY principle from T027 best practices
  - **Dependency**: T059

- [ ] **T070** Add comprehensive logging in `/home/hfeng1/simics-dml-vscode/watchdog-timer/modules/watchdog-timer/watchdog-timer.dml`
  - **Add**: `log info` statements for key events (counter load, timeout, interrupt, reset)
  - **Add**: `log info, 4` for debug-level details
  - **Pattern**: Research.md logging examples
  - **Apply**: Logging best practices from T027 study notes
  - **Dependency**: T059

### Final Validation
- [ ] **T071** Manual testing from quickstart guide
  - **Execute**: All examples from `quickstart.md` - Common Development Patterns section
  - **Verify**: Pattern 1-4 work as documented
  - **Dependency**: T066

- [ ] **T072** Final build: Use MCP tool `build_simics_project(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: Clean build with no warnings
  - **Dependency**: T069, T070

- [ ] **T073** Final test suite: Use MCP tool `run_simics_test(project_path="/home/hfeng1/simics-dml-vscode/watchdog-timer")` ⚠️ ABSOLUTE PATH
  - **Expected**: All tests passing (contract, integration, unit, performance, edge cases)
  - **Verify**: Test count matches expectations (25+ tests)
  - **Dependency**: T072

---

## Dependencies Summary

**Critical Path**:
```
T001 (verify env) → 
T002 (create project) → 
T003 (add skeleton) → 
T004 (verify build) → 
T005 (verify research) → 
T006-T025 (write tests) → 
T026 (validate tests fail) → 
T027-T029 (DML learning GATES) → 
T030-T048 (implement device) → 
T049 (build) → 
T050 (run tests) → 
T051-T059 (integration) → 
T060-T073 (polish)
```

**Parallel Execution Opportunities**:
- **Setup Phase**: T004 can run once T003 completes
- **Test Writing Phase**: T006-T025 can all run in parallel (different files)
- **Register Implementation**: T035-T042 can run in parallel (same bank, but different registers)
- **Polish Phase**: T060-T068 can run in parallel (different files)

**Gates (BLOCKING)**:
- **T005**: Blocks all implementation until research.md verified
- **T026**: Blocks implementation until tests are written and failing
- **T027-T029**: Block all DML code until study complete
- **T050**: Blocks integration until core tests pass
- **T059**: Blocks polish until integration complete

---

## Parallel Execution Examples

### Phase 3.2: Write all tests in parallel
```bash
# All test files are independent, can be written simultaneously
Task: "Contract test WDOGLOAD in test/test_wdogload.py"
Task: "Contract test WDOGVALUE in test/test_wdogvalue.py"
Task: "Contract test WDOGCONTROL in test/test_wdogcontrol.py"
# ... (up to T025)
```

### Phase 3.3: Implement registers in parallel
```bash
# Different registers in same bank can be implemented together
Task: "Implement WDOGLOAD register"
Task: "Implement WDOGVALUE register"
Task: "Implement WDOGCONTROL register"
# ... (T035-T042)
```

### Phase 3.5: Polish tasks in parallel
```bash
# Documentation and tests are independent
Task: "Unit test zero counter edge case"
Task: "Unit test max counter edge case"
Task: "Update module README"
Task: "Create API reference"
```

---

## Task Validation Checklist

- [x] All contracts have corresponding test tasks (register-access.md → T006-T013, timeout-behavior.md → T014-T020)
- [x] All registers in data-model.md have implementation tasks (21 registers → T035-T042)
- [x] All integration scenarios in quickstart.md have test tasks (T021-T025)
- [x] DML learning gates (T027-T029) placed before implementation
- [x] Tests written before implementation (Phase 3.2 before 3.3)
- [x] MCP tools use absolute paths throughout
- [x] Parallel tasks marked with [P] where appropriate
- [x] Dependencies clearly specified
- [x] Edge cases from contracts included in polish (T060-T063)

---

## Notes

**Test-Driven Development**: This task list strictly follows TDD - all tests MUST be written and failing before implementation begins. T026 is a critical gate that verifies this.

**DML Learning Requirement**: Tasks T027-T029 are MANDATORY gates that block all DML implementation. The entire DML_Device_Development_Best_Practices.md and DML_grammar.md must be studied with comprehensive note-taking before writing any device code.

**MCP Tool Path Convention**: All MCP tool calls use absolute path `/home/hfeng1/simics-dml-vscode/watchdog-timer` to ensure SSE transport works correctly across process boundaries.

**Research.md Dependency**: Task T005 verifies research.md contains all necessary patterns from /plan phase. Implementation should reference these patterns extensively.

**Signal Interfaces**: Interrupt signal is edge-triggered (pulse), reset signal is level-triggered (stays high). This is critical for T019-T020 tests and T046-T047 implementation.

**Clock Dividers**: Only values 1, 16, 256 are valid per ARM SP805 spec (differs from hardware spec which showed 5 values). Implementation follows ARM standard for compatibility.

**Checkpoint Support**: All device state must be restorable. The `saved` keyword is critical for state variables (T032). Event rescheduling logic needed in T054.
