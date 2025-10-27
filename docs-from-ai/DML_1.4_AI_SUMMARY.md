# DML 1.4 Language Summary for AI Code Generation

## Overview
DML (Device Modeling Language) v1.4 is a domain-specific language for writing Simics device models. It combines C-like algorithmic constructs with object-oriented features for defining device structures and automatic Simics bindings.

## File Structure

### Required Declarations
```dml
dml 1.4;                    // Version declaration (must be first)
device device_name;         // Device declaration (main file only)
```

### Optional Global Declarations
```dml
bitorder le;                // or 'be' (default: le)
import "filename.dml";      // Import other DML files
loggroup group_name;        // Define log groups (max 63)
constant NAME = expr;       // Named constants
typedef struct {...} name;  // Type definitions
extern typedef ...;         // External C types
```

## Object Hierarchy

### Device (Top Level)
- Exactly one per model
- Contains banks, ports, subdevices, attributes, connects, events

### Banks
```dml
bank bank_name {
    param register_size = 4;        // Default register size
    param byte_order = "little-endian";  // or "big-endian"
    // Contains registers
}

bank bank_array[i < N] { ... }      // Bank arrays
```

### Registers
```dml
register reg_name size 4 @ 0x0100 {
    param offset = 0x0100;          // Address offset
    param size = 4;                 // Size in bytes (1-8)
    // Contains fields
}

register unmapped_reg is (unmapped);  // Not mapped to address
register regs[i < 16] size 2 @ 0x100 + 2*i;  // Register arrays
```

### Fields
```dml
field field_name @ [31:24] {        // Bit range [msb:lsb]
    // Field-specific behavior
}

field single_bit @ [7];             // Single bit field
```

### Groups
```dml
group group_name {
    // Neutral container for organizing objects
    // Can contain any objects parent can contain
}

group blocks[i < 8] { ... }         // Group arrays
```

### Ports
```dml
port port_name {
    // Contains implement objects for interfaces
}

port ports[i < N] { ... }           // Port arrays
```

### Subdevices
```dml
subdevice sub_name {
    // Distinct subsystem with own config object
    // Can contain banks, ports, attributes
}
```

### Attributes
```dml
attribute attr_name {
    param type = "i";               // Simics attribute type
    param configuration = "optional"; // or "required", "pseudo"
    method get() -> (attr_value_t) { ... }
    method set(attr_value_t val) throws { ... }
}

// Standard templates
attribute my_int is (int64_attr) {
    param init_val = 0;
}
```

### Connects
```dml
connect conn_name {
    param configuration = "optional";
    interface interface_name {
        param required = true;      // or false
    }
}
```

### Implements
```dml
implement interface_name {
    method interface_method(...) { ... }
}
```

### Events
```dml
event evt_name is (simple_time_event) {
    method event() {
        // Called when event triggers
    }
}

// Event types: simple_time_event, simple_cycle_event,
//              uint64_time_event, uint64_cycle_event,
//              custom_time_event, custom_cycle_event
```

## Templates

### Template Definition
```dml
template template_name {
    param param_name default value;
    session int session_var;
    saved uint64 saved_var;
    
    method method_name() default {
        // Overridable method
    }
    
    shared method shared_method() {
        // Shared across all instances
    }
}

template derived is base_template {
    // Inherits from base_template
}
```

### Template Usage
```dml
register r is (read, write) { ... }
register r {
    is read;
    is write;
}

in each register {
    // Applied to all registers in scope
    param size default 4;
}
```

### Common Templates
- `read`, `write` - Basic register access
- `read_only`, `write_only` - Restricted access
- `unimpl` - Unimplemented behavior
- `int64_attr`, `uint64_attr`, `bool_attr`, `double_attr` - Attribute types

## Parameters

### Parameter Declaration
```dml
param name;                         // Abstract (must be defined)
param name = value;                 // Assignment
param name default value;           // Default (overridable)
param name : type;                  // Typed (in templates)
param name : type = value;          // Combined (with explicit_param_decls)
param name := value;                // Inferred type (with explicit_param_decls)
```

### Special Parameters
- `offset` - Register address offset
- `size` - Register/field size
- `byte_order` - Endianness ("little-endian" or "big-endian")
- `configuration` - Attribute configuration ("optional", "required", "pseudo")
- `qname` - Qualified name (auto-generated)
- `desc` - Short description
- `documentation` - Detailed description

## Methods

### Method Declaration
```dml
method method_name() { ... }                    // No params, no return
method method_name(int x) { ... }               // With params
method method_name() -> (int) { ... }           // With return
method method_name(int x) -> (int, bool) { ... } // Multiple returns

method method_name() default { ... }            // Overridable
method method_name() throws { ... }             // Can throw exceptions

shared method shared_method() { ... }           // Shared implementation
independent method indep_method() { ... }       // No device instance
independent startup method startup() { ... }    // Called at model load
independent startup memoized method memo() -> (int) { ... } // Cached

inline method inline_method(inline int x) { ... } // Inline parameter
```

### Method Calls
```dml
method_name();                      // No return
local int x = method_name();        // Single return
(a, b) = method_name();             // Multiple returns
local int x = default();            // Call overridden method
obj.templates.template_name.method(); // Template-qualified call
```

## Data Types

### Integer Types
```dml
int1..int64, uint1..uint64          // Specific width integers
int, char                           // Aliases for int32, int8
bool                                // true/false
size_t, uintptr_t                   // Standard C types
```

### Endian Integer Types
```dml
int8_le_t, int8_be_t                // 8-bit endian integers
int16_le_t, int16_be_t              // 16-bit endian integers
int24_le_t, int24_be_t              // 24-bit endian integers
int32_le_t, int32_be_t              // 32-bit endian integers
int64_le_t, int64_be_t              // 64-bit endian integers
// Also uint* variants
```

### Other Types
```dml
double                              // Floating point
struct { ... }                      // Structures
layout "big-endian" { ... }         // Memory layouts
bitfields 32 { ... }                // Bit fields
template_name                       // Template types
hook(int, bool)                     // Hook reference types
```

### Serializable Types
Types that can be checkpointed:
- Primitive types (int, bool, double)
- Structs/layouts/arrays of serializable types
- Template types
- Hook reference types
- NOT pointers or extern structs

## Variables

### Session Variables
```dml
session int counter = 0;            // Per-device instance, not checkpointed
session (int x, int y) = (0, 0);    // Multiple declarations
```

### Saved Variables
```dml
saved uint64 state = 0;             // Per-device, checkpointed
saved bool flags[4] = {false, false, false, false};
```

### Local Variables
```dml
local int temp;                     // Function-local
local (int a, bool b) = (1, true);  // Multiple declarations
```

## Statements

### Control Flow
```dml
if (condition) { ... } else { ... }
while (condition) { ... }
for (init; condition; update) { ... }
switch (expr) { case val: ... }
break;
continue;
return;
return value;
return (val1, val2);                // Multiple returns
```

### Compile-Time Control
```dml
#if (const_condition) { ... } #else { ... }
#foreach x in ([1,2,3]) { ... }
#select x in ([1,2,3]) where (x > 1) { ... } #else { ... }
```

### DML-Specific Statements
```dml
// Assignment
x = value;
(x, y) = (a, b);                    // Simultaneous assignment

// Exception handling
try { ... } catch { ... }
throw;

// Logging
log info: "message";
log info, 2: "verbose message";
log error: "error: %d", errno;
log spec_viol, 1, (loggroup): "msg";

// Assertions
assert condition;

// Memory management
local int *ptr = new int;
local int *arr = new int[10];
delete ptr;

// After statements
after 0.1 s: callback();
after 100 cycles: callback();
after hook_ref -> (msg): callback(msg);
after: immediate_callback();

// Foreach
foreach item in (sequence) { ... }
#foreach item in ([1,2,3]) { ... }

// Error (compile-time)
error "compilation error message";
```

## Expressions

### Operators (C-like)
```dml
+, -, *, /, %                       // Arithmetic
<<, >>                              // Shift
&, |, ^, ~                          // Bitwise
==, !=, <, <=, >, >=                // Comparison
&&, ||, !                           // Logical
condition ? true_val : false_val    // Conditional
```

### DML-Specific Expressions
```dml
cast(expr, type)                    // Type cast
sizeof expr                         // Size of expression
sizeoftype type                     // Size of type
typeof(expr)                        // Type of expression

expr[7:0]                           // Bit slicing
expr[7:0, be]                       // Bit slicing with endianness
expr[3]                             // Single bit

defined expr                        // Check if defined
undefined                           // Undefined value

stringify(expr)                     // Convert to string
"str1" + "str2"                     // String concatenation

[1, 2, 3]                           // Compile-time list
list.len                            // List length
array.len                           // Array length

each template_name in (obj)         // Iterate objects with template

condition #? true_expr #: false_expr // Compile-time conditional

&method_name                        // Method as function pointer

new type                            // Allocate memory
new type[count]                     // Allocate array
```

## Hooks

### Hook Declaration
```dml
hook() hook_name;                   // No message data
hook(int) hook_name;                // Single message component
hook(int, bool) hook_name;          // Multiple components

shared hook(int) shared_hook;       // In templates
```

### Hook Usage
```dml
hook_name.send(msg);                // Asynchronous send
hook_name.send_now(msg);            // Synchronous send
local uint64 count = hook_name.suspended; // Count suspended computations

after hook_name -> (msg): callback(msg);  // Bind callback
```

## Common Patterns

### Simple Register
```dml
register reg size 4 @ 0x100 is (read, write);
```

### Register with Fields
```dml
register status size 4 @ 0x200 {
    field enable @ [0] is (read, write);
    field ready @ [1] is (read_only);
    field error @ [7:4] is (read, write);
}
```

### Custom Read/Write
```dml
register control size 4 @ 0x300 is (read, write) {
    method write(uint64 value) {
        default(value);
        if (value & 0x1) {
            // Trigger action
        }
    }
}
```

### Register Array
```dml
register data[i < 16] size 4 @ 0x400 + i*4 is (read, write);
```

### Attribute with Storage
```dml
attribute config is (uint64_attr) {
    param init_val = 0;
    param configuration = "optional";
}
```

### Event with Callback
```dml
event timer is (simple_time_event) {
    method event() {
        log info: "Timer fired";
        // Reschedule if needed
        this.post(1.0);
    }
}
```

### Interface Implementation
```dml
implement signal {
    method signal_raise() {
        log info: "Signal raised";
    }
}
```

## Best Practices

1. **Always declare language version**: `dml 1.4;`
2. **Use templates for reusable behavior**: Create templates for common patterns
3. **Prefer saved variables over unmapped registers**: For simple state storage
4. **Use typed parameters in templates**: For shared method access
5. **Document with desc and documentation params**: Aid readability
6. **Use explicit_param_decls**: Catch parameter typos
7. **Leverage standard library**: Import utility.dml and other standard modules
8. **Use groups for organization**: Structure complex banks
9. **Prefer independent methods for callbacks**: When device state not needed
10. **Use hooks for event notification**: Decouple components

## Common Imports
```dml
import "utility.dml";               // Standard utilities
import "simics/devs/signal.dml";    // Signal interface
import "simics/devs/ethernet.dml";  // Ethernet interfaces
```

## Error Handling
```dml
method risky_operation() throws {
    if (error_condition) {
        throw;
    }
}

method caller() {
    try {
        risky_operation();
    } catch {
        log error: "Operation failed";
    }
}
```

## Checkpointing
- Registers automatically checkpointed via `val` member
- Use `saved` variables for additional state
- Attributes with `configuration != "pseudo"` are checkpointed
- Session variables are NOT checkpointed

## Key Differences from C

1. **All arithmetic is 64-bit**: Truncated on assignment
2. **No implicit bool conversion**: Must use explicit comparisons
3. **Multiple return values**: `(a, b) = method();`
4. **No assignment expressions**: `x = y = 0;` OK, but not `if (x = 0)`
5. **Cast syntax**: `cast(expr, type)` not `(type)expr`
6. **Local keyword required**: `local int x;` not `int x;`
7. **Sizeof on types**: `sizeoftype type` not `sizeof(type)`
8. **Method references**: `&method` for function pointers
9. **Bit slicing**: `x[7:0]` extracts bits
10. **Compile-time evaluation**: `#if`, `#foreach`, `#select`
