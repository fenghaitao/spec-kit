# DML Device Development Best Practices for Beginners

## Overview

This guide provides a comprehensive introduction to writing Device Modeling Language (DML) devices for the Simics simulation platform. It covers the essential syntax, common patterns, and best practices learned from solving compilation issues.

## Table of Contents

1. [DML Compilation Setup](#dml-compilation-setup)
2. [Basic DML Syntax](#basic-dml-syntax)
3. [Device Structure](#device-structure)
4. [Common Patterns](#common-patterns)
5. [Compilation Issues and Solutions](#compilation-issues-and-solutions)
6. [Best Practices](#best-practices)
7. [Example Devices](#example-devices)
8. [Testing Best Practices](#testing-best-practices)

## DML Compilation Setup

### Required Compiler Flags

The key to successful DML compilation is using the correct compiler flags:

```bash
dmlc --simics-api=7 -I ../linux64/bin/dml/api/7/1.4 -I ../linux64/bin/dml/1.4 input.dml output
```

**Critical Points:**
- `--simics-api=7`: Specifies Simics API version
- `-I ../linux64/bin/dml/api/7/1.4`: Include path for Simics API
- `-I ../linux64/bin/dml/1.4`: Include path for DML builtins

### Environment Setup

Ensure the DML compiler has UTF-8 mode enabled:

```bash
# Method 1: Environment variable
export PYTHONUTF8=1

# Method 2: Modified dmlc script (recommended)
exec env PYTHONUTF8=1 "$_MINI_PYTHON" "$DMLC_DIR/dml/python" "$@"
```

## Basic DML Syntax

### Minimal DML Device

```dml
dml 1.4;

device simple_device;

param classname = "simple_device";
param desc = "A simple device for learning";
```

**Key Points:**
- Start with `dml 1.4;`
- Device declaration is a single line: `device device_name;`
- **NO braces after device declaration**
- Parameters go at top level, not inside device blocks

### Common Imports

```dml
dml 1.4;

device my_device;

import "simics/device-api.dml";  // Always needed for devices
```

## Device Structure

### Correct vs. Incorrect Syntax

❌ **WRONG** (old DML style):
```dml
device my_device {
    param classname = "my_device";
    // ...
}
```

✅ **CORRECT** (DML 1.4 style):
```dml
device my_device;

param classname = "my_device";
param desc = "Device description";
```

### Memory-Mapped Device with Registers

```dml
dml 1.4;

device uart_device;

import "simics/device-api.dml";

param classname = "uart_device";
param desc = "Simple UART device";

bank regs {
    param function = 0x3f8;        // Base address
    param register_size = 1;       // 1 byte registers

    register data @ 0x00 {
        param size = 1;
        param desc = "Data register";

        method write(uint64 value) {
            log info: "UART data write: 0x%02x", value;
        }

        method read() -> (uint64 value) {
            log info: "UART data read";
            return 0x00;
        }
    }

    register status @ 0x05 {
        param size = 1;
        param desc = "Line status register";
        param init_val = 0x60;  // TX empty and ready
    }
}
```

## Common Patterns

### 1. Basic Memory-Mapped Device

```dml
dml 1.4;

device basic_mmio;

import "simics/device-api.dml";

param classname = "basic_mmio";
param desc = "Basic memory-mapped I/O device";

bank control_regs {
    param function = 0x1000;
    param register_size = 4;

    register CONTROL @ 0x00 {
        param size = 4;
        param desc = "Control register";
    }

    register STATUS @ 0x04 {
        param size = 4;
        param desc = "Status register";
        param init_val = 0x1;  // Device ready
    }
}
```

### 2. Device with Interrupts

```dml
dml 1.4;

device interrupt_device;

import "utility.dml";
import "simics/devs/signal.dml";
import "simics/device-api.dml";

param classname = "interrupt_device";
param desc = "Device that can generate interrupts";

// connect attribute is used for wire/bus signal/transaction to output
connect irq {
    param configuration = "optional";
    param c_type = "simple_interrupt";
    interface signal;
}

// port attribute is used for wire/bus signal/transaction to input
port reset_n {
    param configuration = "optional";
    param desc = "reset signal input";

    implement signal {
        // empty implementation as a simple example
        method signal_raise() {}
        // empty implementation as a simple example
        method signal_lower() {}
    }
}

bank regs {
    param function = 0x2000;
    param register_size = 4;

    register INTERRUPT_ENABLE @ 0x00 {
        param size = 4;
        param desc = "Interrupt enable register";
    }

    register INTERRUPT_STATUS @ 0x04 {
        param size = 4;
        param desc = "Interrupt status register";

        method write(uint64 value) {
            // Clear interrupt on write
            this.val = this.val & ~value;
            update_interrupt();
        }
    }
}

method update_interrupt() {
    if (regs.INTERRUPT_ENABLE.val & regs.INTERRUPT_STATUS.val) {
        if (irq.obj) {
            irq.signal.signal_raise();
        }
    }
}
```

### 3. Timer Device

```dml
dml 1.4;

device timer_device;

import "simics/device-api.dml";

param classname = "timer_device";
param desc = "Simple timer device";

event timer_tick;

bank timer_regs {
    param function = 0x4000;
    param register_size = 4;

    register TIMER_VALUE @ 0x00 {
        param size = 4;
        param desc = "Current timer value";
    }

    register TIMER_CONTROL @ 0x04 {
        param size = 4;
        param desc = "Timer control register";

        method write(uint64 value) {
            this.val = value;
            if (value & 0x1) {  // Enable bit
                start_timer();
            }
        }
    }
}

method start_timer() {
    after 1.0 s: timer_expired();
}

method timer_expired() {
    log info: "Timer expired";
    timer_regs.TIMER_VALUE.val = 0;
    // Could trigger interrupt here
}
```

## Compilation Issues and Solutions

### Issue 1: "syntax error at 'device'"

**Cause**: Using old DML syntax with braces after device declaration.

**Solution**: Remove braces from device declaration:
```dml
// Wrong
device my_device { ... }

// Correct
device my_device;
```

### Issue 2: "cannot find file to import: dml-builtins.dml"

**Cause**: Missing include path for DML builtins.

**Solution**: Add both include paths:
```bash
dmlc --simics-api=7 -I ../linux64/bin/dml/api/7/1.4 -I ../linux64/bin/dml/1.4 file.dml output
```

### Issue 3: "assert sys.flags.utf8_mode"

**Cause**: Python not running in UTF-8 mode.

**Solution**: Set environment variable or modify dmlc script:
```bash
export PYTHONUTF8=1
```

### Issue 4: "unknown template: 'device'"

**Cause**: DML builtins not found in include path.

**Solution**: Ensure `-I ../linux64/bin/dml/1.4` is included.

## Best Practices

### 1. File Organization

```
simics-project/
├── modules/
│   ├── device1/
│   │   ├── device.dml
│   │   └── Makefile
│   └── device2/
│       ├── device.dml
│       └── Makefile
├── common/
│   └── device-common.dml
└── Makefile
```

### 2. Naming Conventions

- **Device names**: lowercase_with_underscores
- **Bank names**: lowercase_with_underscores
- **Register names**: descriptive_uppercase
- **Field names**: descriptive_camelCase
- **Parameters**: lowercase or camelCase
- **Methods**: lowercase_with_underscores

### 3. Documentation

Always include meaningful descriptions:

```dml
param desc = "Detailed description of what this device does";

register CONTROL @ 0x00 {
    param desc = "Main control register - bit 0 enables device";
}
```

### 4. Error Handling

```dml
method write(uint64 value) {
    if (value > 0xFF) {
        log error: "Invalid value written to 8-bit register: 0x%x", value;
        return;
    }
    this.val = value;
}
```

### 5. Logging

Use appropriate log levels:

```dml
log info: "Device initialized";
log warning: "Unusual register access pattern";
log error: "Invalid operation attempted";
```

## Example Devices

### Complete UART Example

```dml
dml 1.4;

device uart_16550;

import "simics/device-api.dml";

param classname = "uart_16550";
param desc = "16550-compatible UART device";

bank uart_regs {
    param function = 0x3f8;
    param register_size = 1;

    // Data register / Divisor latch low
    register RBR_THR_DLL @ 0x00 {
        param size = 1;
        param desc = "Receiver buffer/Transmitter holding/Divisor latch low";

        method write(uint64 value) {
            if (LCR.val & 0x80) {
                // Divisor latch access
                log info: "Divisor latch low set to 0x%02x", value;
            } else {
                // Transmit data
                log info: "UART transmit: 0x%02x ('%c')", value,
                         (value >= 32 && value < 127) ? value : '?';
            }
            this.val = value;
        }

        method read() -> (uint64) {
            if (LCR.val & 0x80) {
                return this.val;  // Divisor latch
            } else {
                log info: "UART receive read";
                return 0x00;  // No data available
            }
        }
    }

    // Interrupt enable register / Divisor latch high
    register IER_DLH @ 0x01 {
        param size = 1;
        param desc = "Interrupt enable/Divisor latch high";
    }

    // Line control register
    register LCR @ 0x03 {
        param size = 1;
        param desc = "Line control register";
        param init_val = 0x03;  // 8N1
    }

    // Line status register
    register LSR @ 0x05 {
        param size = 1;
        param desc = "Line status register";
        param init_val = 0x60;  // TX empty and ready
    }
}
```

### Simple PCI Device Template

```dml
dml 1.4;

device simple_pci;

import "simics/device-api.dml";

param classname = "simple_pci";
param desc = "Simple PCI device template";

// PCI configuration space
bank pci_config {
    param function = 0;  // Will be mapped by PCI bus
    param register_size = 4;

    register VENDOR_ID @ 0x00 {
        param size = 2;
        param desc = "PCI Vendor ID";
        param init_val = 0x8086;  // Intel
        param read_only = true;
    }

    register DEVICE_ID @ 0x02 {
        param size = 2;
        param desc = "PCI Device ID";
        param init_val = 0x1234;  // Custom device
        param read_only = true;
    }

    register COMMAND @ 0x04 {
        param size = 2;
        param desc = "PCI Command register";
    }

    register STATUS @ 0x06 {
        param size = 2;
        param desc = "PCI Status register";
        param init_val = 0x0200;  // 66MHz capable
    }
}

// Device-specific registers
bank device_regs {
    param function = 0x1000;  // BAR0 mapping
    param register_size = 4;

    register CONTROL @ 0x00 {
        param size = 4;
        param desc = "Device control register";
    }

    register STATUS @ 0x04 {
        param size = 4;
        param desc = "Device status register";
        param init_val = 0x1;  // Ready
    }
}
```

## Testing Your DML Device

### 1. Compilation Test

```bash
# Test basic compilation
dmlc --simics-api=7 -I ../linux64/bin/dml/api/7/1.4 -I ../linux64/bin/dml/1.4 my_device.dml my_device

# Check for warnings
dmlc -T --simics-api=7 -I ../linux64/bin/dml/api/7/1.4 -I ../linux64/bin/dml/1.4 my_device.dml my_device
```

## Compilation Issues and Solutions

### Issue 1: "syntax error at 'device'"

**Cause**: Using old DML syntax with braces after device declaration.

**Solution**: Remove braces from device declaration:
```dml
// Wrong
device my_device { ... }

// Correct
device my_device;
```

### Issue 2: "cannot find file to import: dml-builtins.dml"

**Cause**: Missing include path for DML builtins.

**Solution**: Add both include paths:
```bash
dmlc --simics-api=7 -I ../linux64/bin/dml/api/7/1.4 -I ../linux64/bin/dml/1.4 file.dml output
```

### Issue 3: "assert sys.flags.utf8_mode"

**Cause**: Python not running in UTF-8 mode.

**Solution**: Set environment variable or modify dmlc script:
```bash
export PYTHONUTF8=1
```

### Issue 4: "unknown template: 'device'"

**Cause**: DML builtins not found in include path.

**Solution**: Ensure `-I ../linux64/bin/dml/1.4` is included.

## Testing Best Practices

### Clock Queue Configuration for Time-Based Devices

In Intel Simics, **devices that use time events** (e.g., timers, watchdogs, periodic interrupts) require a **clock source** to drive their simulation timing. This clock is set via the device's `queue` attribute.

#### The Clock Queue Problem

Without a properly configured queue, attempting to post time events will fail with:

```
The 'queue' attribute is not set, cannot post event
```

This is one of the most common issues when testing DML devices that implement time-based functionality.

#### What is a Clock Queue?

A **clock queue** is a time management mechanism in Simics that:
- Drives the progression of simulation time for devices
- Allows devices to schedule and execute time-based events
- Provides timing synchronization across the simulated system

#### Types of Clock Sources

Any Simics object that implements the clock interface can serve as a queue:

1. **Dedicated Clock Devices** (`clock` class)
   - Explicitly created clock objects
   - Configured with specific frequency (e.g., `freq_mhz=1`)
   - **Required for unit tests**

2. **System Clocks**
   - Crystal oscillator (XTAL) clocks
   - TSC (Time Stamp Counter) clocks
   - Platform-level clock generators

3. **CPU Models**
   - Can act as clock sources
   - Provide time progression based on instruction execution

#### Default Clock Allocation Behavior

**Important**: By default, Simics will automatically allocate the **first available clock device** in the system to all simple devices that don't have their `queue` attribute explicitly set.

- **In unit tests**: Usually **no default clock exists**, so you **must create one**
- **In integration tests**: System-level clocks may exist and be auto-assigned
- **Best practice**: **Explicitly set the queue** to avoid ambiguity

### Common Test Scenarios

#### Scenario 1: Simple Unit Test (Explicit Clock Required)

```python
# No system clocks exist - must create one
device = SIM_create_object('my_timer_device', 'dev')
clk = SIM_create_object('clock', 'clk', freq_mhz=1)
device.queue = clk  # REQUIRED
```

#### Scenario 2: Integration Test (System Clock Available)

```python
# Assuming a platform with existing clocks
cpu = SIM_create_object('x86-core', 'cpu0')
device = SIM_create_object('my_timer_device', 'dev')

# Option A: Use CPU as clock source
device.queue = cpu

# Option B: Use platform XTAL clock
xtal = SIM_get_object('xtal_clock')
device.queue = xtal

# Option C: Let Simics auto-assign (may be unpredictable)
# device.queue remains unset - Simics uses first available clock
```

#### Scenario 3: Multiple Devices Sharing a Clock

```python
# Create one global clock
global_clk = SIM_create_object('clock', 'system_clock', freq_mhz=100)

# Share across multiple devices
timer1 = SIM_create_object('timer_device', 'timer1')
timer1.queue = global_clk

timer2 = SIM_create_object('timer_device', 'timer2')
timer2.queue = global_clk

wdt = SIM_create_object('watchdog', 'wdt')
wdt.queue = global_clk
```

### Testing Best Practices Checklist

#### ✅ DO

1. **Always create and assign a clock in unit tests**
   ```python
   clk = SIM_create_object('clock', 'clk', freq_mhz=1)
   device.queue = clk
   ```

2. **Document clock requirements in test files**
   ```python
   # This device requires a clock queue for timer events
   ```

3. **Create clock BEFORE posting events**
   ```python
   # CORRECT ORDER:
   device = SIM_create_object('my_device', 'dev')
   clk = SIM_create_object('clock', 'clk', freq_mhz=1)
   device.queue = clk  # Set before enabling timers
   device.enable_timer()
   ```

4. **Use appropriate clock frequency for your device**
   ```python
   # Match device requirements
   rtc_clk = SIM_create_object('clock', 'rtc', freq_mhz=0.032768)  # 32.768 kHz
   cpu_clk = SIM_create_object('clock', 'cpu_clk', freq_mhz=3000)   # 3 GHz
   ```

5. **Test time-dependent behavior explicitly**
   ```python
   # Read initial state
   value_before = device.counter.read()
   
   # Advance simulation time
   SIM_continue(1000)
   
   # Verify state changed
   value_after = device.counter.read()
   stest.expect_true(value_after != value_before, "Timer should advance")
   ```

#### ❌ DON'T

1. **Don't assume a default clock exists in unit tests**
   ```python
   # BAD - will fail in unit tests
   device = SIM_create_object('my_device', 'dev')
   # Missing: device.queue = ...
   device.enable_timer()  # ← CRASH!
   ```

2. **Don't forget to handle missing queue in DML code**
   ```dml
   // Good practice: check queue before posting
   method start_timer() {
       if (dev.queue != NULL) {
           timer_event.post(delay);
       } else {
           log error: "Cannot post event - no queue configured";
       }
   }
   ```

3. **Don't mix incompatible clock domains without consideration**
   ```python
   # RISKY - devices may expect synchronized timing
   dev1.queue = clk_100mhz
   dev2.queue = clk_50mhz  # Different frequency - be careful!
   ```

### Troubleshooting Test Issues

#### Error: "The 'queue' attribute is not set, cannot post event"

**Cause**: Device is trying to schedule a time event without a configured clock queue.

**Solution**:
```python
# Before running the test
clk = SIM_create_object('clock', 'clk', freq_mhz=1)
device.queue = clk
```

#### Error: "Attribute 'queue' not found"

**Cause**: Device doesn't support time events (not a simple device).

**Solution**: Check if device actually needs a queue. Not all devices require timing.

#### Warning: Timer events not executing

**Cause**: Clock frequency may be misconfigured, or time not advancing.

**Solution**:
```python
# Verify clock configuration
print(f"Clock frequency: {clk.freq_mhz} MHz")
print(f"Device queue: {device.queue}")

# Ensure time is advancing
SIM_continue(1000)  # Run simulation for 1000 cycles
```

#### Events execute but at wrong frequency

**Cause**: Clock frequency doesn't match device expectations.

**Solution**:
```python
# Check device requirements
# If device expects 1 MHz timer ticks:
clk = SIM_create_object('clock', 'clk', freq_mhz=1)  # Match expectation

# If device has configurable frequency, set it:
device.timer_frequency = 1000000  # 1 MHz
```

### Clock Queue Summary

| Aspect | Description |
|--------|-------------|
| **Purpose** | Provides simulation time progression for devices |
| **Requirement** | Mandatory for devices posting time events |
| **Configuration** | Set via `device.queue = clock_object` |
| **Unit Tests** | Must explicitly create and assign clock |
| **Integration Tests** | May use system clocks or CPU as queue |
| **Default Behavior** | Simics auto-assigns first available clock (if any) |

**Key Takeaway**: Always create and assign a clock queue in unit tests for devices that use time events. This is essential for avoiding the `'queue' attribute is not set` error, as demonstrated in the watchdog timer test case.

## Conclusion

DML device development requires understanding the specific syntax requirements and testing practices:

### Development Requirements:

1. **Device declarations are single lines without braces**
2. **Include paths must include both API and builtins directories**
3. **UTF-8 mode must be enabled for the compiler**
4. **Parameters and banks go at the top level**
5. **Use proper logging and error handling**

### Testing Requirements:

6. **Always configure clock queue for time-based devices in unit tests**
7. **Create explicit clock objects before posting time events**
8. **Test time-dependent behavior with `SIM_continue()`**
9. **Document clock requirements in test files**

Following these practices will help you write robust, maintainable DML devices and reliable tests for Simics simulation.

## Quick Reference

### Minimal Device Template

```dml
dml 1.4;

// `device` statements must be placed immediately after the DML version declaration
// Only one device statement is allowed per device (including all imported DML files)
device DEVICE_NAME;

import "simics/device-api.dml";

param classname = "DEVICE_NAME";
param desc = "Device description";

// Add banks, registers, methods here
```

### Compilation Command

```bash
dmlc --simics-api=7 -I ../linux64/bin/dml/api/7/1.4 -I ../linux64/bin/dml/1.4 input.dml output
```

---

**Document Status**: ✅ Complete
**Last Updated**: November 18, 2025 - Added Testing Best Practices section
**Tested With**: Simics 7.57.0, DML 1.4, API version 7
