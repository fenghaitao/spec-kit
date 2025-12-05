# Simics Watchdog Timer Device Specification

## 1. Device Overview

The Simics Watchdog Timer is a 32-bit decrementing counter device compatible with ARM PrimeCell specification. It provides configurable timeout periods with interrupt generation on first timeout and system reset on second timeout if the interrupt is not cleared. The device includes lock protection mechanisms and integration test capabilities.

- **Device Name**: Simics Watchdog Timer
- **Category**: Timer/Counter
- **Base Address**: 0x1000 (4KB address space: 0x1000 - 0x1FFF)
- **Clock Interface**: wclk (work clock), wclk_en (clock enable), wrst_n (reset)
- **Bus Interface**: APB for register access

## 2. Register Map

### 2.1 Register Map Overview

| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|
| 0x00 | WDOGLOAD | R/W | 32 | 0xFFFFFFFF | Watchdog reload value |
| 0x04 | WDOGVALUE | R | 32 | 0xFFFFFFFF | Current counter value |
| 0x08 | WDOGCONTROL | R/W | 32 | 0x00 | Control register (INTEN, RESEN, step_value) |
| 0x0C | WDOGINTCLR | W | 32 | 0x00 | Interrupt clear register |
| 0x10 | WDOGRIS | R | 32 | 0x00 | Raw interrupt status |
| 0x14 | WDOGMIS | R | 32 | 0x00 | Masked interrupt status |
| 0xC00 | WDOGLOCK | R/W | 32 | 0x00000000 | Lock register (0x1ACCE551 to unlock) |
| 0xF00 | WDOGITCR | R/W | 32 | 0x00000000 | Integration test control |
| 0xF04 | WDOGITOP | W | 32 | 0x00000000 | Integration test output |
| 0xFD0 | WDOGPERIPHID4 | R | 8 | 0x04 | Peripheral ID 4 |
| 0xFD4 | WDOGPERIPHID5 | R | 8 | 0x00 | Peripheral ID 5 |
| 0xFD8 | WDOGPERIPHID6 | R | 8 | 0x00 | Peripheral ID 6 |
| 0xFDC | WDOGPERIPHID7 | R | 8 | 0x00 | Peripheral ID 7 |
| 0xFE0 | WDOGPERIPHID0 | R | 8 | 0x24 | Peripheral ID 0 |
| 0xFE4 | WDOGPERIPHID1 | R | 8 | 0xB8 | Peripheral ID 1 |
| 0xFE8 | WDOGPERIPHID2 | R | 8 | 0x1B | Peripheral ID 2 |
| 0xFEC | WDOGPERIPHID3 | R | 8 | 0x00 | Peripheral ID 3 |
| 0xFF0 | WDOGPCELLID0 | R | 8 | 0x0D | PrimeCell ID 0 |
| 0xFF4 | WDOGPCELLID1 | R | 8 | 0xF0 | PrimeCell ID 1 |
| 0xFF8 | WDOGPCELLID2 | R | 8 | 0x05 | PrimeCell ID 2 |
| 0xFFC | WDOGPCELLID3 | R | 8 | 0xB1 | PrimeCell ID 3 |

### 2.2 Side-Effect Register Descriptions

#### 2.2.1 WDOGLOAD (0x00)
- **Type**: R/W
- **Width**: 32 bits
- **Reset**: 0xFFFFFFFF
- **Write side-effect**: When INTEN bit in WDOGCONTROL is 0 and INTEN is set to 1, counter reloads from this register

#### 2.2.2 WDOGVALUE (0x04)
- **Type**: R (Read-only)
- **Width**: 32 bits
- **Reset**: 0xFFFFFFFF
- **Read side-effect**: Returns current value of watchdog counter, does not change the counter value

#### 2.2.3 WDOGCONTROL (0x08)
- **Type**: R/W
- **Width**: 32 bits
- **Reset**: 0x00
- **Bit 0 (INTEN)**: Enable interrupt bit
  - Write side-effect: When set to 1 after being previously disabled, reloads counter from WDOGLOAD
- **Bit 1 (RESEN)**: Enable reset output bit
- **Bits 4:2 (step_value)**: Clock divider (000=÷1, 001=÷2, 010=÷4, 011=÷8, 100=÷16)

#### 2.2.4 WDOGINTCLR (0x0C)
- **Type**: W (Write-only)
- **Width**: 32 bits
- **Reset**: 0x00
- **Write side-effect**: Clears the interrupt signal (wdogint) and reloads counter from WDOGLOAD register
- Any value written will trigger this behavior

#### 2.2.5 WDOGRIS (0x10)
- **Type**: R (Read-only)
- **Width**: 32 bits
- **Reset**: 0x00
- **Bit 0**: Raw watchdog interrupt status (not affected by INTEN bit)

#### 2.2.6 WDOGMIS (0x14)
- **Type**: R (Read-only)
- **Width**: 32 bits
- **Reset**: 0x00
- **Bit 0**: Masked interrupt status (WDOGRIS[0] AND WDOGCONTROL[0])

#### 2.2.7 WDOGLOCK (0xC00)
- **Type**: R/W
- **Width**: 32 bits
- **Reset**: 0x00000000
- **Write side-effect**: Writing 0x1ACCE551 enables write access to other registers; writing any other value disables write access to other registers
- **Read return**: Lock status: 0x0 for unlocked, 0x1 for locked

#### 2.2.8 WDOGITCR (0xF00)
- **Type**: R/W
- **Width**: 32 bits
- **Reset**: 0x00000000
- **Bit 0**: Integration test mode enable (1=enabled, 0=normal operation)
- **Write side-effect**: Controls entry/exit from integration test mode

#### 2.2.9 WDOGITOP (0xF04)
- **Type**: W (Write-only)
- **Width**: 32 bits
- **Reset**: 0x00000000
- **Write side-effect**: In test mode, directly controls wdogint (bit 1) and wdogres (bit 0) outputs

## 3. External Interfaces & Signals

### 3.1 Clock and Reset Signals
- **wclk**: Work clock input (functional model, not cycle-accurate)
- **wclk_en**: Work clock enable signal
- **wrst_n**: Work clock domain reset (active low, asynchronous)
- **prst_n**: APB bus reset signal (active low, asynchronous)

### 3.2 Interrupt and Reset Outputs
- **wdogint**: Watchdog interrupt output (edge-triggered, active high)
  - Asserted when counter reaches zero and INTEN=1 in WDOGCONTROL
  - Cleared by writing any value to WDOGINTCLR register
- **wdogres**: Watchdog reset output (active high)
  - Asserted when counter reaches zero again while interrupt is pending and RESEN=1 in WDOGCONTROL
  - Cleared by system reset only

## 4. Register Side-Effects & Behaviors

### 4.1 Counter/Timer Behavior
- When timer reaches zero and INTEN=1, set WDOGRIS[0]=1 and assert wdogint
- When timer reaches zero again while interrupt asserted and RESEN=1, assert wdogres
- Writing to WDOGINTCLR clears interrupt and reloads counter from WDOGLOAD
- Counter decrement rate determined by step_value field in WDOGCONTROL

### 4.2 State Machine Behavior
- When INTEN transitions 0→1, counter reloads from WDOGLOAD if previously disabled
- When WDOGINTCLR is written, interrupt clears and counter reloads
- In integration test mode (WDOGITCR[0]=1), WDOGITOP directly controls outputs

### 4.3 Cross-Register Dependencies
- WDOGMIS[0] = WDOGRIS[0] AND WDOGCONTROL[0] (INTEN)
- WDOGINTCLR write affects WDOGRIS[0] and counter reload
- WDOGLOCK controls access to all other registers (except itself)

## 5. Device Operational Model

### 5.1 Device States
```
State: RESET
- Entry conditions: wrst_n or prst_n active low
- Observable indicators: All registers at reset values
- Exit conditions: Reset removal
- Test Scenario: Verify registers return to reset values during reset

State: IDLE
- Entry conditions: WDOGCONTROL.INTEN = 0
- Observable indicators: Counter stopped, no interrupts
- Exit conditions: WDOGCONTROL.INTEN set to 1
- Test Scenario: Verify counter doesn't decrement when INTEN=0

State: COUNTING
- Entry conditions: WDOGCONTROL.INTEN = 1, counter > 0
- Observable indicators: Counter decrements, WDOGVALUE changes
- Exit conditions: Counter reaches 0 or INTEN set to 0
- Test Scenario: Verify counter decrements from WDOGLOAD

State: INTERRUPT_PENDING
- Entry conditions: Counter reaches 0 and WDOGCONTROL.INTEN = 1
- Observable indicators: WDOGRIS[0] = 1, wdogint asserted
- Exit conditions: Write to WDOGINTCLR or WDOGCONTROL.INTEN to 0
- Test Scenario: Verify interrupt is generated at counter zero

State: RESET_PENDING
- Entry conditions: Interrupt pending and counter reaches 0 again with RESEN=1
- Observable indicators: wdogres asserted
- Exit conditions: System reset
- Test Scenario: Verify reset occurs on second timeout
```

### 5.2 State Transitions
- [IDLE] → [COUNTING]: Set WDOGCONTROL.INTEN to 1
- [COUNTING] → [INTERRUPT_PENDING]: Counter reaches zero and INTEN=1
- [INTERRUPT_PENDING] → [COUNTING]: Write to WDOGINTCLR
- [INTERRUPT_PENDING] → [RESET_PENDING]: Counter reaches zero again with RESEN=1

### 5.3 SW/HW Interaction Flows

#### 5.3.1 Normal Timer Operation Flow
- **State Transition**: IDLE → COUNTING → INTERRUPT_PENDING → COUNTING
- **Flow Description**: Basic watchdog operation with interrupt clearing

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| Write to WDOGLOAD | Store value | Register updated |
| Set INTEN to 1 | Reload and start | WDOGVALUE shows decreasing values |
| Monitor WDOGRIS | Assert interrupt at zero | WDOGRIS[0] = 1, wdogint asserted |
| Write to WDOGINTCLR | Clear interrupt, reload | WDOGRIS[0] = 0, counter continues |

#### 5.3.2 Reset Generation Flow
- **State Transition**: COUNTING → INTERRUPT_PENDING → RESET_PENDING
- **Flow Description**: Watchdog reset generation when interrupt not cleared

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| Configure INTEN=1, RESEN=1 | Prepare for reset | Both bits set in WDOGCONTROL |
| Allow counter to zero | Assert wdogint | WDOGRIS[0] = 1, wdogint asserted |
| Don't clear interrupt, wait | Assert wdogres | wdogres signal asserted |

## 6. Functional Requirements

### 6.1 Timer Functionality Requirements
**FUNC-001**: The watchdog timer shall be a 32-bit decrementing counter that decrements based on the clock divider setting.
**FUNC-002**: The timer shall decrement at a rate determined by the step_value field in WDOGCONTROL register.
**FUNC-003**: The timer shall reload from WDOGLOAD register when INTEN transitions from 0 to 1.
**FUNC-004**: The timer shall reload from WDOGLOAD register when WDOGINTCLR is written.

### 6.2 Interrupt and Reset Requirements
**FUNC-005**: When counter reaches zero and INTEN=1 in WDOGCONTROL, device shall assert wdogint signal.
**FUNC-006**: When counter reaches zero with INTEN=1, WDOGRIS[0] shall be set to 1.
**FUNC-007**: If counter reaches zero again while interrupt asserted and RESEN=1 in WDOGCONTROL, device shall assert wdogres signal.
**FUNC-008**: Writing any value to WDOGINTCLR register shall clear the wdogint signal and reload the counter.
**FUNC-009**: WDOGMIS register bit 0 shall reflect the logical AND of WDOGRIS[0] and WDOGCONTROL[0].

### 6.3 Register Access Requirements
**FUNC-010**: WDOGLOAD register supports read and write operations with 32-bit width.
**FUNC-011**: WDOGVALUE register supports read operations only with 32-bit width, returning current counter value.
**FUNC-012**: WDOGCONTROL register supports read and write operations with 32-bit width.
**FUNC-013**: WDOGINTCLR register supports write operations only with 32-bit width.
**FUNC-014**: All registers except WDOGLOCK shall be write-protected when lock mechanism is enabled.

### 6.4 Clock Divider Requirements
**FUNC-015**: Clock divider setting in WDOGCONTROL[4:2] shall determine timer decrement rate.
**FUNC-016**: When step_value is 000, timer shall decrement at full clock rate (÷1).
**FUNC-017**: When step_value is 001, timer shall decrement at half clock rate (÷2).
**FUNC-018**: When step_value is 010, timer shall decrement at quarter clock rate (÷4).
**FUNC-019**: When step_value is 011, timer shall decrement at eighth clock rate (÷8).
**FUNC-020**: When step_value is 100, timer shall decrement at sixteenth clock rate (÷16).

### 6.5 Lock Protection Requirements
**FUNC-021**: Writing 0x1ACCE551 to WDOGLOCK register shall unlock write access to other registers.
**FUNC-022**: Writing any value other than 0x1ACCE551 to WDOGLOCK register shall lock write access to other registers.
**FUNC-023**: WDOGLOCK register read shall return 0x0 when unlocked, 0x1 when locked.
**FUNC-024**: Locked state shall prevent writes to all registers except WDOGLOCK itself.

### 6.6 Integration Test Mode Requirements
**FUNC-025**: When WDOGITCR[0]=1, device shall enter integration test mode.
**FUNC-026**: In integration test mode, WDOGITOP register shall directly control wdogint and wdogres outputs.
**FUNC-027**: When WDOGITCR[0]=0, device shall operate in normal mode.
**FUNC-028**: WDOGITOP[1] shall control wdogint output in integration test mode.
**FUNC-029**: WDOGITOP[0] shall control wdogres output in integration test mode.

### 6.7 Identification Requirements
**FUNC-030**: Device shall implement all PrimeCell identification registers at 0xFF0-0xFFC.
**FUNC-031**: WDOGPERIPHID0-7 registers shall contain correct peripheral identification values.

## 7. Register Access Requirements
**REG-001**: WDOGLOAD register shall preserve written value and allow read access.
**REG-002**: WDOGVALUE register shall return current counter value on read without affecting counter.
**REG-003**: WDOGCONTROL register shall support individual bit access.
**REG-004**: WDOGINTCLR register shall trigger interrupt clear on any write operation regardless of value.
**REG-005**: Read-only registers (WDOGVALUE, WDOGRIS, WDOGMIS, ID registers) shall return defined values on read.
**REG-006**: Reserved register bits shall not affect functionality and may return undefined values.
**REG-007**: All registers shall be accessible via APB bus interface.

## 8. Behavioral Requirements
**BEHAV-001**: When INTEN=0 in WDOGCONTROL, timer shall not decrement regardless of clock.
**BEHAV-002**: When INTEN=1 in WDOGCONTROL and timer reaches zero, WDOGRIS[0] shall be set to 1.
**BEHAV-003**: When wdogint is asserted, it shall remain asserted until cleared by WDOGINTCLR write.
**BEHAV-004**: When wdogres is asserted, it shall remain asserted until system reset occurs.
**BEHAV-005**: The device shall handle clock enable (wclk_en) properly, decrementing only when enabled.
**BEHAV-006**: The device shall reset properly on wrst_n and prst_n signals.
**BEHAV-007**: WDOGMIS[0] shall always equal WDOGRIS[0] AND WDOGCONTROL[0] with minimal delay.
**BEHAV-008**: Counter shall not wrap around after reaching zero, but shall remain at zero if not reloaded.

## 9. Test Scenarios

### 9.1 Basic Timer Operation Test
**TEST-001**: Verify basic timer countdown functionality.
- Setup: Write small value to WDOGLOAD, set INTEN=1 in WDOGCONTROL
- Action: Verify counter decrements in WDOGVALUE register
- Expected: Counter value decreases, interrupt is generated at zero

### 9.2 Interrupt and Reset Generation Test
**TEST-002**: Verify interrupt and reset generation sequence.
- Setup: Write value to WDOGLOAD, set INTEN=1, RESEN=1 in WDOGCONTROL
- Action: Allow timer to count to zero twice without clearing interrupt
- Expected: First zero generates interrupt, second generates reset

### 9.3 Lock Protection Test
**TEST-003**: Verify lock protection mechanism.
- Setup: Write 0x1ACCE551 to WDOGLOCK to unlock
- Action: Write to WDOGLOAD (should succeed), then lock, then try again
- Expected: First write succeeds, second write fails (locked)

### 9.4 Clock Divider Test
**TEST-004**: Verify different clock divider settings.
- Setup: Configure timer with same value but different step_value settings
- Action: Measure time to reach zero for each setting
- Expected: Larger divider → proportionally longer countdown

### 9.5 Integration Test Mode Test
**TEST-005**: Verify integration test mode functionality.
- Setup: Set WDOGITCR[0]=1 to enable test mode
- Action: Write different values to WDOGITOP register
- Expected: Direct control of wdogint and wdogres outputs

### 9.6 Interrupt Clear Test
**TEST-006**: Verify interrupt clearing mechanism.
- Setup: Configure timer to generate interrupt
- Action: Allow interrupt to occur, then write to WDOGINTCLR
- Expected: Interrupt signal cleared, counter reloaded

### 9.7 Register Status Test
**TEST-007**: Verify register status reporting.
- Setup: Configure timer for interrupt
- Action: Monitor WDOGRIS and WDOGMIS registers
- Expected: WDOGRIS[0] shows raw status, WDOGMIS[0] shows masked status

### 9.8 Reset Behavior Test
**TEST-008**: Verify reset behavior of registers.
- Setup: Modify various registers to non-reset values
- Action: Assert wrst_n or prst_n reset
- Expected: All registers return to reset values

### 9.9 Counter Reload Test
**TEST-009**: Verify counter reload on INTEN enable.
- Setup: Set INTEN=0, load counter value
- Action: Set INTEN=1
- Expected: Counter reloads from WDOGLOAD value

### 9.10 Reserved Bit Test
**TEST-010**: Verify handling of reserved register bits.
- Setup: Read reserved bits in WDOGCONTROL and other registers
- Action: Write to reserved areas
- Expected: No impact on functionality, bits may be read as defined