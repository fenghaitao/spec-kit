# Interface Behavior Contracts: Simics Watchdog Timer Device

## Overview

This document specifies the interface behavior contracts for the Simics Watchdog Timer device. It defines the expected behavior of all external interfaces, including signal connections and memory-mapped register access. This contract ensures proper integration with the simulated system and defines clear boundaries between the watchdog device and its environment.

## Clock and Reset Interfaces

### wclk (Work Clock Input)
- **Interface Type**: Clock input
- **Connection Type**: Required input
- **Function**: Provides timing reference for timer decrement operations
- **Behavior**: 
  - The timer decrements based on this clock when enabled
  - Clock frequency determines the base rate of timer decrement
  - Used to schedule timeout events and calculate elapsed time
- **Constraints**: 
  - Must be connected for proper timer functionality
  - Frequency should match system expectations for proper timing

### wclk_en (Work Clock Enable)
- **Interface Type**: Signal input
- **Connection Type**: Required input
- **Function**: Enables/disables timer decrementing based on clock
- **Behavior**:
  - When high (1), timer decrements according to clock and prescaler
  - When low (0), timer stops decrementing regardless of wclk
- **Constraints**:
  - Must be properly driven to control timer operation
  - Changes should be reflected in timer behavior immediately

### wrst_n (Work Clock Domain Reset)
- **Interface Type**: Signal input (active low)
- **Connection Type**: Required input
- **Function**: Asynchronous reset for watchdog timer logic
- **Behavior**:
  - When low (0), device resets all internal state and registers to reset values
  - When high (1), device operates normally
  - Reset affects timer state, interrupt pending, and all registers
- **Constraints**:
  - Must be properly driven to handle system resets
  - Should reset the device to a known state matching specification

### prst_n (APB Bus Reset)
- **Interface Type**: Signal input (active low)
- **Connection Type**: Required input
- **Function**: Asynchronous reset for register interface and APB bus logic
- **Behavior**:
  - When low (0), resets all registers to their reset values
  - When high (1), register interface operates normally
  - Reset affects register values but may not immediately affect timer state
- **Constraints**:
  - Must be properly driven to handle bus resets
  - Should reset all registers to specification-defined reset values

## Interrupt and Reset Output Interfaces

### wdogint (Watchdog Interrupt Output)
- **Interface Type**: Signal output
- **Connection Type**: Optional output to interrupt controller
- **Function**: Interrupt signal output when counter reaches zero with INTEN enabled
- **Behavior**:
  - Initially low (0)
  - Rises to high (1) when counter reaches zero and WDOGCONTROL.INTEN=1
  - Remains high until cleared by writing to WDOGINTCLR or by disabling INTEN
  - Falls to low when WDOGINTCLR is written or INTEN is cleared
- **Signal Characteristics**:
  - Edge-triggered interrupt (rising edge)
  - Active high signal
  - Should follow interrupt controller signal interface specification
- **Timing Requirements**:
  - Should assert promptly when timeout condition occurs
  - Should deassert promptly when cleared via WDOGINTCLR

### wdogres (Watchdog Reset Output)
- **Interface Type**: Signal output
- **Connection Type**: Optional output to system reset logic
- **Function**: System reset signal output when counter reaches zero again with RESEN enabled and interrupt pending
- **Behavior**:
  - Initially low (0)
  - Rises to high (1) when counter reaches zero again while interrupt is pending and WDOGCONTROL.RESEN=1
  - Remains high until system reset occurs
  - Only cleared by system-level reset (not by WDOGINTCLR)
- **Signal Characteristics**:
  - Level-triggered signal (stays high)
  - Active high signal
  - Should follow system reset signal interface specification
- **Timing Requirements**:
  - Should assert promptly when double-timeout condition occurs
  - Should remain asserted until system reset

## Memory-Mapped Register Interface

### APB Bus Interface
- **Interface Type**: Memory-mapped register access via APB protocol
- **Connection Type**: Required for register access
- **Function**: Provides access to all device registers at specified address offsets
- **Address Range**: 0x1000 to 0x1FFF (4KB address space)
- **Register Access Behavior**:
  - Supports 32-bit and 8-bit read/write operations as specified
  - Byte enables for partial writes should be properly handled
  - Address decoding for register selection
  - Proper handling of read and write strobes

### Register Bank Configuration
- **Base Address**: 0x1000
- **Register Alignment**: 32-bit aligned for 32-bit registers, byte-aligned for 8-bit ID registers
- **Access Latency**: 
  - Read operations: Should complete in minimal simulation cycles
  - Write operations: Should complete in minimal simulation cycles
- **Error Handling**:
  - Invalid addresses should return appropriate defaults
  - Unsupported access sizes should return appropriate defaults
  - Unimplemented registers should be handled gracefully

## Register Interface Specifications

### WDOGLOAD (0x00) Interface
- **Access**: Read/Write
- **Behavior**: Stores reload value for timer; returns stored value on read
- **Side Effects**: None directly via interface; affects timer behavior internally

### WDOGVALUE (0x04) Interface
- **Access**: Read-Only
- **Behavior**: Returns current counter value calculated from internal state
- **Side Effects**: None; timer state unchanged by reads

### WDOGCONTROL (0x08) Interface
- **Access**: Read/Write
- **Behavior**: Controls timer operation, interrupt enable, reset enable, and clock divider
- **Side Effects**: Changes timer behavior, may trigger counter reload

### WDOGINTCLR (0x0C) Interface
- **Access**: Write-Only
- **Behavior**: Clears interrupt and reloads counter when written
- **Side Effects**: Updates internal interrupt state, triggers counter reload, may affect wdogint signal

### WDOGRIS (0x10) Interface
- **Access**: Read-Only
- **Behavior**: Returns raw interrupt status (unmasked)
- **Side Effects**: None

### WDOGMIS (0x14) Interface
- **Access**: Read-Only
- **Behavior**: Returns masked interrupt status (WDOGRIS AND WDOGCONTROL.INTEN)
- **Side Effects**: None

### WDOGLOCK (0xC00) Interface
- **Access**: Read/Write
- **Behavior**: Controls write access to other registers
- **Side Effects**: Affects write access permissions for all other registers

### WDOGITCR (0xF00) Interface
- **Access**: Read/Write
- **Behavior**: Controls integration test mode
- **Side Effects**: Changes operational mode, affects WDOGITOP functionality

### WDOGITOP (0xF04) Interface
- **Access**: Write-Only
- **Behavior**: Directly controls wdogint and wdogres when in test mode
- **Side Effects**: Directly drives output signals in test mode

### ID Registers (0xFD0-0xFFC) Interface
- **Access**: Read-Only
- **Behavior**: Return fixed identification values
- **Side Effects**: None

## State Machine Behavior

### IDLE State
- **Entry Condition**: WDOGCONTROL.INTEN = 0
- **Observable Indicators**: Counter stopped, no interrupts
- **Exit Condition**: WDOGCONTROL.INTEN set to 1
- **Interface Behavior**: Timer does not decrement; wdogint remains unchanged

### COUNTING State
- **Entry Condition**: WDOGCONTROL.INTEN = 1, counter > 0
- **Observable Indicators**: Counter decrements, WDOGVALUE changes
- **Exit Conditions**: Counter reaches 0 OR INTEN set to 0
- **Interface Behavior**: Timer decrements; wdogint remains unchanged

### INTERRUPT_PENDING State
- **Entry Condition**: Counter reaches 0 and WDOGCONTROL.INTEN = 1
- **Observable Indicators**: WDOGRIS[0] = 1, wdogint asserted
- **Exit Conditions**: Write to WDOGINTCLR OR WDOGCONTROL.INTEN to 0
- **Interface Behavior**: wdogint signal is driven high; counter reloads on WDOGINTCLR

### RESET_PENDING State
- **Entry Condition**: Interrupt pending and counter reaches 0 again with RESEN=1
- **Observable Indicators**: wdogres asserted
- **Exit Condition**: System reset
- **Interface Behavior**: wdogres signal is driven high; only cleared by system reset

## Integration Test Mode Interface Behavior

### Normal Mode (WDOGITCR[0] = 0)
- **Register Access**: All registers function as normal
- **Timer Operation**: Timer decrements normally based on configuration
- **Signal Outputs**: wdogint/wdogres controlled by timer logic

### Test Mode (WDOGITCR[0] = 1)
- **Register Access**: All registers accessible as normal
- **Timer Operation**: Timer decrementing suspended
- **Signal Outputs**: wdogint/wdogres controlled by WDOGITOP register
- **WDOGITOP Function**: Directly controls output signals
  - Bit 0: Controls wdogres signal
  - Bit 1: Controls wdogint signal

## Timing and Synchronization

### Clock Domain Crossing
- **wclk Domain**: Timer counter and related state
- **APB Domain**: Register interface and control logic
- **Synchronization**: Proper synchronization between domains for shared state variables

### Reset Synchronization
- **wrst_n**: Affects timer logic and state
- **prst_n**: Affects register state and interface
- **Coordinated Reset**: Both reset signals should properly reset all device state

## Error Handling and Robustness

### Invalid Register Access
- **Unaligned Accesses**: Should be handled gracefully with appropriate responses
- **Invalid Address Ranges**: Should return appropriate default values
- **Unsupported Access Sizes**: Should be handled per APB protocol

### Signal Integrity
- **Clock/Reset Glitches**: Device should handle brief glitches gracefully
- **Power Domain Issues**: Proper handling when clocks or resets are unstable

### Lock and Safety Features
- **Lock Status**: Proper enforcement of write protection
- **Test Mode Safety**: Safe transition between normal and test modes
- **Interrupt/Reset Sequences**: Proper handling of complex interrupt/reset sequences

## Performance Considerations

### Simulation Efficiency
- **Register Access**: Should maintain good simulation performance
- **Timer Updates**: Lazy evaluation to prevent per-cycle overhead
- **State Updates**: Efficient state change handling

### Memory Footprint
- **Saved Variables**: Minimal checkpointed state
- **Runtime Variables**: Efficient data structures
- **Interface Objects**: Proper memory management