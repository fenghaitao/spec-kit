# Quick Start: Simics Watchdog Timer Device Implementation

## Goal
Create and test a Simics watchdog timer device model compatible with ARM PrimeCell specification that provides timeout monitoring with interrupt and reset capabilities.

## Prerequisites
- Simics Base 7.57.0
- QSP-x86 platform package
- Python 7.13.0 or later
- Required packages: simics-base, simics-qsp-x86

## Validation Steps

### Step 1: Device Model Creation
**What to do**:
1. Create a new Simics project using the project creation tools
2. Add a DML device skeleton for the watchdog timer
3. Implement all 21 registers according to the ARM PrimeCell specification
4. Add timer functionality with configurable timeout periods
5. Implement interrupt and reset signal generation
6. Add lock protection mechanism with magic unlock value
7. Implement integration test mode support

**Expected Result**:
- A functional watchdog timer device model
- All registers accessible at their specified offsets
- Timer counts down and generates interrupts/resets as configured
- Lock mechanism protects register writes
- Integration test mode allows direct signal control

**Success Criteria**:
- Device loads without errors in Simics
- All registers readable with correct reset values
- Device appears in Simics object hierarchy
- No compilation errors in DML code

### Step 2: Basic Timer Functionality Test
**What to do**:
1. Configure watchdog timer with specific timeout value
2. Enable interrupt generation (INTEN=1)
3. Allow timer to count down to zero
4. Verify interrupt signal is generated
5. Clear interrupt with WDOGINTCLR write
6. Allow timer to timeout again with pending interrupt
7. Verify reset signal is generated

**Expected Result**:
- First timeout generates interrupt signal
- Interrupt clear reloads timer correctly
- Second timeout with pending interrupt generates reset
- Timer values match expected countdown sequence

**Success Criteria**:
- Interrupt signal asserted on first timeout
- Reset signal asserted on second timeout
- Timer reloads correctly after interrupt clear
- No unexpected signal assertions

### Step 3: Lock Protection Verification
**What to do**:
1. Verify registers are initially unlocked (WDOGLOCK read returns 0)
2. Lock registers by writing value other than 0x1ACCE551 to WDOGLOCK
3. Attempt to write to protected registers
4. Verify writes are ignored
5. Unlock registers by writing 0x1ACCE551 to WDOGLOCK
6. Verify writes to registers now succeed

**Expected Result**:
- Locked registers ignore write operations
- WDOGLOCK register always remains writable
- Identification registers always remain readable
- Unlocking restores normal register write access

**Success Criteria**:
- Register values unchanged when written while locked
- WDOGLOCK read returns 1 when locked, 0 when unlocked
- Normal operation restored after unlocking
- No device errors or crashes

### Step 4: Integration Test Mode Validation
**What to do**:
1. Enable integration test mode by writing 1 to WDOGITCR[0]
2. Write test values to WDOGITOP register
3. Verify interrupt and reset outputs reflect test values
4. Disable integration test mode by writing 0 to WDOGITCR[0]
5. Verify normal timer operation resumes

**Expected Result**:
- Output signals controlled directly by WDOGITOP values when test mode enabled
- Normal timer operation suspended during test mode
- Normal operation resumes when test mode disabled
- Timer continues from where it left off

**Success Criteria**:
- Output signals match WDOGITOP values in test mode
- Normal timer behavior restored after test mode exit
- No corruption of timer state during mode transitions

### Step 5: Clock Divider Functionality Test
**What to do**:
1. Configure timer with different step_value settings (000-100)
2. Measure timeout periods for each setting
3. Verify timeout periods match expected ratios
4. Test with various reload values

**Expected Result**:
- ÷1 setting provides fastest timeout
- ÷16 setting provides slowest timeout
- Intermediate settings provide proportional timeouts
- All settings maintain accurate timing

**Success Criteria**:
- Timeout periods scale correctly with step_value
- No timing irregularities or glitches
- Timer maintains accuracy across all divider settings

## Troubleshooting

### Device Fails to Load
- Check for DML syntax errors in compilation output
- Verify all required imports are present
- Ensure device name matches file name
- Check that dml 1.4; declaration is first line

### Registers Not Accessible
- Verify register offsets are correctly implemented
- Check for conflicts in register address mapping
- Ensure bank parameters are correctly set
- Verify register size declarations

### Timer Not Counting
- Check clock input connection
- Verify step_value configuration
- Confirm INTEN bit is set for interrupt operation
- Check for locked register preventing configuration

### Signals Not Generated
- Verify signal connections to interrupt and reset controllers
- Check RESEN and INTEN bits in WDOGCONTROL
- Confirm integration test mode is not active
- Verify signal interface implementations

### Lock Mechanism Not Working
- Verify WDOGLOCK register implementation
- Check that 0x1ACCE551 correctly unlocks registers
- Confirm other values correctly lock registers
- Ensure WDOGLOCK register itself is never locked

## Next Steps
- Review the data-model.md file for detailed register specifications
- Examine contracts/register-access.md for detailed register behavior requirements
- Examine contracts/interface-behavior.md for detailed interface specifications
- Run the full test suite to verify all functionality
- Integrate with QSP-x86 platform for system-level testing
