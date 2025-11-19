# Simics Timer Implementation Guide

This guide demonstrates how to implement hardware timer functionality in Simics using DML (Device Modeling Language). The implementation is based on real-world examples from the codebase.

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Basic Implementation Flow](#basic-implementation-flow)
4. [Complete Code Example](#complete-code-example)
5. [Implementation Details](#implementation-details)

---

## Overview

A hardware timer in Simics typically involves:
- A **timer register** with control fields (enable, start, value)
- A **time event** that fires when the timer expires
- **Frequency conversion** between simulation time and timer cycles
- **Start time tracking** for calculating elapsed time

---

## Key Concepts

### 1. Simulation Time vs Timer Cycles
- **Simulation Time**: Absolute time in seconds returned by `SIM_time()`
- **Timer Cycles**: Hardware-specific count based on timer frequency
- **Conversion Formula**:
  ```
  cycles = simulation_time * frequency_hz
  simulation_time = cycles / frequency_hz
  ```

### 2. Timer Event Flow
```
Software Write → Start Timer → Post Event → Event Fires → Handle Timeout
     ↓              ↓              ↓             ↓              ↓
  Enable=1    Log start time  Calc timeout   Clear enable   Set status
```

### 3. Reading Elapsed Time
```
Current Time (SIM_time) - Start Time = Elapsed Simulation Time
Elapsed Simulation Time * Frequency = Elapsed Cycles
```

---

## Basic Implementation Flow

### Write Path (Starting Timer)
1. Software writes to timer control register
2. Check if enable/start bit is set
3. Record current simulation time
4. Calculate timeout in simulation seconds
5. Post/arm the timer event
6. Log the operation

### Read Path (Getting Elapsed Time)
1. Software reads timer value register
2. Get current simulation time with `SIM_time()`
3. Calculate elapsed time since start
4. Convert to cycles using frequency
5. Return remaining or elapsed cycles

### Event Handler (Timer Expiration)
1. Event fires at scheduled time
2. Clear enable/busy bit
3. Set interrupt/status flags
4. Execute any required actions

---

## Complete Code Example

```dml
// filepath: example-timer.dml
dml 1.4;

// Define log group for timer messages
loggroup timer_example;

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
        log info, 1, timer_example: "Timer expired at sim time %f", 
            SIM_time(dev.obj);
        
        // Optionally trigger an interrupt
        // interrupt_pin.signal_raise();
    }
    
    // Arm the timer with a timeout in simulation seconds
    method arm(double timeout_seconds) {
        local bool is_posted = posted();
        
        // If already posted, remove the old event
        if (is_posted) {
            remove();
            log info, 2, timer_example: "Removed previously posted timer";
        }
        
        // Post the new event
        post(timeout_seconds);
        log info, 2, timer_example: "Timer armed for %f seconds", timeout_seconds;
    }
    
    // Cancel the timer
    method cancel() {
        if (posted()) {
            remove();
            log info, 2, timer_example: "Timer cancelled";
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
// Timer Register Bank
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
                
                log info, 1, timer_example: 
                    "Timer started: %lld cycles (%f sec) at simtime %f",
                    timeout_cycles, timeout_seconds, timer_start_simtime;
            } 
            else {
                // Timer is being disabled - cancel the event
                timer_event.cancel();
                log info, 1, timer_example: "Timer stopped by software";
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
            log info, 2, timer_example: "Timer value configured: %lld cycles", 
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
            
            log info, 3, timer_example: 
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
                log info, 2, timer_example: "Timeout flag cleared";
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
            
            log info, 3, timer_example: 
                "Elapsed time: %f sec = %lld cycles",
                elapsed_simtime, elapsed_cycles;
            
            return elapsed_cycles;
        }
    }
}

// ============================================================================
// Additional Example: Absolute Target Timer
// ============================================================================

// This example shows a timer that uses an absolute target time
// (like the TSC100_TIMER in the reference code)

event absolute_timer_event is (simple_time_event) {
    method event() {
        timer_bank_abs.ABS_TIMER_CONTROL.Run_Busy.set(0);
        timer_bank_abs.ABS_TIMER_STATUS.Expired.set(1);
        log info, 1, timer_example: "Absolute timer expired";
    }
    
    method arm(double timeout) {
        if (posted())
            remove();
        post(timeout);
    }
}

bank timer_bank_abs is (timer_helper) {
    
    // Free-running counter register (like TSC_100)
    register FREE_RUNNING_COUNTER size 8 @ 0x00 is (timer_helper) {
        method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
            // Return current simulation time converted to cycles
            return get_current_cycles();
        }
    }
    
    // Absolute target timer
    register ABS_TIMER_CONTROL size 4 @ 0x10 {
        field Run_Busy @ [0] "Timer is running";
        field Reserved @ [31:1];
    }
    
    register ABS_TIMER_TARGET size 8 @ 0x14 {
        field Target_Cycles @ [63:0] "Absolute cycle count to trigger at";
        
        method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
            default(value, enabled_bytes, aux);
            
            // If timer is enabled, arm it with the new target
            if (ABS_TIMER_CONTROL.Run_Busy.val == 1) {
                local uint64 target_cycles = Target_Cycles.val;
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
                
                log info, 1, timer_example: 
                    "Absolute timer armed: target=%lld, current=%lld, delta=%lld cycles (%f sec)",
                    target_cycles, current_cycles, delta_cycles, timeout_seconds;
                
                // Arm the event
                absolute_timer_event.arm(timeout_seconds);
            }
        }
    }
    
    register ABS_TIMER_STATUS size 4 @ 0x1C {
        field Expired @ [0] "Timer has expired";
    }
}
```

---

## Implementation Details

### 1. Event Definition and Management

The timer event inherits from `simple_time_event`:

```dml
event timer_event is (simple_time_event) {
    method event() {
        // Called when timer expires
        // Clear running status, set flags, trigger interrupts
    }
    
    method arm(double timeout_seconds) {
        // Remove existing event if posted
        if (posted())
            remove();
        // Schedule new event
        post(timeout_seconds);
    }
}
```

**Key Points:**
- Check `posted()` before posting a new event to avoid multiple pending events
- Use `remove()` to cancel a posted event
- `post(seconds)` schedules the event relative to current simulation time

### 2. Tracking Start Time

**Critical for elapsed time calculation:**

```dml
saved double timer_start_simtime = 0.0;

// When timer starts:
timer_start_simtime = SIM_time(dev.obj);

// When reading elapsed time:
local double elapsed = SIM_time(dev.obj) - timer_start_simtime;
local uint64 elapsed_cycles = cast(elapsed * TIMER_FREQ_HZ, uint64);
```

### 3. Frequency Conversion

**Helper methods for clean conversion:**

```dml
method cycles_to_simtime(uint64 cycles) -> (double) {
    return cast(cycles, double) / frequency_hz;
}

method simtime_to_cycles(double simtime) -> (uint64) {
    return cast(simtime * frequency_hz, uint64);
}
```

### 4. Write Register Handler (Starting Timer)

```dml
method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
    default(value, enabled_bytes, aux);  // Update register fields
    
    if (Enable.val == 1) {
        // Get timeout from value register
        local uint64 timeout_cycles = TIMER_VALUE.Value.val;
        
        // Record start time
        timer_start_simtime = SIM_time(dev.obj);
        
        // Convert cycles to seconds
        local double timeout_seconds = cycles_to_simtime(timeout_cycles);
        
        // Arm the timer
        timer_event.arm(timeout_seconds);
    }
}
```

### 5. Read Register Handler (Getting Elapsed/Remaining Time)

```dml
method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
    if (TIMER_CONTROL.Enable.val == 0) {
        return default(enabled_bytes, aux);  // Return stored value
    }
    
    // Calculate elapsed time
    local double current_simtime = SIM_time(dev.obj);
    local double elapsed_simtime = current_simtime - timer_start_simtime;
    local uint64 elapsed_cycles = simtime_to_cycles(elapsed_simtime);
    
    // Calculate remaining
    local uint64 remaining = initial_value - elapsed_cycles;
    
    return remaining;
}
```

### 6. Absolute vs Relative Timers

**Relative Timer** (countdown):
- Software writes timeout duration
- Timer counts down from initial value
- Expires after duration elapses

**Absolute Timer** (target-based):
- Uses a free-running counter
- Software writes absolute target cycle count
- Timer expires when counter reaches target
- Example from reference code: `TSC100_TIMER`

```dml
// Calculate delta from current to target
local uint64 current = FREE_RUNNING_COUNTER.get();
local uint64 target = TARGET.val;
local uint64 delta = (target > current) ? (target - current) : 0;
local double timeout = cycles_to_simtime(delta);
timer_event.arm(timeout);
```

---

## Common Patterns and Best Practices

### 1. Always Check for Pending Events
```dml
if (timer_event.posted()) {
    timer_event.remove();
}
```

### 2. Use Saved Variables for State
```dml
saved double start_time;
saved uint64 target_cycles;
```

### 3. Validate Input Values
```dml
if (timeout_cycles == 0) {
    log error: "Invalid timeout value";
    return;
}
```

### 4. Log Important Operations
```dml
log info, 1, timer_example: "Timer started: %lld cycles (%f sec)",
    timeout_cycles, timeout_seconds;
```

### 5. Handle Edge Cases
- Zero timeout
- Timer already running (restart vs ignore)
- Reading while timer is not running
- Target time in the past (for absolute timers)

---

## Testing Your Timer Implementation

### Basic Test Sequence

1. **Configure Timer**
   ```
   Write TIMER_VALUE = 1000000  // 1M cycles at 100MHz = 10ms
   ```

2. **Start Timer**
   ```
   Write TIMER_CONTROL.Enable = 1
   ```

3. **Read During Countdown**
   ```
   Read TIMER_VALUE (should show decreasing value)
   Read TIMER_CURRENT (should show increasing elapsed)
   ```

4. **Wait for Expiration**
   ```
   Advance simulation by 10ms
   Read TIMER_STATUS.Timeout (should be 1)
   Read TIMER_CONTROL.Enable (should be 0)
   ```

### Simics CLI Test Commands
```python
# Create device and configure
$dev = (create-<your-device>)

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

---

## Summary

The key to implementing a timer in Simics:

1. **Use `simple_time_event`** for timer expiration callbacks
2. **Record `SIM_time()`** when timer starts for elapsed time calculation
3. **Convert between cycles and simulation time** using frequency
4. **Post events with simulation time** (seconds), not cycles
5. **Check and remove** pending events before posting new ones
6. **Calculate dynamically** when reading current/remaining values

This pattern provides accurate timer simulation that integrates properly with Simics' time management system.

