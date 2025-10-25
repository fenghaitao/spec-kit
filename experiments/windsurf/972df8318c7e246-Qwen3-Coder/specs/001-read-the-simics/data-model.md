# Data Model: Simics Watchdog Timer Device Implementation

## Registers (Simics Projects)

### Register: WDOGLOAD
- **Offset**: 0x00
- **Size**: 32 bits
- **Access**: Read/Write
- **Reset Value**: 0xFFFFFFFF
- **Purpose**: Watchdog timer reload value
- **Fields**: 
  * wdog_load [31:0] - 32-bit watchdog timer reload value

### Register: WDOGVALUE
- **Offset**: 0x04
- **Size**: 32 bits
- **Access**: Read Only
- **Reset Value**: 0xFFFFFFFF
- **Purpose**: Current value of watchdog timer counter
- **Fields**: 
  * count_read [31:0] - 32-bit current value of watchdog counter

### Register: WDOGCONTROL
- **Offset**: 0x08
- **Size**: 32 bits
- **Access**: Read/Write
- **Reset Value**: 0x00000000
- **Purpose**: Control register for timer operation and interrupt/reset enable
- **Fields**: 
  * Reserved [31:5] - Reserved bits
  * step_value [4:2] - 3-bit clock divider setting (000=÷1, 001=÷2, 010=÷4, 011=÷8, 100=÷16)
  * RESEN [1] - Reset enable bit (1=enable reset output, 0=disable reset output)
  * INTEN [0] - Interrupt enable bit (1=enable interrupt, 0=disable interrupt)

### Register: WDOGINTCLR
- **Offset**: 0x0C
- **Size**: 32 bits
- **Access**: Write Only
- **Reset Value**: 0x00000000
- **Purpose**: Interrupt clear register - writing any value clears interrupt and reloads timer
- **Fields**: None (write-only register)

### Register: WDOGRIS
- **Offset**: 0x10
- **Size**: 1 bit (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000000
- **Purpose**: Raw interrupt status from the counter
- **Fields**: 
  * raw watchdog interrupt [0] - Raw interrupt status (1=interrupt pending, 0=no interrupt)
  * Reserved [31:1] - Reserved bits

### Register: WDOGMIS
- **Offset**: 0x14
- **Size**: 1 bit (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000000
- **Purpose**: Masked interrupt status (WS0 & INTEN)
- **Fields**: 
  * watchdog interrupt [0] - Masked interrupt status (1=interrupt enabled and pending, 0=no interrupt or interrupt disabled)
  * Reserved [31:1] - Reserved bits

### Register: WDOGLOCK
- **Offset**: 0xC00
- **Size**: 32 bits
- **Access**: Read/Write
- **Reset Value**: 0x00000000
- **Purpose**: Lock register controlling write access to other registers
- **Fields**: 
  * wdog_lock [31:0] - Lock value (0x1ACCE551=unlock, any other value=lock)

### Register: WDOGITCR
- **Offset**: 0xF00
- **Size**: 1 bit (in 32-bit register)
- **Access**: Read/Write
- **Reset Value**: 0x00000000
- **Purpose**: Integration test control register
- **Fields**: 
  * Integration test mode enable [0] - Test mode enable (1=enable test mode, 0=normal mode)
  * Reserved [31:1] - Reserved bits

### Register: WDOGITOP
- **Offset**: 0xF04
- **Size**: 2 bits (in 32-bit register)
- **Access**: Write Only
- **Reset Value**: 0x00000000
- **Purpose**: Integration test output set register
- **Fields**: 
  * Integration test mode WDOGINT value [1] - Test interrupt output value
  * Integration test mode WDOGRES value [0] - Test reset output value
  * Reserved [31:2] - Reserved bits

### Register: WDOGPERIPHID0
- **Offset**: 0xFE0
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000024
- **Purpose**: Peripheral identification register 0
- **Fields**: 
  * WDOG_PERIPH_ID0 [7:0] - Part number bits [7:0]
  * Reserved [31:8] - Reserved bits

### Register: WDOGPERIPHID1
- **Offset**: 0xFE4
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x000000B8
- **Purpose**: Peripheral identification register 1
- **Fields**: 
  * WDOG_PERIPH_ID1 [7:0] - JEP106 ID and part number bits [11:8]
  * Reserved [31:8] - Reserved bits

### Register: WDOGPERIPHID2
- **Offset**: 0xFE8
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x0000001B
- **Purpose**: Peripheral identification register 2
- **Fields**: 
  * WDOG_PERIPH_ID2 [7:0] - Revision, JEDEC used flag, and JEP106 ID bits [6:4]
  * Reserved [31:8] - Reserved bits

### Register: WDOGPERIPHID3
- **Offset**: 0xFEC
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 3
- **Fields**: 
  * WDOG_PERIPH_ID3 [7:0] - ECO revision number and customer modification number
  * Reserved [31:8] - Reserved bits

### Register: WDOGPERIPHID4
- **Offset**: 0xFD0
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000004
- **Purpose**: Peripheral identification register 4
- **Fields**: 
  * WDOG_PERIPH_ID4 [7:0] - Block count and JEP106 c code
  * Reserved [31:8] - Reserved bits

### Register: WDOGPERIPHID5
- **Offset**: 0xFD4
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 5
- **Fields**: 
  * WDOG_PERIPH_ID5 [7:0] - Peripheral ID register 5 (not used)
  * Reserved [31:8] - Reserved bits

### Register: WDOGPERIPHID6
- **Offset**: 0xFD8
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 6
- **Fields**: 
  * WDOG_PERIPH_ID6 [7:0] - Peripheral ID register 6 (not used)
  * Reserved [31:8] - Reserved bits

### Register: WDOGPERIPHID7
- **Offset**: 0xFDC
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 7
- **Fields**: 
  * WDOG_PERIPH_ID7 [7:0] - Peripheral ID register 7 (not used)
  * Reserved [31:8] - Reserved bits

### Register: WDOGPCELLID0
- **Offset**: 0xFF0
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x0000000D
- **Purpose**: PrimeCell identification register 0
- **Fields**: 
  * WDOG_PCELL_ID0 [7:0] - Component ID register 0
  * Reserved [31:8] - Reserved bits

### Register: WDOGPCELLID1
- **Offset**: 0xFF4
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x000000F0
- **Purpose**: PrimeCell identification register 1
- **Fields**: 
  * WDOG_PCELL_ID1 [7:0] - Component ID register 1
  * Reserved [31:8] - Reserved bits

### Register: WDOGPCELLID2
- **Offset**: 0xFF8
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x00000005
- **Purpose**: PrimeCell identification register 2
- **Fields**: 
  * WDOG_PCELL_ID2 [7:0] - Component ID register 2
  * Reserved [31:8] - Reserved bits

### Register: WDOGPCELLID3
- **Offset**: 0xFFC
- **Size**: 8 bits (in 32-bit register)
- **Access**: Read Only
- **Reset Value**: 0x000000B1
- **Purpose**: PrimeCell identification register 3
- **Fields**: 
  * WDOG_PCELL_ID3 [7:0] - Component ID register 3
  * Reserved [31:8] - Reserved bits

## Device State (Simics Projects)

### State Variable: timer_counter
- **Type**: uint64
- **Purpose**: Current value of the watchdog timer counter
- **Persistence**: checkpointed

### State Variable: timer_reload_value
- **Type**: uint64
- **Purpose**: Reload value for the watchdog timer
- **Persistence**: checkpointed

### State Variable: interrupt_pending
- **Type**: bool
- **Purpose**: Flag indicating if an interrupt is pending
- **Persistence**: checkpointed

### State Variable: registers_locked
- **Type**: bool
- **Purpose**: Flag indicating if registers are locked (write protection enabled)
- **Persistence**: checkpointed

### State Variable: integration_test_mode
- **Type**: bool
- **Purpose**: Flag indicating if integration test mode is enabled
- **Persistence**: checkpointed

### State Variable: test_interrupt_value
- **Type**: bool
- **Purpose**: Test value for interrupt output in integration test mode
- **Persistence**: checkpointed

### State Variable: test_reset_value
- **Type**: bool
- **Purpose**: Test value for reset output in integration test mode
- **Persistence**: checkpointed

## Interfaces (Simics Projects)

### Interface: interrupt_signal
- **Type**: signal_connect
- **Methods**: 
  * signal_raise() - Assert the interrupt signal
  * signal_lower() - Deassert the interrupt signal
- **Purpose**: Output interrupt signal for first timeout

### Interface: reset_signal
- **Type**: signal_connect
- **Methods**: 
  * signal_raise() - Assert the reset signal
  * signal_lower() - Deassert the reset signal
- **Purpose**: Output reset signal for second timeout

### Interface: clock
- **Type**: input signal
- **Methods**: 
  * clock_input() - Receive clock signal for timer operation
- **Purpose**: Input clock signal for timer operation

### Interface: reset_input
- **Type**: input signal
- **Methods**: 
  * reset_assert() - Handle reset assertion
- **Purpose**: Input reset signal for device reset
