# IP-XACT Register Description Generation Guide

## Task
Generate an IP-XACT 1685-2022 compliant register description for a hardware IP block based on the provided specification.
**Your mission**: Parse hardware specification → Extract register/field details → Extract register/field side-effects → Generate complete, valid IP-XACT 1685-2022 XML

## Output Format
- Single complete XML file
- IEEE 1685-2022 compliant
- Immediately usable in IP-XACT tools
- Starting with `<?xml` and ending with `</ipxact:component>`
- Include all necessary namespaces and schema locations
- No explanatory text before or after
- Use proper indentation for readability

## Instructions

Follow this complete workflow to generate IP-XACT XML with comprehensive side-effect documentation:

### Step 1: Extract Register Map and Layout

Parse the hardware specification to identify and extract:

**Address Block Information**:
- Address block name and base address (typically 0x0)
- Address range (calculate from highest register offset + size)
- Data width (default 32 bits unless specified)

**For EACH Register**:
- **Name**: Register identifier (preserve exact capitalization)
- **Address Offset**: Hexadecimal offset from base address (e.g., 0x00, 0x04, 0x10)
- **Size**: Register width in bits (default 32 if not specified)
- **Access Type**: Register-level access mode (RO, RW, WO, etc.)

**For EACH Bit Field within Each Register**:
- **Name**: Field identifier
- **Bit Range**: Position in register (e.g., [31:16], [7:4], [0])
  - Calculate **bitOffset** = LSB (lower bit number)
  - Calculate **bitWidth** = MSB - LSB + 1
- **Access Type**: Field access mode (RO, RW, WO, W1C, RC, etc.)
- **Reset Value**: Default value after reset (if specified)
- **Enumerated Values**: Named constants for field values (if defined)

### Step 2: Extract I/O Port/Signal Interfaces

Parse the hardware specification to identify and extract:

**Bus Interface Information**:
- **Bus Type**: Interface protocol (APB, AXI4, AXI4-Lite, Wishbone, etc.)
- **Role**: Master or Slave
- **Bus Parameters**: Data width, addressing mode, specific protocol details

**For EACH I/O Port/Signal**:
- **Name**: Port identifier (e.g., clk, rst_n, irq, data_out)
- **Direction**: Signal direction (in, out, inout)
- **Width**: Bit width (1 for scalar signals, N for vectors)
- **Type**: Signal type (clock, reset, interrupt, data, control, status)
- **Description**: Purpose and behavior of the port

### Step 3: Generate IP-XACT Register Description XML File

Generate the initial IP-XACT XML structure with all extracted information:

**3.1 Component Identification**:
- Use placeholders: `[VENDOR_NAME]`, `[LIBRARY_NAME]`, `[IP_NAME]`, `[VERSION]`
- Include proper namespaces and schema location

**3.2 Bus Interface** (if applicable):
- Determine bus type from specification (APB, AXI, etc.)
- Configure as slave or master
- Reference memory map

**3.3 Memory Map**:
- Create `<ipxact:memoryMap>` with extracted address block information
- Set base address (typically 0x0)
- Calculate range from highest register offset + size

**3.4 Register Definitions** (for EACH register):
- Define basic properties: name, offset, size, access type
- Add placeholder `<ipxact:description>` (will be filled in Step 5)
- Add reset value and mask (if specified)

**3.5 Field Definitions** (for EACH field in EACH register):
- Calculate bitOffset and bitWidth from bit range
- Set access type (map W1C → write-1-clear, RC → read-clear, etc.)
- Add placeholder `<ipxact:description>` (will be filled in Step 5)
- Add reset value (if specified)
- Add enumerated values (if defined)

**3.6 Port Definitions**:
- Extract I/O signals from Step 2
- Define direction (in/out/inout)
- Specify wire type and width

### Step 4: Identify Side-Effects

Analyze the functional behavior descriptions to identify read/write side-effects for both registers and fields. Document these for filling into the XML in Step 5.

**Register-to-Functionality Relationships**:
- Identify all hardware functionalities (timer, interrupt, DMA, etc.)
- Determine which registers control each functionality
- Document dependencies between registers
- Understand how registers work together to implement features

**Register Relationships and Cross-Dependencies**:

- **Lock/Protection Mechanisms**: If a register controls write access to others (e.g., WDOGLOCK):
  - Lock register description: "Writing 0x1ACCE551 unlocks all other registers for writing. Any other value locks them."
  - Protected register description: "Write is ignored if WDOGLOCK is locked."

- **Enable/Disable Dependencies**: If one register enables/disables others, document in all affected registers

- **Reload/Copy Operations**: If writing one register updates another (e.g., LOAD → VALUE):
  - Source: "Writing this register immediately copies value to TARGET register"
  - Target: "Value is updated when SOURCE register is written"

- **Clear/Set Relationships**: If one register clears/sets bits in another (e.g., INTCLR clears INTSTAT)

**Read Side-Effects** to document in description:
- Does reading change hardware state?
- Are status flags cleared on read? (e.g., "Reading clears ERROR flag")
- Are values computed dynamically?
- Any timing or ordering requirements?
- Dependencies on other register states?

**Write Side-Effects** to document in description:
- Hardware actions triggered (e.g., "Starting timer", "Asserting interrupt")
- Internal states modified (e.g., "Resets counter to 0")
- Signals asserted/deasserted (e.g., "Deasserts interrupt signal")
- Field-specific behaviors (e.g., "Write 1 enables interrupt generation")
- Register interactions (e.g., "Writing this copies value to COUNTER")
- Write conditions (e.g., "Write is ignored if locked", "Write 1 to clear")

**Field-Level Side-Effects**:
- Document field-specific behaviors when different from register-level
- Include bit-level semantics (W1C, enable/disable, state transitions)
- Note field value effects (e.g., "0=disabled, 1=enabled")
- Omit if field behavior is same as register-level

### Step 5: Fill Description Fields in XML File

Update the XML file generated in Step 3 by filling in the `<ipxact:description>` tags for all registers and fields with the side-effects identified in Step 4.

**For EACH Register** - Update `<ipxact:description>`:
- **CRITICAL**: Populate with comprehensive documentation including:
  - Functional purpose
  - Read side-effects (if any)
  - Write side-effects (if any)
  - Register relationships
  - Example: "Control register. Bit 0 enables timer. Writing 1 starts countdown. Write ignored if locked."

**For EACH Field** - Update `<ipxact:description>`:
- **CRITICAL**: Populate with detailed field-level documentation including:
  - Field purpose
  - Field-specific side-effects (W1C, read-to-clear, enable/disable)
  - Conditions (e.g., "ignored if locked", "write 1 to clear")
  - Cross-register effects (e.g., "copies to COUNTER")
  - Example: "Enable bit. Write 1 to start timer countdown from LOAD value. Write 0 to stop timer."

### Step 6: Validate Output

**Completeness Checks**:
- [ ] Every register has side-effects documented (or noted as "no side-effects")
- [ ] Every field with special behavior has it documented
- [ ] All register relationships documented in affected registers
- [ ] All addresses properly aligned
- [ ] No overlapping bit fields
- [ ] Reset values within valid ranges
- [ ] All XML tags properly closed
- [ ] Proper indentation used

**Quality Checks**:
- [ ] Descriptions are implementation-ready
- [ ] All cross-register dependencies bidirectionally documented
- [ ] Lock/enable mechanisms clearly explained
- [ ] W1C, RC, and other special access types documented

### Result

A complete, valid IP-XACT 1685-2022 XML file with comprehensive side-effect documentation in all description fields, ready for device simulation implementation.

## Required Components

This section provides XML templates for all required IP-XACT components. Use these as patterns to generate complete, valid XML output.

**Document Structure Order**:
1. Component Identification (required - document root)
2. Bus Interfaces (optional - if device has bus connectivity)
3. Memory Maps (required - contains address blocks and registers)
4. Ports (optional - if device has I/O signals)

**Key Generation Rules**:
- Replace ALL `[PLACEHOLDER]` values with actual extracted data
- Preserve exact XML structure and indentation
- Include xmlns declarations only in component root
- Close all tags properly
- Use consistent naming (UPPERCASE for registers/fields)

---

### 1. Component Identification

**Purpose**: Document root element with metadata and namespace declarations.

**When to use**: Always required as the outermost element.

**What to extract**:
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

**When to use**: Include if device connects via standard bus protocol (APB, AXI4, AXI4-Lite, AHB, Wishbone, etc.).

**What to extract** (from Step 2):
- `[BUS_TYPE]`: Protocol name (APB4, AXI4, AXI4-Lite, AHB, etc.)
- `[MEMORY_MAP_NAME]`: Reference to memory map name (defined in section 3)
- Role: "slave" for peripheral devices, "master" for DMA/bus masters

**Common Bus Types**:
- **APB (Advanced Peripheral Bus)**: `vendor="AMBA" library="AMBA4" name="APB4" version="r0p0"`
- **AXI4-Lite**: `vendor="AMBA" library="AMBA4" name="AXI4-Lite" version="r0p0"`
- **AXI4**: `vendor="AMBA" library="AMBA4" name="AXI4" version="r0p0"`

**XML Template** (APB slave example):
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

**When to use**: Always required - contains all register definitions.

**What to extract** (from Step 1):
- `[MEMORY_MAP_NAME]`: Descriptive name (e.g., "RegisterMap", "ControlRegisters")
- `[BLOCK_NAME]`: Address block name (e.g., "MainBlock", "ControlBlock")
- `[BASE_ADDRESS]`: Starting address in hex (typically `0x0` for device-relative addressing)
- `[RANGE]`: Total address space size in hex (e.g., `0x1000` for 4KB)
- `[WIDTH]`: Data bus width in bits (typically `32`)

**Calculation Rules**:
- Range = (Highest Register Offset + Register Size) rounded up to next power of 2
- Width = Register size (8, 16, 32, or 64 bits)

**XML Template**:
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

**When to use**: For EVERY register extracted in Step 1.

**Critical Requirements**:
- Define registers in order by ascending `addressOffset`
- Include comprehensive `<ipxact:description>` with side-effects (filled in Step 5)
- Nest ALL fields within their parent register
- Ensure fields don't overlap (validate bitOffset + bitWidth)

---

#### 4.1 Basic Register Structure

**What to extract** (from Step 1):
- `[REGISTER_NAME]`: Register identifier in UPPERCASE (e.g., "CONTROL", "STATUS", "WDOGLOAD")
- `[ADDRESS_OFFSET]`: Hex offset from base address (e.g., "0x00", "0x04", "0x10")
- `[SIZE]`: Register size in bits (8, 16, 32, or 64)
- `[ACCESS]`: Access type (see access type table below)
- `[RESET_VALUE]`: Default value after reset in hex (e.g., "0x00000000")
- `[RESET_MASK]`: Bit mask for valid reset bits (typically all 1s: "0xFFFFFFFF")

**Access Type Mapping**:
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

**Volatile Flag**:
- Set to `true` for registers that change without CPU writes (counters, status registers updated by hardware)
- Set to `false` for control registers that only change on writes

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

**When to use**: For EVERY bit field extracted in Step 1.

**What to extract** (from Step 1):
- `[FIELD_NAME]`: Field identifier (e.g., "ENABLE", "INTEN", "ERROR_FLAG")
- `[BIT_OFFSET]`: LSB position (e.g., bit [7:4] → bitOffset=4)
- `[BIT_WIDTH]`: Number of bits (e.g., bit [7:4] → bitWidth=4, bit [0] → bitWidth=1)
- `[FIELD_ACCESS]`: Field-level access type (can differ from register access)
- `[FIELD_RESET]`: Field's reset value (if different from register-level)

**Bit Position Calculation**:
- For bit range `[MSB:LSB]`:
  - `bitOffset` = LSB (lower number)
  - `bitWidth` = MSB - LSB + 1
- Examples:
  - Bit [0]: bitOffset=0, bitWidth=1
  - Bits [7:4]: bitOffset=4, bitWidth=4
  - Bits [31:16]: bitOffset=16, bitWidth=16

**Field Access Types**: Same as register access types (read-write, read-only, write-1-clear, etc.)

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

**Example 1: Simple Control Bit (Read/Write)**
```xml
<ipxact:field>
    <ipxact:name>ENABLE</ipxact:name>
    <ipxact:description>Timer enable control. Write 1 to start countdown from WDOGLOAD value. Write 0 to stop countdown. Transition 0→1 reloads counter. Write ignored if locked.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>read-write</ipxact:access>
</ipxact:field>
```

**Example 2: Status Bit (Read-Only)**
```xml
<ipxact:field>
    <ipxact:name>BUSY</ipxact:name>
    <ipxact:description>Device busy status. Returns 1 when operation in progress, 0 when idle. Updated by hardware. No read side-effects.</ipxact:description>
    <ipxact:bitOffset>1</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>read-only</ipxact:access>
</ipxact:field>
```

**Example 3: Write-1-to-Clear Interrupt (W1C)**
```xml
<ipxact:field>
    <ipxact:name>IRQ_STATUS</ipxact:name>
    <ipxact:description>Interrupt pending flag. Read returns 1 if interrupt pending, 0 otherwise. Write 1 to clear interrupt and deassert IRQ signal. Write 0 has no effect.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>write-1-clear</ipxact:access>
</ipxact:field>
```

**Example 4: Read-to-Clear Status (RC)**
```xml
<ipxact:field>
    <ipxact:name>ERROR</ipxact:name>
    <ipxact:description>Error status flag. Returns 1 if error occurred since last read, 0 otherwise. Automatically cleared to 0 when read (read-to-clear). Hardware can set this bit again after clearing.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>read-clear</ipxact:access>
</ipxact:field>
```

**Example 5: Field with Cross-Register Dependencies**
```xml
<ipxact:field>
    <ipxact:name>LOAD_VALUE</ipxact:name>
    <ipxact:description>Timer load value. Writing this field immediately copies the value to WDOGVALUE register and restarts countdown. Write is ignored if WDOGLOCK register is locked (value != 0x1ACCE551). Read returns last written value.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>32</ipxact:bitWidth>
    <ipxact:access>read-write</ipxact:access>
</ipxact:field>
```

**Example 6: Multi-Bit Field with Enumerated Values**

**When to use**: Include `<ipxact:enumeratedValues>` when field has named constants or specific meaning for each value.

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
            <ipxact:description>Clock division by 1 (1GHz clock, 1ns per tick)</ipxact:description>
            <ipxact:value>0</ipxact:value>
        </ipxact:enumeratedValue>
        <ipxact:enumeratedValue>
            <ipxact:name>DIV_16</ipxact:name>
            <ipxact:description>Clock division by 16 (62.5MHz clock, 16ns per tick)</ipxact:description>
            <ipxact:value>1</ipxact:value>
        </ipxact:enumeratedValue>
        <ipxact:enumeratedValue>
            <ipxact:name>DIV_256</ipxact:name>
            <ipxact:description>Clock division by 256 (3.9MHz clock, 256ns per tick)</ipxact:description>
            <ipxact:value>2</ipxact:value>
        </ipxact:enumeratedValue>
        <!-- Additional enumerated values as needed -->
    </ipxact:enumeratedValues>
</ipxact:field>
```

---

### 5. Port Definitions

**Purpose**: Define I/O signals for device external connectivity.

**When to use**: Include if device has signals extracted in Step 2 (clock, reset, interrupts, data I/O, etc.).

**Placement**: After `</ipxact:memoryMaps>` and before `</ipxact:component>`.

**What to extract** (from Step 2):
- `[PORT_NAME]`: Signal name (e.g., "clk", "rst_n", "irq", "data_out")
- `[DIRECTION]`: Signal direction (`in`, `out`, or `inout`)
- `[WIDTH]`: Bit width (1 for scalar, N for vector)
- `[TYPE_NAME]`: Wire type (`std_logic` for single bit, `std_logic_vector` for multi-bit)

**Structure**: Wrap all port definitions in `<ipxact:ports>` container.

---

#### 5.1 Scalar Port (Single-Bit Signal)

**Use for**: Clock, reset, interrupt, enable signals (1-bit width).

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

**Example - Interrupt Output**:
```xml
<ipxact:port>
    <ipxact:name>wdogint</ipxact:name>
    <ipxact:description>Watchdog interrupt output. Asserted high when counter reaches zero and INTEN=1. Cleared by writing to WDOGINTCLR.</ipxact:description>
    <ipxact:wire>
        <ipxact:direction>out</ipxact:direction>
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

**Use for**: Data buses, address lines, multi-bit status signals.

**What to extract**:
- `[LEFT]`: MSB index (e.g., 7 for [7:0])
- `[RIGHT]`: LSB index (e.g., 0 for [7:0])

**XML Template**:
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

**Example - 8-Bit Data Input**:
```xml
<ipxact:port>
    <ipxact:name>data_in</ipxact:name>
    <ipxact:description>8-bit data input bus for configuration values.</ipxact:description>
    <ipxact:wire>
        <ipxact:direction>in</ipxact:direction>
        <ipxact:vector>
            <ipxact:left>7</ipxact:left>
            <ipxact:right>0</ipxact:right>
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

## XML Generation Checklist

Before delivering final XML, verify:

**Structure Completeness**:
- [ ] XML declaration present: `<?xml version="1.0" encoding="UTF-8"?>`
- [ ] Component root with all xmlns declarations
- [ ] Bus interfaces section (if device has bus connectivity)
- [ ] Memory maps section with at least one address block
- [ ] All registers from specification included
- [ ] All fields within registers included
- [ ] Ports section (if device has I/O signals)
- [ ] Proper closing tag: `</ipxact:component>`

**Data Accuracy**:
- [ ] All `[PLACEHOLDER]` values replaced with actual data
- [ ] Register addresses in ascending order
- [ ] No overlapping bit fields (validate bitOffset + bitWidth)
- [ ] Reset values within valid ranges for field widths
- [ ] Access types correctly mapped from specification
- [ ] Enumerated values match specification constants

**Description Quality** (filled in Step 5):
- [ ] Every register has comprehensive description with side-effects
- [ ] Every field has description (or inherits from register if identical)
- [ ] Cross-register dependencies documented bidirectionally
- [ ] Lock/protection mechanisms explained
- [ ] W1C, RC, and special access behaviors documented

**XML Validity**:
- [ ] All tags properly closed
- [ ] Consistent indentation (2 or 4 spaces)
- [ ] No syntax errors
- [ ] Schema-compliant structure

---

## Common Patterns and Best Practices

### Description Writing for Complex Behaviors

**Asymmetric Read/Write Operations** (e.g., lock registers):
```xml
<ipxact:description>
Write Behavior: Writing 0x1ACCE551 unlocks the register block. Any other value locks it.
Read Behavior: Returns 1 if locked, 0 if unlocked.
</ipxact:description>
```

**Multi-Stage Operations** (e.g., write triggers multiple actions):
```xml
<ipxact:description>
Control register. Writing 1 to ENABLE (bit 0) triggers: (1) reloads counter from LOAD register, (2) starts countdown, (3) clears any pending interrupts. Writing 0 stops countdown but preserves counter value. Write ignored if LOCK register is locked.
</ipxact:description>
```

**Conditional Side-Effects** (e.g., behavior depends on other register state):
```xml
<ipxact:description>
Timer load value register. Writing this register immediately copies value to COUNTER and restarts countdown IF and ONLY IF CONTROL.ENABLE is set to 1. If ENABLE is 0, write updates LOAD but does not affect COUNTER. All writes ignored when LOCK != 0x1ACCE551.
</ipxact:description>
```

### Address Alignment Rules

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
