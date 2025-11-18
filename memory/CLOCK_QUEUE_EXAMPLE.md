# Simics Device Clock Queue Configuration - Test Example

## Overview

In Intel Simics, **simple devices** (devices that use time events) require a **clock source** to drive their simulation timing. This clock is set via the device's `queue` attribute. Without a properly configured queue, attempting to post time events will fail with the error:

```
The 'queue' attribute is not set, cannot post event
```

## Clock Queue Concepts

### What is a Clock Queue?

A **clock queue** is a time management mechanism in Simics that:
- Drives the progression of simulation time for devices
- Allows devices to schedule and execute time-based events
- Provides timing synchronization across the simulated system

### Types of Clock Sources

Any Simics object that implements the clock interface can serve as a queue:

1. **Dedicated Clock Devices** (`clock` class)
   - Explicitly created clock objects
   - Configured with specific frequency (e.g., `freq_mhz=1`)
   - Used in simple unit tests

2. **System Clocks**
   - Crystal oscillator (XTAL) clocks
   - TSC (Time Stamp Counter) clocks
   - Platform-level clock generators

3. **CPU Models**
   - Can act as clock sources
   - Provide time progression based on instruction execution

### Default Clock Allocation

**Important**: By default, Simics will automatically allocate the **first available clock device** in the system to all simple devices that don't have their `queue` attribute explicitly set.

- **In unit tests**: Usually no default clock exists, so you must create one
- **In integration tests**: System-level clocks may exist and be auto-assigned
- **Best practice**: Explicitly set the queue to avoid ambiguity

---

## Test Case Example: Watchdog Timer

### Test File: `s-watchdog.py`

This test demonstrates the **critical role of clock queue configuration** for a watchdog timer device that posts time events.

### The Problem

The watchdog timer device (`demo_watchdog`) needs to post timer events when enabled. The relevant code in `demo_watchdog.dml` includes:

```dml
event wdt_timer is simple_time_event {
    method event() {
        tick_watchdog();
    }
}

method tick_watchdog() {
    if (!wdt_enabled) return;
    
    if (wdt_counter > 0) {
        wdt_counter -= 1;
    }
    
    // ... timeout handling ...
    
    // Schedule next tick - THIS REQUIRES A QUEUE
    if (wdt_enabled) {
        wdt_timer.post(1.0 / wdt_tick_frequency);  // ← Fails without queue!
    }
}
```

When `WDOGCONTROL` register is written to enable the timer (bit 0 = INTEN), the device attempts to post a timer event. **Without a clock queue, this fails immediately.**

### Test Failure Log

```log
TEST 4: Enable Timer Side Effect
----------------------------------------------------------------------
Setting INTEN bit (bit 0) in WDOGCONTROL...
[wdt.bank.watchdog_memap info] WDOGCONTROL: simple write with 0xffffffff enabled. 0x00000000 -> 0x00000001
*** Unhandled Python exception:
[wdt error] The 'queue' attribute is not set, cannot post event
[wdt.bank.watchdog_memap info] Watchdog timer enabled
*** Python script 'modules/demo_watchdog/test/s-watchdog.py' failed
```

### The Solution: Create and Assign a Clock

**Lines 32-33 in `s-watchdog.py`** (currently commented out):

```python
# clk = simics.SIM_create_object('clock', 'clk', freq_mhz=1)
# wdt.queue = clk
```

**With these lines enabled:**

```python
# Create a clock with 1 MHz frequency
clk = simics.SIM_create_object('clock', 'clk', freq_mhz=1)

# Assign the clock to the watchdog's queue attribute
wdt.queue = clk
```

### Complete Test Setup (Fixed)

```python
#!/usr/bin/env python
"""
Watchdog Timer Side Effects Test
This script demonstrates all the side effects implemented in demo_watchdog.dml
"""

import dev_util
import stest

stest.untrap_log('spec-viol')
stest.untrap_log('unimpl')

print("=" * 70)
print("Watchdog Timer Side Effects Test")
print("=" * 70)

# Step 1: Create the watchdog device
wdt = SIM_create_object('demo_watchdog', 'wdt')

# Step 2: Create a clock source (CRITICAL FOR TIME EVENTS)
clk = SIM_create_object('clock', 'clk', freq_mhz=1)

# Step 3: Assign the clock to the device's queue attribute
wdt.queue = clk

# Step 4: Enable verbose logging
wdt.cli_cmds.log_level(level=4, _r=True)

# Step 5: Get register handles
bank = dev_util.bank_regs(wdt.bank.watchdog_memap)
WDOGCONTROL = bank.WDOGCONTROL

# Now this works - timer events can be posted!
print("Enabling timer...")
WDOGCONTROL.write(0x01)  # ✓ SUCCESS - queue is configured

print("Advancing simulation time...")
SIM_continue(1000)  # Timer events execute properly
```

### Test Results Comparison

| Configuration | Result |
|---------------|--------|
| **Without clock queue** | ❌ `FAIL: The 'queue' attribute is not set, cannot post event` |
| **With clock queue** | ✅ `PASS: Timer enabled, events posted successfully` |

---

## Integration Test Scenarios

### Scenario 1: Simple Unit Test (Explicit Clock Required)

```python
# No system clocks exist - must create one
wdt = SIM_create_object('demo_watchdog', 'wdt')
clk = SIM_create_object('clock', 'clk', freq_mhz=1)
wdt.queue = clk  # REQUIRED
```

### Scenario 2: Complex Integration Test (System Clock Available)

```python
# Assuming a platform with existing clocks
cpu = SIM_create_object('x86-core', 'cpu0')
wdt = SIM_create_object('demo_watchdog', 'wdt')

# Option A: Use CPU as clock source
wdt.queue = cpu

# Option B: Use platform XTAL clock
xtal = SIM_get_object('xtal_clock')
wdt.queue = xtal

# Option C: Let Simics auto-assign the first clock (may be unpredictable)
# wdt.queue remains unset - Simics uses first available clock
```

### Scenario 3: Multiple Devices Sharing a Clock

```python
# Create one global clock
global_clk = SIM_create_object('clock', 'system_clock', freq_mhz=100)

# Share across multiple devices
wdt1 = SIM_create_object('demo_watchdog', 'wdt1')
wdt1.queue = global_clk

wdt2 = SIM_create_object('demo_watchdog', 'wdt2')
wdt2.queue = global_clk

timer = SIM_create_object('timer_device', 'timer0')
timer.queue = global_clk
```

---

## Best Practices

### ✅ DO

1. **Explicitly set `queue` in unit tests**
   ```python
   clk = SIM_create_object('clock', 'clk', freq_mhz=1)
   device.queue = clk
   ```

2. **Document clock requirements** in test files
   ```python
   # This device requires a clock queue for timer events
   ```

3. **Create clock before posting events**
   ```python
   # CORRECT ORDER:
   device = SIM_create_object('my_device', 'dev')
   clk = SIM_create_object('clock', 'clk', freq_mhz=1)
   device.queue = clk  # Set before enabling timers
   device.enable_timer()
   ```

4. **Use appropriate clock frequency**
   ```python
   # Match device requirements
   slow_clk = SIM_create_object('clock', 'rtc', freq_mhz=0.032768)  # 32.768 kHz RTC
   fast_clk = SIM_create_object('clock', 'cpu_clk', freq_mhz=3000)  # 3 GHz CPU
   ```

### ❌ DON'T

1. **Don't assume default clock exists**
   ```python
   # BAD - may fail in unit tests
   device = SIM_create_object('my_device', 'dev')
   # Missing: device.queue = ...
   device.enable_timer()  # ← CRASH!
   ```

2. **Don't post events without queue**
   ```dml
   // In DML code - check queue before posting
   if (dev.queue != NULL) {
       timer_event.post(delay);
   } else {
       log error: "Cannot post event - no queue configured";
   }
   ```

3. **Don't mix incompatible clock domains** without proper handling
   ```python
   # RISKY - devices may expect synchronized timing
   dev1.queue = clk_100mhz
   dev2.queue = clk_50mhz  # Different frequency - be careful!
   ```

---

## Troubleshooting

### Error: "The 'queue' attribute is not set, cannot post event"

**Cause**: Device is trying to schedule a time event without a configured clock queue.

**Solution**:
```python
# Before running the test
clk = SIM_create_object('clock', 'clk', freq_mhz=1)
device.queue = clk
```

### Error: "Attribute 'queue' not found"

**Cause**: Device doesn't support time events (not a simple device).

**Solution**: Check if device actually needs a queue. Not all devices require timing.

### Warning: Events not executing

**Cause**: Clock frequency may be misconfigured.

**Solution**:
```python
# Check clock configuration
print(f"Clock frequency: {clk.freq_mhz} MHz")
print(f"Device queue: {device.queue}")

# Verify time is advancing
SIM_continue(1000)  # Run simulation
```

---

## Summary

The **clock queue** is essential for Simics devices that use time-based events:

| Aspect | Description |
|--------|-------------|
| **Purpose** | Provides simulation time progression for devices |
| **Requirement** | Mandatory for devices posting time events |
| **Configuration** | Set via `device.queue = clock_object` |
| **Unit Tests** | Must explicitly create and assign clock |
| **Integration Tests** | May use system clocks or CPU as queue |
| **Default Behavior** | Simics auto-assigns first available clock (if any) |

**Key Takeaway**: Always create and assign a clock queue in unit tests to avoid the `'queue' attribute is not set` error, as demonstrated in the watchdog timer test case.

---

## References

- **Test File**: `/home/coder/ai_agents/tests/wdt_test_ipxact/modules/demo_watchdog/test/s-watchdog.py`
- **Device Implementation**: `/home/coder/ai_agents/tests/wdt_test_ipxact/modules/demo_watchdog/demo_watchdog.dml`
- **Test Log**: `/home/coder/ai_agents/tests/wdt_test_ipxact/test.log`
- **Simics Documentation**: "Time and Events in Simics" (Model Builder User's Guide)
