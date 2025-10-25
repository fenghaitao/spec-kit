# Quickstart Guide: Watchdog Timer Device

## Overview

This guide helps developers quickly get started with the watchdog timer device implementation. It covers setup, basic usage, testing, and common development patterns.

**Target Audience**: Simics device developers implementing or testing the watchdog timer
**Prerequisites**: Simics Base 7.57.0, DML 1.4 knowledge, Python for testing
**Time to Complete**: 30-45 minutes

---

## Quick Reference

### Device at a Glance
- **Type**: Memory-mapped peripheral (ARM PrimeCell SP805-compatible)
- **Register Count**: 21 registers (0x000-0xFFC)
- **Memory Size**: 4KB address space
- **Key Features**: Dual-stage timeout, lock protection, integration test mode
- **Signals**: Interrupt output (edge), Reset output (level)

### Essential Register Addresses
```
0x000  WDOGLOAD      - Load counter value (starts countdown)
0x004  WDOGVALUE     - Read current counter value
0x008  WDOGCONTROL   - Enable interrupt/reset, set divider
0x00C  WDOGINTCLR    - Write any value to clear interrupt
0x010  WDOGRIS       - Raw interrupt status (read-only)
0xC00  WDOGLOCK      - Write 0x1ACCE551 to unlock registers
```

---

## Environment Setup

### 1. Verify Simics Installation

```bash
# Check Simics version
cd /path/to/simics-project
./bin/project-setup --list-packages | grep Simics-Base
# Should show: Simics-Base 7.57.0 (or compatible)

# Verify required packages
./bin/project-setup --list-packages | grep -E "QSP-x86|Python"
```

### 2. Create Simics Project (if needed)

```bash
# Using MCP server tool (recommended)
# This will be done automatically in /implement phase

# Or manually:
mkdir -p ~/simics-projects/watchdog-timer
cd ~/simics-projects/watchdog-timer
/opt/simics/bin/project-setup .
```

### 3. Add DML Device Module

```bash
# Directory structure after /implement phase:
watchdog-timer/
├── modules/
│   └── watchdog-timer/
│       ├── watchdog-timer.dml    # Main device implementation
│       ├── module_load.py         # Python device registration
│       └── Makefile               # Build configuration
├── targets/
│   └── qsp-x86/
│       └── watchdog-test.simics   # Test script
└── tests/
    └── watchdog/
        ├── test_basic.py
        ├── test_timeout.py
        └── test_lock.py
```

---

## Basic Usage

### Device Instantiation

#### From Simics Script (.simics)
```python
# Create the watchdog timer device
$wdt = (create-watchdog-timer name = wdt0)

# Map to memory address 0x1000
$phys_mem = (lookup-objects -all name = phys_mem)[0]
$phys_mem.map[0x1000] = $wdt 0 4096

# Connect interrupt output to PIC
$pic = (lookup-objects -all name = pic)[0]
connect $wdt.irq_dev $pic.irq[5]

# Connect reset output to system reset
$system = (lookup-objects -all name = system)[0]
connect $wdt.rst_dev $system.reset_in
```

#### From Python Test
```python
import simics
import dev_util

# Create device
wdt = simics.SIM_create_object('watchdog-timer', 'wdt0')

# Create memory space
phys_mem = simics.pre_conf_object('phys_mem', 'memory-space')
phys_mem.attr.map = [[0x1000, wdt, 0, 0, 4096]]

# Create clock
clock = simics.pre_conf_object('clock', 'clock', freq_mhz=1000)
wdt.attr.queue = clock

# Instantiate all objects
simics.SIM_add_configuration([clock, wdt, phys_mem], None)

# Get instantiated objects
wdt_obj = simics.SIM_get_object('wdt0')
mem_obj = simics.SIM_get_object('phys_mem')
```

### Register Access Patterns

#### Writing Registers
```python
import dev_util

# Create register accessor (little-endian)
WDOGLOAD = dev_util.Register_LE(wdt_obj.bank.regs, 0x000, size=4)
WDOGCONTROL = dev_util.Register_LE(wdt_obj.bank.regs, 0x008, size=4)
WDOGLOCK = dev_util.Register_LE(wdt_obj.bank.regs, 0xC00, size=4)

# Unlock device (required before writing WDOGLOAD or WDOGCONTROL)
WDOGLOCK.write(0x1ACCE551)

# Load counter with timeout value
WDOGLOAD.write(1000000)  # Timeout in 1M cycles (1ms @ 1GHz)

# Enable interrupt and reset
WDOGCONTROL.write(0x3)  # INTEN=1, RESEN=1, divider=1
```

#### Reading Registers
```python
# Read current counter value
current_value = WDOGVALUE.read()
print(f"Counter: {current_value}")

# Check interrupt status
raw_status = WDOGRIS.read()
masked_status = WDOGMIS.read()
print(f"Interrupt: raw={raw_status}, masked={masked_status}")

# Check lock state
lock_state = WDOGLOCK.read()
print(f"Locked: {lock_state == 1}")
```

---

## Common Development Patterns

### Pattern 1: Basic Watchdog Operation

```python
def setup_basic_watchdog(wdt, timeout_cycles):
    """
    Configure watchdog for basic operation.
    
    Args:
        wdt: Watchdog timer device object
        timeout_cycles: Number of cycles until timeout
    """
    WDOGLOCK = dev_util.Register_LE(wdt.bank.regs, 0xC00, size=4)
    WDOGLOAD = dev_util.Register_LE(wdt.bank.regs, 0x000, size=4)
    WDOGCONTROL = dev_util.Register_LE(wdt.bank.regs, 0x008, size=4)
    
    # Unlock device
    WDOGLOCK.write(0x1ACCE551)
    
    # Configure: interrupt enabled, reset enabled, divider=1
    WDOGCONTROL.write(0x3)
    
    # Start countdown
    WDOGLOAD.write(timeout_cycles)
    
    # Lock device to prevent accidental modification
    WDOGLOCK.write(0x0)
```

### Pattern 2: Servicing the Watchdog (Kicking)

```python
def kick_watchdog(wdt, timeout_cycles):
    """
    Reset watchdog timer (service the watchdog).
    
    Must be called periodically before timeout to prevent reset.
    """
    WDOGLOCK = dev_util.Register_LE(wdt.bank.regs, 0xC00, size=4)
    WDOGLOAD = dev_util.Register_LE(wdt.bank.regs, 0x000, size=4)
    
    # Unlock
    WDOGLOCK.write(0x1ACCE551)
    
    # Reload counter (restarts countdown)
    WDOGLOAD.write(timeout_cycles)
    
    # Lock
    WDOGLOCK.write(0x0)
```

### Pattern 3: Interrupt Handler Simulation

```python
def handle_watchdog_interrupt(wdt):
    """
    Simulate interrupt handler that clears interrupt.
    
    Should be called when WDOGMIS reads as 1.
    """
    WDOGINTCLR = dev_util.Register_LE(wdt.bank.regs, 0x00C, size=4)
    WDOGMIS = dev_util.Register_LE(wdt.bank.regs, 0x014, size=4)
    
    # Check if interrupt is pending
    if WDOGMIS.read() & 0x1:
        # Clear interrupt (write any value)
        WDOGINTCLR.write(0)
        print("Watchdog interrupt cleared")
        return True
    return False
```

### Pattern 4: Using Clock Dividers

```python
def set_clock_divider(wdt, divider):
    """
    Set watchdog clock divider.
    
    Args:
        wdt: Watchdog device object
        divider: 1, 16, or 256
    """
    WDOGLOCK = dev_util.Register_LE(wdt.bank.regs, 0xC00, size=4)
    WDOGCONTROL = dev_util.Register_LE(wdt.bank.regs, 0x008, size=4)
    
    # Map divider to control bits
    divider_map = {1: 0b00, 16: 0b01, 256: 0b10}
    if divider not in divider_map:
        raise ValueError(f"Invalid divider: {divider}")
    
    # Unlock
    WDOGLOCK.write(0x1ACCE551)
    
    # Set divider and enable bits
    # Keep INTEN and RESEN, change divider
    control = WDOGCONTROL.read() & 0x3  # Preserve enable bits
    control |= (divider_map[divider] << 2)  # Set divider bits
    WDOGCONTROL.write(control)
    
    # Lock
    WDOGLOCK.write(0x0)
```

---

## Testing Guide

### Running Tests

```bash
# Navigate to project directory
cd /path/to/watchdog-timer-project

# Build the device module
make

# Run all tests
./bin/test-runner tests/watchdog/

# Run specific test
./bin/test-runner tests/watchdog/test_basic.py

# Run with verbose output
./bin/test-runner -v tests/watchdog/test_timeout.py
```

### Writing a Simple Test

```python
# File: tests/watchdog/test_example.py
import stest
import simics
import dev_util

def test_counter_countdown():
    """Test that counter decrements over time."""
    # Setup
    wdt = create_watchdog_device()
    WDOGLOCK = dev_util.Register_LE(wdt.bank.regs, 0xC00, size=4)
    WDOGLOAD = dev_util.Register_LE(wdt.bank.regs, 0x000, size=4)
    WDOGVALUE = dev_util.Register_LE(wdt.bank.regs, 0x004, size=4)
    
    # Unlock and load counter
    WDOGLOCK.write(0x1ACCE551)
    WDOGLOAD.write(1000)
    
    # Read initial value
    initial = WDOGVALUE.read()
    stest.expect_equal(initial, 1000)
    
    # Advance simulation by 100 cycles
    simics.SIM_continue(100)
    
    # Counter should have decremented
    current = WDOGVALUE.read()
    stest.expect_equal(current, 900)
    
    print("Test passed: Counter counts down correctly")

def create_watchdog_device():
    """Helper to create and configure device."""
    wdt = simics.SIM_create_object('watchdog-timer', 'wdt_test')
    clock = simics.pre_conf_object('clock', 'clock', freq_mhz=1000)
    wdt.attr.queue = clock
    simics.SIM_add_configuration([clock, wdt], None)
    return simics.SIM_get_object('wdt_test')

# Run test
if __name__ == '__main__':
    test_counter_countdown()
```

### Test Checklist

Essential tests to implement:
- [ ] Register read/write basic functionality
- [ ] Lock mechanism blocks protected registers
- [ ] Counter counts down at correct rate
- [ ] First timeout generates interrupt
- [ ] Second timeout generates reset
- [ ] WDOGINTCLR clears interrupt and prevents reset
- [ ] Clock dividers work correctly (1, 16, 256)
- [ ] Integration test mode controls signals
- [ ] Checkpoint/restore preserves state
- [ ] Peripheral ID registers return correct values

---

## Debugging Tips

### 1. Checking Device State

```python
# Dump all register values
def dump_registers(wdt):
    """Print all watchdog registers."""
    regs = [
        (0x000, "WDOGLOAD"),
        (0x004, "WDOGVALUE"),
        (0x008, "WDOGCONTROL"),
        (0x010, "WDOGRIS"),
        (0x014, "WDOGMIS"),
        (0xC00, "WDOGLOCK"),
    ]
    
    print("Watchdog Timer Registers:")
    for offset, name in regs:
        reg = dev_util.Register_LE(wdt.bank.regs, offset, size=4)
        value = reg.read()
        print(f"  {name:15s} (0x{offset:03X}): 0x{value:08X}")
```

### 2. Monitoring Counter

```python
def monitor_counter(wdt, duration_cycles):
    """Monitor counter value over time."""
    WDOGVALUE = dev_util.Register_LE(wdt.bank.regs, 0x004, size=4)
    
    print(f"Monitoring counter for {duration_cycles} cycles:")
    for i in range(0, duration_cycles, duration_cycles // 10):
        value = WDOGVALUE.read()
        cycle = simics.SIM_cycle_count(wdt)
        print(f"  Cycle {cycle}: Counter = {value}")
        simics.SIM_continue(duration_cycles // 10)
```

### 3. Enabling DML Logging

```dml
// Add to watchdog-timer.dml for debugging

method log_register_access(const char *reg_name, uint64 value, bool is_write) {
    if (is_write) {
        log info: "Write %s = 0x%08x", reg_name, value;
    } else {
        log info: "Read %s => 0x%08x", reg_name, value;
    }
}

// Use in register methods:
register WDOGLOAD @ 0x000 {
    method write(uint64 val) {
        log_register_access("WDOGLOAD", val, true);
        // ... rest of implementation
    }
}
```

### 4. Common Issues and Solutions

**Issue**: Counter not counting down
- **Check**: Clock object connected? (`wdt.attr.queue` should return clock)
- **Check**: Divider set correctly? (Read WDOGCONTROL bits [1:0])
- **Check**: Counter actually loaded? (Read WDOGLOAD to verify)

**Issue**: Writes to WDOGLOAD ignored
- **Solution**: Unlock device first: `WDOGLOCK.write(0x1ACCE551)`
- **Verify**: Read WDOGLOCK, should return 0 when unlocked

**Issue**: Interrupt not firing
- **Check**: WDOGCONTROL.INTEN = 1?
- **Check**: Counter reached zero? (Read WDOGVALUE)
- **Check**: Interrupt signal connected?

**Issue**: Reset firing unexpectedly
- **Check**: Was interrupt cleared in time? (Read WDOGRIS)
- **Check**: WDOGCONTROL.RESEN = 1?
- **Solution**: Clear interrupt before second timeout

---

## Integration with QSP-x86

### Adding to QSP Target Script

```python
# File: targets/qsp-x86/watchdog-qsp-system.simics

# Load standard QSP configuration
run-command-file "%simics%/targets/qsp-x86/qsp-system.simics"

# Create watchdog timer
$wdt = (create-watchdog-timer name = system_watchdog)

# Map to I/O address space (example: 0xFEE00000)
$system.mb.sb.lpc_bus.map[0xFEE00000] = $wdt 0 4096

# Connect to PIC (use unused IRQ line)
connect $wdt.irq_dev $system.mb.nb.nb_pic.irq[11]

# Connect reset to system reset
connect $wdt.rst_dev $system.mb.reset_sink

# Enable in BIOS or bootloader
# (Software must configure watchdog registers)
```

### BIOS/Bootloader Configuration Example

```c
/* C code to configure watchdog from BIOS */
#define WDT_BASE         0xFEE00000
#define WDOGLOAD         (*(volatile uint32_t *)(WDT_BASE + 0x000))
#define WDOGCONTROL      (*(volatile uint32_t *)(WDT_BASE + 0x008))
#define WDOGLOCK         (*(volatile uint32_t *)(WDT_BASE + 0xC00))

void init_watchdog(uint32_t timeout_ms) {
    /* Unlock registers */
    WDOGLOCK = 0x1ACCE551;
    
    /* Enable interrupt and reset, divider=16 */
    WDOGCONTROL = 0x3 | (1 << 2);
    
    /* Calculate timeout (assuming 1GHz clock) */
    uint32_t cycles = timeout_ms * 1000000 / 16;
    WDOGLOAD = cycles;
    
    /* Lock registers */
    WDOGLOCK = 0;
}

void kick_watchdog(void) {
    WDOGLOCK = 0x1ACCE551;
    WDOGLOAD = WDOGLOAD;  /* Reload current value */
    WDOGLOCK = 0;
}
```

---

## Performance Considerations

### Efficient Counter Reading

```python
# GOOD: Read counter only when needed
def check_timeout_imminent(wdt, threshold):
    WDOGVALUE = dev_util.Register_LE(wdt.bank.regs, 0x004, size=4)
    return WDOGVALUE.read() < threshold

# BAD: Polling counter in tight loop
# (Simics handles this efficiently, but avoid in real hardware)
while WDOGVALUE.read() > 0:
    pass  # Busy wait
```

### Event Scheduling Efficiency

The DML implementation uses event-based timeouts:
- Counter value calculated on-demand (no continuous updates)
- Events scheduled only when counter loaded
- No CPU overhead during countdown (event-driven)

This is efficient even for large timeout values (e.g., 0xFFFFFFFF cycles).

---

## Next Steps

After completing this quickstart:

1. **Read Full Contracts**: Review `contracts/` directory for detailed behavior specs
2. **Examine Data Model**: Study `data-model.md` for register details
3. **Implement Device**: Follow tasks in `tasks.md` (generated by /tasks command)
4. **Write Tests**: Start with basic tests, then edge cases
5. **Integration Testing**: Test with QSP-x86 platform and guest OS

---

## Additional Resources

### Documentation
- Simics Base 7.57 User Guide: `/path/to/simics/doc/simics-user-guide/`
- DML 1.4 Reference Manual: `/path/to/simics/doc/dml-reference-manual/`
- ARM SP805 Watchdog Specification: (see hardware spec)

### MCP Tools
- `mcp_simics-mcp-se_perform_rag_query`: Search Simics documentation
- `mcp_simics-mcp-se_build_simics_project`: Build device module
- `mcp_simics-mcp-se_run_simics_test`: Run test suites

### Community
- Simics Forum: https://www.intel.com/content/www/us/en/developer/tools/simics-simulator/overview.html
- Internal Wiki: (if applicable)

---

## Troubleshooting

### Build Errors
```bash
# Clean build
make clean
make

# Verbose build
make VERBOSE=1

# Check DML syntax
./bin/dmlc --check modules/watchdog-timer/watchdog-timer.dml
```

### Runtime Errors
```python
# Enable Simics logging
simics.SIM_log_level(wdt, 2, simics.Sim_Log_Info)

# Check object attributes
print(dir(wdt))
print(wdt.attr.classname)

# Verify memory mapping
mem_obj.attr.map  # Should show watchdog device mapping
```

### Test Failures
```bash
# Run single test with full output
./bin/test-runner -vv tests/watchdog/failing_test.py

# Check test logs
cat test_output.log

# Run in debugger
gdb --args ./bin/simics -no-gui -batch test_script.simics
```

---

**Questions or Issues?** Refer to contracts and data model documents, or consult Simics documentation.
