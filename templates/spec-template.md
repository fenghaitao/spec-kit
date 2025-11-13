# Feature Specification Template for Simics Device Models

**INSTRUCTIONS FOR AI AGENT**: This template has two parts:
1. **PART A: GUIDANCE SECTIONS** - Read these but DO NOT include them in the generated spec
2. **PART B: SPEC CONTENT TEMPLATE** - Fill these out and include in the generated spec

---

# PART A: GUIDANCE SECTIONS (DO NOT COPY TO GENERATED SPEC)

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
   → Set Created date to current date in YYYY-MM-DD format
   → Extract: Simics device type (timer, controller, interface, peripheral)
   → Extract: registers, interfaces, operational behavior, target platform

2. Mark ALL uncertainties with [NEEDS CLARIFICATION: specific question]
   → Test: Can you write a test without guessing? NO → Mark it
   → Be specific: "interrupt type - level or edge-triggered?"

3. Complete Test-Driven Specification: User Stories & Validation Strategy (mandatory)
   → Primary user story + 6+ test scenarios (3 core functional, 2 error/edge case, 1+ integration if applicable)
   → If unclear: ERROR "Cannot determine testable device operation"

4. Generate Functional Requirements (minimum 5)
   → Each must be testable: "Device MUST [specific capability]"
   → Mark ambiguous behaviors with [NEEDS CLARIFICATION: ...]

5. Complete Hardware Specification (7 subsections)
   → Device Purpose, Register Map, Bit Fields, External Interfaces
   → Operational Behavior, Software Visibility, Memory Interface

6. Generate IP-XACT 1685-2022 Register Description File (MANDATORY)
   → Create separate file: [feature-name]-registers.xml (DO NOT include XML in spec.md)
   → Analyze Hardware Specification section (Register Map table, bit field descriptions, External Interfaces)
   → For EACH register from Register Map table:
     * Define basic properties (name, description, offset, size, access)
     * Add reset value and mask from register bit field descriptions
     * Define ALL fields with bit positions and access types from bit field descriptions
     * Add enumerated values where applicable (extract from bit field enumeration descriptions)
   → Define memory map structure using information from Memory Interface Requirements
   → Add bus interface based on External Interfaces (Bus Connection)
   → Include ALL I/O ports from External Interfaces section (Clock, Reset, Interrupt, Signal Outputs, Other Connections)
   → Add comprehensive documentation extracted from register and field descriptions
   → Follow XML schema structure detailed in "IP-XACT Register Description Generation Guide" section below
   → Output: Complete, valid IP-XACT 1685-2022 XML file in separate .xml file

7. Complete Simics-Specific Sections (mandatory)
   → Device Behavioral Model (4 subsections)

8. Run Review Checklist and Update Status Field
   → Search entire spec content for [NEEDS CLARIFICATION: ...] markers
   → Count the markers found in the actual content (ignore references in headers/instructions)
   → Update the Status field at the top of the spec:
     * If ZERO markers: Set Status to "Ready for Planning"
     * If 1+ markers: Set Status to "Draft ([N] clarifications needed)"
   → Mark [x] objective items if passing (no DML, sections complete)

9. Update Execution Status
   → Mark [x] all completed steps (1-9)
   → Return: SUCCESS (spec ready for human review)
```

## Core Principles

### PRINCIPLE 1: Never Guess
**IF** you don't know something → **THEN** mark `[NEEDS CLARIFICATION: specific question]`
**NEVER** infer, assume, or guess unstated requirements

### PRINCIPLE 2: Test-Driven Thinking
**BEFORE** writing any requirement → **ASK** "Can I write a test for this without guessing?"
**IF** answer is NO → **THEN** mark for clarification

### PRINCIPLE 3: Hardware Behavior Only (WHAT, not HOW)
**DO**: Describe what the device does from hardware perspective
**DON'T**: Include DML syntax, code structure, or implementation details
**FOCUS**: Register behaviors, state transitions, interface protocols

### PRINCIPLE 4: Completeness Over Perfection
**BETTER**: Complete spec with [NEEDS CLARIFICATION] markers
**WORSE**: Incomplete spec with no markers
**GOAL**: All sections filled (even if some need clarification)

### PRINCIPLE 5: Always Update Status Field
**CRITICAL**: After completing the spec, count [NEEDS CLARIFICATION: ...] markers and update Status field
**IF** zero markers → Status: "Ready for Planning"
**IF** 1+ markers → Status: "Draft ([N] clarifications needed)"

## Simics DML Device Modeling Guidance

**Note**: For Simics device modeling projects, comprehensive DML learning resources are available:
- **.specify/memory/DML_grammar.md**: Complete DML 1.4 grammar reference with syntax rules and language constructs
- **.specify/memory/DML_Device_Development_Best_Practices.md**: Best practices, patterns, and common pitfalls for DML development

**During /specify phase**: Focus on WHAT the device does (hardware behavior specification)
- Describe device functionality from hardware perspective
- Specify register behaviors without DML implementation details
- Define interfaces and protocols the device supports
- Document timing and state machine behaviors
- Specify system integration requirements
- Define device behavioral model and platform integration requirements

**Functional Modeling Defaults** (unless explicitly stated otherwise):
- **Timing**: Precise timing is NOT required for functional models - focus on functional correctness
- **Checkpoint/Restore**: Checkpoint and restore functionality is NOT required - Simics handles this automatically for register state

### Structure Requirements
Each requirement must have:
1. **User Story**: "As a [role], I want [capability], so that [benefit]"
2. **Acceptance Criteria**: Numbered list of testable SHALL statements

## Decision Tree: When to Mark [NEEDS CLARIFICATION]

```
Is the requirement stated explicitly in user input?
├─ YES → Can you write a test without guessing details?
│  ├─ YES → Write the requirement (no marker needed)
│  └─ NO → Mark [NEEDS CLARIFICATION: what detail is ambiguous?]
└─ NO → Is it inferable from standard practice/context?
   ├─ YES → Write the requirement (no marker needed)
   └─ NO → Mark [NEEDS CLARIFICATION: what is missing?]
```

## Common Underspecified Areas (CHECK THESE)

**For Simics Devices - High Priority:**
1. **Abstraction Level**: Functional vs cycle-accurate modeling? (Default: Functional)
2. **Interrupt Behavior**: Level-triggered or edge-triggered?
3. **Register Side Effects**: What happens when register is read/written? (Document side effects when they exist - e.g., write triggers action, read clears status)
4. **Reset Values**: What are the default/reset values for each register and bit field? (MUST document - critical for testing and initialization)
5. **Reset Behavior**: What state after reset? How do registers initialize?
6. **Error Handling**: How are errors detected and reported?
7. **System Dependencies**: What other components are required?
8. **Register Access Types**: Ensure correct access type (R/W, R/O, W/O, W1C) for each register
9. **Device Identification**: Are there peripheral/vendor ID registers that need documentation?

**NOT Required for Functional Models** (do NOT mark as [NEEDS CLARIFICATION]):
- Precise timing requirements (cycle-accurate timing)
- Checkpoint/restore implementation details
- Performance targets (throughput/latency) unless explicitly part of device specification

## Examples: Good vs Bad Clarification Markers

**BAD** (too vague):
- `[NEEDS CLARIFICATION: interrupt unclear]`
- `[NEEDS CLARIFICATION: more details needed]`

**GOOD** (specific with options):
- `[NEEDS CLARIFICATION: interrupt type - level-triggered or edge-triggered?]`
- `[NEEDS CLARIFICATION: reset behavior - does COUNTER reset to 0 or preserve value?]`
- `[NEEDS CLARIFICATION: DMA support - required, optional, or not supported?]`

## Example Feature Description

[Write 2-4 sentence paragraph summarizing:
- What the feature/device is
- Primary purpose and capabilities
- Key technical context (platform, standards, technology)
- Scope boundaries]

Example:
"This document specifies the requirements for a Simics watchdog timer device implementation based on the ARM PrimeCell watchdog specification. The watchdog timer is a 32-bit down-counter that provides system protection through configurable timeout intervals, interrupt generation, and system reset capabilities. The device includes 21 memory-mapped registers for control, status monitoring, peripheral identification, and integration testing. The implementation targets the QSP-x86 platform with a base address of 0x1000 and follows DML 1.4 standards for Simics device modeling."

## IP-XACT Register Description Generation Guide

**Purpose**: This section provides the XML schema and structure for generating IP-XACT 1685-2022 register description files. The AI agent should generate a **separate .xml file** (NOT included in spec.md).

**File Naming**: `[feature-name]-registers.xml` (e.g., `watchdog-timer-registers.xml`)

**CRITICAL**: Generate complete XML in a separate file. DO NOT copy XML templates or examples into the spec.md file.

### XML Structure Template

#### 1. Component Identification
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

#### 2. Bus Interface
Define the bus interface (e.g., APB4, AXI, AHB) with memory map reference.
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

#### 3. Memory Map Structure
Define address block with base address, range, and width.
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

#### 4. Register Definitions
For EACH register from the Register Map table:
- Extract: name, description, address offset, size, access type, reset value
- Define ALL bit fields with: name, description, bitOffset, bitWidth, access
- Add enumerated values for fields where applicable (from bit field descriptions)

**Basic Register Structure:**
```xml
<ipxact:register>
    <ipxact:name>REGISTER_NAME</ipxact:name>
    <ipxact:description>Brief description of the register's purpose</ipxact:description>
    <ipxact:addressOffset>0x00</ipxact:addressOffset>
    <ipxact:size>32</ipxact:size>
    <ipxact:access>read-write|read-only|write-only</ipxact:access>
    <ipxact:reset>
        <ipxact:value>0x00000000</ipxact:value>
        <ipxact:mask>0xFFFFFFFF</ipxact:mask>
    </ipxact:reset>

    <!-- Field definitions go here -->

</ipxact:register>
```

**Basic Field Structure:**
```xml
<ipxact:field>
    <ipxact:name>field_name</ipxact:name>
    <ipxact:description>Description of the field's purpose</ipxact:description>
    <ipxact:bitOffset>0</ipxact:bitOffset>
    <ipxact:bitWidth>8</ipxact:bitWidth>
    <ipxact:access>read-write</ipxact:access>
</ipxact:field>
```

#### 5. Port Definitions
For EACH interface from External Interfaces section:
- Create port for each signal (clock, reset, interrupt, etc.)
- Specify direction (in/out/inout) and wire type

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

### Best Practices

**Naming Conventions:**
- Use UPPERCASE for register and field names (match Hardware Specification)
- Use descriptive names from the specification
- Be consistent with naming patterns

**Documentation:**
- Include clear descriptions for all registers and fields
- Document reset values and behaviors
- Note any hardware constraints or requirements

**Organization:**
- Group related registers together
- Order registers by address offset
- Use XML comments to separate functional blocks

**Validation:**
- Ensure all addresses are properly aligned
- Verify bit fields don't overlap
- Check that reset values are within field ranges

---
---

# PART B: SPEC CONTENT TEMPLATE (COPY AND FILL OUT IN GENERATED SPEC)

---

# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [Current date in YYYY-MM-DD format]
**Status**: [Set based on [NEEDS CLARIFICATION] markers - see Step 7]
**Input**: User description: "$ARGUMENTS" (text provided after /specify command)

---

## Test-Driven Specification: User Stories & Validation Strategy

**Purpose**: Define comprehensive, testable scenarios that drive both specification clarity and test case development. Each scenario should be implementable as automated tests in subsequent phases.

### Functional Test Scenarios (Given-When-Then Format)

**Core Functional Tests** (must have 3+ scenarios):
1. **Scenario**: Device initialization and register access
   - **Given** device is in reset state
   - **When** software writes [specific value] to [register name]
   - **Then** [register state changes] AND [observable device behavior]
   - **Test Validation**: Read register to verify value, check status bits, verify no error flags

2. **Scenario**: Primary device operation
   - **Given** device is initialized with [configuration]
   - **When** [trigger event or register write sequence]
   - **Then** device performs [expected operation] AND generates [expected output/interrupt]
   - **Test Validation**: [How to verify the operation completed correctly]

3. **Scenario**: Interrupt handling (if applicable)
   - **Given** device interrupt is enabled via [register/bit]
   - **When** [interrupt condition occurs]
   - **Then** interrupt signal is asserted AND [status register reflects condition]
   - **Test Validation**: Verify interrupt status, check clear mechanism works

*Mark any unclear cases with [NEEDS CLARIFICATION: specific behavior under [condition]]?*

### Test Coverage Requirements
- **Register Coverage**: All registers must be tested (read, write, reset value verification)
- **Bit Field Coverage**: All functional bit fields must be tested (set, clear, combinations)
- **State Coverage**: All device states must be reachable and testable
- **Transition Coverage**: All state transitions must be exercised
- **Error Coverage**: All error conditions must be testable (detection, reporting, recovery)
- **Protocol Coverage**: All bus protocol sequences must be validated (if applicable)

### Test Automation Considerations
*For later /plan and /implement phases:*
- Each scenario above should map to 1+ automated test cases
- Test cases should be executable in Simics simulation environment
- Tests should verify both register state AND device behavior/outputs
- Consider using Simics scripting (Python) for test automation
- Define pass/fail criteria explicitly for each test scenario

---

## Requirements

### Requirement 1

**User Story:** As a [role], I want [capability], so that [benefit]

#### Acceptance Criteria

1. THE [System] SHALL [specific behavior with precise details]
2. WHEN [condition], THE [System] SHALL [action with specific outcome]
3. THE [System] SHALL provide [resource/interface] with [specific attributes]
4. WHILE [state], THE [System] SHALL [continuous behavior]
5. THE [System] SHALL NOT [prohibited action] [under specific conditions]

*Mark unclear items:*
- THE [System] SHALL [NEEDS CLARIFICATION: specific question about missing detail]

### Requirement 2

**User Story:** As a [role], I want [capability], so that [benefit]

#### Acceptance Criteria

1. THE [System] SHALL [behavior]
2. WHEN [condition], THE [System] SHALL [action]
3. [Continue with numbered criteria...]

### Requirement 3

**User Story:** As a [role], I want [capability], so that [benefit]

#### Acceptance Criteria

1. THE [System] SHALL [behavior]
2. [Continue...]

[Continue with Requirement 4, 5, 6... minimum 5 requirements]

---

## Hardware Specification

### Register Map

| Offset | Name | Size | Access | Reset | Purpose |
|--------|------|------|--------|-------|---------|
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control and enable flags |
| 0x04 | STATUS | 32-bit | R/O | 0x0001 | Device status indicators |
| 0x08 | TIMEOUT | 32-bit | R/W | 0x0000 | Timeout period configuration |
| 0x0C | COUNTER | 32-bit | R/O | 0x0000 | Current countdown value |
| 0x10 | INTCLR | 32-bit | W/O | 0x0000 | Write any value to clear interrupt |
| ... | ... | ... | ... | ... | ... |

*Access types: R/W (Read/Write), R/O (Read-Only), W/O (Write-Only), W1C (Write-1-to-Clear)*

*Reset values: MUST be extracted from specification. Use 0 for write-only registers or when reset value is unknown.*

*Note: Include ALL registers in the register map, including device identification registers (e.g., peripheral ID, vendor ID) if applicable.*

*For each register with bit fields, detail the fields with their reset value. Document side effects only when they exist (e.g., write triggers action, read clears status, write reloads counter):*

**CONTROL Register (0x00)** - Reset: 0x00000000, bit fields:
- Bits [31:8]: Reserved (must be 0) - Reset: 0x000000
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupt generation - Reset: 0
  * Side effect: When set to 1, enables interrupt generation; when cleared, disables interrupts
- Bit 6: DMA_ENABLE (R/W) - Enable DMA transfers - Reset: 0
  * Side effect: When set to 1, enables DMA engine; when cleared, stops DMA transfers
- Bits [5:1]: Reserved - Reset: 0x00
- Bit 0: DEVICE_ENABLE (R/W) - Master enable for device operation - Reset: 0
  * Side effect: Writing 1 triggers device initialization sequence, resets COUNTER to 0, clears STATUS.ERROR; writing 0 disables device

**STATUS Register (0x04)** - Reset: 0x00000001, bit fields:
- Bits [31:4]: Reserved - Reset: 0x0000000
- Bit 3: ERROR (R/O) - Error condition detected - Reset: 0
- Bit 2: BUSY (R/O) - Device busy processing - Reset: 0
- Bit 1: INTERRUPT_PENDING (R/O) - Interrupt waiting to be serviced - Reset: 0
- Bit 0: READY (R/O) - Device ready for operations - Reset: 1
  * Note: This is a read-only status register with no side effects

**TIMEOUT Register (0x08)** - Reset: 0x00000000, bit fields:
- Bits [31:0]: TIMEOUT_VALUE (R/W) - Timeout period in milliseconds - Reset: 0x00000000

**COUNTER Register (0x0C)** - Reset: 0x00000000, bit fields:
- Bits [31:0]: COUNTER_VALUE (R/O) - Current countdown value in milliseconds - Reset: 0x00000000
  * Side effect: Reading returns current counter value without affecting countdown

**INTCLR Register (0x10)** - Reset: 0x00000000 (Write-Only), bit fields:
- Bits [31:0]: CLEAR (W/O) - Write any value to clear interrupt - Reset: 0x00000000
  * Side effect: Writing any value clears the interrupt status and reloads counter from TIMEOUT register

*Continue for all registers with bit fields, including device identification registers if present...*

### External Interfaces
- **Bus Connection**: [direction: bidirectional] [e.g., "APB bus interface for register access", "Memory-mapped I/O at base address 0x1000", or NEEDS CLARIFICATION]
- **Interrupt Lines**: [direction: output] [e.g., "WDOGINT signal for timeout events", "IRQ 5 for timeout events", or NEEDS CLARIFICATION]
- **DMA Channels**: [direction: input/output/bidirectional] [e.g., "Channel 2 for data transfer (bidirectional)", "No DMA required", or NEEDS CLARIFICATION]
- **Clock Signals**: [direction: input] [e.g., "wclk (work clock), wclk_en (clock enable)", "System clock input", "None", or NEEDS CLARIFICATION]
- **Reset Signals**: [direction: input] [e.g., "wrst_n (work reset), prst_n (APB reset)", "System reset input", or NEEDS CLARIFICATION]
- **Signal Outputs**: [direction: output] [e.g., "WDOGRES (hardware reset line to system controller)", "Status LEDs", "None", or NEEDS CLARIFICATION]
- **Other Connections**: [direction: specify] [e.g., "GPIO pins for external control (input/output)", or NEEDS CLARIFICATION]

### Operational Behavior *(parsed from hardware specification)*
- **Initialization**: [Sequence of register writes needed to initialize device, e.g., "Unlock registers if lock mechanism exists, configure control registers, set timeout/load values, enable device"]
- **Normal Operation**: [Key register interactions during typical use, e.g., "Counter decrements from load value; when reaches zero, asserts interrupt; software writes to clear register to acknowledge"]
- **Error Handling**: [How errors are signaled and cleared, e.g., "Register lock prevents unauthorized access; error status bits set on failure; write to clear register to reset error state"]
- **Interrupts**: [When interrupts fire and how to acknowledge, e.g., "Interrupt asserted when counter reaches zero and interrupt enable bit set; cleared by writing to interrupt clear register"]

### Software Visibility *(what software can observe/control)*
- Software can observe: [e.g., "Counter value through VALUE register, interrupt status through status registers, device identity through ID registers"]
- Software cannot observe: [e.g., "Internal countdown timing details, internal state machine states, clock divider internal operation"]
- Ordering requirements: [e.g., "Must unlock registers before writing to them, must write to clear register to acknowledge interrupts, must configure control registers before enabling device"]

### Memory Interface Requirements *(for complex devices)*
- **Address Space**: [Base address and size requirements, e.g., "0x1000 base address, 0x1000 bytes (4KB) address space", or NEEDS CLARIFICATION]
- **Access Patterns**: [Byte access, unaligned access support, ordering requirements, e.g., "32-bit aligned access for control registers, 8-bit access for ID registers"]
- **Coherency**: [Cache coherency participation, DMA coherency requirements, e.g., "No special coherency requirements beyond standard memory-mapped I/O"]
- **Timing**: [Setup/hold times, wait states, burst capabilities, countdown precision, e.g., "Register access timing requirements", "Watchdog timing precision requirements", or NEEDS CLARIFICATION]

---

**Note**: IP-XACT register description XML is generated in a separate file `[feature-name]-registers.xml` following the guidelines in Part A. Do NOT include XML content in this specification document.

---

## Device Behavioral Model

### System Context
- **Simulation Purpose**: [e.g., Boot validation, Software development, Performance analysis]
- **Abstraction Level**: Functional (default for Simics device models)

### State Management
- **Device State Variables**: [internal state that must be maintained]
- **State Transitions**: [how device state changes based on register writes/external events]
- **Reset Behavior**: [how device state is initialized/reset]
- **Save/Restore**: Not required (Simics handles checkpoint/restore automatically for register state)

### Data Processing
- **Input Data Flow**: [how device processes input data]
- **Output Generation**: [how device generates outputs]
- **Buffer Management**: [internal buffer requirements and management]
- **Timing Behavior**: Functional timing (precise cycle-accurate timing not required)

### Error Scenarios and Recovery
- **Error Detection**: [how device detects error conditions]
- **Error Reporting**: [how errors are communicated to software]
- **Recovery Mechanisms**: [how device recovers from errors]
- **Fault Injection**: [support for testing error scenarios, or NEEDS CLARIFICATION]

---

## Review & Acceptance Checklist

### AUTOMATED CHECKS (AI Agent MUST verify)

**Content Quality** (objective - can be checked automatically):
- [ ] No implementation details (DML syntax, code structure, algorithms)
  - *Check: Search for "dml", "method", "template", code blocks*
- [ ] Focused on hardware behavior and device operation
  - *Check: Sections describe WHAT device does, not HOW to implement*
- [ ] All mandatory sections completed
  - *Check: Every section below has content (not just headers)*

**Hardware Specification Completeness** (objective):
- [ ] Device type identified and specified
  - *Check: "Device Purpose" subsection filled*
- [ ] Register map described at high level
  - *Check: Register Map table exists with at least 1 register*
- [ ] External interfaces documented
  - *Check: "External Interfaces" subsection filled*
- [ ] Operational behavior flows specified
  - *Check: "Operational Behavior" subsection filled*
- [ ] IP-XACT register description XML file generated
  - *Check: Complete IP-XACT 1685-2022 XML content provided in "Complete IP-XACT XML Output" section*
  - *Check: XML includes component ID, bus interface, memory map, ALL registers with ALL fields*
  - *Check: NO placeholders remain - all [...] replaced with actual extracted values*
  - *Check: ALL ports from External Interfaces defined*
  - *Check: Register count matches Register Map table row count*

**Simics-Specific Completeness** (objective - MANDATORY):
- [ ] Device behavioral model documented
  - *Check: All 4 subsections of "Device Behavioral Model" filled*
- [ ] Test-driven specification with essential test scenarios
  - *Check: "Test-Driven Specification" section has 6+ test scenarios (3 core functional, 2 error/edge case, 1+ integration if applicable)*

---

## Execution Status
*AI Agent: Mark [x] as you complete each step (corresponds to Execution Flow in guidance)*

- [ ] **STEP 1**: User description parsed and device context extracted
- [ ] **STEP 2**: All uncertainties marked with [NEEDS CLARIFICATION: ...]
- [ ] **STEP 3**: Test-Driven Specification completed (user story + 6+ test scenarios + coverage requirements)
- [ ] **STEP 4**: Functional requirements generated (minimum 5)
- [ ] **STEP 5**: Hardware specification completed (7 subsections)
- [ ] **STEP 6**: IP-XACT 1685-2022 register description XML file generated in separate .xml file
- [ ] **STEP 7**: Simics-specific sections completed (Device Behavioral Model)
- [ ] **STEP 8**: Review checklist executed and Status field updated
- [ ] **STEP 9**: Execution status updated (all items marked [x])

**COMPLETION CRITERIA**: All 9 steps marked [x] = Specification ready for human review

---
