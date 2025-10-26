# DML 1.4 (Device Modeling Language) Grammar Reference for AI

## Overview

This document provides a comprehensive grammar specification for the Device Modeling Language (DML) 1.4 used in Intel Simics. DML is used to model hardware devices for simulation.

## Language Characteristics

- **Version**: DML 1.4
- **Purpose**: Hardware device modeling for Simics simulator
- **Paradigm**: Declarative with imperative elements
- **Type System**: Static typing with C-like type declarations
- **Compilation**: Compiles to C code that interfaces with Simics API
- **File Extension**: `.dml`

## Lexical Elements

### Keywords

```
device, template, is, import, header, footer, loggroup, constant
extern, typedef, sizeof, typeof, sizeoftype, cast, new, delete
if, else, while, do, for, switch, case, default, break, continue
goto, return, try, catch, throw, throws, nothrow
log, assert, error, after, foreach, select, each, in, where
defined, undefined, this, auto, then
register, field, bank, group, port, attribute, connect, interface
event, implement, subdevice, method, inline, size, bitorder
session, local, static
param, saved, async, await, with, shared, stringify, export, as
independent, startup, memoized, hook, provisional
```

### Operators

#### Arithmetic
```
+  -  *  /  %  ++  --
```

#### Bitwise
```
&  |  ^  ~  <<  >>
```

#### Logical
```
&&  ||  !
```

#### Comparison
```
==  !=  <  >  <=  >=
```

#### Assignment
```
=  +=  -=  *=  /=  %=  &=  |=  ^=  <<=  >>=
```

#### Special
```
?:      # Ternary conditional
#?#:    # Compile-time conditional
.       # Member access
->      # Pointer member access
[]      # Array/bit indexing
()      # Function call/grouping
```

### Literals

#### Integer Literals
```
123         # Decimal
0x1A2B      # Hexadecimal
0b1010      # Binary
```

#### Floating Point
```
3.14
1.0e-5
```

#### String Literals
```
"hello"
"multi" + "part"    # String concatenation
```

#### Character Literals
```
'a'
'\n'
```

#### Boolean
```
true
false
```

### Comments
```
// Single line comment
/* Multi-line
   comment */
```

## Grammar Structure

### Top-Level Structure

```
dml_file ::= 
    [provisional_declaration]
    [device_declaration]
    [bitorder_declaration]
    device_statement*

provisional_declaration ::=
    "provisional" identifier_list ";"

device_declaration ::=
    "device" identifier ";"

bitorder_declaration ::=
    "bitorder" ("be" | "le") ";"
```

### Device Statements

```
device_statement ::=
    | template_definition
    | object_declaration
    | parameter_declaration
    | method_declaration
    | is_template_statement
    | conditional_statement
    | error_statement
    | in_each_statement
    | header_block
    | footer_block
    | loggroup_declaration
    | constant_declaration
    | extern_declaration
    | typedef_declaration
    | import_statement
    | export_statement
```

### Template Definition

```
template_definition ::=
    "template" identifier ["is" template_list] "{" template_statement* "}"

template_list ::=
    | identifier
    | "(" identifier_list ")"

template_statement ::=
    | object_declaration
    | parameter_declaration
    | method_declaration
    | shared_method_declaration
    | shared_hook_declaration
    | is_template_statement
    | conditional_statement
```

### Object Declarations

```
object_declaration ::=
    | register_declaration
    | field_declaration
    | bank_declaration
    | group_declaration
    | port_declaration
    | attribute_declaration
    | connect_declaration
    | interface_declaration
    | event_declaration
    | implement_declaration
    | subdevice_declaration
    | session_declaration
    | saved_declaration
    | hook_declaration

register_declaration ::=
    "register" identifier array_spec* size_spec offset_spec 
    ["is" template_list] object_body

field_declaration ::=
    "field" identifier array_spec* bitrange_spec
    ["is" template_list] object_body

bank_declaration ::=
    "bank" identifier array_spec* ["is" template_list] object_body

group_declaration ::=
    "group" identifier array_spec* ["is" template_list] object_body

port_declaration ::=
    "port" identifier array_spec* ["is" template_list] object_body

attribute_declaration ::=
    "attribute" identifier array_spec* ["is" template_list] object_body

connect_declaration ::=
    "connect" identifier array_spec* ["is" template_list] object_body

interface_declaration ::=
    "interface" identifier array_spec* ["is" template_list] object_body

event_declaration ::=
    "event" identifier array_spec* ["is" template_list] object_body

implement_declaration ::=
    "implement" identifier array_spec* ["is" template_list] object_body

subdevice_declaration ::=
    "subdevice" identifier array_spec* ["is" template_list] object_body

array_spec ::=
    "[" identifier "<" expression "]"
    | "[" identifier "<" "..." "]"

size_spec ::=
    "size" expression
    | <empty>

offset_spec ::=
    "@" expression
    | <empty>

bitrange_spec ::=
    "@" "[" expression "]"
    | "@" "[" expression ":" expression "]"
    | <empty>

object_body ::=
    [description] ";"
    | [description] "{" object_statement* "}"

description ::=
    string_literal
    | description "+" string_literal
```

### Data Declarations

```
session_declaration ::=
    "session" c_declaration ";"
    | "session" c_declaration "=" initializer ";"
    | "session" "(" c_declaration_list ")" ";"
    | "session" "(" c_declaration_list ")" "=" initializer ";"

saved_declaration ::=
    "saved" c_declaration ";"
    | "saved" c_declaration "=" initializer ";"
    | "saved" "(" c_declaration_list ")" ";"
    | "saved" "(" c_declaration_list ")" "=" initializer ";"

hook_declaration ::=
    "hook" "(" c_declaration_list ")" identifier array_spec* ";"
```

### Parameter Declarations

```
parameter_declaration ::=
    "param" identifier param_spec
    | "param" identifier "auto" ";"
    | "param" identifier ":" param_spec
    | "param" identifier ":" type_declaration param_spec

param_spec ::=
    ";"
    | "=" expression ";"
    | "default" expression ";"
```

### Method Declarations

```
method_declaration ::=
    method_qualifiers "method" identifier method_params ["default"] compound_statement
    | "inline" "method" identifier method_params ["default"] compound_statement

method_qualifiers ::=
    <empty>
    | "independent"
    | "independent" "startup"
    | "independent" "startup" "memoized"

shared_method_declaration ::=
    "shared" method_qualifiers "method" identifier method_params ";"
    | "shared" method_qualifiers "method" identifier method_params "default" compound_statement
    | "shared" method_qualifiers "method" identifier method_params compound_statement

method_params ::=
    "(" [c_declaration_list] ")" [output_params] [throws_spec]

output_params ::=
    "->" "(" c_declaration_list ")"

throws_spec ::=
    "throws"
    | <empty>
```

### Type System

```
type_declaration ::=
    ["const"] base_type pointer_spec

base_type ::=
    | type_identifier
    | struct_type
    | layout_type
    | bitfields_type
    | typeof_expression
    | sequence_type
    | hook_type

type_identifier ::=
    identifier
    | "char" | "int" | "short" | "long" | "float" | "double"
    | "signed" | "unsigned" | "void"

struct_type ::=
    "struct" "{" struct_member* "}"

struct_member ::=
    c_declaration ";"

layout_type ::=
    "layout" string_literal "{" layout_member* "}"

layout_member ::=
    c_declaration ";"

bitfields_type ::=
    "bitfields" integer_literal "{" bitfield_member* "}"

bitfield_member ::=
    c_declaration "@" "[" bitfield_range "]" ";"

bitfield_range ::=
    expression
    | expression ":" expression

sequence_type ::=
    "sequence" "(" type_identifier ")"

hook_type ::=
    "hook" "(" c_declaration_list ")"

typeof_expression ::=
    "typeof" expression

pointer_spec ::=
    <empty>
    | "*" ["const"] pointer_spec
    | "vect" pointer_spec
```

### C Declarations

```
c_declaration ::=
    ["const"] base_type declarator

declarator ::=
    identifier
    | <empty>
    | declarator "[" expression "]"
    | declarator "(" c_declaration_list_opt_ellipsis ")"
    | "(" declarator ")"
    | "*" ["const"] declarator
    | "vect" declarator

c_declaration_list ::=
    <empty>
    | c_declaration
    | c_declaration_list "," c_declaration

c_declaration_list_opt_ellipsis ::=
    c_declaration_list
    | c_declaration_list "," "..."
    | "..."
```

### Expressions

```
expression ::=
    # Literals
    | integer_literal
    | hex_literal
    | binary_literal
    | float_literal
    | char_literal
    | string_literal
    | "true" | "false"
    | "undefined"
    
    # Identifiers
    | identifier
    | "this"
    | "default"
    
    # Unary operators
    | "+" expression
    | "-" expression
    | "!" expression
    | "~" expression
    | "&" expression
    | "*" expression
    | "++" expression
    | "--" expression
    | expression "++"
    | expression "--"
    | "sizeof" expression
    | "sizeoftype" type_declaration
    | "defined" expression
    | "typeof" expression
    
    # Binary operators
    | expression "+" expression
    | expression "-" expression
    | expression "*" expression
    | expression "/" expression
    | expression "%" expression
    | expression "<<" expression
    | expression ">>" expression
    | expression "<" expression
    | expression ">" expression
    | expression "<=" expression
    | expression ">=" expression
    | expression "==" expression
    | expression "!=" expression
    | expression "&" expression
    | expression "|" expression
    | expression "^" expression
    | expression "&&" expression
    | expression "||" expression
    
    # Ternary
    | expression "?" expression ":" expression
    | expression "#?" expression "#:" expression  # Compile-time conditional
    
    # Member access
    | expression "." identifier
    | expression "->" identifier
    
    # Array/bit access
    | expression "[" expression "]"
    | expression "[" expression "," identifier "]"  # With endianness
    | expression "[" expression ":" expression "]"  # Bit slice
    | expression "[" expression ":" expression "," identifier "]"  # Bit slice with endianness
    
    # Function call
    | expression "(" ")"
    | expression "(" expression_list ")"
    | expression "(" expression_list "," ")"
    
    # Type operations
    | "cast" "(" expression "," type_declaration ")"
    | "new" type_declaration
    | "new" type_declaration "[" expression "]"
    
    # Array literal
    | "[" expression_list "]"
    
    # Each expression
    | "each" identifier "in" "(" expression ")"
    
    # Grouping
    | "(" expression ")"

expression_list ::=
    <empty>
    | expression
    | expression_list "," expression
```

### Statements

```
statement ::=
    | compound_statement
    | expression_statement
    | declaration_statement
    | assignment_statement
    | if_statement
    | while_statement
    | do_while_statement
    | for_statement
    | switch_statement
    | try_catch_statement
    | log_statement
    | assert_statement
    | after_statement
    | foreach_statement
    | select_statement
    | goto_statement
    | break_statement
    | continue_statement
    | return_statement
    | throw_statement
    | delete_statement
    | error_statement
    | warning_statement
    | empty_statement

compound_statement ::=
    "{" statement* "}"

expression_statement ::=
    expression ";"

declaration_statement ::=
    local_declaration ";"

local_declaration ::=
    ("local" | "session" | "saved") c_declaration ["=" initializer]
    | ("local" | "session" | "saved") "(" c_declaration_list ")" ["=" initializer]

assignment_statement ::=
    expression "=" expression ";"
    | expression "=" initializer ";"
    | tuple_literal "=" initializer ";"
    | expression "+=" expression ";"
    | expression "-=" expression ";"
    | expression "*=" expression ";"
    | expression "/=" expression ";"
    | expression "%=" expression ";"
    | expression "&=" expression ";"
    | expression "|=" expression ";"
    | expression "^=" expression ";"
    | expression "<<=" expression ";"
    | expression ">>=" expression ";"

tuple_literal ::=
    "(" expression "," expression_list ")"

if_statement ::=
    "if" "(" expression ")" statement
    | "if" "(" expression ")" statement "else" statement
    | "#if" "(" expression ")" statement
    | "#if" "(" expression ")" statement "#else" statement

while_statement ::=
    "while" "(" expression ")" statement

do_while_statement ::=
    "do" statement "while" "(" expression ")" ";"

for_statement ::=
    "for" "(" for_init ";" [expression] ";" for_post ")" statement

for_init ::=
    <empty>
    | local_declaration
    | assignment_statement
    | expression

for_post ::=
    <empty>
    | for_post_item
    | for_post "," for_post_item

for_post_item ::=
    assignment_statement
    | expression

switch_statement ::=
    "switch" "(" expression ")" "{" switch_case* "}"

switch_case ::=
    | statement
    | "case" expression ":"
    | "default" ":"
    | "#if" "(" expression ")" "{" switch_case* "}"
    | "#if" "(" expression ")" "{" switch_case* "}" "#else" "{" switch_case* "}"

try_catch_statement ::=
    "try" statement "catch" statement

log_statement ::=
    "log" log_kind "," log_level "," expression ":" string_literal log_args ";"
    | "log" log_kind "," log_level ":" string_literal log_args ";"
    | "log" log_kind ":" string_literal log_args ";"

log_kind ::=
    identifier
    | "error"

log_level ::=
    expression
    | expression "then" expression

log_args ::=
    <empty>
    | log_args "," expression

assert_statement ::=
    "assert" expression ";"

after_statement ::=
    "after" expression identifier ":" expression ";"
    | "after" expression "->" "(" identifier_list ")" ":" expression ";"
    | "after" expression "->" identifier ":" expression ";"
    | "after" expression ":" expression ";"
    | "after" ":" expression ";"

foreach_statement ::=
    "foreach" identifier "in" "(" expression ")" statement
    | "#foreach" identifier "in" "(" expression ")" statement

select_statement ::=
    "#select" identifier "in" "(" expression ")" "where" "(" expression ")" statement "else" statement

goto_statement ::=
    "goto" identifier ";"

break_statement ::=
    "break" ";"

continue_statement ::=
    "continue" ";"

return_statement ::=
    "return" ";"
    | "return" initializer ";"

throw_statement ::=
    "throw" ";"

delete_statement ::=
    "delete" expression ";"

error_statement ::=
    "error" ";"
    | "error" string_literal ";"

warning_statement ::=
    "_warning" string_literal ";"

empty_statement ::=
    ";"
```

### Initializers

```
initializer ::=
    | single_initializer
    | "(" single_initializer "," single_initializer_list ")"

single_initializer ::=
    | expression
    | "{" single_initializer_list "}"
    | "{" single_initializer_list "," "}"
    | "{" designated_initializer_list "}"
    | "{" designated_initializer_list "," "}"
    | "{" designated_initializer_list "," "..." "}"

single_initializer_list ::=
    single_initializer
    | single_initializer_list "," single_initializer

designated_initializer ::=
    "." identifier "=" single_initializer

designated_initializer_list ::=
    designated_initializer
    | designated_initializer_list "," designated_initializer
```

### Conditional Compilation

```
conditional_statement ::=
    "#if" "(" expression ")" "{" statement* "}"
    | "#if" "(" expression ")" "{" statement* "}" "#else" "{" statement* "}"
    | "#if" "(" expression ")" "{" statement* "}" "#else" conditional_statement

in_each_statement ::=
    "in" "each" template_list "{" object_statement* "}"
```

### Import and Export

```
import_statement ::=
    "import" string_literal ";"

export_statement ::=
    "export" expression "as" expression ";"
```

### Header and Footer Blocks

```
header_block ::=
    "header" "%{" c_code "}%"
    | "_header" "%{" c_code "}%"

footer_block ::=
    "footer" "%{" c_code "}%"
```

### Other Top-Level Declarations

```
loggroup_declaration ::=
    "loggroup" identifier ";"

constant_declaration ::=
    "constant" identifier "=" expression ";"

extern_declaration ::=
    "extern" c_declaration ";"

typedef_declaration ::=
    "typedef" c_declaration ";"
    | "extern" "typedef" c_declaration ";"
```

## Operator Precedence (Highest to Lowest)

1. **160** - Postfix: `a[k]`, `f(...)`, `.`, `->`, `i++`, `i--` (Left associative)
2. **150** - Prefix: `++i`, `--i`, `sizeof`, `~`, `!`, `-i`, `+i`, `&`, `*p`, `new`, `delete` (Right associative)
3. **140** - Cast: `cast(expr, type)` (Right associative)
4. **130** - Multiplicative: `*`, `/`, `%` (Left associative)
5. **120** - Additive: `+`, `-` (Left associative)
6. **110** - Shift: `<<`, `>>` (Left associative)
7. **100** - Relational: `<`, `<=`, `>`, `>=` (Left associative)
8. **90** - Equality: `==`, `!=` (Left associative)
9. **80** - Bitwise AND: `&` (Left associative)
10. **70** - Bitwise XOR: `^` (Left associative)
11. **60** - Bitwise OR: `|` (Left associative)
12. **50** - Logical AND: `&&` (Left associative)
13. **40** - Logical OR: `||` (Left associative)
14. **30** - Conditional: `?:`, `#?#:` (Right associative)
15. **20** - Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `<<=`, `>>=`, `&=`, `^=`, `|=` (Right associative)

## Semantic Rules

### Device Structure

1. A DML file must contain at most one `device` declaration
2. The `device` declaration, if present, must appear before any object declarations
3. Templates can be defined at the top level and inherited using `is` clauses
4. Objects form a hierarchical tree structure

### Object Hierarchy

```
device
├── bank
│   ├── register
│   │   └── field
│   └── group
├── port
│   └── implement
├── attribute
├── connect
├── event
└── subdevice
```

### Type System Rules

1. DML uses C-compatible types with extensions
2. `session` data persists across checkpoints
3. `saved` data is serialized in checkpoints
4. `local` variables are function-scoped
5. Parameters can be compile-time constants or runtime values

### Method Rules

1. Methods can be `inline` (always inlined) or regular
2. `independent` methods have no side effects on device state
3. `startup` methods run during device initialization
4. `memoized` methods cache their results
5. `shared` methods are defined in templates and can be overridden
6. Methods can `throw` exceptions using the `throws` keyword

### Template System

1. Templates define reusable object patterns
2. Objects inherit from templates using `is` clauses
3. Multiple inheritance is supported
4. Parameters in templates can have default values
5. `in each` iterates over template instantiations

### Compile-Time vs Runtime

1. `#if`, `#else`, `#foreach`, `#select` are compile-time constructs
2. `if`, `else`, `foreach` are runtime constructs
3. `#?#:` is compile-time conditional, `?:` is runtime conditional
4. Parameters can be evaluated at compile-time or runtime depending on context

## Common Patterns

### Register Definition
```dml
bank regs {
    register status size 4 @ 0x00 {
        field ready @ [0];
        field error @ [1];
    }
}
```

### Method with Parameters
```dml
method read(uint64 offset, uint32 size) -> (uint64 value) {
    value = this.data[offset];
}
```

### Template Usage
```dml
template my_register {
    param size = 4;
    method after_write(uint64 value) {
        log info: "Written: %d", value;
    }
}

register ctrl @ 0x00 is (my_register) {
    param size = 8;  // Override
}
```

### Conditional Compilation
```dml
#if (defined(DEBUG)) {
    method debug_print() {
        log info: "Debug mode";
    }
}
```

## File Organization

Typical DML file structure:
```
1. Provisional declarations (optional)
2. Device declaration
3. Bitorder declaration (optional)
4. Import statements
5. Header blocks
6. Constant declarations
7. Type definitions
8. Template definitions
9. Object declarations (banks, registers, etc.)
10. Footer blocks
```

## Notes for AI Code Generation

1. **Indentation**: Use 4 spaces for indentation
2. **Naming**: Use snake_case for identifiers
3. **Comments**: Use `//` for single-line, `/* */` for multi-line
4. **String Concatenation**: Use `+` to concatenate string literals
5. **Bit Ranges**: Use `[msb:lsb]` notation, e.g., `[7:0]`
6. **Endianness**: Can be specified in bit slicing: `data[0:3, "le"]`
7. **Array Indexing**: Arrays use `[i]`, objects use `.member`
8. **Method Calls**: Use `this.method()` or `object.method()`
9. **Type Casting**: Use `cast(expr, type)` not C-style casts
10. **Error Handling**: Use `try`/`catch` for exceptions, `throws` in method signatures

## Compilation Process

1. **Lexical Analysis**: Tokenize DML source
2. **Parsing**: Build Abstract Syntax Tree (AST)
3. **Template Expansion**: Resolve template inheritance
4. **Type Checking**: Validate types and expressions
5. **Code Generation**: Generate C code for Simics API
6. **C Compilation**: Compile generated C to shared library

## API Versions

DML supports multiple Simics API versions specified via `--simics-api` flag:
- Different API versions may have different available features
- Compatibility features can be disabled with `--no-compat`
- Default API version is defined in the compiler

---

**Note**: This grammar specification is for DML 1.4 only. It is derived from the DML compiler implementation (dmlc) version 7.57.0 and the official DML 1.4 Reference Manual. DML 1.2 is not covered in this document.
