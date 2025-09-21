# Example: Simple UART Controller Device

This example demonstrates the complete workflow for developing a UART controller device model using spec-kit's Simics integration.

## Overview

We'll create a 16550-compatible UART controller with:
- Standard register interface (THR, RBR, IER, IIR, FCR, LCR, MCR, LSR, MSR)
- FIFO buffers for transmit and receive
- Interrupt generation for various events
- Configurable baud rates
- Hardware flow control support

## Step 1: Create Device Specification

Use the `/simics-device` command to create the initial specification:

```
/simics-device Create a 16550-compatible UART controller with 16-byte FIFO buffers for both transmit and receive, interrupt generation for receive data available, transmitter empty, line status changes, and modem status changes. Support configurable baud rates from 1200 to 115200 bps. Include hardware flow control using RTS/CTS signals. The device should occupy 8 bytes in the memory map and be compatible with standard 16550 driver software.
```

### Generated Specification Extract

```markdown
# Device Model Specification: uart-controller

## Device Overview

### Device Type and Purpose
16550-compatible UART (Universal Asynchronous Receiver/Transmitter) controller providing serial communication interface with FIFO buffering and interrupt support.

### Target System Context
- **System Architecture**: ARM/x86 embedded or server platforms
- **Simulation Purpose**: Software development and driver validation
- **Abstraction Level**: Functional modeling with accurate register behavior

## Device Behavioral Model

### Core Functionality
The UART controller provides bidirectional asynchronous serial communication with:
- Programmable baud rate generation
- 16-byte FIFO buffers for transmit and receive paths
- Interrupt generation for various events
- Hardware flow control using RTS/CTS signals
- Standard 16550 register interface for software compatibility

### State Management
- **Device States**: Reset, Configured, Transmitting, Receiving, Error
- **State Transitions**: Configuration changes, data availability, error conditions
- **Reset Behavior**: All registers reset to default values, FIFOs cleared

## Register Interface Specifications

### Register Map Overview
| Offset | Name | Width | Access | Description |
|--------|------|-------|--------|-------------|
| 0x00 | THR/RBR | 8-bit | WO/RO | Transmit Hold/Receive Buffer Register |
| 0x01 | IER | 8-bit | RW | Interrupt Enable Register |
| 0x02 | IIR/FCR | 8-bit | RO/WO | Interrupt ID/FIFO Control Register |
| 0x03 | LCR | 8-bit | RW | Line Control Register |
| 0x04 | MCR | 8-bit | RW | Modem Control Register |
| 0x05 | LSR | 8-bit | RO | Line Status Register |
| 0x06 | MSR | 8-bit | RO | Modem Status Register |
| 0x07 | SCR | 8-bit | RW | Scratch Register |
```

## Step 2: Generate Implementation Plan

Use the `/plan` command to create the implementation approach:

```
/plan Implement using DML for register model and basic device structure, Python callbacks for FIFO management and serial data processing, integrate with Simics interrupt system for event notifications. Focus on accurate 16550 register behavior and timing characteristics.
```

### Generated Plan Extract

```markdown
# Implementation Plan: uart-controller

## Technical Context
**Language/Version**: DML 1.4, Python 3.11
**Primary Dependencies**: Simics 6.0, DML register modeling
**Target Platform**: Linux simulation host
**Performance Goals**: 1M characters/sec simulation throughput
**Constraints**: <10ms interrupt latency, accurate baud rate timing

## Phase 1: Design & Contracts

### Register Interface Contracts
- DML register bank with 16550-compatible layout
- Python callbacks for register side effects
- Interrupt generation through processor_info_v2 interface

### FIFO Implementation
- Python-based circular buffer implementation
- Configurable FIFO depth (16 bytes default)
- Trigger level configuration for interrupts

### Simics Interface Requirements
- int_register interface for register access
- processor_info_v2 interface for interrupt delivery
- io_memory interface for memory-mapped access
```

## Step 3: Generate Implementation Tasks

Use the `/tasks` command to create actionable implementation tasks:

```
/tasks
```

### Generated Tasks Extract

```markdown
# Tasks: uart-controller

## Phase 3.2: Tests First (TDD)
- [ ] T004 [P] Contract test register access in tests/contract/test_uart_registers.py
- [ ] T005 [P] Contract test FIFO behavior in tests/contract/test_uart_fifo.py
- [ ] T006 [P] Integration test data transmission in tests/integration/test_uart_transmission.py
- [ ] T007 [P] Integration test interrupt generation in tests/integration/test_uart_interrupts.py

## Phase 3.3: Core Implementation
- [ ] T008 [P] UART register model in src/models/uart_registers.dml
- [ ] T009 [P] FIFO management in src/services/uart_fifo.py
- [ ] T010 [P] Interrupt controller in src/services/uart_interrupts.py
- [ ] T011 Device configuration and initialization
- [ ] T012 Baud rate calculation and timing
- [ ] T013 Hardware flow control implementation
```

## Step 4: Implementation Files

### DML Register Model (src/models/uart_registers.dml)

```dml
dml 1.4;
device uart_controller;

import "simics/devs/signal.dml";
import "simics/simulator/processor-info.dml";

parameter desc = "16550-compatible UART Controller";
parameter documentation = "Implements standard 16550 UART with FIFO support";

// Register bank definition
bank registers {
    parameter register_size = 1;
    parameter byte_order = "little-endian";
    
    // Transmit Hold Register / Receive Buffer Register
    register THR_RBR size 1 @ 0x00 {
        parameter documentation = "Transmit Hold / Receive Buffer Register";
        
        method write(uint64 value) {
            call $uart_transmit_byte(value & 0xFF);
        }
        
        method read() -> (uint64) {
            return call $uart_receive_byte();
        }
    }
    
    // Interrupt Enable Register
    register IER size 1 @ 0x01 {
        parameter documentation = "Interrupt Enable Register";
        field ERBFI @ [0] { parameter documentation = "Enable Received Data Available Interrupt"; }
        field ETBEI @ [1] { parameter documentation = "Enable Transmitter Holding Register Empty Interrupt"; }
        field ELSI @ [2] { parameter documentation = "Enable Receiver Line Status Interrupt"; }
        field EDSSI @ [3] { parameter documentation = "Enable Modem Status Interrupt"; }
        
        method write(uint64 value) {
            call $update_interrupt_enables(value & 0x0F);
        }
    }
    
    // ... Additional registers follow similar pattern
}

// Interface implementations
implement int_register {
    parameter byte_order = "little-endian";
    
    method read_register(uint64 offset, uint32 size) -> (uint64) {
        return call registers.read(offset, size);
    }
    
    method write_register(uint64 offset, uint64 value, uint32 size) {
        call registers.write(offset, value, size);
    }
}

// Python callback methods
extern method uart_transmit_byte(uint8 data) -> (void);
extern method uart_receive_byte() -> (uint8);
extern method update_interrupt_enables(uint8 enables) -> (void);
```

### Python FIFO Implementation (src/services/uart_fifo.py)

```python
"""UART FIFO Management Service"""

class UartFifo:
    """Circular buffer implementation for UART FIFO"""
    
    def __init__(self, depth=16):
        self.depth = depth
        self.buffer = [0] * depth
        self.head = 0
        self.tail = 0
        self.count = 0
        self.trigger_level = 1
    
    def is_empty(self):
        return self.count == 0
    
    def is_full(self):
        return self.count == self.depth
    
    def push(self, data):
        """Add data to FIFO, returns True if successful"""
        if self.is_full():
            return False
        
        self.buffer[self.tail] = data & 0xFF
        self.tail = (self.tail + 1) % self.depth
        self.count += 1
        return True
    
    def pop(self):
        """Remove data from FIFO, returns data or None if empty"""
        if self.is_empty():
            return None
        
        data = self.buffer[self.head]
        self.head = (self.head + 1) % self.depth
        self.count -= 1
        return data
    
    def trigger_reached(self):
        """Check if FIFO has reached trigger level"""
        return self.count >= self.trigger_level
    
    def set_trigger_level(self, level):
        """Set FIFO trigger level for interrupts"""
        self.trigger_level = min(level, self.depth)

class UartController:
    """Main UART controller implementation"""
    
    def __init__(self, simics_device):
        self.device = simics_device
        self.rx_fifo = UartFifo(16)
        self.tx_fifo = UartFifo(16)
        self.baud_rate = 9600
        self.interrupt_pending = False
    
    def uart_transmit_byte(self, data):
        """Callback from DML for transmit operations"""
        if self.tx_fifo.push(data):
            self._schedule_transmission()
            self._update_interrupts()
    
    def uart_receive_byte(self):
        """Callback from DML for receive operations"""
        data = self.rx_fifo.pop()
        if data is not None:
            self._update_interrupts()
            return data
        return 0
    
    def _schedule_transmission(self):
        """Schedule transmission of next byte"""
        if not self.tx_fifo.is_empty():
            # Calculate timing based on baud rate
            bit_time = 1.0 / self.baud_rate
            byte_time = bit_time * 10  # 8 data + start + stop bits
            
            # Schedule Simics event for transmission completion
            self.device.post_time(byte_time, self._transmit_complete)
    
    def _transmit_complete(self):
        """Handle transmission completion"""
        if not self.tx_fifo.is_empty():
            data = self.tx_fifo.pop()
            # Send data to connected device/terminal
            self._send_serial_data(data)
            
            # Schedule next transmission if more data available
            if not self.tx_fifo.is_empty():
                self._schedule_transmission()
        
        self._update_interrupts()
    
    def _update_interrupts(self):
        """Update interrupt status based on FIFO states"""
        interrupt_needed = False
        
        # Check receive data available
        if self.rx_fifo.trigger_reached():
            interrupt_needed = True
        
        # Check transmitter empty
        if self.tx_fifo.is_empty():
            interrupt_needed = True
        
        # Generate interrupt if needed and enabled
        if interrupt_needed and not self.interrupt_pending:
            self.device.signal_raise()
            self.interrupt_pending = True
        elif not interrupt_needed and self.interrupt_pending:
            self.device.signal_lower()
            self.interrupt_pending = False
```

### Test Implementation (tests/contract/test_uart_registers.py)

```python
"""Contract tests for UART register interface"""

import pytest
from simics_test_framework import SimicsTest

class TestUartRegisters(SimicsTest):
    """Test UART register access and behavior"""
    
    def setup_method(self):
        """Set up test environment"""
        self.uart = self.create_device("uart_controller")
        self.uart.reset()
    
    def test_register_access(self):
        """Test basic register read/write access"""
        # Test IER register
        self.uart.write_register(0x01, 0x0F)
        assert self.uart.read_register(0x01) == 0x0F
        
        # Test read-only registers return expected values
        lsr = self.uart.read_register(0x05)  # LSR
        assert (lsr & 0x60) == 0x60  # THR empty, TSR empty
    
    def test_fifo_control(self):
        """Test FIFO control register functionality"""
        # Enable FIFOs
        self.uart.write_register(0x02, 0x01)  # FCR
        
        # Verify FIFO enabled in IIR
        iir = self.uart.read_register(0x02)
        assert (iir & 0xC0) == 0xC0  # FIFOs enabled
    
    def test_data_transmission(self):
        """Test data transmission through THR"""
        # Write data to transmit
        test_data = 0x55
        self.uart.write_register(0x00, test_data)  # THR
        
        # Verify transmission started (LSR.THRE should be clear initially)
        # Then become set when transmission completes
        self.wait_for_transmission_complete()
        
        lsr = self.uart.read_register(0x05)
        assert (lsr & 0x20) == 0x20  # THRE set
    
    def test_interrupt_generation(self):
        """Test interrupt generation for various conditions"""
        # Enable interrupts
        self.uart.write_register(0x01, 0x02)  # Enable THRE interrupt
        
        # Transmit data to trigger interrupt
        self.uart.write_register(0x00, 0xAA)
        
        # Wait for transmission and verify interrupt
        self.wait_for_interrupt()
        
        # Read IIR to check interrupt source
        iir = self.uart.read_register(0x02)
        assert (iir & 0x02) == 0x02  # THRE interrupt pending
```

## Step 5: Validation and Testing

### Running Tests

```bash
# Run contract tests
python -m pytest tests/contract/test_uart_registers.py -v

# Run integration tests  
python -m pytest tests/integration/test_uart_transmission.py -v

# Run performance tests
python -m pytest tests/performance/test_uart_performance.py -v
```

### Expected Results

```
tests/contract/test_uart_registers.py::TestUartRegisters::test_register_access PASSED
tests/contract/test_uart_registers.py::TestUartRegisters::test_fifo_control PASSED
tests/contract/test_uart_registers.py::TestUartRegisters::test_data_transmission PASSED
tests/contract/test_uart_registers.py::TestUartRegisters::test_interrupt_generation PASSED

tests/integration/test_uart_transmission.py::TestUartTransmission::test_serial_loopback PASSED
tests/integration/test_uart_transmission.py::TestUartTransmission::test_baud_rate_accuracy PASSED

tests/performance/test_uart_performance.py::TestUartPerformance::test_throughput PASSED
tests/performance/test_uart_performance.py::TestUartPerformance::test_interrupt_latency PASSED
```

## Summary

This example demonstrates the complete spec-kit Simics integration workflow:

1. **Specification Generation**: Created comprehensive device specification using `/simics-device`
2. **Implementation Planning**: Generated technical implementation plan using `/plan`
3. **Task Generation**: Created ordered implementation tasks using `/tasks`
4. **Implementation**: Showed DML register model and Python service implementation
5. **Testing**: Demonstrated contract and integration testing approach

The resulting UART controller provides:
- Full 16550 compatibility
- Accurate register behavior
- FIFO buffering with configurable trigger levels
- Interrupt generation and handling
- Configurable baud rates and timing
- Hardware flow control support

This approach ensures that the device model meets both functional requirements and Simics integration standards while maintaining specification traceability throughout the development process.