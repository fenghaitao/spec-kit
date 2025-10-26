# Data Model: Simics Watchdog Timer Device

**Branch**: `001-create-a-comprehensive`
**Phase**: Phase 1 - Design
**Created**: 2025
**Status**: Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Register Definitions](#register-definitions)
3. [Device State Variables](#device-state-variables)
4. [Interface Specifications](#interface-specifications)
5. [Memory-Mapped Regions](#memory-mapped-regions)
6. [State Machine](#state-machine)

---

## Overview

The Simics Watchdog Timer device implements the ARM PrimeCell SP805 watchdog timer specification using DML 1.4. This document defines the complete data model including all registers, state variables, interfaces, and memory-mapped regions.

**Device Type**: Timer peripheral  
**Memory Footprint**: 4KB (0x000 - 0xFFF)  
**Register Count**: 21  
**Output Signals**: 2 (wdogint, wdogres)  
**Input Signals**: 3 (wclk, prst_n, wrst_n)  

---

## Register Definitions

### Control and Status Registers

#### WDOGLOAD (0x000)
**Load Register**

| Property | Value |
|----------|-------|
| Offset | 0x000 |
| Size | 4 bytes (32-bit) |
| Access | Read/Write |
| Reset Value | 0xFFFFFFFF |
| Lock Protected | Yes |

**Description**: Contains the value from which the counter is to decrement. When written, this value is immediately loaded into the counter. This value is reloaded when WDOGINTCLR is written (interrupt clear and counter reload).

**Field Layout**:
```
[31:0] LOAD - Watchdog load value
```

---

#### WDOGVALUE (0x004)
**Value Register**

| Property | Value |
|----------|-------|
| Offset | 0x004 |
| Size | 4 bytes (32-bit) |
| Access | Read-Only |
| Reset Value | 0xFFFFFFFF |
| Lock Protected | No |

**Description**: Provides the current value of the decrementing counter. This is a read-only register that dynamically calculates the counter value based on elapsed cycles.

**Field Layout**:
```
[31:0] VALUE - Current counter value (read-only)
```

**Implementation Note**: This register does not store a static value. The `read()` method must calculate the current counter value based on:
- `counter_start_value`: Value loaded from WDOGLOAD
- `counter_start_time`: Cycle count when counter started (SIM_cycle_count)
- `step_value`: Clock divider (1, 16, or 256)
- Current cycle count: `SIM_cycle_count(dev.obj)`

---

#### WDOGCONTROL (0x008)
**Control Register**

| Property | Value |
|----------|-------|
| Offset | 0x008 |
| Size | 4 bytes (32-bit) |
| Access | Read/Write |
| Reset Value | 0x00000000 |
| Lock Protected | Yes |

**Description**: Enables the watchdog timer and interrupt generation.

**Field Layout**:
```
[31:2] Reserved (RAZ/WI)
[1]    RESEN - Reset enable (0=disabled, 1=enabled)
[0]    INTEN - Interrupt enable (0=disabled, 1=enabled)
```

**Field Descriptions**:
- **INTEN** (bit 0): When set, enables interrupt generation on counter timeout
- **RESEN** (bit 1): When set, enables reset generation on second timeout (if interrupt not cleared)

**Implementation Note**: Writing to this register when locked is ignored. Writing 1 to INTEN starts the counter if not already running. Writing 0 stops the counter.

---

#### WDOGINTCLR (0x00C)
**Interrupt Clear Register**

| Property | Value |
|----------|-------|
| Offset | 0x00C |
| Size | 4 bytes (32-bit) |
| Access | Write-Only |
| Reset Value | N/A |
| Lock Protected | Yes |

**Description**: Writing any value to this register clears the watchdog interrupt and reloads the counter from WDOGLOAD.

**Field Layout**:
```
[31:0] INTCLR - Interrupt clear (write any value)
```

**Implementation Note**: 
- This is a write-only register; reads return undefined values (typically 0)
- Writing clears interrupt signal, reloads counter from WDOGLOAD, and cancels pending reset event
- Writes blocked when locked or in integration test mode

---

#### WDOGRIS (0x010)
**Raw Interrupt Status Register**

| Property | Value |
|----------|-------|
| Offset | 0x010 |
| Size | 4 bytes (32-bit) |
| Access | Read-Only |
| Reset Value | 0x00000000 |
| Lock Protected | No |

**Description**: Provides the raw interrupt status (not affected by INTEN).

**Field Layout**:
```
[31:1] Reserved (RAZ)
[0]    RAWINT - Raw interrupt status (0=no interrupt, 1=interrupt pending)
```

**Implementation Note**: This reflects the internal `interrupt_pending` state variable, regardless of INTEN setting.

---

#### WDOGMIS (0x014)
**Masked Interrupt Status Register**

| Property | Value |
|----------|-------|
| Offset | 0x014 |
| Size | 4 bytes (32-bit) |
| Access | Read-Only |
| Reset Value | 0x00000000 |
| Lock Protected | No |

**Description**: Provides the masked interrupt status (WDOGRIS AND WDOGCONTROL.INTEN).

**Field Layout**:
```
[31:1] Reserved (RAZ)
[0]    MASKINT - Masked interrupt status
```

**Implementation Note**: Calculated as `WDOGRIS.RAWINT & WDOGCONTROL.INTEN`.

---

### Lock Register

#### WDOGLOCK (0xC00)
**Lock Register**

| Property | Value |
|----------|-------|
| Offset | 0xC00 |
| Size | 4 bytes (32-bit) |
| Access | Read/Write |
| Reset Value | 0x00000001 (locked) |
| Lock Protected | No (self-locking) |

**Description**: Protects the watchdog control registers from inadvertent modification. Writing the magic unlock value 0x1ACCE551 unlocks the device.

**Field Layout**:
```
[31:1] Reserved
[0]    LOCK - Lock status (0=unlocked, 1=locked)
```

**Magic Values**:
- **0x1ACCE551**: Unlock value (read returns 0 when unlocked)
- **Any other value**: Lock value (read returns 1 when locked)

**Implementation Note**: 
- Device starts locked after reset (reads as 0x1)
- Writing 0x1ACCE551 unlocks device (reads as 0x0)
- Writing any other value locks device (reads as 0x1)
- Lock state persists across operations until explicitly changed

---

### Integration Test Registers

#### WDOGITCR (0xF00)
**Integration Test Control Register**

| Property | Value |
|----------|-------|
| Offset | 0xF00 |
| Size | 4 bytes (32-bit) |
| Access | Read/Write |
| Reset Value | 0x00000000 |
| Lock Protected | No |

**Description**: Enables integration test mode for direct control of output signals.

**Field Layout**:
```
[31:1] Reserved (RAZ/WI)
[0]    ITEN - Integration test mode enable (0=normal mode, 1=test mode)
```

**Implementation Note**: When ITEN=1, WDOGITOP register controls output signals directly, bypassing normal watchdog logic.

---

#### WDOGITOP (0xF04)
**Integration Test Output Set Register**

| Property | Value |
|----------|-------|
| Offset | 0xF04 |
| Size | 4 bytes (32-bit) |
| Access | Write-Only |
| Reset Value | N/A |
| Lock Protected | No |

**Description**: Directly controls interrupt and reset output signals when integration test mode is enabled.

**Field Layout**:
```
[31:2] Reserved
[1]    WDOGRES - Direct reset output control (when ITEN=1)
[0]    WDOGINT - Direct interrupt output control (when ITEN=1)
```

**Implementation Note**: 
- Writes ignored when WDOGITCR.ITEN=0
- Writing 1 to bit sets corresponding output signal high
- Writing 0 to bit sets corresponding output signal low
- This is a write-only register; reads return undefined values

---

### Peripheral Identification Registers

#### WDOGPeriphID0 (0xFE0)
**Peripheral ID Register 0**

| Property | Value |
|----------|-------|
| Offset | 0xFE0 |
| Size | 4 bytes (32-bit) |
| Access | Read-Only |
| Reset Value | 0x00000005 |

**Field Layout**:
```
[7:0] PARTNUMBER0 - Bits [7:0] of part number (0x05)
```

---

#### WDOGPeriphID1 (0xFE4)
**Peripheral ID Register 1**

| Property | Value |
|----------|-------|
| Offset | 0xFE4 |
| Size | 4 bytes (32-bit) |
| Access | Read-Only |
| Reset Value | 0x00000018 |

**Field Layout**:
```
[7:4] DESIGNER0 - Bits [3:0] of designer identity (0x1)
[3:0] PARTNUMBER1 - Bits [11:8] of part number (0x8)
```

---

#### WDOGPeriphID2 (0xFE8)
**Peripheral ID Register 2**

| Property | Value |
|----------|-------|
| Offset | 0xFE8 |
| Size | 4 bytes (32-bit) |
| Access | Read-Only |
| Reset Value | 0x00000018 |

**Field Layout**:
```
[7:4] REVISION - Revision number (0x1)
[3]   USESJEPCODE - JEP code indicator (1)
[2:0] DESIGNER1 - Bits [6:4] of designer identity (0x0)
```

---

#### WDOGPeriphID3 (0xFEC)
**Peripheral ID Register 3**

| Property | Value |
|----------|-------|
| Offset | 0xFEC |
| Size | 4 bytes (32-bit) |
| Access | Read-Only |
| Reset Value | 0x00000000 |

**Field Layout**:
```
[7:4] CONFIGURATION - Configuration options (0x0)
[3:0] MOD_NUMBER - Module number (0x0)
```

---

#### WDOGPCellID0-3 (0xFF0-0xFFC)
**PrimeCell ID Registers**

| Offset | Reset Value | Description |
|--------|-------------|-------------|
| 0xFF0 | 0x0000000D | PrimeCell ID byte 0 |
| 0xFF4 | 0x000000F0 | PrimeCell ID byte 1 |
| 0xFF8 | 0x00000005 | PrimeCell ID byte 2 |
| 0xFFC | 0x000000B1 | PrimeCell ID byte 3 |

**Purpose**: Standard ARM PrimeCell identification pattern (0xB105F00D when read as word sequence).

---

## Device State Variables

### Saved State Variables (Checkpoint Persistent)

These variables are marked as `saved` and persist across checkpoint/restore operations:

```dml
bank regs {
    // Counter timing state
    saved cycles_t counter_start_time;      // Cycle count when counter started
    saved uint32 counter_start_value;       // Value loaded into counter
    saved uint32 step_value;                // Clock divider (1, 16, or 256)
    
    // Interrupt and reset state
    saved bool interrupt_pending;           // Raw interrupt status
    saved bool reset_pending;               // Reset event pending
    
    // Lock protection state
    saved bool lock_state;                  // Lock status (true=locked)
    
    // Integration test mode state
    saved bool integration_test_mode;       // Test mode enabled
}
```

### Session State Variables (Transient)

These variables are marked as `session` and are not persisted in checkpoints:

```dml
bank regs {
    // Event handles (automatically rescheduled on restore)
    session event_handle_t interrupt_event;  // Scheduled interrupt timeout
    session event_handle_t reset_event;      // Scheduled reset timeout
}
```

### Computed Values (No Storage)

These values are computed on-demand and do not require storage:

- **current_counter_value**: Calculated in WDOGVALUE.read() method
- **masked_interrupt_status**: Calculated as WDOGRIS & WDOGCONTROL.INTEN
- **cycles_to_timeout**: Calculated for event scheduling

---

## Interface Specifications

### io_memory Interface

**Purpose**: Handles memory-mapped register access from CPU/bus masters

**Methods**:
- `operation(generic_transaction_t *trans)`: Process read/write transactions
- Auto-dispatches to appropriate register based on offset

**Address Range**: 0x000 - 0xFFF (4KB)

**Transaction Types**:
- **Read**: Returns current register value (or computed value for WDOGVALUE)
- **Write**: Updates register value (subject to lock protection and access type)

**Error Handling**:
- Invalid address access logs warning and returns/ignores data
- Writes to read-only registers log warning and are ignored
- Reads from write-only registers return 0

---

### signal Interface (Outputs)

#### wdogint_signal
**Purpose**: Interrupt output signal to interrupt controller

**Type**: signal_connect

**Protocol**:
- Level signal (held high while interrupt pending)
- Cleared by writing to WDOGINTCLR
- Can be directly controlled via WDOGITOP when integration test mode enabled

**Implementation**:
```dml
connect wdogint_signal is signal_connect {
    param documentation = "Watchdog interrupt output signal";
}
```

**Operations**:
- `set_level(1)`: Assert interrupt (raise)
- `set_level(0)`: Deassert interrupt (lower)

---

#### wdogres_signal
**Purpose**: Reset output signal to system reset controller

**Type**: signal_connect

**Protocol**:
- Pulse signal (asserted when counter reaches zero for second time without interrupt clear)
- Typically triggers system reset
- Can be directly controlled via WDOGITOP when integration test mode enabled

**Implementation**:
```dml
connect wdogres_signal is signal_connect {
    param documentation = "Watchdog reset output signal";
}
```

**Operations**:
- `set_level(1)`: Assert reset
- `set_level(0)`: Deassert reset (typically held low except during reset event)

---

### event Interface (Internal)

#### Countdown Event Scheduling

**Purpose**: Schedule timeout events based on counter value and clock divider

**API**: DML `after` statement

**Event Types**:
1. **Interrupt Timeout Event**: Fires when counter reaches zero for first time
2. **Reset Timeout Event**: Fires when counter reaches zero for second time (if interrupt not cleared)

**Scheduling Formula**:
```
cycles_to_timeout = counter_value * step_value
after cycles_to_timeout cycles: timeout_handler();
```

**Event Management**:
- `cancel_after()`: Cancel pending event (called when counter modified)
- Events automatically rescheduled on checkpoint restore
- Event handles stored as `session` variables (transient)

---

## Memory-Mapped Regions

### Complete Register Map

```
Base Address: 0x0000 (configurable during device instantiation)
Total Size: 4KB (0x1000)

┌─────────────────────────────────────────────────────────────┐
│ Control and Status Registers        0x000 - 0x01F (32 bytes)│
├─────────────────────────────────────────────────────────────┤
│ 0x000  WDOGLOAD       [RW]  Load value register             │
│ 0x004  WDOGVALUE      [RO]  Current counter value           │
│ 0x008  WDOGCONTROL    [RW]  Interrupt/reset enable          │
│ 0x00C  WDOGINTCLR     [WO]  Interrupt clear                 │
│ 0x010  WDOGRIS        [RO]  Raw interrupt status            │
│ 0x014  WDOGMIS        [RO]  Masked interrupt status         │
│ 0x018-0x01F           Reserved                              │
├─────────────────────────────────────────────────────────────┤
│ Reserved                            0x020 - 0xBFF (3040 B)  │
├─────────────────────────────────────────────────────────────┤
│ Lock Register                       0xC00 - 0xC03 (4 bytes) │
├─────────────────────────────────────────────────────────────┤
│ 0xC00  WDOGLOCK       [RW]  Lock register (0x1ACCE551)      │
├─────────────────────────────────────────────────────────────┤
│ Reserved                            0xC04 - 0xEFF (764 B)   │
├─────────────────────────────────────────────────────────────┤
│ Integration Test Registers          0xF00 - 0xF0F (16 bytes)│
├─────────────────────────────────────────────────────────────┤
│ 0xF00  WDOGITCR       [RW]  Integration test control        │
│ 0xF04  WDOGITOP       [WO]  Integration test output set     │
│ 0xF08-0xF0F           Reserved                              │
├─────────────────────────────────────────────────────────────┤
│ Reserved                            0xF10 - 0xFDF (208 B)   │
├─────────────────────────────────────────────────────────────┤
│ Peripheral ID Registers             0xFE0 - 0xFEF (16 bytes)│
├─────────────────────────────────────────────────────────────┤
│ 0xFE0  WDOGPeriphID0  [RO]  Peripheral ID 0 (0x05)          │
│ 0xFE4  WDOGPeriphID1  [RO]  Peripheral ID 1 (0x18)          │
│ 0xFE8  WDOGPeriphID2  [RO]  Peripheral ID 2 (0x18)          │
│ 0xFEC  WDOGPeriphID3  [RO]  Peripheral ID 3 (0x00)          │
├─────────────────────────────────────────────────────────────┤
│ PrimeCell ID Registers              0xFF0 - 0xFFF (16 bytes)│
├─────────────────────────────────────────────────────────────┤
│ 0xFF0  WDOGPCellID0   [RO]  PrimeCell ID 0 (0x0D)           │
│ 0xFF4  WDOGPCellID1   [RO]  PrimeCell ID 1 (0xF0)           │
│ 0xFF8  WDOGPCellID2   [RO]  PrimeCell ID 2 (0x05)           │
│ 0xFFC  WDOGPCellID3   [RO]  PrimeCell ID 3 (0xB1)           │
└─────────────────────────────────────────────────────────────┘

Legend:
  [RO] Read-Only
  [WO] Write-Only
  [RW] Read-Write
```

### Access Protection Rules

1. **Lock Protected Registers** (require WDOGLOCK unlocked):
   - WDOGLOAD (0x000)
   - WDOGCONTROL (0x008)
   - WDOGINTCLR (0x00C)

2. **Read-Only Registers** (writes ignored):
   - WDOGVALUE (0x004)
   - WDOGRIS (0x010)
   - WDOGMIS (0x014)
   - All PeriphID and PCellID registers (0xFE0-0xFFF)

3. **Write-Only Registers** (reads return 0):
   - WDOGINTCLR (0x00C)
   - WDOGITOP (0xF04)

4. **Reserved Regions** (access logs warning):
   - 0x018-0x01F
   - 0x020-0xBFF
   - 0xC04-0xEFF
   - 0xF08-0xF0F
   - 0xF10-0xFDF

---

## State Machine

### Operational States

```
┌──────────────────────────────────────────────────────────────┐
│                      IDLE STATE                              │
│  - Counter not running                                       │
│  - WDOGCONTROL.INTEN = 0                                     │
│  - No events scheduled                                       │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ Write WDOGCONTROL.INTEN=1
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    COUNTING STATE                            │
│  - Counter decrementing                                      │
│  - WDOGCONTROL.INTEN = 1                                     │
│  - Interrupt event scheduled                                 │
│  - WDOGVALUE dynamically calculated                          │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ Counter reaches 0
                           ▼
┌──────────────────────────────────────────────────────────────┐
│               INTERRUPT PENDING STATE                        │
│  - Interrupt asserted (wdogint=1)                            │
│  - Counter reloaded and counting down again                  │
│  - Reset event scheduled                                     │
│  - WDOGRIS.RAWINT = 1                                        │
└──────────────────────────────────────────────────────────────┘
        │                                  │
        │ Write WDOGINTCLR                 │ Counter reaches 0 again
        │                                  │ (WDOGCONTROL.RESEN=1)
        ▼                                  ▼
┌────────────────────┐          ┌─────────────────────────────┐
│  COUNTING STATE    │          │     RESET ASSERTED          │
│  (interrupt clear) │          │  - wdogres=1                │
│  - wdogint=0       │          │  - System reset triggered   │
│  - WDOGRIS.RAWINT=0│          │                             │
└────────────────────┘          └─────────────────────────────┘
```

### State Transitions

| From State | Event | To State | Actions |
|------------|-------|----------|---------|
| IDLE | Write WDOGCONTROL.INTEN=1 | COUNTING | Load counter from WDOGLOAD, record start time, schedule interrupt event |
| COUNTING | Counter reaches 0 | INTERRUPT_PENDING | Assert wdogint, set WDOGRIS.RAWINT=1, reload counter, schedule reset event |
| INTERRUPT_PENDING | Write WDOGINTCLR | COUNTING | Clear wdogint, clear WDOGRIS.RAWINT, reload counter, cancel reset event |
| INTERRUPT_PENDING | Counter reaches 0 & RESEN=1 | RESET_ASSERTED | Assert wdogres |
| COUNTING | Write WDOGCONTROL.INTEN=0 | IDLE | Cancel interrupt event |
| Any | Write WDOGLOAD | Same | Update counter_start_value, reschedule events |

### Special Mode: Integration Test

When WDOGITCR.ITEN=1:
- Normal state machine bypassed
- WDOGITOP directly controls wdogint and wdogres signals
- Counter continues operating but interrupt/reset generation disabled
- WDOGINTCLR writes ignored

---

## Summary

This data model defines:
- **21 registers** organized at specific offsets (0x000-0xFFF)
- **7 saved state variables** for checkpoint persistence
- **2 session state variables** for event handles
- **2 signal interfaces** for interrupt and reset outputs
- **1 memory-mapped I/O interface** for register access
- **3 operational states** (Idle, Counting, Interrupt Pending)

The design follows DML 1.4 best practices with clear separation between saved (persistent) and session (transient) state, read-only vs read-write registers, and proper lock protection for control registers.

---

**Document Status**: Complete  
**Next Artifact**: contracts/ directory with register-access.md and interface-behavior.md
