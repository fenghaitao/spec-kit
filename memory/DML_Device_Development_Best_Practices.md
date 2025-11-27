# DML Device Development Best Practices for Beginners

## Overview

This guide provides a comprehensive introduction to writing Device Modeling Language (DML) devices for the Simics simulation platform. It covers the essential syntax, common patterns, and best practices learned from solving compilation issues.

## Table of Contents

1. [Modeling in Simics](#modeling-in-simics)
2. [DML Compilation Setup](#dml-compilation-setup)
3. [Basic DML Syntax](#basic-dml-syntax)
4. [Device Structure](#device-structure)
5. [Common Patterns](#common-patterns)
6. [Compilation Issues and Solutions](#compilation-issues-and-solutions)
7. [Best Practices](#best-practices)
8. [Example Devices](#example-devices)

## Modeling in Simics

### Transaction-Level Device Modeling

In Transaction-Level Device Modeling (TLM), each interaction with a device, typically, a processor reading from or writing to the registers of the devices, is handled at once: the device is presented with a request, computes the reply, and returns it in a single function call. This is far more efficient and easier to program than modeling the details of how bits and bytes are moved across interconnects, cycle-by-cycle.

In general, immediate non-pipelined completion of an operation is sufficient for modeling device's behavior. When the device driver expects a delay, that delay must be modeled, however the specific action or activity that leads to the delay does not need to be modeled. A classic example is a device that uses a hardware interrupt to signal command completion. The driver expects to be able to run code to prepare for the interrupt after writing the command to the device. In a transactional model, the device model must include a delay between the completion of the command and the interrupt signaling the completion to the system. In this manner, the device local effects of a transaction are computed immediately, but notification of completion is deferred until the proper time has elapsed.

Transaction-level models are typically implemented using the DML tool. DML provides a C-like programming language designed specifically for this type of modeling. Although device models can be written directly in C, using DML reduces development time and makes the code more readable and maintainable, and reduces the risk of making errors.

### Simics High Level Modeling Approach

Simics models take a functional approach to modeling where entire transactions are handled in a single function.

- Models should focus on the what instead of the how.
  - Model details are optimized for the software that will run on those models. Details that are irrelevant to software execution do not need to be modeled.
  - Explicit pre-defined device states can be easily provided to the software.
- Models should be incrementally created to support different phases of the product development life cycle.
  - Initial model provides just enough emulation in order for the firmware team to begin their efforts.
- Functional models can be quickly created and connected together like building blocks.
  - The system configuration is separate from device models.

### Do Not Model Unnecessary Detail

It is easy to fall into the trap of modeling detailed aspects of the hardware that are invisible to the software. The overhead of modeling this detail can significantly slow the simulation. A trivial example is a counter that counts down on each clock cycle and interrupts when it gets to zero. An obvious way to model this is to model the counter register and decrement it on each clock cycle until it gets to zero. Simics will waste a lot of processing resources accurately maintaining the value of the counter. But this is not necessary. The counter is only visible to the software if it is explicitly read. A much better implementation is for the model to sleep until the appropriate time to interrupt arrives. If, in the meantime, the software reads the register then a calculation will need to be done to work out what would be in the register at that point. Since this probably happens rarely, if at all, the overhead of this is minimal.

A good Simics model implements the what and not the how of device functionality, timing of the hardware can also often be simplified to make more efficient and simple device models.

### Timing-Related Feature Modeling Best Practices

This document summarizes best practices for modeling timing-related features in Simics DML, based on analysis of the DML reference manual and real device implementations in the Simics packages.

#### 1. Core Timing Mechanisms in DML

- The `after` Statement

The `after` statement is the primary mechanism for scheduling delayed callbacks in DML.

**Syntax:**
```dml
// Time-based delay (seconds)
after delay s: callback_method();

// Cycle-based delay
after cycles_count cycles: callback_method();

// Immediate (next simulation step)
after: callback_method();
```

**Example from sample-timer-device:**
```dml
method update_event() {
    cancel_after();  // Cancel any pending callback

    if (step.val == 0)
        return;

    local cycles_t now = SIM_cycle_count(dev.obj);
    local cycles_t cycles_left =
        (reference.val - counter_start_value) * step.val
        - (now - counter_start_time);

    // Schedule callback after cycles_left cycles
    after cycles_left cycles: on_match();
}
```

- Event Objects

For more complex timing scenarios, use `event` objects with one of six templates:

| Template | Time Unit | Data |
|----------|-----------|------|
| `simple_time_event` | Seconds (double) | None |
| `simple_cycle_event` | Cycles (uint64) | None |
| `uint64_time_event` | Seconds (double) | uint64 |
| `uint64_cycle_event` | Cycles (uint64) | uint64 |
| `custom_time_event` | Seconds (double) | Custom (serializable) |
| `custom_cycle_event` | Cycles (uint64) | Custom (serializable) |

**Example from HPET:**
```dml
event tim_event is simple_time_event {
    method event() {
        regs.on_event();
    }
}

// Posting the event
method update_event() {
    if (event_tick.posted) {
        tim_event.remove();
    }

    local double delay = offs * COUNTER_CLK_PERIOD;
    tim_event.post(delay);
    event_tick.posted = true;
}
```

#### 2. Timer Counter Modeling Patterns

- Lazy Counter Evaluation (Recommended)

Instead of updating a counter every cycle, calculate the current value on-demand based on elapsed time.

**Pattern from sample-timer-device:**
```dml
bank regs {
    // Records the time when the counter was started
    saved cycles_t counter_start_time;
    // Records the start value of the counter
    saved cycles_t counter_start_value;

    register counter is (get, read, write) {
        param configuration = "none";  // Don't checkpoint raw value

        method get() -> (uint64) {
            if (step.val == 0) {
                return counter_start_value;  // Counter stopped
            }

            local cycles_t now = SIM_cycle_count(dev.obj);
            return (now - counter_start_time) / step.val
                + counter_start_value;
        }

        method write(uint64 value) {
            counter_start_value = value;
            restart();
        }

        method restart() {
            counter_start_time = SIM_cycle_count(dev.obj);
            update_event();
        }
    }
}
```

**Benefits:**
- No per-cycle overhead
- Accurate timing
- Efficient for high-frequency counters

- HPET Main Counter Pattern

For high-precision timers like HPET:

```dml
param COUNTER_CLK_PERIOD = 6.984127871e-8;  // ~14.318 MHz

attribute start_time is double_attr {
    param documentation = "Latest start time of the main counter";
}

register main_cnt {
    // Get running counter value
    method get_main_cnt() -> (uint64) {
        local uint64 value = this.val;
        if (gen_conf.enable_cnf.val != 0) {
            local double delta = SIM_time(dev.obj) - start_time.val + 1.0e-8;
            local uint64 cnt = cast(delta / COUNTER_CLK_PERIOD, uint64);
            value += cnt;
        }
        return value;
    }

    // Renormalize to maintain precision
    method renormalize_main_cnt() {
        this.val = get_main_cnt();
        start_time.val = SIM_time(dev.obj);
    }
}
```

#### 3. Countdown Timer / Watchdog Pattern

- Basic Countdown Timer

```dml
register countdown {
    saved cycles_t start_time;
    saved uint64 start_value;

    method get() -> (uint64) {
        if (!enabled.val)
            return start_value;

        local cycles_t elapsed = SIM_cycle_count(dev.obj) - start_time;
        local uint64 decremented = elapsed / prescaler.val;

        if (decremented >= start_value)
            return 0;  // Expired
        return start_value - decremented;
    }

    method write(uint64 value) {
        start_value = value;
        start_time = SIM_cycle_count(dev.obj);
        schedule_expiry();
    }

    method schedule_expiry() {
        cancel_after();
        if (enabled.val && start_value > 0) {
            local cycles_t cycles_to_zero = start_value * prescaler.val;
            after cycles_to_zero cycles: on_expired();
        }
    }

    method on_expired() {
        log info: "Countdown timer expired!";
        // Trigger interrupt, reset, etc.
        if (auto_reload.val) {
            start_value = reload_value.val;
            start_time = SIM_cycle_count(dev.obj);
            schedule_expiry();
        }
    }
}
```

- Watchdog Timer Pattern

```dml
event watchdog_event is simple_time_event {
    method event() {
        log error: "Watchdog timeout! System reset triggered.";
        // Trigger system reset
        reset_signal.signal.signal_raise();
    }
}

register watchdog_ctrl {
    field enable @ [0];
    field kick @ [1] is (write_1_clears);

    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);

        if (kick.val) {
            // Kick the watchdog - restart timeout
            kick.val = 0;
            restart_watchdog();
        }
    }
}

method restart_watchdog() {
    if (watchdog_event.posted())
        watchdog_event.remove();

    if (watchdog_ctrl.enable.val) {
        local double timeout = cast(timeout_value.val, double) / clock_freq;
        watchdog_event.post(timeout);
        log info, 4: "Watchdog restarted, timeout in %f seconds", timeout;
    }
}
```

#### 4. Timestamp Counter (TSC) Pattern

For modeling CPU timestamp counters that return different values at different simulation times:

```dml
// TSC-like counter that increments with CPU cycles
register tsc {
    param configuration = "none";  // Calculated, not checkpointed directly

    saved cycles_t tsc_base;      // Base value at last reset/write
    saved cycles_t tsc_base_time; // Cycle count when base was set

    method get() -> (uint64) {
        local cycles_t now = SIM_cycle_count(dev.obj);
        return tsc_base + (now - tsc_base_time);
    }

    method read() -> (uint64) {
        local uint64 value = get();
        log info, 4: "TSC read: 0x%x at cycle %d",
            value, SIM_cycle_count(dev.obj);
        return value;
    }

    method write(uint64 value) {
        tsc_base = value;
        tsc_base_time = SIM_cycle_count(dev.obj);
    }
}
```

- TSC with Frequency Scaling

```dml
param TSC_FREQ_MHZ = 2000.0;  // 2 GHz

register tsc {
    saved double tsc_base;
    saved double tsc_base_time;

    method get() -> (uint64) {
        local double now = SIM_time(dev.obj);
        local double elapsed = now - tsc_base_time;
        local uint64 ticks = cast(elapsed * TSC_FREQ_MHZ * 1e6, uint64);
        return cast(tsc_base, uint64) + ticks;
    }
}
```

#### 5. Periodic Timer Pattern

For timers that fire at regular intervals:

```dml
event periodic_timer is simple_time_event {
    method event() {
        // Handle timer tick
        on_timer_tick();

        // Reschedule for next period
        if (timer_enabled.val) {
            local double period = cast(period_reg.val, double) / clock_freq;
            this.post(period);
        }
    }
}

method start_periodic_timer() {
    if (periodic_timer.posted())
        periodic_timer.remove();

    local double period = cast(period_reg.val, double) / clock_freq;
    periodic_timer.post(period);
}

method stop_periodic_timer() {
    if (periodic_timer.posted())
        periodic_timer.remove();
}
```

#### 6. Comparator Match Pattern

For timers that trigger when counter matches a reference value:

```dml
// From HPET implementation
method comparator_match(int index) {
    // Update comparator for periodic interrupts
    local bool is_periodic = this.is_periodic(index);
    if (is_periodic) {
        local uint64 mask = get_mask(index);
        tim_comp[index].val += tim_period[index].val & mask;
    }

    // Set interrupt status for level interrupts
    local bool is_level = this.is_level(index);
    if (is_level) {
        if (gintr_sta.status.val[index] == 1)
            return;  // Already pending
        gintr_sta.status.val[index] = 1;
    }

    if (tim_conf[index].timer_intr_en_cnf.val == 1)
        send_interrupt(index);
}

method next_match_tick() -> (uint64) {
    local uint64 now = main_cnt.get_main_cnt();
    local uint64 offs = MAX64;

    for (int i = 0; i < num_of_timer; i++) {
        local uint64 diff = tim_comp[i].val - now;
        local uint64 mask = get_mask(i);
        diff &= mask;

        // Skip already handled matches
        if (cast(now + diff - handled_tick.val, int64) <= 0) {
            if (mask < offs)
                offs = mask + 1;
            continue;
        }

        if (diff < offs)
            offs = diff;
    }
    return now + offs;
}
```

#### 7. Best Practices Summary

- DO:

1. **Use lazy evaluation** for counters - calculate on read, not every cycle
2. **Use `saved` variables** for timing state that needs checkpointing
3. **Cancel pending events** before posting new ones
4. **Use appropriate time units** - cycles for CPU-bound, seconds for real-time
5. **Renormalize counters** periodically to maintain precision
6. **Handle counter overflow** correctly with proper masking
7. **Log timing events** at appropriate verbosity levels

- DON'T:

1. **Don't update counters every cycle** - use lazy evaluation
2. **Don't use `after` with stack-allocated data** - causes security issues
3. **Don't forget to cancel events** when disabling timers
4. **Don't mix time units** without explicit conversion
5. **Don't checkpoint calculated values** - checkpoint the base values instead

- Checkpointing Timing State

```dml
// GOOD: Checkpoint base values
saved cycles_t counter_start_time;
saved uint64 counter_start_value;

// BAD: Don't checkpoint calculated values
// register counter { param configuration = "optional"; }  // Wrong!

// GOOD: Use configuration = "none" for calculated registers
register counter {
    param configuration = "none";
    method get() -> (uint64) {
        // Calculate from saved base values
    }
}
```

#### 8. Common Timing Constants

```dml
// Common clock periods
param NS_PER_SECOND = 1e9;
param US_PER_SECOND = 1e6;
param MS_PER_SECOND = 1e3;

// HPET standard frequency (~14.318 MHz)
param HPET_FREQ_MHZ = 14.318179941;
param HPET_PERIOD = 1.0 / (HPET_FREQ_MHZ * 1e6);

// PIT frequency (1.193182 MHz)
param PIT_FREQ_MHZ = 1.193182;
param PIT_PERIOD = 1.0 / (PIT_FREQ_MHZ * 1e6);

// Convert cycles to time
method cycles_to_seconds(cycles_t cycles) -> (double) {
    return cast(cycles, double) / (clock_freq_mhz * 1e6);
}

// Convert time to cycles
method seconds_to_cycles(double seconds) -> (cycles_t) {
    return cast(seconds * clock_freq_mhz * 1e6, cycles_t);
}
```

#### 9. Quick Reference Card

| Task | Method |
|------|--------|
| Schedule callback in N cycles | `after N cycles: method()` |
| Schedule callback in N seconds | `after N s: method()` |
| Schedule immediate callback | `after: method()` |
| Cancel pending `after` | `cancel_after()` |
| Get current simulation time | `SIM_time(dev.obj)` |
| Get current cycle count | `SIM_cycle_count(dev.obj)` |
| Post event (time) | `event.post(delay_seconds)` |
| Post event (cycles) | `event.post(delay_cycles)` |
| Remove posted event | `event.remove()` |
| Check if event posted | `event.posted()` |
| Get time to next event | `event.next()` |

#### 10. Anti-Patterns to AVOID (For LLM Code Generation)

- ❌ Anti-Pattern 1: Clock Signal Modeling
```dml
// WRONG - Do NOT model clock signals!
connect clk {
    interface signal;
}
method clock_edge() {
    counter++;  // WRONG!
}
```

**Correct approach:** Use `SIM_cycle_count()` or `after` statements.

- ❌ Anti-Pattern 2: Cycle-Accurate Counter Updates
```dml
// WRONG - Do NOT update counters every cycle!
event tick is simple_cycle_event {
    method event() {
        counter.val++;
        this.post(1);  // Post for next cycle - WRONG!
    }
}
```

**Correct approach:** Lazy evaluation - calculate on read.

- ❌ Anti-Pattern 3: RTL-Style Sequential Logic
```dml
// WRONG - This is NOT Verilog!
session uint1 q;
session uint1 d;
method on_clock() {
    q = d;  // Flip-flop modeling - WRONG!
}
```

---

### Develop Device Models Using DML

The primary interface between software and the devices is the set of device registers. The method that many users have adapted when developing a new model is to work in an iterative fashion to determine the registers and functions that actually need to be implemented in a device in order to support software by testing the software with incomplete device models. DML and Simics support a number of techniques for efficiently exploring the needed functionality.

- Device: Each DML file mentioned in the module's Makefile defines a Simics class automatically. The class name is provide by the device statement at the beginning of the DML file.
    ```dml
    device my_device;
    ```

- Parameters: Parameters are mostly compile-time constant-valued object members. You can only set their value once. A parameter can be set to a value of any of the types integer, float, string, bool, list, reference or undefined. The type is automatically set from the value. To declare a parameter use the param keyword, in code you refer to parameters by directly by using their name
    ```dml
    param classname = "my_device";
    param desc = "This is my device";

    method print_info() {
        log info: "Device description: %s", desc;
    }
    ```

- Attributes: an attribute declaration, including name and type. If the type of the attribute is simple then using a built-in template is advised, this will setup the storage for the attribute and provide default set and get methods. When the data type of an attribute is more complex, the type parameter must be set, and the set and get methods must be provided.
    ```dml
    // A simple integer attribute with built-in storage and methods
    attribute counter is int64_attr {
        param documentation = "A sample counter attribute";
    }
    // A complex attribute with custom storage and methods
    attribute add_counter is write_only_attr {
        param documentation = "A sample pseudo attribute";
        param type = "i";

        method set(attr_value_t val) throws {
            counter.val += SIM_attr_integer(val);
        }
    }
    ```

- Bank and Registers: DML uses registers and banks to model hardware registers. Banks represent continuous address ranges containing registers. The registers are mapped in their banks with an offset and size. The default behavior of registers is to return the register's value when read and set the register's value when written. This behavior can be changed by overriding the write_register or read_register methods. A more simple way of modifying the behavior is to use the read or write templates, and then overriding the corresponding read or write methods.Real hardware registers often have a number of fields with separate meaning. Registers in Simics also support fields.
    ```dml
    bank regs {
        register r0 size 4 @ 0x0000;
        register r1 size 4 @ 0x0004;
        register r2 size 4 @ 0x0008;
    }

    //[...]
    bank regs {
        // customize read and write behavior with overriding read_register and write_register methods
        register r0 {
            method read_register(uint64 enabled_bytes, void *aux)-> (uint64) {
                log info: "Reading register r returns a constant";
                return 42;
            }

            method write_register(uint64 value, uint64 enabled_bytes, void *aux){
                log info: "Wrote register r";
                this.val = value;
            }
        }
        // or customize read and write behavior with read and write method
        register r1 is (read, write) {
            method read () -> (uint64) {
                log info: "Reading register r returns a constant";
                return 42;
            }

            method write (uint64 value) {
                log info: "Wrote register r";
                this.val = value;
            }
        }
        // register with fields, read and write behavior customized at field level
        register r2 {
            field status @ [0];
            field counter @ [4:1] is read {
                method read() -> (uint64) {
                    log info: "read from counter";
                    return default() + 1;
                }
            }
        }
    }
    ```

- Interfaces: nterfaces is the mechanism used in Simics when Simics objects, such as device models, need to communicate with each other. A DML device can both implement interfaces to provide additional services which other devices and objects can call, and call methods in interfaces implemented by other objects.
  - Using interfaces: Using an interface in a module implemented in DML, is done by connecting an object to the device model you are developing, specifying which interfaces you are planning to use.
    ```dml
    connect irq_dev {
        param documentation = "The device that interrupts are sent to.";
        param configuration = "required";
        interface signal;
    }

    method trigger_interrupt() {
        if (!irq_raised.val && irq_dev.obj) {
            log info, 3: "Raising interrupt";
            irq_dev.signal.signal_raise();
        }
    }
    ```
    To connect the created attribute set it to either a configuration object implementing the correct interfaces or a configuration object and the name of a port in that object which implements the interfaces.

    Here is a Python example how to do the connection to an object:
    ```python
    dev = SIM_create_object("my_device", "my_device_instance")
    intc = SIM_get_object("irq_device", "interrupt_controller")
    dev.irq_dev = intc

    # if the interrupt signal interface is implemented as a port
    # here is an example showing how to connect to a port named "input_levels"
    dev.irq_dev = (intc, "input_levels")
    ```

    - Implementing interfaces: Implementing an interface in DML is done with the implement declaration, which contains the implementation of all the functions listed in the interface. A device can use interface ports to have several implementations of the same interface. The ports have names that can be used to select the implementation when connecting to the device
    ```dml
    implement ethernet_common {
        // Called when a frame is received from the network.
        method frame(const frags_t *frame, eth_frame_crc_status_t crc_status) {
            if (crc_status == Eth_Frame_CRC_Mismatch) {
                log info, 2: "Bad CRC for received frame";
            }
            receive_packet(frame);
        }
    }

    port pin0 {
        implement signal {
            method signal_raise() {
                log info: "pin0 raised";
            }
            method signal_lower() {
                log info: "pin0 lowered";
            }
        }
    }
    port pin1 {
        implement signal {
            method signal_raise() {
                log info: "pin1 raised";
            }
            method signal_lower() {
                log info: "pin1 lowered";
            }
        }
    }
    ```

- Templates: Templates are a powerful tool when programming in DML. The code in a template can be used multiple times. A template can also implement other templates. Templates are commonly used on registers, but they can be used on all DML object types. Here is a simple template:
    ```dml
    template spam is write {
        method write(uint64 value) {
            log error: "spam, spam, spam, ...";
        }
    }

    bank regs {
        // [...]
        register A size 4 @ 0x0 is spam;
    ```

- Events: In a hardware simulation, it can often be useful to let something happen only after a certain amount of (simulated) time. This can be done in Simics by posting an event, which means that a callback function is placed in a queue, to be executed later in the simulation. The amount of simulated time before the event is triggered is usually specified in a number of seconds (as a floating-point number), but other units are possible, e.g. cycles, steps, defined through timebase parameter.
    ```dml
    dml 1.4;
    device sample_device;
    param documentation = "Timer example for Model Builder User's Guide";
    param desc = "example of timer";
    import "utility.dml";

    bank regs {
        register delay size 4 is unmapped;
        register r size 4 @ 0x0000 is write {
            method write(uint64 val) {
                this.val = 0;
                delay.val = val;
                ev.post(delay.val);
                log info: "Posted tick event";
            }
            event ev is simple_time_event {
                method event() {
                    r.val++;
                    log info: "Tick: %d.", r.val;
                    this.post(delay.val);
                }
            }
        }
    }
    ```
    - After: DML also provides a convenient shortcut with the after statement. An after statement is used to call a DML method some time in the future.
    ```dml
    method schedule_my_method() {
        // call my_method() after 10.5s
        after 10.5 s: my_method();
    }
    method hard_reset() {
        // cancel the scheduled call to my_method()
        cancel_after();
    }
    ```

- Methods: Methods are similar to C functions, but also have an implicit (invisible) parameter which allows them to refer to the current device instance, i.e., the Simics configuration object representing the device. Methods also support exception handling in DML, using try and throw.
    ```dml
    method m1() -> () {...}
    method m2(int a) -> () {...}
    method m3(int a, int b) -> (int) {
        return a + b;
    }
    method m4() -> (int, int) {
        ...;
        return (x, y);
    }
    method m5(int x) -> (int) throws {
        if (x < 0)
            throw;
        return x * x;
    }
    // calling methods
    typedef struct {
        int x;
        int y;
    } struct_t;

    method copy_struct(struct_t *tgt, struct_t src) {
        *tgt = src;
    }

    method m() {
        local struct_t s;
        copy_struct(&s, {1, 4});
        copy_struct(&s, {.y = 1, .x = 4});
        copy_struct(&s, {.y = 1, ...}); // Partial designated initializer
    }
    ```

- Session variables: A session declaration creates a number of named storage locations for arbitrary run-time values. The names belongs to the same namespace as objects and methods. A _saved_ declaration creates a named storage location for an arbitrary run-time value, and automatically creates an attribute that checkpoints this variable. Saved variables can be declared in object or statement scope, and the name will belong to the namespace of other declarations in that scope.
    ```dml
    // session declarations = initializer;
    session int id = 1;
    session bool active;
    session double table[4] = {0.1, 0.2, 0.4, 0.8};
    session (int x, int y) = (4, 3);
    session conf_object_t *obj;
    typedef struct { int x; struct { int i; int j; } y; } struct_t;
    session struct_t s = { .x = 1, .y = { .i = 2, .j = 3 } }

    // saved declarations = initializer;
    saved int id = 1;
    saved bool active;
    saved double table[4] = {0.1, 0.2, 0.4, 0.8};
    ```

---

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
**Last Updated**: Generated after solving DML compilation issues
**Tested With**: Simics 7.57.0, DML 1.4, API version 7
