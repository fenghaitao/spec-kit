# Simics Model Development Flow Example

This document provides a complete, end-to-end example of developing a Simics device model using the spec-kit framework. We'll implement a Simple UART Controller to demonstrate all phases of the development workflow.

**Updated for spec-kit v0.0.17** - This example now includes the latest features including ADK support, enhanced AI agent integration, and improved Simics-specific templates.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Phase 1: Specification](#phase-1-specification)
3. [Phase 2: Planning](#phase-2-planning)
4. [Phase 3: Task Generation](#phase-3-task-generation)
5. [Phase 4: Implementation](#phase-4-implementation)
6. [Key Learnings](#key-learnings)

---

## Project Overview

**Device**: Simple UART Controller  
**Purpose**: Serial communication interface for embedded systems  
**Complexity**: Moderate (good for learning the workflow)  
**Key Features**: 
- 8-bit data transmission/reception
- Configurable baud rate
- Interrupt generation
- Status monitoring

This example follows the complete spec-kit workflow while demonstrating Simics-specific considerations and best practices.

---

## Phase 1: Specification

### User Input
"Implement a simple UART controller for embedded systems that can transmit and receive 8-bit data with configurable baud rates and interrupt support."

### Command Usage
```bash
# Initialize project with Simics support
specify init uart-controller --ai adk

# Generate specification
cd uart-controller
.specify/scripts/bash/specify.sh "Implement a simple UART controller for embedded systems..."
```

### Generated Specification (`spec.md`)

```markdown
# Feature Specification: Simple UART Controller

**Feature Branch**: `001-uart-controller`  
**Created**: 2024-01-15  
**Status**: Draft  
**Input**: User description: "Implement a simple UART controller for embedded systems..."

## User Scenarios & Testing

### Primary User Story
An embedded system developer needs to configure a UART controller to communicate with external devices. They should be able to set baud rates, transmit data, receive data, and handle communication events through interrupts.

### Acceptance Scenarios
1. **Given** UART is powered on, **When** baud rate is configured to 9600, **Then** device operates at 9600 bps
2. **Given** data is written to TX register, **When** transmission completes, **Then** interrupt is generated
3. **Given** external data arrives, **When** RX buffer receives data, **Then** RX interrupt is triggered
4. **Given** UART is busy transmitting, **When** new data is written, **Then** TX busy status is indicated

### Edge Cases
- What happens when TX buffer is full and new data is written?
- How does the device handle framing errors in received data?
- What occurs during baud rate changes while transmission is active?

## Requirements

### Functional Requirements
- **FR-001**: System MUST support configurable baud rates (300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 bps)
- **FR-002**: System MUST transmit 8-bit data frames with start/stop bits
- **FR-003**: System MUST receive 8-bit data frames and detect framing errors
- **FR-004**: System MUST generate interrupts for TX complete and RX ready events
- **FR-005**: System MUST provide status indicators for TX busy, RX ready, and error conditions
- **FR-006**: System MUST support software reset of all registers and state

### Key Entities
- **UART Registers**: Control, status, data, and baud rate configuration
- **TX Buffer**: Outgoing data staging area
- **RX Buffer**: Incoming data storage
- **Interrupt Controller**: Event signaling to processor

### Hardware Specification *(Simics projects only)*
- **Device Type**: Serial communication controller
- **Register Map**: Control, Status, TX Data, RX Data, Baud Rate, Interrupt Enable
- **External Interfaces**: Serial TX/RX lines, interrupt line to processor
- **Software Visibility**: All registers accessible via memory-mapped I/O
```

---

## Phase 2: Planning

### Command Usage
```bash
# Generate implementation plan
.specify/scripts/bash/plan.sh

# The plan command will:
# 1. Detect project type as "simics" from context
# 2. Generate Simics-specific technical context
# 3. Create DML project structure
# 4. Include Simics research tasks
```

### Generated Implementation Plan (`plan.md`)

```markdown
# Implementation Plan: Simple UART Controller

## Register Analysis

### Control Register (CTRL) - Offset 0x00
- **Bit 0**: UART Enable (1=enabled, 0=disabled)
- **Bit 1**: TX Enable (1=enabled, 0=disabled)  
- **Bit 2**: RX Enable (1=enabled, 0=disabled)
- **Bit 3**: Software Reset (write 1 to reset)
- **Bits 7-4**: Reserved (read as 0)
- **Access**: Read/Write
- **Reset Value**: 0x00

### Status Register (STAT) - Offset 0x04
- **Bit 0**: TX Ready (1=ready for new data, 0=busy)
- **Bit 1**: RX Ready (1=data available, 0=empty)
- **Bit 2**: TX Complete (1=transmission finished, cleared on read)
- **Bit 3**: RX Error (1=framing error detected, cleared on read)
- **Bits 7-4**: Reserved (read as 0)
- **Access**: Read-only
- **Reset Value**: 0x01 (TX Ready)

### TX Data Register (TXDATA) - Offset 0x08
- **Bits 7-0**: Transmit data byte
- **Access**: Write-only
- **Side Effects**: Writing starts transmission if TX enabled and ready

### RX Data Register (RXDATA) - Offset 0x0C
- **Bits 7-0**: Received data byte
- **Access**: Read-only
- **Side Effects**: Reading clears RX Ready status

### Baud Rate Register (BAUD) - Offset 0x10
- **Bits 3-0**: Baud rate selector
  - 0x0: 300 bps
  - 0x1: 1200 bps
  - 0x2: 2400 bps
  - 0x3: 4800 bps
  - 0x4: 9600 bps (default)
  - 0x5: 19200 bps
  - 0x6: 38400 bps
  - 0x7: 57600 bps
  - 0x8: 115200 bps
  - 0x9-0xF: Reserved
- **Bits 7-4**: Reserved
- **Access**: Read/Write
- **Reset Value**: 0x04 (9600 bps)

### Interrupt Enable Register (IE) - Offset 0x14
- **Bit 0**: TX Complete Interrupt Enable
- **Bit 1**: RX Ready Interrupt Enable
- **Bit 2**: RX Error Interrupt Enable
- **Bits 7-3**: Reserved
- **Access**: Read/Write
- **Reset Value**: 0x00

## Interface Definition

### Ports and Connections
- **serial_link**: External serial communication interface
- **interrupt_line**: Connection to system interrupt controller
- **memory_bus**: Memory-mapped register access

### External Interfaces
- Serial TX/RX pins for external communication
- Interrupt output to processor/interrupt controller

## Workflow Documentation

### Transmission Flow
1. Software writes baud rate to BAUD register
2. Software enables UART and TX via CTRL register
3. Software writes data to TXDATA register
4. Hardware begins transmission (STAT.TX_Ready = 0)
5. On completion, hardware sets STAT.TX_Complete and optionally generates interrupt
6. Hardware sets STAT.TX_Ready = 1 for next transmission

### Reception Flow
1. External device sends serial data
2. Hardware receives and validates frame
3. On valid frame: data → RXDATA, STAT.RX_Ready = 1, optional interrupt
4. On framing error: STAT.RX_Error = 1, optional interrupt
5. Software reads RXDATA (clears RX_Ready status)

## Abstraction Strategy
- **Timing Simulation**: Calculate transmission time based on baud rate, but don't simulate bit-level timing
- **Serial Protocol**: Focus on byte-level data transfer, abstract physical layer details
- **Error Simulation**: Implement basic framing error detection for software testing

## File Structure
```
uart-controller/
├── uart-controller.dml          # Main device implementation
├── registers.dml                # Register definitions
├── interfaces.dml              # External interface declarations
├── utility.dml                 # Helper methods and templates
└── tests/
    ├── unit/
    │   ├── test_registers.py    # Register access tests
    │   └── test_transmission.py # TX/RX logic tests
    └── integration/
        ├── test_interrupts.py   # Interrupt behavior tests
        └── test_protocols.py    # Communication protocol tests
```

## Implementation Dependencies
- Simics base device modeling framework
- DML compiler and syntax validation tools
- Python test framework for device validation
```

---

## Phase 3: Task Generation

### Command Usage
```bash
# Generate tasks from plan
.specify/scripts/bash/tasks.sh

# The tasks command will:
# 1. Load plan.md and extract Simics project structure
# 2. Generate DML-specific tasks for device modeling
# 3. Create TDD tasks for register access and behavior
# 4. Include Simics integration and testing tasks
```

### Generated Task List (`tasks.md`)

```markdown
# Tasks: Simple UART Controller

## Phase 3.1: Setup
- [ ] T001 Create device directory structure (uart-controller/, tests/)
- [ ] T002 Initialize DML project with Simics module dependencies  
- [ ] T003 [P] Configure DML syntax checking and validation tools

## Phase 3.2: Tests First (TDD)
- [ ] T004 [P] Register access test in uart-controller/tests/unit/test_registers.py
- [ ] T005 [P] Transmission logic test in uart-controller/tests/unit/test_transmission.py  
- [ ] T006 [P] Reception workflow test in uart-controller/tests/unit/test_reception.py
- [ ] T007 [P] Interrupt behavior test in uart-controller/tests/integration/test_interrupts.py
- [ ] T008 [P] Communication protocol test in uart-controller/tests/integration/test_protocols.py

## Phase 3.3: Core Implementation
- [ ] T009 [P] Register definitions in uart-controller/registers.dml
- [ ] T010 [P] Interface declarations in uart-controller/interfaces.dml
- [ ] T011 [P] Utility methods in uart-controller/utility.dml
- [ ] T012 Main device structure in uart-controller/uart-controller.dml
- [ ] T013 Register read/write logic implementation  
- [ ] T014 Transmission state machine and timing
- [ ] T015 Reception logic and error handling
- [ ] T016 Interrupt generation and management

## Phase 3.4: Integration  
- [ ] T017 Connect device to memory interface using transact() methods
- [ ] T018 Implement interrupt line connections and events
- [ ] T019 Add serial port communications and protocols
- [ ] T020 Integrate with Simics checkpointing and state management

## Phase 3.5: Polish
- [ ] T021 [P] Unit tests for edge cases in uart-controller/tests/unit/test_edge_cases.py
- [ ] T022 Performance validation (transmission timing accuracy)
- [ ] T023 [P] Update documentation and usage examples
- [ ] T024 Code review and cleanup
```

---

## Phase 4: Implementation

### Key Implementation Files

#### 1. Register Definitions (`registers.dml`)

```dml
dml 1.4;

// Control Register - Offset 0x00
bank regs {
    register ctrl size 4 @ 0x00 "UART Control Register" {
        field enable @ [0] "UART Enable";
        field tx_enable @ [1] "Transmitter Enable";  
        field rx_enable @ [2] "Receiver Enable";
        field soft_reset @ [3] "Software Reset";
        field reserved @ [7:4] "Reserved bits";
        
        method write(uint64 value) {
            if (value & 0x8) { // Soft reset
                call $soft_reset();
                this.val = 0;
            } else {
                this.val = value & 0x7; // Only bits 0-2 writable
            }
        }
    }
    
    register stat size 4 @ 0x04 "UART Status Register" {
        field tx_ready @ [0] "Transmitter Ready";
        field rx_ready @ [1] "Receiver Ready"; 
        field tx_complete @ [2] "Transmission Complete";
        field rx_error @ [3] "Reception Error";
        field reserved @ [7:4] "Reserved bits";
        
        method write(uint64 value) {
            // Status register is read-only
            log info: "Attempt to write read-only status register";
        }
        
        method read() -> (uint64) {
            uint64 value = this.val;
            // Clear TX complete and RX error on read
            this.tx_complete = 0;
            this.rx_error = 0;
            return value;
        }
    }
    
    register txdata size 4 @ 0x08 "Transmit Data Register" {
        method write(uint64 value) {
            if ($regs.ctrl.enable && $regs.ctrl.tx_enable) {
                if ($regs.stat.tx_ready) {
                    call $start_transmission(value & 0xFF);
                } else {
                    log info: "TX busy - data write ignored";
                }
            }
        }
        
        method read() -> (uint64) {
            log info: "Reading write-only TX data register";
            return 0;
        }
    }
    
    register rxdata size 4 @ 0x0C "Receive Data Register" {
        method write(uint64 value) {
            log info: "Attempt to write read-only RX data register";
        }
        
        method read() -> (uint64) {
            uint64 data = this.val;
            $regs.stat.rx_ready = 0; // Clear RX ready on read
            return data;
        }
    }
    
    register baud size 4 @ 0x10 "Baud Rate Register" {
        field rate @ [3:0] "Baud Rate Selector";
        field reserved @ [7:4] "Reserved bits";
        
        method write(uint64 value) {
            uint8 rate = value & 0xF;
            if (rate <= 8) { // Valid baud rates 0-8
                this.rate = rate;
                call $update_baud_rate(rate);
            }
        }
    }
    
    register ie size 4 @ 0x14 "Interrupt Enable Register" {
        field tx_complete_ie @ [0] "TX Complete Interrupt Enable";
        field rx_ready_ie @ [1] "RX Ready Interrupt Enable";
        field rx_error_ie @ [2] "RX Error Interrupt Enable"; 
        field reserved @ [7:3] "Reserved bits";
        
        method write(uint64 value) {
            this.val = value & 0x7; // Only bits 0-2 writable
        }
    }
}
```

#### 2. Main Device Structure (`uart-controller.dml`)

```dml
dml 1.4;

device uart_controller;

import "simics/devs/signal.dml";
import "registers.dml";
import "interfaces.dml";
import "utility.dml";

// Device attributes for state management
attribute tx_data_attr {
    type: uint8;
    documentation: "Current transmission data";
}

attribute rx_buffer_attr {
    type: uint8;
    documentation: "Received data buffer";
}

attribute baud_period_attr {
    type: double;
    documentation: "Current baud period in seconds";
    default: 1.0 / 9600.0; // Default 9600 bps
}

// Transmission timing event
event tx_complete_event {
    method event() {
        // Mark transmission complete
        $regs.stat.tx_ready = 1;
        $regs.stat.tx_complete = 1;
        
        // Generate interrupt if enabled
        if ($regs.ie.tx_complete_ie) {
            call $raise_interrupt();
        }
        
        log info: "Transmission completed";
    }
}

// Main device methods
method init() {
    call $soft_reset();
}

method soft_reset() {
    // Reset all registers to default values
    $regs.ctrl.val = 0;
    $regs.stat.val = 1; // TX ready by default
    $regs.baud.val = 4; // Default 9600 bps
    $regs.ie.val = 0;
    
    // Cancel any pending events
    cancel tx_complete_event;
    
    log info: "UART controller reset";
}

method start_transmission(uint8 data) {
    $tx_data_attr = data;
    $regs.stat.tx_ready = 0;
    
    // Calculate transmission time (8 data + 1 start + 1 stop = 10 bits)
    double tx_time = $baud_period_attr * 10.0;
    
    // Schedule completion event
    after (tx_time) call tx_complete_event.event();
    
    // In real implementation, would interact with serial interface
    log info: "Starting transmission of 0x%02x", data;
}

method update_baud_rate(uint8 rate_code) {
    local uint32 baud_rates[9] = {300, 1200, 2400, 4800, 9600, 
                                  19200, 38400, 57600, 115200};
    
    if (rate_code < 9) {
        $baud_period_attr = 1.0 / baud_rates[rate_code];
        log info: "Baud rate set to %d bps", baud_rates[rate_code];
    }
}

method raise_interrupt() {
    // Signal interrupt line if connected
    if ($interrupt_pin.signal_raise) {
        call $interrupt_pin.signal_raise();
    }
}

// Simulate external data reception
method receive_data(uint8 data) {
    if ($regs.ctrl.enable && $regs.ctrl.rx_enable) {
        if (!$regs.stat.rx_ready) {
            $regs.rxdata.val = data;
            $regs.stat.rx_ready = 1;
            
            if ($regs.ie.rx_ready_ie) {
                call $raise_interrupt();
            }
            
            log info: "Received data: 0x%02x", data;
        } else {
            log info: "RX buffer full - data lost";
        }
    }
}
```

#### 3. Test Example (`test_registers.py`)

```python
import pytest
from simics_test_framework import SimicsTestDevice

class TestUARTRegisters:
    def setup_method(self):
        self.device = SimicsTestDevice("uart-controller")
        
    def test_control_register_enable(self):
        # Test UART enable functionality
        self.device.write_register(0x00, 0x1)  # Enable UART
        assert self.device.read_register(0x00) == 0x1
        
    def test_baud_rate_configuration(self):
        # Test baud rate register
        self.device.write_register(0x10, 0x8)  # 115200 bps
        assert self.device.read_register(0x10) == 0x8
        
        # Test invalid baud rate (should be ignored)
        self.device.write_register(0x10, 0xF)  
        assert self.device.read_register(0x10) == 0x8  # Unchanged
        
    def test_status_register_readonly(self):
        # Status register should be read-only
        original_status = self.device.read_register(0x04)
        self.device.write_register(0x04, 0xFF)
        assert self.device.read_register(0x04) == original_status
        
    def test_transmission_flow(self):
        # Enable UART and transmitter
        self.device.write_register(0x00, 0x3)  # Enable UART + TX
        
        # Check TX ready status
        status = self.device.read_register(0x04)
        assert (status & 0x1) == 0x1  # TX ready
        
        # Start transmission
        self.device.write_register(0x08, 0x55)  # Send 0x55
        
        # TX should now be busy
        status = self.device.read_register(0x04)
        assert (status & 0x1) == 0x0  # TX busy
        
    def test_soft_reset(self):
        # Configure device
        self.device.write_register(0x00, 0x7)  # Enable all
        self.device.write_register(0x10, 0x8)  # High baud rate
        
        # Perform soft reset
        self.device.write_register(0x00, 0x8)  # Set reset bit
        
        # Verify reset state
        assert self.device.read_register(0x00) == 0x0  # Disabled
        assert self.device.read_register(0x04) == 0x1  # TX ready only
        assert self.device.read_register(0x10) == 0x4  # Default baud
```

---

## Key Learnings

### 1. Specification-Driven Development
- **Clear Requirements**: Every register bit and behavior must be explicitly specified
- **Software Perspective**: Focus on what software can observe and control
- **Edge Cases**: Consider error conditions and boundary behaviors early

### 2. Simics-Specific Considerations
- **Functional Simulation**: Abstract timing where appropriate (calculate vs. simulate)
- **State Management**: Use attributes for checkpoint/restore compatibility
- **Event Handling**: Leverage Simics event system for asynchronous operations
- **Interface Design**: Proper separation between registers, logic, and external interfaces

### 3. Test-Driven Development Benefits
- **Verification**: Tests catch register access issues and behavioral bugs
- **Documentation**: Tests serve as executable specifications
- **Confidence**: Comprehensive testing enables safe refactoring

### 4. Workflow Efficiency
- **Parallel Development**: Independent files can be developed simultaneously
- **Incremental Testing**: Each phase builds on validated foundations
- **Clear Dependencies**: Explicit task ordering prevents integration issues

### 5. Best Practices Demonstrated
- **Register-Centric Design**: Registers drive device behavior and state
- **Separation of Concerns**: Distinct files for registers, interfaces, and logic
- **Comprehensive Logging**: Detailed logging aids debugging and validation
- **Error Handling**: Graceful handling of invalid operations and states

### 6. Latest spec-kit Features (v0.0.17)
- **Enhanced AI Support**: Support for 12 AI agents including Claude, Cursor, Windsurf, ADK, and more
- **Simics Integration**: Automatic detection of hardware device projects
- **Improved Templates**: Simics-specific sections in spec, plan, and tasks templates
- **ADK Support**: Agent Development Kit for custom AI agent integration
- **Constitution Framework**: Simics Model Development Constitution for best practices
- **MCP Server Integration**: Integration with simics-mcp-server for automated project management
- **Simics MCP Tools**: Project creation, building, testing, and package management via MCP protocol

This example demonstrates how the spec-kit framework supports systematic Simics device development, from initial specification through complete implementation, ensuring both correctness and maintainability.