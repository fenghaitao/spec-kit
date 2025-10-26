# Feature Specification: Simics Watchdog Timer Device

**Feature Branch**: `001-read-the-simics`
**Created**: October 26, 2025
**Status**: Ready for Planning
**Input**: User description: "Read the Simics WDT specification from /home/hfeng1/adk-python/simics-wdt-spec.md and the hardware specifications from /home/hfeng1/adk-python/wdt.md to create a comprehensive Simics watchdog timer device implementation."

---

## User Scenarios & Testing

### Primary User Story
As a Simics platform developer, I need a watchdog timer device model that accurately simulates ARM PrimeCell watchdog hardware behavior, allowing guest software to configure timeout periods, receive timeout interrupts, and trigger system resets when the watchdog is not serviced, enabling realistic testing of watchdog-dependent firmware and operating systems.

### Acceptance Scenarios

1. **Given** the watchdog device is initialized and unlocked, **When** software writes a timeout value to WDOGLOAD and enables the timer via WDOGCONTROL, **Then** the counter begins decrementing and reaches zero after the configured timeout period

2. **Given** the watchdog counter reaches zero with INTEN enabled, **When** software does not clear the interrupt, **Then** the device asserts the wdogint interrupt signal and the raw interrupt status (WDOGRIS) reflects the interrupt state

3. **Given** the watchdog has generated an interrupt (first timeout), **When** the counter reaches zero again with RESEN enabled, **Then** the device asserts the wdogres reset signal to trigger a system reset

4. **Given** the watchdog is locked (WDOGLOCK != 0x1ACCE551), **When** software attempts to write to control registers, **Then** the writes are ignored and register values remain unchanged

5. **Given** the watchdog is in integration test mode (WDOGITCR[0] = 1), **When** software writes to WDOGITOP, **Then** the interrupt and reset signals are directly controlled by the WDOGITOP register values

6. **Given** the watchdog is running, **When** software writes any value to WDOGINTCLR, **Then** the interrupt is cleared and the counter reloads from WDOGLOAD

7. **Given** the watchdog is configured with a clock divider (step_value in WDOGCONTROL), **When** the counter decrements, **Then** the effective timeout period is scaled by the divider factor (1, 2, 4, 8, or 16)

8. **Given** a Simics checkpoint is created while the watchdog is running, **When** the checkpoint is restored, **Then** the watchdog resumes operation with the exact counter value and configuration state preserved

### Edge Cases

- What happens when software writes to WDOGLOAD while the counter is running?
  * Counter continues with current value; new load value takes effect on next reload (interrupt clear or enable transition)

- How does the system handle rapid lock/unlock sequences?
  * Each write to WDOGLOCK is processed independently; lock state changes immediately based on magic value comparison

- What happens when INTEN is disabled while an interrupt is pending?
  * Masked interrupt status (WDOGMIS) clears immediately; raw status (WDOGRIS) remains until explicitly cleared via WDOGINTCLR

- What happens when the counter reaches zero with both INTEN and RESEN disabled?
  * Counter wraps to 0xFFFFFFFF and continues decrementing; no interrupt or reset is generated

- How does the device behave during reset?
  * All registers return to reset values; counter loads 0xFFFFFFFF; lock state is unlocked (0x0); interrupts and resets are deasserted

- What happens when step_value contains an invalid encoding (>4)?
  * Behavior is undefined per specification; implementation should treat as step_value=1 or log warning

---

## Requirements

### Functional Requirements

#### Core Timer Functionality
- **FR-001**: Device MUST implement a 32-bit down-counter that decrements on each enabled clock cycle
- **FR-002**: Device MUST support five clock divider settings via step_value field: ÷1 (0b000), ÷2 (0b001), ÷4 (0b010), ÷8 (0b011), ÷16 (0b100)
- **FR-003**: Device MUST reload the counter from WDOGLOAD register when INTEN transitions from 0 to 1
- **FR-004**: Device MUST reload the counter from WDOGLOAD register when WDOGINTCLR is written with any value
- **FR-005**: Device MUST allow software to read the current counter value via WDOGVALUE register

#### Interrupt and Reset Generation
- **FR-006**: Device MUST assert wdogint interrupt signal when counter reaches zero and INTEN bit is set
- **FR-007**: Device MUST maintain wdogint signal asserted until interrupt is cleared via WDOGINTCLR write
- **FR-008**: Device MUST assert wdogres reset signal when counter reaches zero a second time (after first timeout) and RESEN bit is set
- **FR-009**: Device MUST maintain wdogres signal asserted until device reset occurs
- **FR-010**: Device MUST provide raw interrupt status via WDOGRIS register (unmasked by INTEN)
- **FR-011**: Device MUST provide masked interrupt status via WDOGMIS register (WDOGRIS AND INTEN)

#### Register Lock Protection
- **FR-012**: Device MUST implement lock mechanism via WDOGLOCK register with magic unlock value 0x1ACCE551
- **FR-013**: Device MUST block writes to WDOGLOAD, WDOGCONTROL when WDOGLOCK is in locked state (not 0x1ACCE551)
- **FR-014**: Device MUST return lock status when WDOGLOCK is read: 0x0 for unlocked, 0x1 for locked
- **FR-015**: Device MUST allow WDOGLOCK itself to be written regardless of current lock state

#### Integration Test Mode
- **FR-016**: Device MUST support integration test mode enabled via WDOGITCR register bit 0
- **FR-017**: Device MUST allow direct control of wdogint and wdogres signals via WDOGITOP register when in test mode
- **FR-018**: Device MUST disable normal counter operation when in integration test mode

#### Register Map Implementation
- **FR-019**: Device MUST implement all 21 registers at specified offsets: WDOGLOAD (0x00), WDOGVALUE (0x04), WDOGCONTROL (0x08), WDOGINTCLR (0x0C), WDOGRIS (0x10), WDOGMIS (0x14), WDOGLOCK (0xC00), WDOGITCR (0xF00), WDOGITOP (0xF04), WDOGPERIPHID0-7 (0xFE0-0xFDC), WDOGPCELLID0-3 (0xFF0-0xFFC)
- **FR-020**: Device MUST implement correct reset values for all registers as specified in hardware documentation
- **FR-021**: Device MUST implement correct read/write permissions for each register (R, W, R/W)
- **FR-022**: Device MUST return peripheral identification values matching ARM PrimeCell specification

#### Simulation Integration
- **FR-023**: Device MUST support memory-mapped I/O access via Simics platform bus interface
- **FR-024**: Device MUST provide interrupt signal output connectable to platform interrupt controller
- **FR-025**: Device MUST provide reset signal output connectable to platform reset controller
- **FR-026**: Device MUST support Simics checkpoint/restore functionality preserving all device state
- **FR-027**: Device MUST use cycle-accurate timing based on simulation clock cycles

#### Observability and Debugging
- **FR-028**: Device MUST provide logging for register accesses (reads/writes with addresses and values)
- **FR-029**: Device MUST provide logging for state transitions (counter zero, interrupt assertion, reset assertion)
- **FR-030**: Device MUST provide logging for lock state changes
- **FR-031**: Device MUST provide logging for integration test mode operations

### Non-Functional Requirements

#### Performance
- **NFR-001**: Device MUST introduce minimal simulation overhead (target: <1% impact on platform simulation speed)
- **NFR-002**: Device MUST handle register accesses within single simulation cycle

#### Compatibility
- **NFR-003**: Device MUST be compatible with Simics 7.x platform framework
- **NFR-004**: Device MUST support both 32-bit and 64-bit simulation environments
- **NFR-005**: Device MUST conform to ARM PrimeCell watchdog timer specification

#### Reliability
- **NFR-006**: Device MUST provide deterministic behavior across simulation runs with identical inputs
- **NFR-007**: Device MUST validate register write values and handle invalid configurations gracefully
- **NFR-008**: Device MUST maintain state consistency during checkpoint/restore operations

---

### Key Entities

- **Watchdog Counter**: 32-bit down-counter that decrements based on clock divider setting; reloads from WDOGLOAD on enable or interrupt clear; reaches zero to trigger timeout events

- **Clock Divider**: Configurable frequency divider (÷1, ÷2, ÷4, ÷8, ÷16) that controls counter decrement rate; set via step_value field in WDOGCONTROL register

- **Interrupt State**: Binary state tracking whether first timeout has occurred; reflected in WDOGRIS (raw) and WDOGMIS (masked) registers; cleared via WDOGINTCLR write

- **Lock State**: Binary protection state controlled by WDOGLOCK register; prevents unauthorized modification of critical registers when locked

- **Integration Test State**: Binary mode flag controlled by WDOGITCR register; switches device between normal countdown operation and direct signal control mode

---

### Hardware Specification

**Device Type**: Timer device - ARM PrimeCell Watchdog Timer (SP805)

#### Register Map

The device implements 21 memory-mapped registers organized into functional groups:

**Control and Data Registers (0x00-0x14)**:
- **WDOGLOAD (0x00)**: 32-bit read/write register holding reload value for counter; reset value 0xFFFFFFFF
- **WDOGVALUE (0x04)**: 32-bit read-only register providing current counter value; reset value 0xFFFFFFFF
- **WDOGCONTROL (0x08)**: 32-bit read/write control register with fields:
  * Bits [4:2] step_value: Clock divider selection (0=÷1, 1=÷2, 2=÷4, 3=÷8, 4=÷16)
  * Bit [1] RESEN: Enable reset output on second timeout
  * Bit [0] INTEN: Enable interrupt output and counter operation
  * Reset value: 0x00
- **WDOGINTCLR (0x0C)**: 32-bit write-only register; any write clears interrupt and reloads counter
- **WDOGRIS (0x10)**: 1-bit read-only raw interrupt status (bit 0); reflects unmasked timeout state
- **WDOGMIS (0x14)**: 1-bit read-only masked interrupt status (bit 0); equals WDOGRIS AND INTEN

**Lock Register (0xC00)**:
- **WDOGLOCK (0xC00)**: 32-bit read/write register; write 0x1ACCE551 to unlock, any other value to lock; read returns 0x0 (unlocked) or 0x1 (locked); reset value 0x00000000

**Integration Test Registers (0xF00-0xF04)**:
- **WDOGITCR (0xF00)**: 1-bit read/write test mode enable (bit 0); 1=test mode, 0=normal mode
- **WDOGITOP (0xF04)**: 2-bit write-only output control; bit[1]=wdogint value, bit[0]=wdogres value in test mode

**Identification Registers (0xFD0-0xFFC)**:
- **WDOGPERIPHID4-7 (0xFD0-0xFDC)**: Peripheral ID registers; values 0x04, 0x00, 0x00, 0x00
- **WDOGPERIPHID0-3 (0xFE0-0xFEC)**: Peripheral ID registers; values 0x24, 0xB8, 0x1B, 0x00
- **WDOGPCELLID0-3 (0xFF0-0xFFC)**: PrimeCell ID registers; values 0x0D, 0xF0, 0x05, 0xB1

#### External Interfaces

**Memory-Mapped I/O Interface**:
- Device connects to platform via memory-mapped I/O bus
- Occupies 4KB address space (0x000-0xFFF offset range)
- Supports 32-bit read and write transactions
- Responds to accesses within single bus cycle

**Clock and Reset Inputs**:
- **wclk**: Working clock input driving counter decrement logic
- **wclk_en**: Clock enable signal; counter decrements only when asserted
- **wrst_n**: Asynchronous active-low reset for working clock domain
- **prst_n**: Asynchronous active-low reset for APB bus clock domain

**Interrupt and Reset Outputs**:
- **wdogint**: Interrupt signal output (active high); connects to platform interrupt controller
- **wdogres**: Reset signal output (active high); connects to platform reset controller

#### Software Visibility

Software can observe and control:
- **Counter value**: Read current countdown value via WDOGVALUE
- **Timeout configuration**: Set reload value via WDOGLOAD and divider via WDOGCONTROL
- **Interrupt status**: Check raw (WDOGRIS) and masked (WDOGMIS) interrupt states
- **Lock status**: Query write protection state via WDOGLOCK read
- **Device identity**: Read peripheral and PrimeCell ID registers for device identification

Software cannot directly observe:
- Internal clock divider counter state
- Exact timing of counter decrements between register reads

#### Device Behavior

**Normal Operation Flow**:
1. Software unlocks device by writing 0x1ACCE551 to WDOGLOCK
2. Software configures WDOGLOAD with desired timeout value
3. Software configures WDOGCONTROL with clock divider, RESEN, and INTEN settings
4. When INTEN transitions 0→1, counter loads from WDOGLOAD and begins decrementing
5. Counter decrements by 1 each (wclk cycle × divider factor) when wclk_en is asserted
6. When counter reaches 0x00000000:
   - If INTEN=1: wdogint signal asserts, WDOGRIS[0] sets to 1
   - Counter reloads from WDOGLOAD and continues
7. If interrupt not cleared and counter reaches zero again:
   - If RESEN=1: wdogres signal asserts and remains high until system reset
8. Software services watchdog by writing any value to WDOGINTCLR (clears interrupt, reloads counter)

**State Machine**:
- **Idle State**: INTEN=0, counter holds value, no interrupts/resets
- **Counting State**: INTEN=1, counter actively decrementing
- **First Timeout**: Counter reached zero once, interrupt asserted if INTEN=1
- **Second Timeout**: Counter reached zero twice, reset asserted if RESEN=1

**Clock Divider Behavior**:
- Internal divider counter tracks wclk cycles
- Main counter decrements when divider counter reaches (step_value × 2) cycles
- Example: step_value=3 (÷8) means counter decrements every 8 wclk cycles

#### Reset Behavior

On assertion of wrst_n or prst_n:
- All registers reset to documented reset values
- Counter loads 0xFFFFFFFF
- WDOGCONTROL clears to 0x00 (timer disabled)
- WDOGLOCK resets to 0x00000000 (unlocked state)
- WDOGRIS and WDOGMIS clear to 0
- wdogint and wdogres signals deassert to 0
- Integration test mode disabled (WDOGITCR = 0)

#### Interrupt Generation

Interrupt conditions:
- **Assertion**: Counter reaches zero AND INTEN=1
- **Persistence**: Interrupt remains asserted until cleared via WDOGINTCLR write
- **Masking**: WDOGMIS reflects interrupt only when INTEN=1; WDOGRIS always reflects raw state
- **Clearing**: Write any value to WDOGINTCLR; interrupt clears immediately and counter reloads

Reset conditions:
- **Assertion**: Counter reaches zero for second time (after first timeout) AND RESEN=1
- **Persistence**: Reset signal remains asserted until system reset occurs
- **No clearing**: Reset signal cannot be cleared by software; requires hardware reset

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

### Simics Hardware Completeness
- [x] Device type identified and specified
- [x] Register map described at high level (no implementation details)
- [x] External interfaces and software visibility documented

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
