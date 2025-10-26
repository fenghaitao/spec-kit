# Quick Start: Simics Watchdog Timer Device

## Goal
Validate the ARM PrimeCell SP805 watchdog timer device model by testing basic counter operation, interrupt generation on first timeout, and reset generation on second timeout.

## Prerequisites

**Environment Requirements** (from research.md):
- Simics Base 7.57.0
- Python package (1033, v7.13.0)
- QSP-x86 platform (2096, v7.38.0) or compatible platform
- Development environment with DML 1.4 compiler
- Simics project structure created at repository root

**Required Packages**:
- Simics-Base (1000, v7.57.0)
- Python (1033, v7.13.0)
- At least one platform package (e.g., QSP-x86)

## Validation Steps

### Step 1: Basic Register Access Validation
**What to do**:
1. Create Simics project and build the watchdog timer device module
2. Instantiate the device in a Simics configuration
3. Map the device to a memory address (e.g., 0x10000000)
4. Read identification registers to verify device presence

**Expected Result**:
- WDOGPERIPHID0 reads as 0x24
- WDOGPERIPHID1 reads as 0xB8
- WDOGPERIPHID2 reads as 0x1B
- WDOGPCELLID0 reads as 0x0D
- WDOGPCELLID1 reads as 0xF0
- WDOGPCELLID2 reads as 0x05
- WDOGPCELLID3 reads as 0xB1

**Success Criteria**:
- All identification registers return correct constant values
- Device is accessible via memory-mapped I/O
- No errors or exceptions during register reads

### Step 2: Counter Operation Validation
**What to do**:
1. Unlock the device by writing 0x1ACCE551 to WDOGLOCK (offset 0xC00)
2. Write a timeout value to WDOGLOAD (offset 0x000), e.g., 0x00001000
3. Write to WDOGCONTROL (offset 0x008) with INTEN=1, RESEN=0, step_value=0 (value 0x01)
4. Read WDOGVALUE (offset 0x004) immediately and after some simulation cycles
5. Run simulation for enough cycles to observe counter decrement

**Expected Result**:
- WDOGVALUE decreases over time
- Counter decrements by 1 per simulation cycle (step_value=0 means ÷1)
- Counter value calculation matches: initial_value - (current_cycles - start_cycles)

**Success Criteria**:
- WDOGVALUE reads show decreasing values
- Decrement rate matches configured clock divider
- Counter reloads from WDOGLOAD when enabled

### Step 3: First Timeout and Interrupt Validation
**What to do**:
1. Configure device with small timeout value (e.g., 100 cycles)
2. Enable interrupt (INTEN=1) but disable reset (RESEN=0)
3. Run simulation until counter reaches zero
4. Check WDOGRIS (offset 0x010) and WDOGMIS (offset 0x014) registers
5. Verify wdogint signal is asserted to interrupt controller

**Expected Result**:
- WDOGRIS[0] = 1 (raw interrupt status set)
- WDOGMIS[0] = 1 (masked interrupt status set, since INTEN=1)
- wdogint signal asserted (observable via interrupt controller)
- Counter reloads from WDOGLOAD and continues counting

**Success Criteria**:
- Interrupt status registers show timeout occurred
- Interrupt signal reaches connected interrupt controller
- Counter automatically reloads and continues after timeout

### Step 4: Interrupt Clear Validation
**What to do**:
1. With interrupt pending from Step 3
2. Write any value to WDOGINTCLR (offset 0x00C)
3. Check WDOGRIS and WDOGMIS registers
4. Verify wdogint signal is deasserted

**Expected Result**:
- WDOGRIS[0] = 0 (interrupt cleared)
- WDOGMIS[0] = 0 (masked status cleared)
- wdogint signal deasserted
- Counter reloads from WDOGLOAD

**Success Criteria**:
- Interrupt status cleared by write to WDOGINTCLR
- Interrupt signal deasserted
- Counter reloaded and restarted

### Step 5: Second Timeout and Reset Validation
**What to do**:
1. Configure device with small timeout value
2. Enable both interrupt and reset (INTEN=1, RESEN=1)
3. Run simulation until first timeout (interrupt asserted)
4. Do NOT clear the interrupt
5. Continue simulation until second timeout
6. Verify wdogres signal is asserted to reset controller

**Expected Result**:
- First timeout: WDOGRIS[0] = 1, wdogint asserted
- Second timeout: wdogres signal asserted
- wdogres remains asserted (cannot be cleared by software)
- Counter continues running even after reset assertion

**Success Criteria**:
- Reset signal asserted after second timeout
- Reset signal remains asserted
- Writing to WDOGINTCLR does NOT clear reset signal
- Reset signal only clears on device reset

### Step 6: Lock Mechanism Validation
**What to do**:
1. Read WDOGLOCK (should return 0x00000000 = unlocked)
2. Write 0x12345678 to WDOGLOCK (any value except 0x1ACCE551)
3. Read WDOGLOCK (should return 0x00000001 = locked)
4. Attempt to write to WDOGLOAD
5. Verify write was ignored
6. Write 0x1ACCE551 to WDOGLOCK to unlock
7. Write to WDOGLOAD again
8. Verify write succeeded

**Expected Result**:
- WDOGLOCK read returns 0x00 when unlocked, 0x01 when locked
- Writes to WDOGLOAD and WDOGCONTROL ignored when locked
- Writes to WDOGLOAD and WDOGCONTROL succeed when unlocked
- WDOGLOCK itself is always writable

**Success Criteria**:
- Lock state correctly reported by WDOGLOCK reads
- Write protection enforced for WDOGLOAD and WDOGCONTROL when locked
- Unlock sequence (0x1ACCE551) correctly unlocks device

### Step 7: Clock Divider Validation
**What to do**:
1. Configure device with WDOGLOAD = 1000, step_value = 0b011 (÷8)
2. Enable counter (INTEN=1)
3. Measure time for counter to decrement by 1
4. Verify it takes 8 simulation cycles per decrement
5. Repeat with different step_value settings (0b000, 0b001, 0b010, 0b100)

**Expected Result**:
- step_value 0b000: 1 cycle per decrement
- step_value 0b001: 2 cycles per decrement
- step_value 0b010: 4 cycles per decrement
- step_value 0b011: 8 cycles per decrement
- step_value 0b100: 16 cycles per decrement

**Success Criteria**:
- Counter decrement rate matches configured clock divider
- Divider settings affect timeout period correctly
- Changing divider while running updates timeout calculation

### Step 8: Integration Test Mode Validation
**What to do**:
1. Write 1 to WDOGITCR[0] (offset 0xF00) to enable integration test mode
2. Verify normal counter operation stops
3. Write 0b01 to WDOGITOP (offset 0xF04) to assert wdogres
4. Verify wdogres signal asserted
5. Write 0b10 to WDOGITOP to assert wdogint
6. Verify wdogint signal asserted
7. Write 0 to WDOGITCR[0] to exit test mode
8. Verify normal operation resumes

**Expected Result**:
- Integration test mode disables normal counter operation
- WDOGITOP directly controls wdogint and wdogres signals
- Exiting test mode restores normal operation
- Test mode does not affect internal state (interrupt_pending, reset_asserted)

**Success Criteria**:
- Test mode correctly disables/enables normal operation
- Direct signal control works via WDOGITOP
- Signals revert to normal control when test mode disabled

### Step 9: Checkpoint/Restore Validation
**What to do**:
1. Configure and start watchdog timer with specific settings
2. Run simulation for some cycles (counter partially decremented)
3. Create Simics checkpoint
4. Continue simulation and observe counter behavior
5. Restore checkpoint
6. Verify counter resumes from checkpointed state
7. Verify timeout events occur at correct time

**Expected Result**:
- Checkpoint saves all device state (counter value, configuration, flags)
- Restored device continues from exact checkpointed state
- Timeout events recalculated correctly after restore
- Behavior after restore matches behavior if checkpoint never occurred

**Success Criteria**:
- Device state fully preserved in checkpoint
- Counter value and timing accurate after restore
- Pending interrupts/resets preserved correctly
- Deterministic behavior across checkpoint/restore

## Troubleshooting

### Counter Not Decrementing
**Symptoms**: WDOGVALUE reads return same value repeatedly  
**Possible Causes**:
- INTEN not set (counter disabled)
- Device locked (WDOGCONTROL write ignored)
- Integration test mode enabled (normal operation disabled)
**Resolution**:
- Verify WDOGCONTROL.INTEN = 1
- Unlock device via WDOGLOCK = 0x1ACCE551
- Disable integration test mode (WDOGITCR[0] = 0)

### Interrupt Not Generated
**Symptoms**: Counter reaches zero but WDOGRIS[0] remains 0  
**Possible Causes**:
- INTEN not set when counter reached zero
- Integration test mode enabled
**Resolution**:
- Ensure INTEN = 1 before counter reaches zero
- Disable integration test mode
- Check that counter actually reached zero (read WDOGVALUE)

### Reset Not Generated
**Symptoms**: Second timeout occurs but wdogres not asserted  
**Possible Causes**:
- RESEN not set
- Interrupt was cleared between first and second timeout
- Only first timeout occurred (not second)
**Resolution**:
- Verify RESEN = 1 in WDOGCONTROL
- Do not clear interrupt between first and second timeout
- Ensure counter reaches zero twice

### Lock Mechanism Not Working
**Symptoms**: Writes to WDOGLOAD succeed even when locked  
**Possible Causes**:
- Device not actually locked (WDOGLOCK read returns 0x00)
- Writing to wrong offset
**Resolution**:
- Verify WDOGLOCK reads as 0x01 (locked)
- Check register offset calculations
- Ensure lock sequence executed correctly

### Identification Registers Wrong Values
**Symptoms**: WDOGPERIPHID* or WDOGPCELLID* return incorrect values  
**Possible Causes**:
- Wrong device instantiated
- Register offset calculation error
- Device not properly initialized
**Resolution**:
- Verify correct device class instantiated
- Check memory mapping and offset calculations
- Review device initialization code

## Next Steps

After completing validation:
1. Review contracts/ for detailed register access and interface behavior specifications
2. Review data-model.md for complete register map and device state documentation
3. Review tasks.md (when generated) for implementation task breakdown
4. Implement device following test-first development approach
5. Run comprehensive test suite to verify all functional requirements
