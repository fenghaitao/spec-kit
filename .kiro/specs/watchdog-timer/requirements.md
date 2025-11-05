# Requirements Document

## Introduction

This document specifies the requirements for a Simics watchdog timer device implementation based on the ARM PrimeCell watchdog specification. The watchdog timer is a 32-bit down-counter that provides system protection through configurable timeout intervals, interrupt generation, and system reset capabilities. The device includes 21 memory-mapped registers for control, status monitoring, peripheral identification, and integration testing. The implementation targets the QSP-x86 platform with a base address of 0x1000 and follows DML 1.4 standards for Simics device modeling.

## Glossary

- **WDT_Device**: The Simics watchdog timer device model implemented in DML 1.4
- **Down_Counter**: A 32-bit counter that decrements from a loaded value to zero
- **WDOGLOAD**: The load register containing the initial counter value
- **WDOGVALUE**: The current value register showing real-time counter state
- **WDOGCONTROL**: The control register managing interrupt enable, reset enable, and step value
- **WDOGINTCLR**: The interrupt clear register for clearing interrupt status
- **WDOGRIS**: The raw interrupt status register showing unmasked interrupt state
- **WDOGMIS**: The masked interrupt status register showing enabled interrupt state
- **WDOGLOCK**: The lock register protecting other registers from unauthorized writes
- **WDOGITCR**: The integration test control register enabling test mode
- **WDOGITOP**: The integration test output register for direct signal control
- **WDOGPERIPHID[0-7]**: Eight peripheral identification registers
- **WDOGPCELLID[0-3]**: Four PrimeCell identification registers
- **wdogint**: The interrupt output signal asserted on first timeout
- **wdogres**: The reset output signal asserted on second consecutive timeout
- **APB_Bus**: Advanced Peripheral Bus interface for register access
- **Lock_State**: The protection state controlled by WDOGLOCK register
- **Integration_Test_Mode**: A special mode for direct output signal control
- **Step_Value**: The decrement amount per clock cycle based on clock frequency divider
- **Timeout_Event**: The condition when Down_Counter reaches zero
- **Magic_Unlock_Value**: The specific value 0x1ACCE551 required to unlock registers

## Requirements

### Requirement 1

**User Story:** As a system designer, I want a 32-bit down-counter with configurable reload values, so that I can set appropriate watchdog timeout periods for different system requirements

#### Acceptance Criteria

1. THE WDT_Device SHALL provide a WDOGLOAD register at offset 0x00 with 32-bit read-write access and reset value 0xFFFFFFFF
2. WHEN WDOGCONTROL bit[0] INTEN transitions from 0 to 1, THE WDT_Device SHALL reload Down_Counter with the value from WDOGLOAD
3. WHEN WDOGINTCLR receives any write operation, THE WDT_Device SHALL reload Down_Counter with the value from WDOGLOAD
4. THE WDT_Device SHALL provide a WDOGVALUE register at offset 0x04 with 32-bit read-only access showing the current Down_Counter value
5. WHEN software reads WDOGVALUE, THE WDT_Device SHALL return the current Down_Counter value without modifying counter state

### Requirement 2

**User Story:** As a system designer, I want configurable clock divider settings, so that I can adjust the watchdog timing resolution for different clock frequencies

#### Acceptance Criteria

1. THE WDT_Device SHALL provide WDOGCONTROL register at offset 0x08 with bits[4:2] as step_value field
2. WHEN step_value equals 3'b000, THE WDT_Device SHALL decrement Down_Counter by 1 per enabled clock cycle
3. WHEN step_value equals 3'b001, THE WDT_Device SHALL decrement Down_Counter by 2 per enabled clock cycle
4. WHEN step_value equals 3'b010, THE WDT_Device SHALL decrement Down_Counter by 4 per enabled clock cycle
5. WHEN step_value equals 3'b011, THE WDT_Device SHALL decrement Down_Counter by 8 per enabled clock cycle
6. WHEN step_value equals 3'b100, THE WDT_Device SHALL decrement Down_Counter by 16 per enabled clock cycle
7. WHEN step_value has value other than 3'b000 through 3'b100, THE WDT_Device SHALL treat the configuration as invalid and maintain current counter state

### Requirement 3

**User Story:** As a system designer, I want interrupt generation on first timeout, so that software can respond to watchdog expiration before system reset occurs

#### Acceptance Criteria

1. THE WDT_Device SHALL provide WDOGCONTROL bit[0] INTEN as interrupt enable control with reset value 1'b0
2. WHEN Down_Counter reaches zero AND INTEN equals 1, THE WDT_Device SHALL assert wdogint output signal
3. WHEN wdogint is asserted, THE WDT_Device SHALL maintain wdogint high until WDOGINTCLR receives a write operation
4. THE WDT_Device SHALL provide WDOGRIS register at offset 0x10 with bit[0] showing raw interrupt status
5. WHEN Down_Counter reaches zero, THE WDT_Device SHALL set WDOGRIS bit[0] to 1
6. THE WDT_Device SHALL provide WDOGMIS register at offset 0x14 with bit[0] equal to (WDOGRIS bit[0] AND INTEN)
7. WHEN WDOGINTCLR receives any write operation, THE WDT_Device SHALL clear WDOGRIS bit[0] to 0

### Requirement 4

**User Story:** As a system designer, I want system reset generation on second consecutive timeout, so that the system can recover from software failures that prevent interrupt handling

#### Acceptance Criteria

1. THE WDT_Device SHALL provide WDOGCONTROL bit[1] RESEN as reset enable control with reset value 1'b0
2. WHEN Down_Counter reaches zero AND RESEN equals 1 AND WDOGRIS bit[0] equals 1, THE WDT_Device SHALL assert wdogres output signal
3. WHEN wdogres is asserted, THE WDT_Device SHALL maintain wdogres high until system reset occurs
4. WHEN Down_Counter reaches zero AND RESEN equals 0, THE WDT_Device SHALL NOT assert wdogres regardless of WDOGRIS state
5. WHEN WDOGINTCLR receives a write operation, THE WDT_Device SHALL prevent wdogres assertion on the next timeout by clearing interrupt status

### Requirement 5

**User Story:** As a system designer, I want register lock protection, so that runaway software cannot accidentally disable or misconfigure the watchdog timer

#### Acceptance Criteria

1. THE WDT_Device SHALL provide WDOGLOCK register at offset 0xC00 with 32-bit read-write access and reset value 0x00000000
2. WHEN WDOGLOCK receives write value 0x1ACCE551, THE WDT_Device SHALL transition Lock_State to unlocked
3. WHEN WDOGLOCK receives write value other than 0x1ACCE551, THE WDT_Device SHALL transition Lock_State to locked
4. WHEN software reads WDOGLOCK AND Lock_State is unlocked, THE WDT_Device SHALL return 0x00000000
5. WHEN software reads WDOGLOCK AND Lock_State is locked, THE WDT_Device SHALL return 0x00000001
6. WHILE Lock_State is locked, THE WDT_Device SHALL ignore write operations to WDOGLOAD, WDOGVALUE, WDOGCONTROL, and WDOGINTCLR registers
7. WHILE Lock_State is unlocked, THE WDT_Device SHALL process write operations to WDOGLOAD, WDOGVALUE, WDOGCONTROL, and WDOGINTCLR registers normally

### Requirement 6

**User Story:** As a test engineer, I want integration test mode, so that I can directly control and verify interrupt and reset outputs without waiting for timeout events

#### Acceptance Criteria

1. THE WDT_Device SHALL provide WDOGITCR register at offset 0xF00 with bit[0] as integration test mode enable
2. WHEN WDOGITCR bit[0] equals 1, THE WDT_Device SHALL enter Integration_Test_Mode
3. WHEN WDOGITCR bit[0] equals 0, THE WDT_Device SHALL operate in normal countdown mode
4. THE WDT_Device SHALL provide WDOGITOP register at offset 0xF04 with bit[1] for wdogint control and bit[0] for wdogres control
5. WHILE in Integration_Test_Mode, THE WDT_Device SHALL drive wdogint output with the value written to WDOGITOP bit[1]
6. WHILE in Integration_Test_Mode, THE WDT_Device SHALL drive wdogres output with the value written to WDOGITOP bit[0]
7. WHILE in Integration_Test_Mode, THE WDT_Device SHALL ignore Down_Counter state for output signal generation

### Requirement 7

**User Story:** As a system integrator, I want peripheral identification registers, so that software can detect and verify the watchdog device type and version

#### Acceptance Criteria

1. THE WDT_Device SHALL provide WDOGPERIPHID4 register at offset 0xFD0 with read-only value 0x04
2. THE WDT_Device SHALL provide WDOGPERIPHID5 register at offset 0xFD4 with read-only value 0x00
3. THE WDT_Device SHALL provide WDOGPERIPHID6 register at offset 0xFD8 with read-only value 0x00
4. THE WDT_Device SHALL provide WDOGPERIPHID7 register at offset 0xFDC with read-only value 0x00
5. THE WDT_Device SHALL provide WDOGPERIPHID0 register at offset 0xFE0 with read-only value 0x24
6. THE WDT_Device SHALL provide WDOGPERIPHID1 register at offset 0xFE4 with read-only value 0xB8
7. THE WDT_Device SHALL provide WDOGPERIPHID2 register at offset 0xFE8 with read-only value 0x1B
8. THE WDT_Device SHALL provide WDOGPERIPHID3 register at offset 0xFEC with read-only value 0x00

### Requirement 8

**User Story:** As a system integrator, I want PrimeCell identification registers, so that software can identify the device as an ARM PrimeCell peripheral

#### Acceptance Criteria

1. THE WDT_Device SHALL provide WDOGPCELLID0 register at offset 0xFF0 with read-only value 0x0D
2. THE WDT_Device SHALL provide WDOGPCELLID1 register at offset 0xFF4 with read-only value 0xF0
3. THE WDT_Device SHALL provide WDOGPCELLID2 register at offset 0xFF8 with read-only value 0x05
4. THE WDT_Device SHALL provide WDOGPCELLID3 register at offset 0xFFC with read-only value 0xB1

### Requirement 9

**User Story:** As a platform integrator, I want the device mapped to QSP-x86 platform memory space, so that software can access watchdog registers through standard memory operations

#### Acceptance Criteria

1. THE WDT_Device SHALL map to base address 0x1000 in the QSP-x86 platform memory space
2. THE WDT_Device SHALL occupy address range 0x1000 to 0x1FFF with 4KB total address space
3. WHEN software accesses addresses within 0x1000 to 0x1FFF, THE WDT_Device SHALL respond to APB_Bus transactions
4. WHEN software accesses register offsets outside defined register map, THE WDT_Device SHALL return zero for reads and ignore writes
5. THE WDT_Device SHALL support 32-bit aligned register access operations

### Requirement 10

**User Story:** As a system designer, I want interrupt and reset signal outputs, so that the watchdog can integrate with platform interrupt and reset controllers

#### Acceptance Criteria

1. THE WDT_Device SHALL provide wdogint as an edge-triggered interrupt output signal
2. THE WDT_Device SHALL provide wdogres as a level-triggered reset output signal
3. WHEN wdogint transitions from low to high, THE WDT_Device SHALL generate an interrupt event for platform routing
4. WHEN wdogres is high, THE WDT_Device SHALL indicate reset request to platform reset controller
5. THE WDT_Device SHALL maintain signal output states independent of register read operations

### Requirement 11

**User Story:** As a developer, I want comprehensive logging and debugging support, so that I can trace watchdog behavior during simulation and development

#### Acceptance Criteria

1. WHEN any register receives a write operation, THE WDT_Device SHALL log the register name, offset, and written value at info level
2. WHEN any register receives a read operation, THE WDT_Device SHALL log the register name, offset, and returned value at debug level
3. WHEN Down_Counter reaches zero, THE WDT_Device SHALL log timeout event with current INTEN and RESEN states at info level
4. WHEN wdogint transitions from low to high, THE WDT_Device SHALL log interrupt assertion at info level
5. WHEN wdogres transitions from low to high, THE WDT_Device SHALL log reset assertion at warning level
6. WHEN Lock_State transitions, THE WDT_Device SHALL log new lock state at info level
7. WHEN Integration_Test_Mode is entered or exited, THE WDT_Device SHALL log mode transition at info level

### Requirement 12

**User Story:** As a Simics developer, I want DML 1.4 compliant implementation, so that the device integrates properly with Simics infrastructure and follows best practices

#### Acceptance Criteria

1. THE WDT_Device SHALL implement device model using DML 1.4 syntax and language features
2. THE WDT_Device SHALL use bank objects for register organization with proper offset specifications
3. THE WDT_Device SHALL use register and field objects for individual register and bit field definitions
4. THE WDT_Device SHALL implement read and write methods for register access behavior
5. THE WDT_Device SHALL use port objects for wdogint and wdogres signal outputs
6. THE WDT_Device SHALL follow Simics device modeling best practices for state management
7. THE WDT_Device SHALL provide proper device documentation through DML description strings
