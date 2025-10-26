# Tasks: Simics Watchdog Timer Device Implementation

**Status**: Not Started
**Input**: Design documents from `/home/hfeng1/latest-vscode/specs/001-create-a-comprehensive/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

---

## Format: `[ID] [P?] Description`
**[P]** = Can run in parallel (different files, no dependencies)
Include exact file paths in descriptions

**⚠️ CRITICAL - MCP Tool Paths (SSE Transport)**:
- **ALWAYS use ABSOLUTE paths** for MCP tools: `create_simics_project()`, `build_simics_project()`, `run_simics_test()`
- **NEVER use relative paths** like `"./simics-project"` or `"../project"`
- **WHY**: SSE transport MCP servers run in different process/directory context
- **HOW**: Use workspace root: `/home/hfeng1/latest-vscode/simics-project`
- **Example**: `create_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project")`

---

## Path Conventions

**Simics Project Structure**:
```
/home/hfeng1/latest-vscode/simics-project/
├── modules/
│   └── watchdog-timer/
│       ├── watchdog-timer.dml       # Main device implementation
│       ├── registers.dml            # Register bank definitions
│       ├── module_load.py           # Python module loading
│       ├── CMakeLists.txt           # Build configuration
│       └── test/
│           ├── tests.py             # Test suite registration
│           ├── s-basic-registers.py # Register access tests
│           ├── s-countdown.py       # Counter decrement tests
│           ├── s-interrupt.py       # Interrupt generation tests
│           ├── s-lock.py            # Lock protection tests
│           └── s-checkpoint.py      # Checkpoint/restore tests
```

---

## Phase 3.1: Setup (MCP Tool Automation)

- [x] **T001** Verify Simics MCP connection
  - **Tool**: `get_simics_version()`
  - **Validation**: Confirm Simics Base 7.57.0 accessible
  - **Duration**: 1 minute

- [x] **T002** Create Simics project workspace
  - **Tool**: `create_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project")`
  - **Validation**: Project directory created at `/home/hfeng1/latest-vscode/simics-project/`
  - **Duration**: 2 minutes

- [x] **T003** Add watchdog-timer device skeleton
  - **Tool**: `add_dml_device_skeleton(project_path="/home/hfeng1/latest-vscode/simics-project", device_name="watchdog-timer")`
  - **Validation**: Module directory created at `modules/watchdog-timer/` with skeleton files
  - **Duration**: 2 minutes

- [x] **T004** Checkout and build DML compiler
  - **Tool**: `checkout_and_build_dmlc(project_path="/home/hfeng1/latest-vscode/simics-project")`
  - **Validation**: DMLC compiler available in `modules/dmlc/`
  - **Duration**: 3 minutes

- [x] **T005** [P] Verify initial skeleton build
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Validation**: Skeleton compiles without errors
  - **Duration**: 2 minutes

- [x] **T006** **GATE**: Verify research.md from planning phase
  - **Action**: Confirm `/home/hfeng1/latest-vscode/specs/001-create-a-comprehensive/research.md` exists
  - **Content Check**: Verify 11 RAG query results present (8 mandatory + 3 requirement-driven)
  - **Key Findings**: sample_timer_device.dml pattern, lock protection strategy, checkpoint patterns
  - **Validation**: Research document contains implementation guidance from Phase 0
  - **Duration**: 2 minutes

- [x] **T007** Git commit: Project setup complete
  - **Command**: `git add simics-project/ && git commit -m "setup: watchdog-timer - Simics project created with device skeleton"`
  - **Duration**: 1 minute

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] **T008** [P] Basic register access test
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/s-basic-registers.py`
  - **Purpose**: Test read/write access to all 21 registers
  - **Pattern**: Use `dev_util.Register_LE` from research.md findings
  - **Test Cases**:
    - Read all registers and verify reset values
    - Write to writable registers (WDOGLOAD, WDOGCONTROL)
    - Verify read-only registers ignore writes (WDOGVALUE, WDOGRIS, WDOGMIS)
    - Verify write-only registers (WDOGINTCLR, WDOGITOP)
  - **Expected**: Tests FAIL (registers not implemented yet)
  - **Duration**: 30 minutes

- [ ] **T009** [P] Counter decrement test
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/s-countdown.py`
  - **Purpose**: Test cycle-based counter countdown
  - **Test Cases**:
    - Start counter with WDOGLOAD=0x100, verify WDOGVALUE decrements
    - Stop counter, verify WDOGVALUE holds constant
    - Reload counter while running, verify restart from new value
    - Test step_value clock divider (÷1, ÷16, ÷256)
  - **Expected**: Tests FAIL (counter logic not implemented)
  - **Duration**: 25 minutes

- [ ] **T010** [P] Interrupt generation test
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/s-interrupt.py`
  - **Purpose**: Test first timeout interrupt behavior
  - **Test Cases**:
    - Verify interrupt asserted when counter reaches zero
    - Verify WDOGRIS.RAWINT set to 1
    - Verify WDOGMIS.MASKINT follows INTEN enable
    - Verify WDOGINTCLR clears interrupt and reloads counter
    - Verify wdogint signal state
  - **Expected**: Tests FAIL (interrupt logic not implemented)
  - **Duration**: 25 minutes

- [ ] **T011** [P] Reset generation test
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/s-reset.py`
  - **Purpose**: Test second timeout reset behavior
  - **Test Cases**:
    - Verify reset NOT triggered when interrupt cleared in time
    - Verify reset triggered on second timeout if interrupt not cleared
    - Verify WDOGCONTROL.RESEN controls reset enable
    - Verify wdogres signal state
  - **Expected**: Tests FAIL (reset logic not implemented)
  - **Duration**: 20 minutes

- [ ] **T012** [P] Lock protection test
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/s-lock.py`
  - **Purpose**: Test register lock protection mechanism
  - **Test Cases**:
    - Verify device starts locked (WDOGLOCK reads as 1)
    - Verify protected register writes blocked when locked
    - Write magic value 0x1ACCE551 to unlock
    - Verify protected register writes accepted when unlocked
    - Verify any non-magic value relocks device
  - **Expected**: Tests FAIL (lock protection not implemented)
  - **Duration**: 20 minutes

- [ ] **T013** [P] Integration test mode test
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/s-integration-test.py`
  - **Purpose**: Test direct signal control in integration test mode
  - **Test Cases**:
    - Enable integration test mode via WDOGITCR.ITEN
    - Verify WDOGITOP directly controls wdogint signal
    - Verify WDOGITOP directly controls wdogres signal
    - Verify normal timeout logic bypassed in test mode
    - Disable test mode, verify normal operation restored
  - **Expected**: Tests FAIL (integration test mode not implemented)
  - **Duration**: 20 minutes

- [ ] **T014** [P] Checkpoint/restore test
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/s-checkpoint.py`
  - **Purpose**: Test state persistence across checkpoint operations
  - **Test Cases**:
    - Start counter, save checkpoint, verify state restored
    - Verify counter resumes counting from checkpoint value
    - Verify interrupt fires at correct time after restore
    - Verify lock state preserved
    - Verify integration test mode preserved
  - **Expected**: Tests FAIL (checkpoint support not implemented)
  - **Duration**: 25 minutes

- [ ] **T015** Create test suite registration
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/tests.py`
  - **Purpose**: Register all test scripts with Simics test framework
  - **Content**:
    ```python
    def tests(suite):
        suite.add_simics_test("s-basic-registers.py")
        suite.add_simics_test("s-countdown.py")
        suite.add_simics_test("s-interrupt.py")
        suite.add_simics_test("s-reset.py")
        suite.add_simics_test("s-lock.py")
        suite.add_simics_test("s-integration-test.py")
        suite.add_simics_test("s-checkpoint.py")
    ```
  - **Duration**: 5 minutes

- [ ] **T016** Validate test environment and confirm failures
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: All tests FAIL (implementation not started yet)
  - **Validation**: Red phase of TDD confirmed
  - **Duration**: 5 minutes

- [ ] **T017** Git commit: Test suite complete (all failing)
  - **Command**: `git add simics-project/modules/watchdog-timer/test/ && git commit -m "test: watchdog-timer - TDD test suite created (all tests failing)"`
  - **Duration**: 1 minute

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

**⚠️ GATE**: Do NOT proceed until T008-T016 complete and all tests are FAILING

- [ ] **T018** **GATE**: Study DML Device Development Best Practices
  - **File**: Read `/home/hfeng1/latest-vscode/.specify/memory/DML_Device_Development_Best_Practices.md`
  - **Action**: Document key learnings in research.md under new "DML Learning Notes" section
  - **Key Topics**:
    - DML 1.4 syntax patterns
    - Register bank organization
    - Saved vs session state variables
    - Event scheduling with `after` statement
    - Signal interface usage
  - **Duration**: 15 minutes

- [ ] **T019** **GATE**: Study DML Grammar Reference
  - **File**: Read `/home/hfeng1/latest-vscode/.specify/memory/DML_grammar.md`
  - **Action**: Document syntax rules in research.md
  - **Key Topics**:
    - Register array syntax `[i < size]`
    - Field bit range syntax `@ [bits]`
    - Method return type declarations
    - Template inheritance with `is` keyword
  - **Duration**: 15 minutes

- [ ] **T020** **GATE**: Review device skeleton structure
  - **File**: Read `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **Action**: Understand generated skeleton, plan modifications
  - **Duration**: 5 minutes

- [ ] **T021** [P] Implement register bank definitions
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/registers.dml`
  - **Reference**: data-model.md register definitions (21 registers)
  - **Pattern**: Apply DML 1.4 syntax from T018-T019 learnings
  - **Registers to Define**:
    - Control/Status: WDOGLOAD, WDOGVALUE, WDOGCONTROL, WDOGINTCLR, WDOGRIS, WDOGMIS
    - Lock: WDOGLOCK
    - Integration Test: WDOGITCR, WDOGITOP
    - Identification: WDOGPeriphID0-3, WDOGPCellID0-3
  - **Implementation**:
    ```dml
    bank regs {
        param register_size = 4;
        param byte_order = "little-endian";
        
        register WDOGLOAD @ 0x000 size 4 {
            param init_val = 0xFFFFFFFF;
        }
        
        register WDOGVALUE @ 0x004 size 4 is (read, read_only) {
            // Read-only, dynamically calculated
        }
        
        // ... all 21 registers ...
    }
    ```
  - **Duration**: 40 minutes

- [ ] **T022** Git commit: Register definitions
  - **Command**: `git add simics-project/modules/watchdog-timer/registers.dml && git commit -m "impl: watchdog-timer - register bank definitions complete"`
  - **Duration**: 1 minute

- [ ] **T023** Check DML syntax with local compiler
  - **Tool**: `check_with_dmlc(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Validation**: No syntax errors, AI diagnostics if errors found
  - **Duration**: 2 minutes

- [ ] **T024** [P] Build with register definitions
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Validation**: Clean build
  - **Duration**: 2 minutes

- [ ] **T025** Implement counter state variables and logic
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **Reference**: research.md sample_timer_device pattern
  - **State Variables**:
    ```dml
    bank regs {
        saved cycles_t counter_start_time;
        saved uint32 counter_start_value;
        saved uint32 step_value = 1;  // Clock divider
        saved bool interrupt_pending = false;
        saved bool reset_pending = false;
        saved bool lock_state = true;  // Start locked
        saved bool integration_test_mode = false;
    }
    ```
  - **WDOGVALUE Dynamic Read**:
    ```dml
    register WDOGVALUE @ 0x004 size 4 is (read, read_only) {
        method read() -> (uint64) {
            if ((WDOGCONTROL.val & 0x1) == 0) {
                return counter_start_value;
            }
            local cycles_t now = SIM_cycle_count(dev.obj);
            local cycles_t elapsed = now - counter_start_time;
            local uint32 decrements = cast(elapsed / step_value, uint32);
            if (decrements >= counter_start_value) return 0;
            return counter_start_value - decrements;
        }
    }
    ```
  - **Duration**: 35 minutes

- [ ] **T026** Implement WDOGCONTROL start/stop logic
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **Implementation**:
    ```dml
    register WDOGCONTROL @ 0x008 size 4 is (write, read) {
        method write(uint64 value) {
            if (lock_state) {
                log info, 2: "WDOGCONTROL write blocked by lock";
                return;
            }
            
            local bool was_enabled = (this.val & 0x1) != 0;
            this.val = value;
            local bool now_enabled = (value & 0x1) != 0;
            
            if (!was_enabled && now_enabled) {
                // Start counter
                counter_start_value = WDOGLOAD.val;
                counter_start_time = SIM_cycle_count(dev.obj);
                schedule_interrupt_timeout();
            } else if (was_enabled && !now_enabled) {
                // Stop counter
                cancel_interrupt_event();
                cancel_reset_event();
            }
        }
    }
    ```
  - **Duration**: 20 minutes

- [ ] **T027** Git commit: Counter logic
  - **Command**: `git add simics-project/modules/watchdog-timer/ && git commit -m "impl: watchdog-timer - counter state and control logic"`
  - **Duration**: 1 minute

- [ ] **T028** [P] Build with counter logic
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Duration**: 2 minutes

- [ ] **T029** Run tests to verify counter tests now pass
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: T009 (countdown test) now PASSES, others still FAIL
  - **Duration**: 3 minutes

- [ ] **T030** Implement signal connections
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **Implementation**:
    ```dml
    connect wdogint_signal is signal_connect {
        param documentation = "Watchdog interrupt output signal";
    }
    
    connect wdogres_signal is signal_connect {
        param documentation = "Watchdog reset output signal";
    }
    ```
  - **Duration**: 5 minutes

- [ ] **T031** Implement interrupt generation logic
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **Methods**:
    ```dml
    method schedule_interrupt_timeout() {
        cancel interrupt_event;
        if ((WDOGCONTROL.val & 0x1) == 0) return;
        
        local cycles_t cycles_to_interrupt = counter_start_value * step_value;
        after cycles_to_interrupt cycles: fire_interrupt();
    }
    
    method fire_interrupt() {
        if (integration_test_mode) return;
        
        interrupt_pending = true;
        WDOGRIS.val = 0x1;
        
        if ((WDOGCONTROL.val & 0x1) != 0) {
            wdogint_signal.set_level(1);
            log info, 2: "Watchdog interrupt asserted";
        }
        
        // Schedule reset event if enabled
        if ((WDOGCONTROL.val & 0x2) != 0) {
            local cycles_t cycles_to_reset = counter_start_value * step_value;
            after cycles_to_reset cycles: fire_reset();
        }
        
        // Reload counter
        counter_start_value = WDOGLOAD.val;
        counter_start_time = SIM_cycle_count(dev.obj);
    }
    ```
  - **Duration**: 30 minutes

- [ ] **T032** Implement WDOGINTCLR interrupt clear logic
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **Implementation**:
    ```dml
    register WDOGINTCLR @ 0x00C size 4 is (write) {
        method write(uint64 value) {
            if (lock_state) return;
            if (integration_test_mode) return;
            
            interrupt_pending = false;
            WDOGRIS.val = 0x0;
            wdogint_signal.set_level(0);
            
            // Reload counter
            counter_start_value = WDOGLOAD.val;
            counter_start_time = SIM_cycle_count(dev.obj);
            
            // Cancel reset event
            cancel reset_event;
            
            log info, 2: "Watchdog interrupt cleared";
        }
    }
    ```
  - **Duration**: 15 minutes

- [ ] **T033** Git commit: Interrupt logic
  - **Command**: `git add simics-project/modules/watchdog-timer/ && git commit -m "impl: watchdog-timer - interrupt generation and clearing"`
  - **Duration**: 1 minute

- [ ] **T034** [P] Build with interrupt logic
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Duration**: 2 minutes

- [ ] **T035** Run tests to verify interrupt tests now pass
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: T010 (interrupt test) now PASSES
  - **Duration**: 3 minutes

- [ ] **T036** Implement reset generation logic
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **Implementation**:
    ```dml
    method fire_reset() {
        if (integration_test_mode) return;
        
        reset_pending = true;
        wdogres_signal.set_level(1);
        log info, 2: "Watchdog reset asserted - system reset triggered";
    }
    ```
  - **Duration**: 10 minutes

- [ ] **T037** Git commit: Reset logic
  - **Command**: `git add simics-project/modules/watchdog-timer/ && git commit -m "impl: watchdog-timer - reset generation on second timeout"`
  - **Duration**: 1 minute

- [ ] **T038** [P] Build with reset logic
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Duration**: 2 minutes

- [ ] **T039** Run tests to verify reset tests now pass
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: T011 (reset test) now PASSES
  - **Duration**: 3 minutes

- [ ] **T040** Implement lock protection mechanism
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **WDOGLOCK Register**:
    ```dml
    register WDOGLOCK @ 0xC00 size 4 is (write, read) {
        param init_val = 0x00000001;  // Locked on reset
        
        method write(uint64 value) {
            if (value == 0x1ACCE551) {
                lock_state = false;
                this.val = 0;
                log info, 2: "Watchdog unlocked";
            } else {
                lock_state = true;
                this.val = 1;
                log info, 2: "Watchdog locked";
            }
        }
        
        method read() -> (uint64) {
            return lock_state ? 1 : 0;
        }
    }
    ```
  - **Update Protected Registers**: Add lock_state check to WDOGLOAD, WDOGCONTROL, WDOGINTCLR write methods
  - **Duration**: 20 minutes

- [ ] **T041** Git commit: Lock protection
  - **Command**: `git add simics-project/modules/watchdog-timer/ && git commit -m "impl: watchdog-timer - lock protection with magic value 0x1ACCE551"`
  - **Duration**: 1 minute

- [ ] **T042** [P] Build with lock protection
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Duration**: 2 minutes

- [ ] **T043** Run tests to verify lock tests now pass
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: T012 (lock test) now PASSES
  - **Duration**: 3 minutes

- [ ] **T044** Implement integration test mode
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **WDOGITCR Register**:
    ```dml
    register WDOGITCR @ 0xF00 size 4 is (write, read) {
        method write(uint64 value) {
            this.val = value;
            integration_test_mode = (value & 0x1) != 0;
            if (integration_test_mode) {
                log info, 2: "Integration test mode ENABLED";
            } else {
                log info, 2: "Integration test mode DISABLED";
            }
        }
    }
    ```
  - **WDOGITOP Register**:
    ```dml
    register WDOGITOP @ 0xF04 size 4 is (write) {
        method write(uint64 value) {
            if (!integration_test_mode) {
                log info, 2: "WDOGITOP write ignored - test mode disabled";
                return;
            }
            
            local bool wdogint_val = (value & 0x1) != 0;
            local bool wdogres_val = (value & 0x2) != 0;
            
            wdogint_signal.set_level(wdogint_val ? 1 : 0);
            wdogres_signal.set_level(wdogres_val ? 1 : 0);
            
            log info, 2: "Integration test: WDOGINT=%d, WDOGRES=%d", 
                         wdogint_val, wdogres_val;
        }
    }
    ```
  - **Duration**: 20 minutes

- [ ] **T045** Git commit: Integration test mode
  - **Command**: `git add simics-project/modules/watchdog-timer/ && git commit -m "impl: watchdog-timer - integration test mode for direct signal control"`
  - **Duration**: 1 minute

- [ ] **T046** [P] Build with integration test mode
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Duration**: 2 minutes

- [ ] **T047** Run tests to verify integration test mode tests now pass
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: T013 (integration test mode test) now PASSES
  - **Duration**: 3 minutes

- [ ] **T048** Implement checkpoint support (post_init)
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/watchdog-timer.dml`
  - **Implementation**:
    ```dml
    method post_init() {
        // Reschedule events after checkpoint restore
        if ((WDOGCONTROL.val & 0x1) != 0) {
            local cycles_t now = SIM_cycle_count(dev.obj);
            local cycles_t elapsed = now - counter_start_time;
            local cycles_t total_duration = counter_start_value * step_value;
            
            if (elapsed < total_duration) {
                local cycles_t remaining = total_duration - elapsed;
                after remaining cycles: fire_interrupt();
            } else if (interrupt_pending && (WDOGCONTROL.val & 0x2) != 0) {
                // Reschedule reset event
                local cycles_t remaining_to_reset = 
                    (counter_start_value * step_value) - 
                    (now - counter_start_time);
                if (remaining_to_reset > 0) {
                    after remaining_to_reset cycles: fire_reset();
                }
            }
        }
        
        log info, 2: "Watchdog checkpoint restored";
    }
    ```
  - **Duration**: 25 minutes

- [ ] **T049** Git commit: Checkpoint support
  - **Command**: `git add simics-project/modules/watchdog-timer/ && git commit -m "impl: watchdog-timer - checkpoint/restore support with event rescheduling"`
  - **Duration**: 1 minute

- [ ] **T050** [P] Build with checkpoint support
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Duration**: 2 minutes

- [ ] **T051** Run tests to verify checkpoint tests now pass
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: T014 (checkpoint test) now PASSES
  - **Duration**: 3 minutes

- [ ] **T052** Implement peripheral identification registers
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/registers.dml`
  - **Implementation**:
    ```dml
    register WDOGPeriphID0 @ 0xFE0 size 4 is (read, read_only) {
        param init_val = 0x00000005;
    }
    register WDOGPeriphID1 @ 0xFE4 size 4 is (read, read_only) {
        param init_val = 0x00000018;
    }
    register WDOGPeriphID2 @ 0xFE8 size 4 is (read, read_only) {
        param init_val = 0x00000018;
    }
    register WDOGPeriphID3 @ 0xFEC size 4 is (read, read_only) {
        param init_val = 0x00000000;
    }
    register WDOGPCellID0 @ 0xFF0 size 4 is (read, read_only) {
        param init_val = 0x0000000D;
    }
    register WDOGPCellID1 @ 0xFF4 size 4 is (read, read_only) {
        param init_val = 0x000000F0;
    }
    register WDOGPCellID2 @ 0xFF8 size 4 is (read, read_only) {
        param init_val = 0x00000005;
    }
    register WDOGPCellID3 @ 0xFFC size 4 is (read, read_only) {
        param init_val = 0x000000B1;
    }
    ```
  - **Duration**: 10 minutes

- [ ] **T053** Git commit: Identification registers
  - **Command**: `git add simics-project/modules/watchdog-timer/ && git commit -m "impl: watchdog-timer - peripheral and PrimeCell identification registers"`
  - **Duration**: 1 minute

- [ ] **T054** [P] Final build verification
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project", module="watchdog-timer")`
  - **Duration**: 2 minutes

- [ ] **T055** Run complete test suite - all tests should pass
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: ALL tests PASS (T008-T014)
  - **Validation**: Green phase of TDD confirmed
  - **Duration**: 5 minutes

---

## Phase 3.4: Integration (Platform Integration)

- [ ] **T056** **RAG SEARCH**: Platform integration patterns
  - **Tool**: `perform_rag_query("Simics device platform integration memory map interrupt routing", source_type="source", match_count=5)`
  - **Purpose**: Find patterns for integrating device into QSP-x86 platform
  - **Duration**: 5 minutes

- [ ] **T057** Create platform configuration script
  - **File**: `/home/hfeng1/latest-vscode/simics-project/scripts/qsp-watchdog-config.py`
  - **Purpose**: Configure watchdog device in QSP-x86 platform at address 0x1000
  - **Implementation**:
    ```python
    # Create watchdog device
    watchdog = SIM_create_object('watchdog-timer', 'watchdog0', [])
    
    # Map into memory space at 0x1000
    phys_mem = conf.board.mb.phys_mem
    phys_mem.map = phys_mem.map + [[0x1000, watchdog, 0, 0, 0x1000]]
    
    # Connect interrupt signal to interrupt controller
    watchdog.wdogint_signal = conf.board.mb.sb.pic
    
    # Connect reset signal to system reset controller
    watchdog.wdogres_signal = conf.board.mb.sb.reset_controller
    ```
  - **Duration**: 30 minutes

- [ ] **T058** Git commit: Platform integration script
  - **Command**: `git add simics-project/scripts/ && git commit -m "integ: watchdog-timer - QSP-x86 platform integration configuration"`
  - **Duration**: 1 minute

- [ ] **T059** Create end-to-end integration test
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/test/s-platform-integration.py`
  - **Purpose**: Test device integrated into full platform
  - **Test Cases**:
    - Boot QSP-x86 platform with watchdog device
    - Access watchdog registers via memory-mapped I/O
    - Trigger interrupt, verify platform interrupt controller receives it
    - Trigger reset, verify platform reset occurs
  - **Duration**: 40 minutes

- [ ] **T060** Git commit: Integration test
  - **Command**: `git add simics-project/modules/watchdog-timer/test/ && git commit -m "integ: watchdog-timer - platform integration test"`
  - **Duration**: 1 minute

- [ ] **T061** [P] Build complete project
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project")`
  - **Duration**: 3 minutes

- [ ] **T062** Run integration test
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: Integration test passes, device functional in platform
  - **Duration**: 5 minutes

---

## Phase 3.5: Polish (Documentation and Validation)

- [ ] **T063** [P] Update module README
  - **File**: `/home/hfeng1/latest-vscode/simics-project/modules/watchdog-timer/README.md`
  - **Content**:
    - Device overview (ARM PrimeCell SP805 compatible)
    - Register map summary
    - Usage examples
    - Test execution instructions
  - **Duration**: 20 minutes

- [ ] **T064** [P] Verify all acceptance scenarios from spec.md
  - **Reference**: `/home/hfeng1/latest-vscode/specs/001-create-a-comprehensive/spec.md` scenarios 1-7
  - **Action**: Manually execute each scenario, document results
  - **Scenarios**:
    1. Counter decrement and interrupt generation ✓
    2. Second timeout reset generation ✓
    3. Lock protection prevents modification ✓
    4. WDOGVALUE reflects countdown ✓
    5. WDOGINTCLR clears and reloads ✓
    6. Integration test mode signal control ✓
    7. Checkpoint/restore preserves state ✓
  - **Duration**: 30 minutes

- [ ] **T065** [P] Performance validation
  - **Test**: Verify counter accuracy at different step values
  - **Test**: Verify interrupt latency is deterministic
  - **Test**: Verify checkpoint/restore overhead acceptable
  - **Duration**: 20 minutes

- [ ] **T066** Remove code duplication and refactor
  - **Action**: Review DML files for duplicated logic
  - **Focus**: Event scheduling code, lock protection checks
  - **Duration**: 15 minutes

- [ ] **T067** Final code review and cleanup
  - **Action**: Review all DML files for:
    - Consistent naming conventions
    - Proper logging levels
    - Complete documentation strings
    - Removed debug code
  - **Duration**: 20 minutes

- [ ] **T068** Git commit: Documentation and polish
  - **Command**: `git add simics-project/ && git commit -m "polish: watchdog-timer - documentation, refactoring, validation complete"`
  - **Duration**: 1 minute

- [ ] **T069** [P] Final build and test verification
  - **Tool**: `build_simics_project(project_path="/home/hfeng1/latest-vscode/simics-project")`
  - **Tool**: `run_simics_test(project_path="/home/hfeng1/latest-vscode/simics-project", suite="modules/watchdog-timer/test")`
  - **Expected**: 100% test pass rate
  - **Duration**: 5 minutes

- [ ] **T070** Update implementation plan with completion status
  - **File**: `/home/hfeng1/latest-vscode/specs/001-create-a-comprehensive/plan.md`
  - **Action**: Mark Progress Tracking section as complete
  - **Duration**: 5 minutes

---

## Dependencies

**Critical Path**:
```
Setup (T001-T007) → 
Tests First (T008-T017) → 
DML Learning Gates (T018-T020) → 
Core Implementation (T021-T055) → 
Integration (T056-T062) → 
Polish (T063-T070)
```

**Key Dependencies**:
- T001-T006: Setup must complete before tests
- T007: Git commit before proceeding to tests
- T008-T016: All tests must FAIL before implementation
- T017: Git commit confirming red phase
- T018-T020: DML learning gates block implementation
- T021-T055: Sequential implementation with incremental testing
- Git commits before every build/test task
- T056-T062: Integration requires completed implementation
- T063-T070: Polish requires completed integration

**Parallel Opportunities**:
- T008-T014: Test files (different files, can write in parallel)
- T021, T030: Register definitions and signal connections (different concerns)
- Build/test tasks marked [P] when no state changes between

---

## Parallel Execution Example

**Phase 3.2 - Writing Tests (T008-T014)**:
```bash
# All test files are independent, can be written in parallel
Task T008: "Basic register access test in s-basic-registers.py"
Task T009: "Counter decrement test in s-countdown.py"
Task T010: "Interrupt generation test in s-interrupt.py"
Task T011: "Reset generation test in s-reset.py"
Task T012: "Lock protection test in s-lock.py"
Task T013: "Integration test mode test in s-integration-test.py"
Task T014: "Checkpoint/restore test in s-checkpoint.py"
```

---

## Notes

- **MCP Tool Paths**: All tools use absolute path `/home/hfeng1/latest-vscode/simics-project`
- **Git Commits**: Mandatory before every build and test execution
- **TDD Enforcement**: Tests T008-T017 must complete and FAIL before T018
- **DML Learning**: T018-T020 gates block implementation start
- **Incremental Testing**: After each implementation milestone (counter, interrupt, reset, lock, test mode, checkpoint), run tests to verify progress
- **Test Pass Progression**:
  - After T029: s-countdown.py passes
  - After T035: s-interrupt.py passes
  - After T039: s-reset.py passes
  - After T043: s-lock.py passes
  - After T047: s-integration-test.py passes
  - After T051: s-checkpoint.py passes
  - After T055: ALL tests pass
- **Duration Estimates**: Total ~10-12 hours for experienced Simics developer

---

## Validation Checklist

- [x] All 21 registers have test coverage (T008)
- [x] All behavioral contracts have tests (T009-T014)
- [x] All tests written before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks truly independent (test files, different concerns)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All MCP tool calls use absolute paths (SSE transport)
- [x] Build validation tasks after implementation changes
- [x] Test execution tasks verify incremental progress
- [x] Git commits before every build/test task
- [x] research.md from /plan phase referenced (T006 gate)
- [x] DML learning gates precede implementation (T018-T020)
- [x] Integration test validates platform connectivity (T059-T062)
- [x] All 7 acceptance scenarios validated (T064)

---

**Status**: Ready for execution
**Next**: Begin with T001 (Verify Simics MCP connection)
