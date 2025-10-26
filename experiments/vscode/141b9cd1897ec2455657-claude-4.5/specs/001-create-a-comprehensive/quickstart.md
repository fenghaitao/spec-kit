# Quickstart Guide: Simics Watchdog Timer Device

**Branch**: `001-create-a-comprehensive`
**Phase**: Phase 1 - Design
**Created**: 2025
**Status**: Complete

---

## Goal

Build and integrate an ARM PrimeCell SP805 compatible watchdog timer device into Simics QSP-x86 platform, then validate interrupt and reset generation functionality.

---

## Prerequisites

- **Simics Base**: 7.57.0 or later
- **QSP-x86 Platform**: 7.38.0 or later  
- **Simics Python**: 7.13.0 or later
- **Model Builder**: 7.44.0 or later
- **Development Tools**: GCC/Clang, Make/CMake
- **Knowledge**: DML 1.4 syntax, Python basics

---

## Step 1: Project Setup

**Task**: Create Simics project workspace

**Actions**:
1. Create new Simics project at repository root
2. Configure project for DML 1.4 device development
3. Set project name to "simics-project"
4. Target QSP-x86 platform for integration

**Validation**:
- Project directory created: `simics-project/`
- Project configuration files generated
- Project successfully listed in Simics

**Expected Duration**: 5 minutes

---

## Step 2: Add Device Module

**Task**: Add watchdog-timer device module to project

**Actions**:
1. Create module directory: `modules/watchdog-timer/`
2. Add DML device skeleton with standard imports
3. Configure module for DML 1.4 compilation
4. Create CMakeLists.txt with build rules

**Validation**:
- Module directory exists: `modules/watchdog-timer/`
- Device skeleton compiles without errors
- Module appears in project module list

**Expected Files**:
```
modules/watchdog-timer/
├── watchdog-timer.dml
├── CMakeLists.txt
└── module_load.py
```

**Expected Duration**: 10 minutes

---

## Step 3: Implement Register Bank

**Task**: Define all 21 registers with proper addresses and access types

**Actions**:
1. Create `registers.dml` file
2. Define `bank regs` with 4-byte register size, little-endian
3. Implement control registers (WDOGLOAD, WDOGCONTROL, etc.)
4. Implement status registers (WDOGVALUE, WDOGRIS, WDOGMIS)
5. Implement lock register (WDOGLOCK) with magic value check
6. Implement identification registers (PeriphID, PCellID)
7. Add integration test registers (WDOGITCR, WDOGITOP)

**Validation**:
- All 21 registers defined at correct offsets
- Register access types match specification (RO/WO/RW)
- Device compiles without errors
- Register map visible via Simics CLI

**Test Command**: `[DEVICE_NAME].bank.regs.WDOGLOAD`

**Expected Duration**: 30 minutes

---

## Step 4: Implement Counter Logic

**Task**: Add cycle-based countdown timer

**Actions**:
1. Add saved state variables: `counter_start_time`, `counter_start_value`, `step_value`
2. Implement dynamic WDOGVALUE.read() method using SIM_cycle_count()
3. Implement WDOGLOAD.write() to update counter start values
4. Implement WDOGCONTROL.write() to start/stop counter
5. Schedule interrupt timeout event using `after` statement

**Validation**:
- WDOGVALUE decrements over time when counter enabled
- Counter starts when WDOGCONTROL.INTEN transitions 0→1
- Counter stops when WDOGCONTROL.INTEN transitions 1→0
- Counter reloads when WDOGLOAD written while running

**Test Command**: Enable counter, run simulation, read WDOGVALUE periodically

**Expected Duration**: 45 minutes

---

## Step 5: Implement Interrupt Generation

**Task**: Add first timeout interrupt functionality

**Actions**:
1. Add signal connection: `connect wdogint_signal is signal_connect`
2. Implement `fire_interrupt()` method called by timeout event
3. Set `interrupt_pending` flag when timeout occurs
4. Assert wdogint signal: `wdogint_signal.set_level(1)`
5. Update WDOGRIS.RAWINT register value
6. Implement WDOGINTCLR.write() to clear interrupt and reload counter

**Validation**:
- Interrupt asserted when counter reaches zero (first timeout)
- WDOGRIS.RAWINT = 1 after timeout
- WDOGMIS.MASKINT = 1 when INTEN enabled
- Writing WDOGINTCLR clears interrupt and reloads counter
- wdogint signal observable in Simics

**Test Commands**:
- Set WDOGLOAD to small value (e.g., 0x100)
- Enable WDOGCONTROL.INTEN
- Run simulation until timeout
- Verify WDOGRIS register shows interrupt
- Write WDOGINTCLR
- Verify interrupt cleared

**Expected Duration**: 30 minutes

---

## Step 6: Implement Reset Generation

**Task**: Add second timeout reset functionality

**Actions**:
1. Add signal connection: `connect wdogres_signal is signal_connect`
2. Schedule reset event in `fire_interrupt()` method if RESEN enabled
3. Implement `fire_reset()` method called by second timeout event
4. Assert wdogres signal: `wdogres_signal.set_level(1)`
5. Cancel reset event when WDOGINTCLR written (interrupt cleared)

**Validation**:
- Reset NOT asserted when interrupt cleared before second timeout
- Reset asserted when counter reaches zero second time (interrupt not cleared)
- wdogres signal observable in Simics
- WDOGCONTROL.RESEN controls reset enable

**Test Commands**:
- Set WDOGLOAD to small value
- Enable both WDOGCONTROL.INTEN and WDOGCONTROL.RESEN
- Run simulation without clearing interrupt
- Verify reset triggered after second timeout

**Expected Duration**: 30 minutes

---

## Step 7: Implement Lock Protection

**Task**: Add register write protection mechanism

**Actions**:
1. Add saved state variable: `lock_state` (initialized to true)
2. Implement WDOGLOCK.write() checking for magic value 0x1ACCE551
3. Add lock state check in protected register write methods
4. Protected registers: WDOGLOAD, WDOGCONTROL, WDOGINTCLR

**Validation**:
- Device starts locked (WDOGLOCK.read() = 1)
- Writing 0x1ACCE551 unlocks (WDOGLOCK.read() = 0)
- Writing any other value locks (WDOGLOCK.read() = 1)
- Writes to protected registers ignored when locked
- Writes to protected registers accepted when unlocked

**Test Commands**:
- Read WDOGLOCK (expect 1)
- Attempt write to WDOGLOAD (expect blocked)
- Write 0x1ACCE551 to WDOGLOCK
- Write to WDOGLOAD (expect success)
- Write 0x0 to WDOGLOCK (relock)

**Expected Duration**: 20 minutes

---

## Step 8: Implement Integration Test Mode

**Task**: Add direct signal control for testing

**Actions**:
1. Add saved state variable: `integration_test_mode`
2. Implement WDOGITCR.write() to enable/disable test mode
3. Implement WDOGITOP.write() to directly control signals in test mode
4. Bypass normal interrupt/reset logic when test mode enabled

**Validation**:
- WDOGITCR.ITEN controls test mode enable
- WDOGITOP.WDOGINT directly controls wdogint signal when test mode enabled
- WDOGITOP.WDOGRES directly controls wdogres signal when test mode enabled
- Normal timeout logic bypassed in test mode
- WDOGITOP writes ignored when test mode disabled

**Test Commands**:
- Write 1 to WDOGITCR (enable test mode)
- Write 0x1 to WDOGITOP (assert WDOGINT)
- Verify wdogint signal asserted
- Write 0x2 to WDOGITOP (assert WDOGRES)
- Verify wdogres signal asserted

**Expected Duration**: 25 minutes

---

## Step 9: Add Checkpoint Support

**Task**: Enable state save/restore

**Actions**:
1. Mark all state variables as `saved` (not `session`)
2. Implement `post_init()` method to reschedule events on restore
3. Calculate remaining cycles for pending events after restore
4. Test checkpoint save and restore

**Validation**:
- Create checkpoint while counter running
- Restore checkpoint
- Counter resumes from exact checkpoint value
- Interrupt fires at correct time after restore
- Lock state preserved
- Integration test mode preserved

**Test Commands**:
- Start counter with WDOGLOAD = 0x10000
- Run simulation for 1000 cycles
- Save checkpoint
- Run additional 1000 cycles
- Restore checkpoint
- Verify WDOGVALUE matches value at checkpoint time
- Continue simulation, verify interrupt fires at expected time

**Expected Duration**: 30 minutes

---

## Step 10: Create Test Suite

**Task**: Implement Python test scripts

**Actions**:
1. Create `test/` directory in module
2. Create test suite registration file: `tests.py`
3. Create test scripts:
   - `s-basic-registers.py`: Register read/write tests
   - `s-countdown.py`: Counter decrement tests
   - `s-interrupt.py`: Interrupt generation tests
   - `s-lock.py`: Lock protection tests
   - `s-checkpoint.py`: Checkpoint/restore tests
4. Use `stest` assertions and `dev_util.Register_LE` for access

**Validation**:
- All tests pass
- Test coverage includes all functional requirements
- Tests verify all acceptance scenarios from specification

**Test Command**: Run test suite using Simics test framework

**Expected Duration**: 60 minutes

---

## Step 11: Platform Integration

**Task**: Integrate device into QSP-x86 platform

**Actions**:
1. Create platform configuration script
2. Instantiate watchdog device at base address 0x1000
3. Connect wdogint signal to platform interrupt controller
4. Connect wdogres signal to platform reset controller
5. Map device memory into platform physical memory space

**Validation**:
- Device accessible at platform address 0x1000
- Interrupt routing works (visible in interrupt controller)
- Reset routing works (triggers platform reset)
- Platform boots and runs with device integrated

**Test Commands**:
- Boot platform
- Access watchdog registers via memory-mapped I/O
- Trigger interrupt, verify platform interrupt controller receives it
- Trigger reset, verify platform resets

**Expected Duration**: 45 minutes

---

## Step 12: End-to-End Validation

**Task**: Run complete acceptance scenario tests

**Actions**:
1. Execute all 7 acceptance scenarios from specification
2. Verify each scenario success criteria
3. Document any issues found
4. Fix issues and retest

**Validation Scenarios**:
1. ✅ Counter decrement and interrupt generation
2. ✅ Second timeout reset generation
3. ✅ Lock protection prevents inadvertent modification
4. ✅ WDOGVALUE accurately reflects countdown
5. ✅ WDOGINTCLR clears interrupt and reloads counter
6. ✅ Integration test mode direct signal control
7. ✅ Checkpoint/restore preserves state and timing

**Expected Duration**: 30 minutes

---

## Troubleshooting

### Issue: Device doesn't compile

**Symptoms**: DML compilation errors, undefined symbols

**Solutions**:
- Verify DML 1.4 syntax (register arrays use `[i < size]`, fields use `@ [bits]`)
- Check all imports present (`utility.dml`, `simics/devs/signal.dml`)
- Verify method signatures match DML 1.4 requirements (explicit return types)
- Check CMakeLists.txt configuration

### Issue: Counter doesn't decrement

**Symptoms**: WDOGVALUE stays constant

**Solutions**:
- Verify WDOGCONTROL.INTEN = 1 (counter enabled)
- Check `counter_start_time` recorded when counter started
- Verify `get_current_counter()` calculation uses SIM_cycle_count()
- Ensure step_value != 0

### Issue: Interrupt never fires

**Symptoms**: WDOGRIS.RAWINT stays 0 after timeout

**Solutions**:
- Verify interrupt event scheduled correctly
- Check event duration calculation: `counter_value * step_value`
- Verify `fire_interrupt()` method sets `interrupt_pending` flag
- Check WDOGCONTROL.INTEN enabled

### Issue: Lock protection doesn't work

**Symptoms**: Writes succeed when locked

**Solutions**:
- Verify `lock_state` initialized to true
- Check protected register write methods check `lock_state` before accepting write
- Verify WDOGLOCK.write() properly detects magic value 0x1ACCE551
- Ensure lock_state marked as `saved` variable

### Issue: Checkpoint restore loses state

**Symptoms**: Counter resets to 0 after restore

**Solutions**:
- Mark all state variables as `saved` (not `session`)
- Implement `post_init()` to reschedule events
- Verify event rescheduling calculates remaining cycles correctly
- Check register values also marked as saved (automatic for register fields)

### Issue: Platform integration fails

**Symptoms**: Device not accessible at expected address

**Solutions**:
- Verify memory-space mapping includes device address range
- Check base address configuration in platform script
- Verify io_memory interface implemented
- Check device instantiation succeeded (no errors in log)

---

## Success Criteria

### Functional Completeness
- ✅ All 21 registers implemented and accessible
- ✅ Counter decrements accurately with cycle-based timing
- ✅ Interrupt generated on first timeout
- ✅ Reset generated on second timeout
- ✅ Lock protection prevents inadvertent writes
- ✅ Integration test mode controls signals directly
- ✅ Checkpoint/restore preserves state and timing

### Quality Gates
- ✅ All acceptance scenarios pass
- ✅ Test suite passes with 100% success rate
- ✅ No DML compilation warnings
- ✅ Device integrates into QSP-x86 platform
- ✅ Interrupt and reset signals route correctly
- ✅ Documentation complete (data-model.md, contracts/, this guide)

### Observability
- ✅ All registers readable via Simics CLI
- ✅ Device state visible through status registers
- ✅ Log messages for key events (unlock, interrupt, reset)
- ✅ Signals observable in Simics

---

## Next Steps

After completing this quickstart:

1. **Performance Validation**: Benchmark counter accuracy at different clock speeds
2. **Edge Case Testing**: Test boundary conditions (counter = 0, counter = 0xFFFFFFFF)
3. **Platform Variants**: Test on additional platforms beyond QSP-x86
4. **Documentation**: Update API documentation with usage examples
5. **Code Review**: Submit for peer review before production use

---

## Reference Materials

- **Specification**: `specs/001-create-a-comprehensive/spec.md`
- **Data Model**: `specs/001-create-a-comprehensive/data-model.md`
- **Contracts**: `specs/001-create-a-comprehensive/contracts/`
- **Research**: `specs/001-create-a-comprehensive/research.md`
- **DML 1.4 Reference**: Simics documentation (linux64/doc/simics)
- **ARM Spec**: ARM PrimeCell SP805 Technical Reference Manual

---

**Document Status**: Complete  
**Total Estimated Time**: 6 hours (for experienced Simics developer)  
**Next Phase**: Phase 2 - /tasks command creates tasks.md
