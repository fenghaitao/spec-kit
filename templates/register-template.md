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

## Hardware Specification Analysis Process

Before generating the IP-XACT XML, follow this complete workflow to extract and document all register information:

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

### Step 2: Identify Side-Effects

Analyze the functional behavior descriptions to identify read/write side-effects for both registers and fields. These side-effects will be included in the `<ipxact:description>` tags.

**Register-to-Functionality Relationships**:
- Identify all hardware functionalities (timer, interrupt, DMA, etc.)
- Determine which registers control each functionality
- Document dependencies between registers

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

**Description Format Guidelines**:
- Be specific: Use exact register/field names and hardware behaviors
- Be complete: Include ALL side-effects for accurate simulation
- Be clear: Write for implementers who need every detail
- Combine functional purpose + side-effects in single description
- Example: "Control register for timer operation. Bit 0 enables timer countdown. Writing 1 starts timer from LOAD value."

### Step 3: Generate IP-XACT XML Structure

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
- **CRITICAL**: Populate `<ipxact:description>` with:
  - Functional purpose
  - Read side-effects (if any)
  - Write side-effects (if any)
  - Register relationships
  - Example: "Control register. Bit 0 enables timer. Writing 1 starts countdown. Write ignored if locked."
- Add reset value and mask (if specified)

**3.5 Field Definitions** (for EACH field in EACH register):
- Calculate bitOffset and bitWidth from bit range
- Set access type (map W1C → write-1-clear, RC → read-clear, etc.)
- **CRITICAL**: Populate field `<ipxact:description>` with:
  - Field purpose
  - Field-specific side-effects (W1C, read-to-clear, enable/disable)
  - Conditions (e.g., "ignored if locked", "write 1 to clear")
  - Cross-register effects (e.g., "copies to COUNTER")
  - Example: "Enable bit. Write 1 to start timer countdown from LOAD value. Write 0 to stop timer."
- Add reset value (if specified)
- Add enumerated values (if defined)

**3.6 Port Definitions**:
- Extract I/O signals from specification
- Define direction (in/out/inout)
- Specify wire type and width

### Step 4: Validate Output

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

### 1. Component Identification
```xml
<ipxact:component
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2022"
    xsi:schemaLocation="http://www.accellera.org/XMLSchema/IPXACT/1685-2022 http://www.accellera.org/XMLSchema/IPXACT/1685-2022/index.xsd">

    <ipxact:vendor>[VENDOR_NAME]</ipxact:vendor>
    <ipxact:library>[LIBRARY_NAME]</ipxact:library>
    <ipxact:name>[IP_NAME]</ipxact:name>
    <ipxact:version>[VERSION]</ipxact:version>
```

### 2. Bus Interface
Example for APB interface:
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

### 3. Memory Map Structure
```xml
<ipxact:memoryMaps>
    <ipxact:memoryMap>
        <ipxact:name>[MEMORY_MAP_NAME]</ipxact:name>
        <ipxact:addressBlock>
            <ipxact:name>[BLOCK_NAME]</ipxact:name>
            <ipxact:baseAddress>0x0</ipxact:baseAddress>
            <ipxact:range>0x1000</ipxact:range>
            <ipxact:width>32</ipxact:width>

            <!-- Register definitions go here -->

        </ipxact:addressBlock>
    </ipxact:memoryMap>
</ipxact:memoryMaps>
```

### 4. Register Definition Template
For each register, include:

#### Basic Register Information
```xml
<ipxact:register>
    <ipxact:name>REGISTER_NAME</ipxact:name>
    <ipxact:description>Register purpose and side-effects. Example: Control register for device operation. Writing bit 0 starts operation. Reading returns current status without side-effects.</ipxact:description>
    <ipxact:addressOffset>0x00</ipxact:addressOffset>
    <ipxact:size>32</ipxact:size>
    <ipxact:access>read-write|read-only|write-only</ipxact:access>
    <!-- Use 'true' for registers that can change value on their own, like counters or status registers updated by hardware. -->
    <ipxact:volatile>false</ipxact:volatile>
    <ipxact:reset>
        <ipxact:value>0x00000000</ipxact:value>
        <ipxact:mask>0xFFFFFFFF</ipxact:mask>
    </ipxact:reset>

    <!-- Field definitions go here -->

</ipxact:register>
```

#### Field Definition Examples

**Simple Field with Side-Effects:**
```xml
<ipxact:field>
    <ipxact:name>ENABLE</ipxact:name>
    <ipxact:description>Enable bit. Write 1 to start timer countdown from LOAD value. Write 0 to stop timer. Transition 0→1 resets counter.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>read-write</ipxact:access>
</ipxact:field>
```

**Read-to-Clear Field:**
```xml
<ipxact:field>
    <ipxact:name>ERROR</ipxact:name>
    <ipxact:description>Error status flag. Returns 1 if error occurred. Automatically cleared to 0 after being read (read-to-clear).</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>read-clear</ipxact:access>
</ipxact:field>
```

**Write-One-to-Clear Field:**
```xml
<ipxact:field>
    <ipxact:name>IRQ_STATUS</ipxact:name>
    <ipxact:description>Interrupt pending flag. Read returns interrupt status. Write 1 to clear interrupt and deassert IRQ signal. Write 0 has no effect.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>1</ipxact:bitWidth>
    <ipxact:access>write-1-clear</ipxact:access>
</ipxact:field>
```

**Field with Cross-Register Dependencies:**
```xml
<ipxact:field>
    <ipxact:name>LOAD_VALUE</ipxact:name>
    <ipxact:description>Timer load value. Writing this field immediately copies the value to COUNTER register and restarts countdown. Write is ignored if LOCK register is locked.</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>32</ipxact:bitWidth>
    <ipxact:access>read-write</ipxact:access>
</ipxact:field>
```

**Field with Enumerated Values:**
```xml
<ipxact:field>
    <ipxact:name>step_value</ipxact:name>
    <ipxact:description>Step value for counter decrement</ipxact:description>
    <ipxact:bitOffset>2</ipxact:bitOffset>
    <ipxact:bitWidth>3</ipxact:bitWidth>
    <ipxact:access>read-write</ipxact:access>
    <ipxact:enumeratedValues>
        <ipxact:enumeratedValue>
            <ipxact:name>STEP_1</ipxact:name>
            <ipxact:description>step_value = 1, 1GHz clock</ipxact:description>
            <ipxact:value>0</ipxact:value>
        </ipxact:enumeratedValue>
        <!-- Additional enumerated values -->
    </ipxact:enumeratedValues>
</ipxact:field>
```

### 5. Port Definitions
```xml
<ipxact:ports>
    <ipxact:port>
        <ipxact:name>port_name</ipxact:name>
        <ipxact:wire>
            <ipxact:direction>in|out|inout</ipxact:direction>
            <ipxact:wireTypeDefs>
                <ipxact:wireTypeDef>
                    <ipxact:typeName>std_logic</ipxact:typeName>
                    <!-- Add vector type if needed: -->
                    <!-- <ipxact:typeName>std_logic_vector(7 downto 0)</ipxact:typeName> -->
                </ipxact:wireTypeDef>
            </ipxact:wireTypeDefs>
        </ipxact:wire>
    </ipxact:port>
    <!-- Additional ports -->
</ipxact:ports>
```

## Best Practices

1. **Naming Conventions**
   - Use UPPERCASE for register and field names
   - Use descriptive names that match the specification
   - Be consistent with naming patterns

2. **Documentation**
   - **CRITICAL**: Include side-effects in all register and field descriptions
   - Register descriptions must document:
     - Functional purpose
     - Read side-effects (state changes, flags cleared, etc.)
     - Write side-effects (hardware actions, signals, state transitions)
     - Register relationships (dependencies, locks, copy operations)
   - Field descriptions must document:
     - Field purpose
     - Field-specific side-effects when different from register-level
     - Special behaviors (W1C, read-to-clear, enable/disable semantics)
     - Cross-register effects (e.g., "copies to COUNTER", "ignored if locked")
   - Document reset values and behaviors
   - Note any hardware constraints or requirements
   - Use clear, implementation-ready language for simulator developers

3. **Organization**
   - Group related registers together
   - Order registers by address offset
   - Use comments to separate functional blocks

4. **Asymmetric Read/Write Behavior**
   - For registers where the read and write operations are different in nature (e.g., writing a key to read a status), clearly separate the behaviors in the description tag for clarity.
   - **Example:**
     ```xml
     <ipxact:description>
     Write Behavior: Writing `0x1ACCE551` unlocks the register block. Writing any other value locks it.
     Read Behavior: Returns `1` if locked, `0` if unlocked.
     </ipxact:description>
     ```

5. **Validation**
   - Ensure all addresses are properly aligned
   - Verify bit fields don't overlap
   - Check that reset values are within field ranges
   - Validate all side-effects are documented
   - Confirm cross-register dependencies are bidirectionally documented
