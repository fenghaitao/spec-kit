# IP-XACT Register Description XML Reference

## Purpose

This document provides XML templates and examples for generating IEEE 1685-2022 compliant IP-XACT register descriptions.

**Usage**: Reference this document when executing Step 4 of the `/specify` command workflow.

**Complete Workflow**: See `templates/commands/specify.md` for the full specification generation process.

**Quick Reference**:

- Access type mapping table: See Section 4.1 (also in specify.md Step 2.2)
- State machine documentation: See specify.md Step 2.4.6
- XML structure templates: Sections 1-5 below

---

## Document Structure

IP-XACT XML documents must follow this exact order:

1. **Component Identification** (required) - Document root with metadata
2. **Bus Interfaces** (optional) - If device has bus connectivity
3. **Memory Maps** (required) - Address blocks and register definitions
4. **Ports** (optional) - If device has I/O signals

---

### 1. Component Identification

**Purpose**: Document root element with metadata and namespace declarations.

**Required Fields**:

- `[VENDOR_NAME]`: Organization/company name (e.g., "ARM", "Intel", "MyCompany")
- `[LIBRARY_NAME]`: Library category (e.g., "AMBA_Devices", "Timers", "Controllers")
- `[IP_NAME]`: Device name from specification (e.g., "Watchdog_Timer", "UART", "GPIO")
- `[VERSION]`: Version string (e.g., "1.0", "2.0.1")

**XML Template**:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2022"
    xsi:schemaLocation="http://www.accellera.org/XMLSchema/IPXACT/1685-2022 http://www.accellera.org/XMLSchema/IPXACT/1685-2022/index.xsd">

    <ipxact:vendor>[VENDOR_NAME]</ipxact:vendor>
    <ipxact:library>[LIBRARY_NAME]</ipxact:library>
    <ipxact:name>[IP_NAME]</ipxact:name>
    <ipxact:version>[VERSION]</ipxact:version>

    <!-- Bus interfaces section (if applicable) -->
    <!-- Memory maps section (required) -->
    <!-- Ports section (if applicable) -->

</ipxact:component>
```

---

### 2. Bus Interfaces

**Purpose**: Define bus connectivity for memory-mapped register access.

**Required Fields**:

- `[BUS_TYPE]`: Protocol name (APB4, AXI4, AXI4-Lite, AHB, etc.)
- `[MEMORY_MAP_NAME]`: Reference to memory map name (defined in section 3)
- Role: "slave" for peripheral devices, "master" for DMA/bus masters

**Common Bus Types**:

- **APB**: `vendor="AMBA" library="AMBA4" name="APB4" version="r0p0"`
- **AXI4-Lite**: `vendor="AMBA" library="AMBA4" name="AXI4-Lite" version="r0p0"`
- **AXI4**: `vendor="AMBA" library="AMBA4" name="AXI4" version="r0p0"`

**XML Template** (APB slave example):
```xml
<ipxact:busInterfaces>
    <ipxact:busInterface>
        <ipxact:name>APB</ipxact:name>
        <ipxact:busType vendor="AMBA" library="AMBA4" name="APB4" version="r0p0"/>
        <ipxact:abstractionType vendor="AMBA" library="AMBA4" name="APB4" version="r0p0"/>
        <ipxact:slave>
            <ipxact:memoryMapRef memoryMapRef="[MEMORY_MAP_NAME]"/>
        </ipxact:slave>
    </ipxact:busInterface>
</ipxact:busInterfaces>
```

---

### 3. Memory Maps

**Purpose**: Define address space containing registers and fields.

**Required Fields**:
- `[MEMORY_MAP_NAME]`: Descriptive name (e.g., "RegisterMap", "ControlRegisters")
- `[BLOCK_NAME]`: Address block name (e.g., "MainBlock", "ControlBlock")
- `[BASE_ADDRESS]`: Starting address in hex (typically `0x0` for device-relative addressing)
- `[RANGE]`: Total address space size in hex (e.g., `0x1000` for 4KB)
- `[WIDTH]`: Data bus width in bits (typically `32`)

**Calculation Rules**:
- Range = (Highest Register Offset + Register Size) rounded up to next power of 2
- Width = Register size (8, 16, 32, or 64 bits)

**XML Template**:
```xml
<ipxact:memoryMaps>
    <ipxact:memoryMap>
        <ipxact:name>[MEMORY_MAP_NAME]</ipxact:name>
        <ipxact:addressBlock>
            <ipxact:name>[BLOCK_NAME]</ipxact:name>
            <ipxact:baseAddress>[BASE_ADDRESS]</ipxact:baseAddress>
            <ipxact:range>[RANGE]</ipxact:range>
            <ipxact:width>[WIDTH]</ipxact:width>

            <!-- Register definitions go here (see section 4) -->

        </ipxact:addressBlock>
    </ipxact:memoryMap>
</ipxact:memoryMaps>
```

**Example with calculated values**:
```xml
<ipxact:memoryMaps>
    <ipxact:memoryMap>
        <ipxact:name>WatchdogRegisters</ipxact:name>
        <ipxact:addressBlock>
            <ipxact:name>MainBlock</ipxact:name>
            <ipxact:baseAddress>0x0</ipxact:baseAddress>
            <ipxact:range>0x1000</ipxact:range>  <!-- 4KB address space -->
            <ipxact:width>32</ipxact:width>      <!-- 32-bit registers -->

            <!-- Register definitions... -->

        </ipxact:addressBlock>
    </ipxact:memoryMap>
</ipxact:memoryMaps>
```

---

### 4. Register Definitions

**Purpose**: Define individual registers with fields, access properties, and side-effects.

**Requirements**:
- Define registers in ascending order by `addressOffset`
- Include comprehensive `<ipxact:description>` with side-effects
- Nest ALL fields within their parent register
- Ensure fields don't overlap (validate bitOffset + bitWidth)

---

#### 4.1 Basic Register Structure

**Required Fields**:
- `[REGISTER_NAME]`: Register identifier in UPPERCASE (e.g., "CONTROL", "STATUS")
- `[ADDRESS_OFFSET]`: Hex offset from base address (e.g., "0x00", "0x04")
- `[SIZE]`: Register size in bits (8, 16, 32, or 64)
- `[ACCESS]`: Access type (see access type table)
- `[RESET_VALUE]`: Default value after reset in hex
- `[RESET_MASK]`: Bit mask for valid reset bits (typically "0xFFFFFFFF")
- `[VOLATILE]`: true for hardware-updated registers, false for control registers

**Access Type Reference**:
| Spec Term | IP-XACT Value | Meaning |
|-----------|---------------|---------|
| R/W, RW | `read-write` | Read and write access |
| R/O, RO | `read-only` | Read-only access |
| W/O, WO | `write-only` | Write-only access |
| W1C | `write-1-clear` | Write 1 to clear bit |
| RC | `read-clear` | Read clears bit |
| RS | `read-set` | Read sets bit |
| WS | `write-set` | Write sets bit |
| WC | `write-clear` | Write clears bit |

**XML Template**:
```xml
<ipxact:register>
    <ipxact:name>[REGISTER_NAME]</ipxact:name>
    <ipxact:description>[PURPOSE + READ_SIDE_EFFECTS + WRITE_SIDE_EFFECTS + DEPENDENCIES]</ipxact:description>
    <ipxact:addressOffset>[ADDRESS_OFFSET]</ipxact:addressOffset>
    <ipxact:size>[SIZE]</ipxact:size>
    <ipxact:access>[ACCESS]</ipxact:access>
    <ipxact:volatile>[true|false]</ipxact:volatile>
    <ipxact:reset>
        <ipxact:value>[RESET_VALUE]</ipxact:value>
        <ipxact:mask>[RESET_MASK]</ipxact:mask>
    </ipxact:reset>

    <!-- Field definitions go here (see section 4.2) -->

</ipxact:register>
```

**Example - Control Register**:
```xml
<ipxact:register>
    <ipxact:name>WDOGCONTROL</ipxact:name>
    <ipxact:description>Watchdog control register. Bit 0 (INTEN) enables interrupt generation. Bit 1 (RESEN) enables reset output. Writing this register when locked (WDOGLOCK != 0x1ACCE551) is ignored. Writing INTEN=1 reloads counter from WDOGLOAD.</ipxact:description>
    <ipxact:addressOffset>0x08</ipxact:addressOffset>
    <ipxact:size>32</ipxact:size>
    <ipxact:access>read-write</ipxact:access>
    <ipxact:volatile>false</ipxact:volatile>
    <ipxact:reset>
        <ipxact:value>0x00000000</ipxact:value>
        <ipxact:mask>0xFFFFFFFF</ipxact:mask>
    </ipxact:reset>

    <!-- Fields defined below -->

</ipxact:register>
```

---

#### 4.2 Field Definitions

**Purpose**: Define bit fields within registers with precise bit positions and behaviors.

**Required Fields**:
- `[FIELD_NAME]`: Field identifier (e.g., "ENABLE", "INTEN", "ERROR_FLAG")
- `[BIT_OFFSET]`: LSB position (e.g., bit [7:4] → bitOffset=4)
- `[BIT_WIDTH]`: Number of bits (e.g., bit [7:4] → bitWidth=4, bit [0] → bitWidth=1)
- `[FIELD_ACCESS]`: Field-level access type (can differ from register access)

**Bit Position Calculation**:
- For bit range `[MSB:LSB]`:
  - `bitOffset` = LSB (lower number)
  - `bitWidth` = MSB - LSB + 1
- Examples:
  - Bit [0]: bitOffset=0, bitWidth=1
  - Bits [7:4]: bitOffset=4, bitWidth=4
  - Bits [31:16]: bitOffset=16, bitWidth=16

**XML Template** (basic field):

```xml
<ipxact:field>
    <ipxact:name>[FIELD_NAME]</ipxact:name>
    <ipxact:description>[PURPOSE + SIDE_EFFECTS + CONDITIONS + CROSS_REGISTER_EFFECTS]</ipxact:description>
    <ipxact:bitOffset>[BIT_OFFSET]</ipxact:bitOffset>
    <ipxact:bitWidth>[BIT_WIDTH]</ipxact:bitWidth>
    <ipxact:access>[FIELD_ACCESS]</ipxact:access>
</ipxact:field>
```

---

#### 4.3 Field Examples by Behavior Type

**Example 1: Simple Control Bit**
```xml
<ipxact:field>
    <ipxact:name>ENABLE</ipxact:name>
    <ipxact:description>Timer enable control. Write 1 to start countdown from WDOGLOAD value. Write 0 to stop countdown. Transition 0→1 reloads counter. Write ignored if locked.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>read-write</ipxact:access>
</ipxact:field>
```

**Example 2: Write-1-to-Clear (W1C)**
```xml
<ipxact:field>
    <ipxact:name>IRQ_STATUS</ipxact:name>
    <ipxact:description>Interrupt pending flag. Write 1 to clear interrupt and deassert IRQ signal. Write 0 has no effect.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>write-1-clear</ipxact:access>
</ipxact:field>
```

**Example 3: Multi-Bit Field with Enumerated Values**
```xml
<ipxact:field>
    <ipxact:name>CLOCK_DIV</ipxact:name>
    <ipxact:description>Clock divider selection. Configures countdown rate based on input clock frequency.</ipxact:description>
    <ipxact:bitOffset>2</ipxact:bitOffset>
    <ipxact:bitWidth>3</ipxact:bitWidth>
    <ipxact:access>read-write</ipxact:access>
    <ipxact:enumeratedValues>
        <ipxact:enumeratedValue>
            <ipxact:name>DIV_1</ipxact:name>
            <ipxact:description>Clock division by 1</ipxact:description>
            <ipxact:value>0</ipxact:value>
        </ipxact:enumeratedValue>
        <ipxact:enumeratedValue>
            <ipxact:name>DIV_16</ipxact:name>
            <ipxact:description>Clock division by 16</ipxact:description>
            <ipxact:value>1</ipxact:value>
        </ipxact:enumeratedValue>
    </ipxact:enumeratedValues>
</ipxact:field>
```

---

### 5. Port Definitions

**Purpose**: Define I/O signals for device external connectivity.

**Required Fields**:
- `[PORT_NAME]`: Signal name (e.g., "clk", "rst_n", "irq", "data_out")
- `[DIRECTION]`: Signal direction (`in`, `out`, or `inout`)
- `[WIDTH]`: Bit width (1 for scalar, N for vector)
- `[TYPE_NAME]`: Wire type (`std_logic` for single bit, `std_logic_vector` for multi-bit)
- `[LEFT]`: MSB index for vectors (e.g., 7 for [7:0])
- `[RIGHT]`: LSB index for vectors (e.g., 0 for [7:0])

**Structure**: Wrap all port definitions in `<ipxact:ports>` container.

---

#### 5.1 Scalar Port (Single-Bit Signal)

**XML Template**:
```xml
<ipxact:port>
    <ipxact:name>[PORT_NAME]</ipxact:name>
    <ipxact:description>[Signal purpose and behavior]</ipxact:description>
    <ipxact:wire>
        <ipxact:direction>[in|out|inout]</ipxact:direction>
        <ipxact:wireTypeDefs>
            <ipxact:wireTypeDef>
                <ipxact:typeName>std_logic</ipxact:typeName>
            </ipxact:wireTypeDef>
        </ipxact:wireTypeDefs>
    </ipxact:wire>
</ipxact:port>
```

---

#### 5.2 Vector Port (Multi-Bit Signal)

**XML Template**:
```xml
<ipxact:port>
    <ipxact:name>[PORT_NAME]</ipxact:name>
    <ipxact:description>[Signal purpose and behavior]</ipxact:description>
    <ipxact:wire>
        <ipxact:direction>[in|out|inout]</ipxact:direction>
        <ipxact:vector>
            <ipxact:left>[LEFT]</ipxact:left>
            <ipxact:right>[RIGHT]</ipxact:right>
        </ipxact:vector>
        <ipxact:wireTypeDefs>
            <ipxact:wireTypeDef>
                <ipxact:typeName>std_logic_vector</ipxact:typeName>
            </ipxact:wireTypeDef>
        </ipxact:wireTypeDefs>
    </ipxact:wire>
</ipxact:port>
```

---

## Description Writing Guidelines

When filling `<ipxact:description>` fields in the XML, include comprehensive side-effect documentation:

### Register-Level Descriptions

Include: Functional purpose, read/write side-effects, cross-register dependencies, access constraints

**Example**:
```xml
<ipxact:description>
Watchdog control register. Bit 0 (INTEN) enables interrupt generation. Bit 1 (RESEN) enables reset output.
Writing this register when locked (WDOGLOCK != 0x1ACCE551) is ignored. Writing INTEN=1 reloads counter from WDOGLOAD.
</ipxact:description>
```

### Field-Level Descriptions

Include: Field purpose, field-specific side-effects (W1C, RC), conditions, cross-register effects

**Example**:
```xml
<ipxact:description>
Enable bit. Write 1 to start timer countdown from LOAD value. Write 0 to stop countdown.
Transition 0→1 triggers reload from LOAD. Write ignored if WDOGLOCK is locked.
</ipxact:description>
```

### Common Patterns

**Asymmetric Read/Write**: "Writing 0x1ACCE551 unlocks registers; other values lock. Read returns 1 if locked, 0 if unlocked."

**Multi-Stage Operations**: "Writing 1 to ENABLE triggers: (1) reloads counter, (2) starts countdown, (3) clears interrupts."

**Conditional Side-Effects**: "Copies value to COUNTER and restarts countdown IF CONTROL.ENABLE=1. Ignored when LOCK != 0x1ACCE551."

---

## XML Generation Checklist

**Reference**: See `templates/validation-checklist.md` Section 2 (XML Generation Checklist) for the complete checklist.

**Quick verification**:
- [ ] XML structure complete (all sections in correct order)
- [ ] All registers and fields from specification included
- [ ] All descriptions comprehensive with side-effects
- [ ] Cross-register dependencies documented bidirectionally
- [ ] All data accurate (no placeholders, correct addresses/sizes/access types)

Use validation-checklist.md for detailed validation before saving XML.

---

## Validation Rules

### Address Alignment

Register addresses must align based on their size:

- **8-bit registers**: Can be at any byte boundary (0x00, 0x01, 0x02...)
- **16-bit registers**: Must align to 2-byte boundaries (0x00, 0x02, 0x04...)
- **32-bit registers**: Must align to 4-byte boundaries (0x00, 0x04, 0x08...)
- **64-bit registers**: Must align to 8-byte boundaries (0x00, 0x08, 0x10...)

### Bit Field Overlap Validation

For each register, verify: `bitOffset + bitWidth ≤ register size` and no two fields occupy the same bit positions.

**Invalid Example** (overlap):
```
Register size: 32 bits
Field A: bitOffset=0, bitWidth=16  (covers bits 0-15)
Field B: bitOffset=8, bitWidth=16  (covers bits 8-23) ❌ OVERLAPS bits 8-15
```

**Valid Example** (no overlap):
```
Register size: 32 bits
Field A: bitOffset=0,  bitWidth=8   (covers bits 0-7)
Field B: bitOffset=8,  bitWidth=8   (covers bits 8-15)
Field C: bitOffset=16, bitWidth=16  (covers bits 16-31)
```

### Reset Value Range Validation

For each field, verify: `reset value < 2^bitWidth`

**Examples**:
- Field with bitWidth=1: Valid reset values are 0 or 1
- Field with bitWidth=3: Valid reset values are 0-7 (0b000 to 0b111)
- Field with bitWidth=8: Valid reset values are 0-255 (0x00 to 0xFF)
