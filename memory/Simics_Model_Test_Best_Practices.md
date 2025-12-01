# Simics Model Test Best Practices

## Overview

This document provides comprehensive best practices for writing Python-based tests for Simics device models. Testing is a critical part of device model development in Simics Model Builder, helping ensure correctness, catch regressions early, and maintain code quality throughout the development lifecycle.

## Structure of a Simics Device Model Test

### Test Suite Organization

A test suite for a Simics module is located in the `test/` directory within the module's source. The typical structure includes:

```
module-name/
├── test/
│   ├── SUITEINFO          # Marks directory as test suite (can be empty)
│   ├── README             # Human-readable description of test suite
│   ├── tests.py           # Optional: custom test generation logic
│   ├── common.py          # Shared definitions and helper functions
│   ├── s-test1.py         # Individual test file (auto-discovered)
│   ├── s-test2.py         # Individual test file
│   └── s-test3.py         # Individual test file
```

### Key Files

- **SUITEINFO**: Required file that identifies the directory as a test suite. Usually empty but can contain configuration parameters.

- **README**: Optional documentation describing the test suite, coverage, and any known omissions.

- **tests.py**: Optional file for custom test generation. If absent, the test system automatically creates a test for every `s-*.py` file.

- **s-*.py**: Test files following this naming pattern are automatically discovered and run in separate Simics processes.

- **common.py**: Shared code including configuration setup, fake object definitions, and helper functions.

## Core Testing Concepts

### 1. Test Configuration Setup

Tests should create minimal configurations containing only what's necessary:

```python
import simics
import conf
import dev_util
import stest

def create_config():
    # Create the device under test
    my_dev = simics.pre_conf_object('dev', 'my_device_class')

    # Configure required attributes
    my_dev.attr1 = 'value'
    my_dev.attr2 = 42

    # Add configuration to Simics
    simics.SIM_add_configuration([my_dev], None)

    # Return reference to configured object
    return conf.dev
```

### 2. Using Fake Objects

Instead of creating full system configurations, use fake objects to simulate the environment:

```python
import pyobj

# Create a fake interrupt controller
class FakePic(pyobj.ConfObject):
    class raised(pyobj.SimpleAttribute(0, 'i')):
        '''Attribute to store signal state'''

    # Implement the signal interface
    class signal(pyobj.Interface):
        def signal_raise(self):
            self._up.raised.val += 1

        def signal_lower(self):
            self._up.raised.val -= 1

# Use the fake object in configuration
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
my_dev = simics.pre_conf_object('dev', 'my_device_class')
my_dev.pic = fake_pic

simics.SIM_add_configuration([my_dev, fake_pic], None)

# Later in test: verify interrupt was raised
stest.expect_equal(conf.fake_pic.raised, 1, 'signal not raised')
```

### 3. Register Access Patterns

#### Using bank_regs (Recommended for Register Testing)

```python
import dev_util
from stest import expect_equal

# Create bank proxy for convenient register access
regs = dev_util.bank_regs(conf.dev.bank.regs)

# Write and read entire registers
regs.control.write(0xdeadbeef)
expect_equal(regs.control.read(), 0xdeadbeef)

# Read-modify-write with fields
regs.status.write(dev_util.READ, enable=1, mode=3)

# Read individual fields
expect_equal(regs.status.field.enable.read(), 1)
expect_equal(regs.status.field.mode.read(), 3)
```

#### Using Register_LE/BE (For Testing Endianness and Offsets)

```python
import dev_util

# Define register with explicit offset and endianness
control_reg = dev_util.Register_LE(
    conf.dev.bank.regs,  # bank
    0x00,                # offset
    size=4,
    bitfield=dev_util.Bitfield_LE({
        'enable': 31,
        'mode': (30, 28),
        'count': (15, 0)
    })
)

# Access register
control_reg.write(0x80000042)
expect_equal(control_reg.enable, 1)
expect_equal(control_reg.mode, 0)
expect_equal(control_reg.count, 0x42)

# Field write (implicit read-modify-write)
control_reg.enable = 0
control_reg.mode = 5
```

### 4. Memory and DMA Testing

#### Using dev_util.Memory

```python
import dev_util

# Create test memory
mem = dev_util.Memory()

# Configure device to use test memory
dma_dev = simics.pre_conf_object('dev', 'my_dma_device')
dma_dev.phys_mem = mem.obj
simics.SIM_add_configuration([dma_dev], None)

# Write test data to memory
test_data = tuple(range(256))
mem.write(0x1000, test_data)

# Trigger DMA operation
# ... device performs DMA ...

# Verify data was copied
expect_equal(mem.read(0x2000, 256), list(test_data))
```


#### Using dev_util.Layout for Descriptors

```python
import dev_util

# Define descriptor layout
desc = dev_util.Layout_LE(
    mem,           # Memory object
    0x1234,        # Address
    {
        'control': (0, 4),
        'address': (4, 4),
        'length': (8, 2),
        'status': (10, 2, dev_util.Bitfield_LE({
            'done': 15,
            'error': 14,
            'count': (7, 0)
        }))
    }
)

# Initialize descriptor
desc.control = 0x00000001
desc.address = 0xabcd0000
desc.length = 512
desc.status.write(0, done=0, error=0, count=0)

# After device processes descriptor
expect_equal(desc.status.done, 1)
expect_equal(desc.status.count, 512)
```

### 5. Interface Testing

#### Calling Interfaces on Devices

```python
# Call interface at device level
conf.dev.iface.signal.signal_raise()

# Call interface on a port
conf.dev.port.reset.iface.signal.signal_raise()
conf.dev.port.reset.iface.signal.signal_lower()
```

#### Testing Custom Transaction Atoms

```python
import simics

# Load module defining custom atom
simics.SIM_load_module('extended-id-atom')

# Create transaction with custom atom
txn = simics.transaction_t(
    size=4,
    write=True,
    value_le=0xdeadbeef,
    extended_id=3000
)

# Send transaction to device
exc = simics.SIM_issue_transaction(conf.dev.bank.regs, txn, 0x420)
```

### 6. Tracking Device Behavior

Use fake objects to record and verify device actions:

```python
class Test_state:
    def __init__(self):
        self.seq = []  # Record sequence of events
        self.memory = dev_util.Memory()

    def read_mem(self, addr, n):
        return self.memory.read(addr, n)

    def write_mem(self, addr, bytes):
        self.memory.write(addr, bytes)

# Fake object that records interface calls
class FakePhy(dev_util.Ieee_802_3_phy_v2):
    def send_frame(self, sim_obj, buf, replace_crc):
        test_state.seq.append(('send_frame', tuple(buf), replace_crc))
        return 0

    def check_tx_bandwidth(self, sim_obj):
        return 1

# Later: verify expected sequence
expect_equal(test_state.seq, [
    ('send_frame', expected_data, 1),
    ('raise', conf.dev, 0),
    ('clear', conf.dev, 0)
])
```


## Best Practices

### Test Coverage

1. **Comprehensive but Focused**: Cover all implemented functionality, but don't test unimplemented features.

2. **Document Omissions**: Clearly note any functionality not covered by tests in the README.

3. **Test Early**: Write tests before or during implementation to catch errors quickly.

### Test Speed

1. **Fast Execution**: Individual tests should complete in seconds, dominated by Simics startup time.

2. **Complete Suite**: All tests for a device should run in under 30 seconds.

3. **Clever Testing**: Cover maximum functionality in minimum time through smart test design.

### Test Organization

1. **Independent Subtests**: Put tests of independent features in separate files so they can fail/succeed independently.

2. **Shared Code**: Factor out common configuration and helper functions into `common.py`.

3. **Logical Grouping**: Group related small tests in the same file to reduce Simics startup overhead.

### Code Quality

1. **Clear Documentation**: Document what each test covers, both in README and as comments.

2. **Descriptive Names**: Use clear, descriptive names for test files and functions.

3. **Good Error Messages**: Provide informative messages when tests fail:

```python
stest.expect_equal(
    actual_value,
    expected_value,
    "Control register enable bit not set after initialization"
)
```

4. **Use Assertions**: Let `stest` functions raise exceptions automatically for clear tracebacks.

### Configuration Principles

1. **Minimal Setup**: Include only objects necessary for the test.

2. **Fake When Possible**: Use fake objects instead of real models to:
   - Verify interface usage
   - Reduce dependencies
   - Simplify configuration

3. **Real When Necessary**: Use real objects for:
   - Clock objects (for timing)
   - Image objects (for large data structures)
   - Objects that can't be faked in Python


## Common Testing Patterns

### Pattern 1: Simple Register Test

```python
from common import create_config, device_regs
from stest import expect_equal

dev = create_config()
regs = device_regs(dev)

# Test register read/write
regs.control.write(0x12345678)
expect_equal(regs.control.read(), 0x12345678)

# Test field access
regs.status.write(dev_util.READ, enable=1, mode=3)
expect_equal(regs.status.field.enable.read(), 1)
```

### Pattern 2: Interrupt Testing

```python
from common import create_config, FakePic
from stest import expect_equal

(dev, pic_state) = create_config()

# Trigger interrupt
# ... perform action that should raise interrupt ...

# Verify interrupt was raised
expect_equal(pic_state.raised, 1, "Interrupt not raised")
```

### Pattern 3: DMA Transfer Test

```python
from common import create_config
from stest import expect_equal
import dev_util

(dev, test_state) = create_config()

# Setup source data
src_addr = 0x1000
dst_addr = 0x2000
size = 256
test_data = tuple(range(size))
test_state.write_mem(src_addr, test_data)

# Configure and trigger DMA
# ... configure device registers ...

# Verify transfer
expect_equal(
    test_state.read_mem(dst_addr, size),
    list(test_data),
    "DMA transfer data mismatch"
)
```

### Pattern 4: Timing-Based Test

```python
from common import create_config
from stest import expect_equal
import simics

(dev, clk) = create_config()

# Record start time
start_cycle = simics.SIM_cycle_count(clk)

# Trigger timed operation
# ... configure device ...

# Advance time
simics.SIM_continue(1000)  # Run for 1000 cycles

# Verify timing
elapsed = simics.SIM_cycle_count(clk) - start_cycle
expect_equal(elapsed, 1000, "Unexpected cycle count")
```


## Helper Utilities

### Custom Assertion Functions

```python
def approx_equal(got, expected, tolerance):
    """Check equality with tolerance for timing variations"""
    if abs(got - expected) > tolerance:
        raise stest.fail(f"got {got}, expected {expected}")

def expect_in_range(value, min_val, max_val, msg=""):
    """Check value is within range"""
    if not (min_val <= value <= max_val):
        raise stest.fail(
            f"{msg}: {value} not in range [{min_val}, {max_val}]"
        )
```

### Struct Helper

```python
class Struct:
    """Simple struct for organizing related values"""
    def __init__(self, **kws):
        for (k, v) in list(kws.items()):
            setattr(self, k, v)

# Usage
regs = Struct(
    control=dev_util.Register_LE(dev.bank.regs, 0x00, 4),
    status=dev_util.Register_LE(dev.bank.regs, 0x04, 4),
    data=dev_util.Register_LE(dev.bank.regs, 0x08, 4)
)
```

## Example Test Suite Structure

```python
# common.py - Shared definitions
import simics
import conf
import dev_util
import pyobj

class FakePic(pyobj.ConfObject):
    # ... fake interrupt controller ...
    pass

def create_config():
    # ... create minimal test configuration ...
    return (conf.dev, fake_pic_state)

def device_regs(dev):
    # ... return struct with register proxies ...
    return Struct(...)

# s-basic.py - Basic functionality test
from common import *
from stest import expect_equal

(dev, pic) = create_config()
regs = device_regs(dev)

# Test basic register access
regs.control.write(0x1)
expect_equal(regs.control.read(), 0x1)

# s-interrupts.py - Interrupt functionality test
from common import *
from stest import expect_equal

(dev, pic) = create_config()

# ... trigger interrupt ...
expect_equal(pic.raised, 1, "Interrupt not raised")

# s-dma.py - DMA functionality test
from common import *
from stest import expect_equal
import dev_util

(dev, test_state) = create_config()

# ... test DMA transfers ...
```

## Conclusion

Effective testing is essential for reliable device models. By following these best practices:

- Write tests early and run them often
- Keep tests focused on the device under test
- Use fake objects to minimize dependencies
- Organize tests logically for maintainability
- Ensure tests run quickly to enable frequent execution
- Document test coverage and any omissions

These practices will help you develop robust, well-tested device models that are easier to maintain and extend over time.
