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

### Advanced Timer Device Implementation

This comprehensive example demonstrates how to implement hardware timer functionality in Simics, including time event management, frequency conversion, and both relative and absolute timer modes.

#### Timer Implementation Concepts

A hardware timer in Simics typically involves:
- A **timer register** with control fields (enable, start, value)
- A **time event** that fires when the timer expires
- **Frequency conversion** between simulation time and timer cycles
- **Start time tracking** for calculating elapsed time

**Simulation Time vs Timer Cycles:**
- **Simulation Time**: Absolute time in seconds returned by `SIM_time()`
- **Timer Cycles**: Hardware-specific count based on timer frequency
- **Conversion Formula**:
  ```
  cycles = simulation_time * frequency_hz
  simulation_time = cycles / frequency_hz
  ```

**Timer Event Flow:**
```
Software Write → Start Timer → Post Event → Event Fires → Handle Timeout
     ↓              ↓              ↓             ↓              ↓
  Enable=1    Log start time  Calc timeout   Clear enable   Set status
```

#### Complete Timer Device Example

```dml
dml 1.4;

device timer_device;

import "simics/device-api.dml";

param classname = "timer_device";
param desc = "Hardware timer device with relative and absolute timer modes";

// Define log group for timer messages
loggroup timer_log;

// Timer frequency: 100 MHz
constant TIMER_FREQ_HZ = 100 * 1000 * 1000;

// ============================================================================
// Timer Event Definition
// ============================================================================

event timer_event is (simple_time_event) {
    // This method is called when the timer expires
    method event() {
        // Clear the running/busy bit
        timer_bank.TIMER_CONTROL.Enable.set(0);
        
        // Set the interrupt/timeout flag
        timer_bank.TIMER_STATUS.Timeout.set(1);
        
        // Log the expiration
        log info, 1, timer_log: "Timer expired at sim time %f", 
            SIM_time(dev.obj);
        
        // Optionally trigger an interrupt here
        // interrupt_pin.signal.signal_raise();
    }
    
    // Arm the timer with a timeout in simulation seconds
    method arm(double timeout_seconds) {
        local bool is_posted = posted();
        
        // If already posted, remove the old event
        if (is_posted) {
            remove();
            log info, 2, timer_log: "Removed previously posted timer";
        }
        
        // Post the new event
        post(timeout_seconds);
        log info, 2, timer_log: "Timer armed for %f seconds", timeout_seconds;
    }
    
    // Cancel the timer
    method cancel() {
        if (posted()) {
            remove();
            log info, 2, timer_log: "Timer cancelled";
        }
    }
}

// ============================================================================
// Helper Template for Time Conversion
// ============================================================================

template timer_helper {
    param frequency_hz default TIMER_FREQ_HZ;
    
    // Convert cycles to simulation time (seconds)
    method cycles_to_simtime(uint64 cycles) -> (double) {
        return cast(cycles, double) / frequency_hz;
    }
    
    // Convert simulation time to cycles
    method simtime_to_cycles(double simtime) -> (uint64) {
        return cast(simtime * frequency_hz, uint64);
    }
    
    // Get current time in cycles
    method get_current_cycles() -> (uint64) {
        local double sim_time = SIM_time(dev.obj);
        return simtime_to_cycles(sim_time);
    }
}

// ============================================================================
// Saved Variables for Timer State
// ============================================================================

// Store the simulation time when timer was started
saved double timer_start_simtime = 0.0;

// Store the target cycle count when timer should expire
saved uint64 timer_target_cycles = 0;

// ============================================================================
// Timer Register Bank (Relative/Countdown Timer)
// ============================================================================

bank timer_bank is (timer_helper) {
    
    // -------------------------------------------------------------------------
    // TIMER_CONTROL Register
    // -------------------------------------------------------------------------
    register TIMER_CONTROL size 4 @ 0x00 {
        field Enable @ [0] "Timer enable/start bit";
        field AutoReload @ [1] "Auto-reload mode";
        field Reserved @ [31:2];
        
        method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
            // Write the value to register fields first
            default(value, enabled_bytes, aux);
            
            // Check if timer is being enabled/started
            if (Enable.val == 1) {
                // Get the configured timeout value
                local uint64 timeout_cycles = TIMER_VALUE.Value.val;
                
                if (timeout_cycles == 0) {
                    log error: "Cannot start timer with zero timeout";
                    Enable.set(0);
                    return;
                }
                
                // Record the start time (critical for elapsed time calculation)
                timer_start_simtime = SIM_time(dev.obj);
                
                // Calculate target expiration time in cycles
                local uint64 current_cycles = get_current_cycles();
                timer_target_cycles = current_cycles + timeout_cycles;
                
                // Convert timeout cycles to simulation seconds
                local double timeout_seconds = cycles_to_simtime(timeout_cycles);
                
                // Arm/post the timer event
                timer_event.arm(timeout_seconds);
                
                log info, 1, timer_log: 
                    "Timer started: %lld cycles (%f sec) at simtime %f",
                    timeout_cycles, timeout_seconds, timer_start_simtime;
            } 
            else {
                // Timer is being disabled - cancel the event
                timer_event.cancel();
                log info, 1, timer_log: "Timer stopped by software";
            }
        }
    }
    
    // -------------------------------------------------------------------------
    // TIMER_VALUE Register
    // -------------------------------------------------------------------------
    register TIMER_VALUE size 4 @ 0x04 {
        field Value @ [31:0] "Timer timeout value in cycles";
        
        method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
            // Just store the value - it will be used when timer is started
            default(value, enabled_bytes, aux);
            log info, 2, timer_log: "Timer value configured: %lld cycles", 
                Value.val;
        }
        
        method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
            // If timer is not running, return the configured value
            if (TIMER_CONTROL.Enable.val == 0) {
                return default(enabled_bytes, aux);
            }
            
            // Timer is running - calculate and return remaining cycles
            local double current_simtime = SIM_time(dev.obj);
            local double elapsed_simtime = current_simtime - timer_start_simtime;
            local uint64 elapsed_cycles = simtime_to_cycles(elapsed_simtime);
            
            local uint64 initial_cycles = Value.val;
            local uint64 remaining_cycles;
            
            if (elapsed_cycles >= initial_cycles) {
                // Timer should have expired (or is about to)
                remaining_cycles = 0;
            } else {
                remaining_cycles = initial_cycles - elapsed_cycles;
            }
            
            log info, 3, timer_log: 
                "Timer read: elapsed=%lld, remaining=%lld cycles",
                elapsed_cycles, remaining_cycles;
            
            return remaining_cycles;
        }
    }
    
    // -------------------------------------------------------------------------
    // TIMER_STATUS Register
    // -------------------------------------------------------------------------
    register TIMER_STATUS size 4 @ 0x08 {
        field Timeout @ [0] "Timer timeout occurred (write 1 to clear)";
        field Running @ [1] "Timer is currently running (read-only)";
        field Reserved @ [31:2];
        
        method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
            // Update running status dynamically
            Running.set(TIMER_CONTROL.Enable.val);
            return default(enabled_bytes, aux);
        }
        
        method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
            // Allow clearing timeout flag by writing 1
            if ((value & 0x1) == 1) {
                Timeout.set(0);
                log info, 2, timer_log: "Timeout flag cleared";
            }
            // Running bit is read-only, ignore writes to it
        }
    }
    
    // -------------------------------------------------------------------------
    // TIMER_CURRENT Register (Read-only elapsed cycles)
    // -------------------------------------------------------------------------
    register TIMER_CURRENT size 4 @ 0x0C {
        field Value @ [31:0] "Current elapsed cycles (read-only)";
        
        method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
            if (TIMER_CONTROL.Enable.val == 0) {
                // Timer not running, return 0
                return 0;
            }
            
            // Calculate elapsed cycles since timer start
            local double current_simtime = SIM_time(dev.obj);
            local double elapsed_simtime = current_simtime - timer_start_simtime;
            local uint64 elapsed_cycles = simtime_to_cycles(elapsed_simtime);
            
            log info, 3, timer_log: 
                "Elapsed time: %f sec = %lld cycles",
                elapsed_simtime, elapsed_cycles;
            
            return elapsed_cycles;
        }
    }
}

// ============================================================================
// Absolute Target Timer Example
// ============================================================================

// This example shows a timer that uses an absolute target time
// (useful for timestamp-based timers like TSC-based timers)

event absolute_timer_event is (simple_time_event) {
    method event() {
        abs_timer_bank.ABS_TIMER_CONTROL.Run_Busy.set(0);
        abs_timer_bank.ABS_TIMER_STATUS.Expired.set(1);
        log info, 1, timer_log: "Absolute timer expired";
    }
    
    method arm(double timeout) {
        if (posted())
            remove();
        post(timeout);
    }

    method cancel() {
        if (posted())
            remove();
    }
}

bank abs_timer_bank is (timer_helper) {
    
    // Free-running counter register (like a TSC counter)
    register FREE_RUNNING_COUNTER size 8 @ 0x20 is (timer_helper) {
        method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
            // Return current simulation time converted to cycles
            return get_current_cycles();
        }
    }
    
    // Absolute target timer control
    register ABS_TIMER_CONTROL size 4 @ 0x28 {
        field Run_Busy @ [0] "Timer is running";
        field Reserved @ [31:1];
        
        method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
            default(value, enabled_bytes, aux);
            
            // If enabling, arm the timer with current target
            if (Run_Busy.val == 1) {
                local uint64 target_cycles = ABS_TIMER_TARGET.Target_Cycles.val;
                local uint64 current_cycles = FREE_RUNNING_COUNTER.get_current_cycles();
                
                // Calculate delta cycles
                local uint64 delta_cycles;
                if (target_cycles > current_cycles) {
                    delta_cycles = target_cycles - current_cycles;
                } else {
                    // Target is in the past, fire immediately
                    delta_cycles = 0;
                }
                
                // Convert to simulation time
                local double timeout_seconds = cycles_to_simtime(delta_cycles);
                
                log info, 1, timer_log: 
                    "Absolute timer started: target=%lld, current=%lld, delta=%lld cycles (%f sec)",
                    target_cycles, current_cycles, delta_cycles, timeout_seconds;
                
                // Arm the event
                absolute_timer_event.arm(timeout_seconds);
            } else {
                // Disabling - cancel the event
                absolute_timer_event.cancel();
            }
        }
    }
    
    register ABS_TIMER_TARGET size 8 @ 0x2C {
        field Target_Cycles @ [63:0] "Absolute cycle count to trigger at";
        
        method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
            default(value, enabled_bytes, aux);
            
            // If timer is already running, re-arm with new target
            if (ABS_TIMER_CONTROL.Run_Busy.val == 1) {
                local uint64 target_cycles = Target_Cycles.val;
                local uint64 current_cycles = FREE_RUNNING_COUNTER.get_current_cycles();
                
                // Calculate delta cycles
                local uint64 delta_cycles;
                if (target_cycles > current_cycles) {
                    delta_cycles = target_cycles - current_cycles;
                } else {
                    delta_cycles = 0;
                }
                
                // Convert to simulation time
                local double timeout_seconds = cycles_to_simtime(delta_cycles);
                
                log info, 1, timer_log: 
                    "Absolute timer target updated: target=%lld, current=%lld, delta=%lld cycles (%f sec)",
                    target_cycles, current_cycles, delta_cycles, timeout_seconds;
                
                // Re-arm the event
                absolute_timer_event.arm(timeout_seconds);
            }
        }
    }
    
    register ABS_TIMER_STATUS size 4 @ 0x34 {
        field Expired @ [0] "Timer has expired (write 1 to clear)";
        
        method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
            if ((value & 0x1) == 1) {
                Expired.set(0);
                log info, 2, timer_log: "Absolute timer expired flag cleared";
            }
        }
    }
}
```

#### Key Timer Implementation Points

**1. Event Management:**
- Always check `posted()` before posting a new event to avoid multiple pending events
- Use `remove()` to cancel a posted event before posting a new one
- `post(seconds)` schedules the event relative to current simulation time

**2. Tracking Start Time:**
```dml
// Critical for elapsed time calculation
saved double timer_start_simtime = 0.0;

// When timer starts:
timer_start_simtime = SIM_time(dev.obj);

// When reading elapsed time:
local double elapsed = SIM_time(dev.obj) - timer_start_simtime;
local uint64 elapsed_cycles = simtime_to_cycles(elapsed);
```

**3. Frequency Conversion Helper Methods:**
```dml
method cycles_to_simtime(uint64 cycles) -> (double) {
    return cast(cycles, double) / frequency_hz;
}

method simtime_to_cycles(double simtime) -> (uint64) {
    return cast(simtime * frequency_hz, uint64);
}
```

**4. Relative vs Absolute Timers:**

- **Relative Timer (countdown)**:
  - Software writes timeout duration
  - Timer counts down from initial value
  - Expires after duration elapses
  - Example: `TIMER_VALUE` in the code above

- **Absolute Timer (target-based)**:
  - Uses a free-running counter
  - Software writes absolute target cycle count
  - Timer expires when counter reaches target
  - Example: `ABS_TIMER_TARGET` in the code above

**5. Testing Your Timer:**

```python
# Create device and configure
$dev = (create-timer_device)

# Configure timer for 10ms (1M cycles at 100MHz)
$dev.bank.timer_bank.TIMER_VALUE = 1000000

# Start timer
$dev.bank.timer_bank.TIMER_CONTROL = 1

# Check immediate status
print $dev.bank.timer_bank.TIMER_VALUE
print $dev.bank.timer_bank.TIMER_CURRENT

# Advance time
run-cycles 500000

# Check mid-flight
print $dev.bank.timer_bank.TIMER_VALUE      # Should be ~500000
print $dev.bank.timer_bank.TIMER_CURRENT    # Should be ~500000

# Wait for expiration
run-cycles 500000

# Check completion
print $dev.bank.timer_bank.TIMER_STATUS     # Timeout bit should be set
print $dev.bank.timer_bank.TIMER_CONTROL    # Enable should be clear
```

**6. Common Timer Best Practices:**

- ✅ Use `saved` variables for timer state that needs to persist across checkpoints
- ✅ Validate input values (e.g., reject zero timeout)
- ✅ Log important timer operations at appropriate levels
- ✅ Handle edge cases (zero timeout, timer already running, target in the past)
- ✅ Check for and remove pending events before posting new ones
- ✅ Calculate elapsed/remaining time dynamically on read
- ❌ Don't forget to cancel events when disabling the timer
- ❌ Don't post events without checking if one is already pending

## Testing Your DML Device

### 1. Compilation Test

```bash
# Test basic compilation
dmlc --simics-api=7 -I ../linux64/bin/dml/api/7/1.4 -I ../linux64/bin/dml/1.4 my_device.dml my_device

# Check for warnings
dmlc -T --simics-api=7 -I ../linux64/bin/dml/api/7/1.4 -I ../linux64/bin/dml/1.4 my_device.dml my_device
```

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
