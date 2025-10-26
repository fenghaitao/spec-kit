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

## DML Compilation Setup

### Required Compiler Flags

The key to successful DML compilation is using the correct compiler flags:

```bash
dmlc --simics-api=6 -I ../linux64/bin/dml/api/6/1.4 -I ../linux64/bin/dml/1.4 input.dml output
```

**Critical Points:**
- `--simics-api=6`: Specifies Simics API version
- `-I ../linux64/bin/dml/api/6/1.4`: Include path for Simics API
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

import "simics/device-api.dml";  // Always needed for devices

device my_device;
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

import "simics/device-api.dml";

device uart_device;

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
        
        method read() -> (uint64) {
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

import "simics/device-api.dml";

device basic_mmio;

param classname = "basic_mmio";
param desc = "Basic memory-mapped I/O device";

bank control_regs {
    param function = 0x1000;
    param register_size = 4;
    
    register control @ 0x00 {
        param size = 4;
        param desc = "Control register";
    }
    
    register status @ 0x04 {
        param size = 4;
        param desc = "Status register";
        param init_val = 0x1;  // Device ready
    }
}
```

### 2. Device with Interrupts

```dml
dml 1.4;

import "simics/device-api.dml";

device interrupt_device;

param classname = "interrupt_device";
param desc = "Device that can generate interrupts";

connect irq {
    param configuration = "optional";
    param c_type = "simple_interrupt";
}

bank regs {
    param function = 0x2000;
    param register_size = 4;
    
    register interrupt_enable @ 0x00 {
        param size = 4;
        param desc = "Interrupt enable register";
    }
    
    register interrupt_status @ 0x04 {
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
    if (regs.interrupt_enable.val & regs.interrupt_status.val) {
        if (irq.signal) {
            irq.signal.signal_raise();
        }
    }
}
```

### 3. Timer Device

```dml
dml 1.4;

import "simics/device-api.dml";

device timer_device;

param classname = "timer_device";
param desc = "Simple timer device";

event timer_tick;

bank timer_regs {
    param function = 0x4000;
    param register_size = 4;
    
    register timer_value @ 0x00 {
        param size = 4;
        param desc = "Current timer value";
    }
    
    register timer_control @ 0x04 {
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
    after (1.0) call timer_expired();
}

method timer_expired() {
    log info: "Timer expired";
    timer_regs.timer_value.val = 0;
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
dmlc --simics-api=6 -I ../linux64/bin/dml/api/6/1.4 -I ../linux64/bin/dml/1.4 file.dml output
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
project/
├── devices/
│   ├── uart.dml
│   ├── timer.dml
│   └── ethernet.dml
├── common/
│   └── device-common.dml
└── Makefile
```

### 2. Naming Conventions

- **Device names**: lowercase_with_underscores
- **Register names**: descriptive_lowercase
- **Parameters**: lowercase or camelCase
- **Methods**: lowercase_with_underscores

### 3. Documentation

Always include meaningful descriptions:

```dml
param desc = "Detailed description of what this device does";

register control @ 0x00 {
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

import "simics/device-api.dml";

device uart_16550;

param classname = "uart_16550";
param desc = "16550-compatible UART device";

bank uart_regs {
    param function = 0x3f8;
    param register_size = 1;
    
    // Data register / Divisor latch low
    register rbr_thr_dll @ 0x00 {
        param size = 1;
        param desc = "Receiver buffer/Transmitter holding/Divisor latch low";
        
        method write(uint64 value) {
            if (lcr.val & 0x80) {
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
            if (lcr.val & 0x80) {
                return this.val;  // Divisor latch
            } else {
                log info: "UART receive read";
                return 0x00;  // No data available
            }
        }
    }
    
    // Interrupt enable register / Divisor latch high
    register ier_dlh @ 0x01 {
        param size = 1;
        param desc = "Interrupt enable/Divisor latch high";
    }
    
    // Line control register
    register lcr @ 0x03 {
        param size = 1;
        param desc = "Line control register";
        param init_val = 0x03;  // 8N1
    }
    
    // Line status register
    register lsr @ 0x05 {
        param size = 1;
        param desc = "Line status register";
        param init_val = 0x60;  // TX empty and ready
    }
}
```

### Simple PCI Device Template

```dml
dml 1.4;

import "simics/device-api.dml";

device simple_pci;

param classname = "simple_pci";
param desc = "Simple PCI device template";

// PCI configuration space
bank pci_config {
    param function = 0;  // Will be mapped by PCI bus
    param register_size = 4;
    
    register vendor_id @ 0x00 {
        param size = 2;
        param desc = "PCI Vendor ID";
        param init_val = 0x8086;  // Intel
        param read_only = true;
    }
    
    register device_id @ 0x02 {
        param size = 2;
        param desc = "PCI Device ID";
        param init_val = 0x1234;  // Custom device
        param read_only = true;
    }
    
    register command @ 0x04 {
        param size = 2;
        param desc = "PCI Command register";
    }
    
    register status @ 0x06 {
        param size = 2;
        param desc = "PCI Status register";
        param init_val = 0x0200;  // 66MHz capable
    }
}

// Device-specific registers
bank device_regs {
    param function = 0x1000;  // BAR0 mapping
    param register_size = 4;
    
    register control @ 0x00 {
        param size = 4;
        param desc = "Device control register";
    }
    
    register status @ 0x04 {
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
dmlc --simics-api=6 -I ../linux64/bin/dml/api/6/1.4 -I ../linux64/bin/dml/1.4 my_device.dml my_device

# Check for warnings
dmlc -T --simics-api=6 -I ../linux64/bin/dml/api/6/1.4 -I ../linux64/bin/dml/1.4 my_device.dml my_device
```

### 2. Integration with AI Tools

The AI scripts in this project can help validate and generate DML code:

```python
from dml_parser_integration import DMLParserIntegration

parser = DMLParserIntegration()
is_valid, errors, info = parser.validate_dml_syntax(dml_code)
```

## Conclusion

DML device development requires understanding the specific syntax requirements:

1. **Device declarations are single lines without braces**
2. **Include paths must include both API and builtins directories**
3. **UTF-8 mode must be enabled for the compiler**
4. **Parameters and banks go at the top level**
5. **Use proper logging and error handling**

Following these practices will help you write robust, maintainable DML devices for Simics simulation.

## Quick Reference

### Minimal Device Template

```dml
dml 1.4;

import "simics/device-api.dml";

device DEVICE_NAME;

param classname = "DEVICE_NAME";
param desc = "Device description";

// Add banks, registers, methods here
```

### Compilation Command

```bash
dmlc --simics-api=6 -I ../linux64/bin/dml/api/6/1.4 -I ../linux64/bin/dml/1.4 input.dml output
```

---

**Document Status**: ✅ Complete  
**Last Updated**: Generated after solving DML compilation issues  
**Tested With**: Simics 7.57.0, DML 1.4, API version 6