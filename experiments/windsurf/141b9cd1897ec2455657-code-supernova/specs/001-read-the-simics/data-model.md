# Data Model: Simics Watchdog Timer Device

## Registers

### Register: WDOGLOAD
- **Offset**: 0x000
- **Size**: 32 bits
- **Access**: R/W
- **Reset Value**: 0xFFFFFFFF
- **Purpose**: Load register containing the reload value for the watchdog counter. When the counter is enabled or when an interrupt is cleared, the counter is reloaded with this value.
- **Fields**: Single 32-bit value (no bit fields)
- **Lock Protection**: Yes - writes ignored when WDOGLOCK is locked

### Register: WDOGVALUE
- **Offset**: 0x004
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0xFFFFFFFF
- **Purpose**: Current value of the watchdog counter. Provides read-only access to the down-counter value.
- **Fields**: Single 32-bit value (no bit fields)
- **Lock Protection**: No - always readable

### Register: WDOGCONTROL
- **Offset**: 0x008
- **Size**: 32 bits
- **Access**: R/W
- **Reset Value**: 0x00000000
- **Purpose**: Control register for watchdog timer configuration
- **Fields**:
  - **Bits [31:5]**: Reserved (read as zero, writes ignored)
  - **Bits [4:2]**: step_value - Clock divider selection
    * 0b000 = ÷1 (no division)
    * 0b001 = ÷2
    * 0b010 = ÷4
    * 0b011 = ÷8
    * 0b100 = ÷16
    * 0b101-0b111 = Undefined (treat as ÷1)
  - **Bit [1]**: RESEN - Reset enable
    * 0 = Reset output disabled
    * 1 = Reset output enabled on second timeout
  - **Bit [0]**: INTEN - Interrupt enable and counter enable
    * 0 = Counter disabled, interrupt disabled
    * 1 = Counter enabled, interrupt enabled
- **Lock Protection**: Yes - writes ignored when WDOGLOCK is locked

### Register: WDOGINTCLR
- **Offset**: 0x00C
- **Size**: 32 bits
- **Access**: WO (Write-Only)
- **Reset Value**: N/A (write-only)
- **Purpose**: Interrupt clear register. Any write to this register clears the watchdog interrupt and reloads the counter from WDOGLOAD.
- **Fields**: Single 32-bit value (value written is ignored, only the write action matters)
- **Lock Protection**: No - always writable

### Register: WDOGRIS
- **Offset**: 0x010
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000000
- **Purpose**: Raw interrupt status register (unmasked by INTEN)
- **Fields**:
  - **Bit [0]**: Raw interrupt status
    * 0 = No interrupt pending
    * 1 = Interrupt pending (counter reached zero)
  - **Bits [31:1]**: Reserved (read as zero)
- **Lock Protection**: No - always readable

### Register: WDOGMIS
- **Offset**: 0x014
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000000
- **Purpose**: Masked interrupt status register (WDOGRIS AND INTEN)
- **Fields**:
  - **Bit [0]**: Masked interrupt status
    * 0 = No masked interrupt
    * 1 = Masked interrupt (WDOGRIS[0] AND WDOGCONTROL.INTEN)
  - **Bits [31:1]**: Reserved (read as zero)
- **Lock Protection**: No - always readable

### Register: WDOGLOCK
- **Offset**: 0xC00
- **Size**: 32 bits
- **Access**: R/W
- **Reset Value**: 0x00000000 (unlocked)
- **Purpose**: Lock register for write protection of WDOGLOAD and WDOGCONTROL
- **Write Behavior**:
  - Write 0x1ACCE551 to unlock (enable writes to protected registers)
  - Write any other value to lock (disable writes to protected registers)
- **Read Behavior**:
  - Returns 0x00000000 when unlocked
  - Returns 0x00000001 when locked
- **Fields**: Single 32-bit value
- **Lock Protection**: No - always writable (to allow unlocking)

### Register: WDOGITCR
- **Offset**: 0xF00
- **Size**: 32 bits
- **Access**: R/W
- **Reset Value**: 0x00000000
- **Purpose**: Integration test control register
- **Fields**:
  - **Bit [0]**: Integration test mode enable
    * 0 = Normal operation mode
    * 1 = Integration test mode (disables normal counter operation)
  - **Bits [31:1]**: Reserved (read as zero, writes ignored)
- **Lock Protection**: No - always writable

### Register: WDOGITOP
- **Offset**: 0xF04
- **Size**: 32 bits
- **Access**: WO (Write-Only)
- **Reset Value**: N/A (write-only)
- **Purpose**: Integration test output set register. In integration test mode, allows direct control of wdogint and wdogres signals.
- **Fields**:
  - **Bit [0]**: wdogres output value (when WDOGITCR[0]=1)
  - **Bit [1]**: wdogint output value (when WDOGITCR[0]=1)
  - **Bits [31:2]**: Reserved (writes ignored)
- **Lock Protection**: No - always writable

### Register: WDOGPERIPHID4
- **Offset**: 0xFD0
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000004
- **Purpose**: Peripheral ID register 4
- **Fields**: Constant value 0x04
- **Lock Protection**: No - always readable

### Register: WDOGPERIPHID5
- **Offset**: 0xFD4
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral ID register 5
- **Fields**: Constant value 0x00
- **Lock Protection**: No - always readable

### Register: WDOGPERIPHID6
- **Offset**: 0xFD8
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral ID register 6
- **Fields**: Constant value 0x00
- **Lock Protection**: No - always readable

### Register: WDOGPERIPHID7
- **Offset**: 0xFDC
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral ID register 7
- **Fields**: Constant value 0x00
- **Lock Protection**: No - always readable

### Register: WDOGPERIPHID0
- **Offset**: 0xFE0
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000024
- **Purpose**: Peripheral ID register 0
- **Fields**: Constant value 0x24
- **Lock Protection**: No - always readable

### Register: WDOGPERIPHID1
- **Offset**: 0xFE4
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x000000B8
- **Purpose**: Peripheral ID register 1
- **Fields**: Constant value 0xB8
- **Lock Protection**: No - always readable

### Register: WDOGPERIPHID2
- **Offset**: 0xFE8
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x0000001B
- **Purpose**: Peripheral ID register 2
- **Fields**: Constant value 0x1B
- **Lock Protection**: No - always readable

### Register: WDOGPERIPHID3
- **Offset**: 0xFEC
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral ID register 3
- **Fields**: Constant value 0x00
- **Lock Protection**: No - always readable

### Register: WDOGPCELLID0
- **Offset**: 0xFF0
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x0000000D
- **Purpose**: PrimeCell ID register 0
- **Fields**: Constant value 0x0D
- **Lock Protection**: No - always readable

### Register: WDOGPCELLID1
- **Offset**: 0xFF4
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x000000F0
- **Purpose**: PrimeCell ID register 1
- **Fields**: Constant value 0xF0
- **Lock Protection**: No - always readable

### Register: WDOGPCELLID2
- **Offset**: 0xFF8
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x00000005
- **Purpose**: PrimeCell ID register 2
- **Fields**: Constant value 0x05
- **Lock Protection**: No - always readable

### Register: WDOGPCELLID3
- **Offset**: 0xFFC
- **Size**: 32 bits
- **Access**: RO (Read-Only)
- **Reset Value**: 0x000000B1
- **Purpose**: PrimeCell ID register 3
- **Fields**: Constant value 0xB1
- **Lock Protection**: No - always readable

## Device State

### State Variable: counter_start_time
- **Type**: cycles_t (Simics cycle count type)
- **Purpose**: Records the simulation cycle count when the counter was last started or reloaded
- **Persistence**: Checkpointed (saved)
- **Usage**: Used to calculate current counter value based on elapsed cycles and clock divider

### State Variable: counter_start_value
- **Type**: uint32
- **Purpose**: Records the value loaded into the counter when it was last started or reloaded
- **Persistence**: Checkpointed (saved)
- **Usage**: Combined with counter_start_time to calculate current counter value

### State Variable: interrupt_pending
- **Type**: bool
- **Purpose**: Tracks whether the first timeout has occurred (raw interrupt status)
- **Persistence**: Checkpointed (saved)
- **Usage**: Corresponds to WDOGRIS[0]; set when counter reaches zero with INTEN=1

### State Variable: reset_asserted
- **Type**: bool
- **Purpose**: Tracks whether the reset signal has been asserted (second timeout occurred)
- **Persistence**: Checkpointed (saved)
- **Usage**: Set when counter reaches zero for second time with RESEN=1; remains set until device reset

### State Variable: lock_state
- **Type**: bool
- **Purpose**: Tracks whether the device is locked (write protection enabled)
- **Persistence**: Checkpointed (saved)
- **Usage**: Controls write access to WDOGLOAD and WDOGCONTROL; true=locked, false=unlocked

### State Variable: integration_test_mode
- **Type**: bool
- **Purpose**: Tracks whether integration test mode is enabled
- **Persistence**: Checkpointed (saved)
- **Usage**: When true, disables normal counter operation and enables direct signal control via WDOGITOP

### State Variable: divider_counter
- **Type**: uint32
- **Purpose**: Internal counter for clock divider implementation
- **Persistence**: Transient (session) - recalculated from counter_start_time
- **Usage**: Tracks cycles within current divider period; counter decrements when divider_counter reaches step_value threshold

## Interfaces

### Interface: io_memory
- **Type**: Simics io_memory interface
- **Methods**: 
  - `operation(generic_transaction_t *memop, map_info_t info) -> exception_type_t`
  - Handles memory-mapped register read/write transactions
- **Purpose**: Provides memory-mapped I/O access to all 21 watchdog timer registers
- **Address Range**: 4KB (0x000 - 0xFFF)
- **Transaction Handling**: 
  - Decode offset to determine target register
  - Apply lock protection for WDOGLOAD and WDOGCONTROL writes
  - Handle write-only registers (WDOGINTCLR, WDOGITOP)
  - Handle read-only registers (WDOGVALUE, WDOGRIS, WDOGMIS, identification registers)

### Interface: signal (wdogint)
- **Type**: Simics signal interface (via signal_connect template)
- **Methods**:
  - `signal_raise()` - Assert interrupt signal
  - `signal_lower()` - Deassert interrupt signal
- **Purpose**: Provides interrupt output signal to platform interrupt controller
- **Behavior**:
  - Raised when counter reaches zero and INTEN=1
  - Lowered when interrupt is cleared via WDOGINTCLR write
  - Directly controlled by WDOGITOP[1] in integration test mode

### Interface: signal (wdogres)
- **Type**: Simics signal interface (via signal_connect template)
- **Methods**:
  - `signal_raise()` - Assert reset signal
  - `signal_lower()` - Deassert reset signal (only on device reset)
- **Purpose**: Provides reset output signal to platform reset controller
- **Behavior**:
  - Raised when counter reaches zero for second time and RESEN=1
  - Remains asserted until device reset occurs
  - Directly controlled by WDOGITOP[0] in integration test mode

## Memory Map Summary

| Offset Range | Register Group | Count | Description |
|--------------|----------------|-------|-------------|
| 0x000-0x014 | Control/Data | 6 | WDOGLOAD, WDOGVALUE, WDOGCONTROL, WDOGINTCLR, WDOGRIS, WDOGMIS |
| 0x018-0xBFC | Reserved | - | Unmapped (reads return 0, writes ignored) |
| 0xC00-0xC00 | Lock | 1 | WDOGLOCK |
| 0xC04-0xEFC | Reserved | - | Unmapped (reads return 0, writes ignored) |
| 0xF00-0xF04 | Integration Test | 2 | WDOGITCR, WDOGITOP |
| 0xF08-0xFCC | Reserved | - | Unmapped (reads return 0, writes ignored) |
| 0xFD0-0xFDC | Peripheral ID 4-7 | 4 | WDOGPERIPHID4-7 |
| 0xFE0-0xFEC | Peripheral ID 0-3 | 4 | WDOGPERIPHID0-3 |
| 0xFF0-0xFFC | PrimeCell ID 0-3 | 4 | WDOGPCELLID0-3 |

**Total Registers**: 21  
**Total Address Space**: 4KB (0x000-0xFFF)  
**Unmapped Regions**: Return 0 on read, ignore writes
