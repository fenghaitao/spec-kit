---
description: Create hardware IP functional specification and register description from IP hardware specification document.
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/specify` in the triggering message **is** the feature description with IP hardware specification or device description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

## Hardware Specification Analysis Process

Given the IP hardware specification, follow this structured workflow:

**Workflow Overview**:
1. **Step 1**: Run feature setup script (creates branch and spec file)
2. **Step 2**: Parse hardware specification document (extract all device information)
   - 2.1: Device overview and categorization
   - 2.2: Register map and bit fields
   - 2.3: I/O ports and signals
   - 2.4: Register side-effects and behaviors
   - 2.5: Validation checkpoint
3. **Step 3**: Generate hardware behavior specification (create spec.md)
   - 3.1: [NEEDS CLARIFICATION] marker guidelines
   - 3.2: Functional requirements generation
   - 3.3: Test scenario generation
   - 3.4: Finalize specification
4. **Step 4**: Generate IP-XACT register XML (create device-registers.xml)
   - 4.1-4.6: XML structure generation
   - 4.7: Validate and finalize XML
5. **Step 5**: Git commit (after Step 3 or Step 4)
6. **Step 6**: Report completion

---

### Step 1: Run Feature Setup Script

Run the script `{SCRIPT}` from repo root and parse its JSON output for BRANCH_NAME and SPEC_FILE. All file paths must be absolute.

**IMPORTANT**: You must only ever run this script once. The JSON is provided in the terminal as output - always refer to it to get the actual content you're looking for.

### Step 2: Parse Hardware Specification Document

**Objective**: Extract hardware behaviors, register definitions, and interface specifications from the IP hardware specification.

Follow this structured extraction workflow to gather all information needed for both the hardware specification (Step 3) and IP-XACT XML (Step 4).

---

#### 2.1: Extract Device Overview

**Device Purpose and Functionality**:
- What is the IP block (timer, UART, DMA controller, interrupt controller, etc.)?
- What is its primary function in the system?
- What hardware features does it provide?

**Common Device Categories and Patterns**:

1. **Timers/Counters**: Devices with countdown/countup functionality
   - Typical registers: LOAD, COUNTER, CONTROL, STATUS, PRESCALER
   - Common states: IDLE, COUNTING, INTERRUPT_PENDING
   - Key behaviors: Counter reload logic, interrupt generation on timeout
   - Examples: Watchdog timers, general-purpose timers, RTCs

2. **Serial Communication (UART/SPI/I2C)**: Data transmission devices
   - Typical registers: TX_DATA, RX_DATA, BAUD_RATE, LINE_CONTROL, STATUS
   - Common states: IDLE, TRANSMITTING, RECEIVING, ERROR
   - Key behaviors: FIFO management, baud rate configuration, parity/stop bits
   - Examples: UART, USART, SPI master/slave, I2C master/slave

3. **DMA Controllers**: Memory-to-memory or peripheral-to-memory transfer engines
   - Typical registers: SRC_ADDR, DST_ADDR, COUNT, CONTROL, STATUS
   - Common states: IDLE, TRANSFERRING, ERROR, PAUSED
   - Key behaviors: Multi-register atomic operations, burst transfers, channel arbitration
   - Examples: DMA controllers, scatter-gather engines

4. **Interrupt Controllers**: Interrupt aggregation and priority management
   - Typical registers: ENABLE, PENDING, PRIORITY, VECTOR, ACKNOWLEDGE
   - Common states: IDLE, PENDING, SERVICING
   - Key behaviors: Priority arbitration, interrupt masking, vector generation
   - Examples: NVIC, GIC, PIC, VIC

5. **GPIOs**: General-purpose input/output pin control
   - Typical registers: DATA, DIRECTION, MODE, PULL, INTERRUPT_CONFIG
   - Common states: INPUT, OUTPUT, ALTERNATE_FUNCTION
   - Key behaviors: Pin direction control, interrupt on edge/level
   - Examples: GPIO banks, pin multiplexers

**Use these patterns to guide extraction of registers, states, and behaviors for the specific device type.**

---

#### 2.2: Extract Register Map and Layout

**For the Address Block**:
- Address block name and base address (typically 0x0)
- Address range (calculate from highest register offset + size)
- Data width (default 32 bits unless specified)

**For EACH Register**:
- **Name**: Register identifier (preserve exact capitalization)
- **Address Offset**: Hexadecimal offset from base address (e.g., 0x00, 0x04, 0x10)
- **Size**: Register width in bits (default 32 if not specified)
- **Access Type**: Register-level access mode (RO, RW, WO, etc.)
- **Reset Value**: Default value after reset (if specified)
- **Reset Mask**: Bit mask for valid reset bits (typically all 1s)
- **Volatile**: true for registers that change without CPU writes (counters, status), false for control registers

**For EACH Bit Field within Each Register**:
- **Name**: Field identifier
- **Bit Range**: Position in register (e.g., [31:16], [7:4], [0])
  - Calculate **bitOffset** = LSB (lower bit number)
  - Calculate **bitWidth** = MSB - LSB + 1
- **Access Type**: Field access mode (RO, RW, WO, W1C, RC, etc.)
- **Reset Value**: Default value after reset (if specified)
- **Enumerated Values**: Named constants for field values (if defined)

**Access Type Mapping** (for XML generation):
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

---

#### 2.3: Extract I/O Port/Signal Interfaces

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

---

#### 2.4: Extract Register Side-Effects and Hardware Behaviors

**CRITICAL**: This is essential for functional simulation. Thoroughly analyze the hardware specification to identify ALL register side-effects and hardware behaviors.

##### 2.4.1: Register-to-Functionality Mapping

**Identify Hardware Functionalities**:
- List all hardware functions (timer, interrupt controller, DMA engine, FIFO, state machine, etc.)
- Map each register to the functionality it controls or monitors
- Identify registers that participate in multiple functionalities

**Example Mapping**:
```
Timer Functionality:
- LOAD register: Sets initial countdown value
- COUNTER register: Shows current countdown value
- CONTROL register: Enables/disables timer, configures step value
- INTCLR register: Acknowledges timeout and reloads counter

Interrupt Functionality:
- CONTROL.INTEN field: Enables interrupt generation
- STATUS/RIS/MIS registers: Show interrupt status
- INTCLR register: Clears interrupt status
- wdogint signal: Physical interrupt output
```

##### 2.4.2: Register Relationships and Cross-Dependencies

**CRITICAL**: Document ALL cross-register dependencies bidirectionally.

**Common Dependency Patterns**:

- **Lock/Protection**: A lock register gates writes to protected configuration registers
  - Example: "LOCK register with magic value unlocks CONTROL/CONFIG writes"

- **Reload/Copy**: A source register value is copied to a target register on specific triggers
  - Example: "LOAD register value copied to COUNTER on enable or clear event"

- **Enable/Disable**: An enable bit gates hardware operation and affects related register behavior
  - Example: "ENABLE bit starts/stops counter, triggers reload on 0→1 transition"

- **Clear/Set**: A trigger register modifies status bits or resets hardware state
  - Example: "INTCLR write clears interrupt status bits and deasserts interrupt signal"

- **Conditional**: An enable/mask bit determines whether hardware actions occur
  - Example: "INTEN bit gates interrupt signal assertion but not status bit setting"

**Documentation Format**:
For each dependency, specify:
- Trigger condition (register write, bit transition, hardware event)
- Affected registers and their behavior changes
- Bidirectional relationship (what reads/writes mean for both registers)
- Any timing or ordering constraints

##### 2.4.3: Read Side-Effects Documentation

**For EACH Register**, identify and document:

- **State-Changing Reads**: Read-to-Clear (RC), Read-to-Set (RS), FIFO pop operations
- **Dynamic Value Computation**: Real-time counter values, masked status computations
- **Read Ordering Requirements**: Must-read-first constraints, integration test mode behaviors
- **No Side-Effects**: Most common - simple register value return

##### 2.4.4: Write Side-Effects Documentation

**For EACH Register**, identify and document:

- **Hardware Actions**: Timer start/stop, DMA requests, self-test triggers
- **Internal State Changes**: State machine resets, error flag clears
- **Signal Assertions**: Interrupt/reset signal control
- **Cross-Register Updates**: Value copies (e.g., LOAD → COUNTER), dependent register modifications
- **Conditional Behaviors**: Lock-protected writes, enable-gated operations, read-only bits in R/W registers
- **Write-1-to-Clear (W1C)**: Write 1 clears bit, write 0 has no effect
- **Write-Only**: Trigger registers with no readable value (reads return 0)

##### 2.4.5: Field-Level Side-Effects

**Document field-specific behaviors when different from register-level**:

- **Enable/Disable Fields**: Transition triggers (0→1 or 1→0)
- **Multi-Bit Configuration**: Divider selections (e.g., 000=div1, 001=div2), mode encodings
- **Status Bits**: W1C semantics, hardware-set conditions
- **Reserved Fields**: Must write 0, read returns 0

##### 2.4.6: Hardware Behavior Flows and State Machines

**CRITICAL**: Document the complete operational model that ties together all register behaviors.

**Device States and Transitions**:

Identify and define all device operational states:
- **State Names**: Clear, descriptive names (e.g., RESET, LOCKED, UNLOCKED_IDLE, COUNTING, INTERRUPT_PENDING)
- **State Characteristics**: What defines each state (register values, hardware activity, signal states)
- **Entry Conditions**: What causes the device to enter this state
- **Exit Conditions**: What causes the device to leave this state
- **Observable Indicators**: How software can detect the current state (which registers/signals to check)

**State Transition Documentation**:
- Document all possible transitions between states
- Specify trigger conditions (register writes, hardware events, external signals)
- Note any timing constraints or ordering requirements
- Identify irreversible transitions (if any)

**Example State Machine Format**:
```
States:
- RESET: Initial state, all registers at defaults
- IDLE: Ready for operation, no activity
- ACTIVE: Performing primary function
- ERROR: Fault condition detected

Transitions:
- RESET → IDLE: On initialization complete
- IDLE → ACTIVE: On enable/start trigger
- ACTIVE → IDLE: On disable/stop trigger
- ACTIVE → ERROR: On fault detection
- ERROR → IDLE: On error clear (if recoverable)
```

**Software/Hardware Interaction Flows**:

Document complete sequences showing how software and hardware work together. Use this template:

```
Flow Template:
Purpose: [What this accomplishes]

1. Software Action: [Register write/read]
   → Hardware Response: [What hardware does]
   → State Change: [Any state transitions]

2. [Next step...]

Observable: [What software can verify happened]
```

**Common Flow Patterns**:

- **Initialization Flow**: Unlock → Configure → Enable → Verify started
- **Interrupt Handling Flow**: Hardware event → Status update → Software reads → Software acknowledges → Hardware clears
- **Error Recovery Flow**: Error detected → Status set → Software reads → Software clears (W1C) → Hardware resets

**Operational Constraints and Requirements**:

Document timing requirements and ordering constraints:

**Common Ordering Patterns**:
- Unlock before configure (for lock-protected registers)
- Configure before enable (set parameters before starting operation)
- Disable before reconfigure (stop operation before changing settings)
- Acknowledge before continue (clear interrupt/status before resuming)

**Timing Considerations**:
- Multi-cycle operations (if any register access spans multiple clocks)
- Hardware response latency (delay from write to effect)
- Signal propagation delays (for external signals)

**Observable State**:
- What software CAN observe: Register values, status bits, interrupt signals
- What software CANNOT observe: Internal state machine details, intermediate clock-cycle states

---

#### 2.5: Side-Effect Extraction Validation

Before proceeding to Step 3, verify your extraction work against **Section 1** of `templates/validation-checklist.md` (**reference only - do not edit that file**):

**Quick self-check** (see validation-checklist.md for comprehensive criteria):
- All registers, fields, and side-effects documented
- Cross-register dependencies identified bidirectionally
- Device states, transitions, and flows documented
- External interfaces (bus, interrupts, clocks, signals) identified
- Ordering constraints and timing requirements specified

**Note**: validation-checklist.md is a reference guide. You verify against it, but mark completion in the spec.md output file, not in validation-checklist.md.

### Step 3: Generate Hardware Behavior Specification

**Objective**: Create comprehensive hardware specification documenting all device behaviors from the Hardware Specification Document analysis.

Load the full content of `templates/spec-template.md` to use as the foundation for the specification.

Write the specification to SPEC_FILE by filling in the placeholders and completing all sections of the loaded template based on your analysis from Step 2. **Do not omit any sections from the template, including all checklists and boilerplate text.**

When completing the template, pay special attention to the **Hardware Behavior Documentation**:
- Describe WHAT the hardware does, not HOW to implement it
- Document software-visible behaviors precisely
- Include software/hardware interaction flows
- Specify register side-effects and cross-dependencies
- Define state machines and operational modes
- Document timing requirements and ordering constraints

---

#### 3.1: [NEEDS CLARIFICATION] Marker Guidelines

Follow these principles when marking unclear requirements:

1. **Never Guess Principle**
   - **IF** you don't know something → **THEN** mark `[NEEDS CLARIFICATION: specific question]`
   - **NEVER** infer, assume, or guess unstated requirements

2. **Test-Driven Thinking**
   - **BEFORE** writing any requirement → **ASK** "Can I write a test for this without guessing?"
   - **IF** answer is NO → **THEN** mark for clarification

3. **Be Specific**
   - **BAD**: `[NEEDS CLARIFICATION: interrupt unclear]`
   - **GOOD**: `[NEEDS CLARIFICATION: interrupt type - level-triggered or edge-triggered?]`
   - Provide options when possible to guide the user

4. **Common Areas to Check** (High Priority):
   - Interrupt behavior: Level-triggered or edge-triggered?
   - Register side effects: What happens on read/write?
   - Reset values: Default/reset value for each register and bit field?
   - Reset behavior: What state after reset?
   - Error handling: How are errors detected and reported?
   - Register access types: Correct type (R/W, R/O, W/O, W1C)?
   - Signal types: Direction, triggering, assertion/clear conditions?

5. **NOT Required for Functional Models** (do NOT mark as [NEEDS CLARIFICATION]):
   - Precise cycle-accurate timing requirements
   - Checkpoint/restore implementation details
   - Performance targets (unless explicitly part of spec)

---

#### 3.2: Functional Requirements Generation

When generating requirements in the "Functional Requirements" section:

1. **Coverage Requirements**:
   - Minimum 5 requirements covering key device capabilities
   - Each requirement must comprehensively cover aspects from Hardware Specification
   - Organize by logical capability groups (core functionality, registers, states, interfaces, errors)

2. **Requirement Structure** - Use this exact format:

```
### Requirement [N]: [Requirement Title - Descriptive Capability Name]

**User Story**: As a [role/stakeholder], I want [desired capability], so that [business/technical benefit]

**Acceptance Criteria**:
1. THE device SHALL [mandatory behavior from Hardware Specification with observable outcome]
2. WHEN [specific condition from state machine/flows], THE device SHALL [action with measurable result]
3. THE device SHALL provide [register/interface/signal] with [specific attributes from Hardware Specification]
4. WHILE in [device state], THE device SHALL [continuous behavior requirement]
5. THE device SHALL NOT [prohibited action or invalid state] under [specific conditions]

*[Additional numbered criteria as needed - minimum 5 per requirement]*
```

3. **Acceptance Criteria Patterns**:
   - **"THE device SHALL [behavior]"**: Unconditional mandatory behavior
   - **"WHEN [condition], THE device SHALL [action]"**: Conditional behavior with trigger
   - **"WHILE [state], THE device SHALL [continuous behavior]"**: State-dependent ongoing behavior
   - **"THE device SHALL NOT [prohibited action] under [conditions]"**: Negative constraint

4. **Key Extraction Principles**:
   - Each requirement MUST be testable without guessing
   - Use SHALL for all mandatory behaviors (not "will", "should", "may")
   - Each requirement must be verifiable through observable hardware behavior (register reads, signal states, state indicators)
   - **Register side-effects**: Explicitly document what happens beyond storing the value (counter reloads, interrupt clears, state changes)
   - Cross-reference sections: side-effects often appear in flows, not register definitions
   - Mark unclear behaviors with [NEEDS CLARIFICATION: specific question]

5. **Testability Check**:
   - Before writing each requirement, ask: "Can I write a test for this without guessing?"
   - If answer is NO, mark for clarification instead of guessing

---

#### 3.3: Test Scenario Generation

When generating test scenarios in the "User Scenarios & Testing" section, use this format:

```
[N]. **Scenario [N]: [Scenario Name]**
   - **States**: [INITIAL_STATE] → [INTERMEDIATE_STATE] → [FINAL_STATE]
   - **Flow**: Flow [X] ([Flow Name])
   - **Requirements**: Requirement [Y] ([requirement description])
   - **Given** [initial device state and preconditions]
   - **When** [software action or hardware event]
     1. [Specific action/step 1]
     2. [Specific action/step 2]
   - **Then** [expected device behavior and observable changes]
     - [Observable outcome 1]
     - [Observable outcome 2]
   - **Test Validation**:
     - [How to verify outcome 1]
     - [How to verify outcome 2]
```

Each scenario MUST explicitly reference:
- **Device States**: Which states are involved (from Device States and Transitions section)
- **Operational Flow**: Which flow it validates (from Software/Hardware Interaction Flows section)
- **Requirements**: Which requirements it verifies (from Functional Requirements section)

This ensures complete traceability from hardware specification → requirements → test scenarios.

---

#### 3.4: Finalize Specification

After completing all sections of the specification:

1. **List All Clarifications**: In the "Clarifications Required" section, list all `[NEEDS CLARIFICATION: ...]` markers found in the document
2. **Count Markers**: Count total number of clarification markers (ignore markers in instructions/headers)
3. **Update Status Field**: At the top of spec.md:
   - If ZERO markers → Status: `"Ready for Planning"`
   - If 1+ markers → Status: `"Draft ([N] clarifications needed)"`
4. **Mark Completion**: Check all applicable boxes in the "Specification Generation Status" section

Then immediately proceed to Step 5 to commit.

### Step 4: Generate IP-XACT Register Description XML

**Objective**: Create machine-readable register map with comprehensive side-effect documentation for DML code generation.

Load `templates/register-template.md` for complete XML structure reference and examples.

---

#### 4.1: Generate Component Identification

Use extracted device information:
- `[VENDOR_NAME]`: Organization/company name (e.g., "ARM", "Intel", "MyCompany")
- `[LIBRARY_NAME]`: Library category (e.g., "AMBA_Devices", "Timers", "Controllers")
- `[IP_NAME]`: Device name from specification (e.g., "Watchdog_Timer", "UART", "GPIO")
- `[VERSION]`: Version string (e.g., "1.0", "2.0.1")

See **register-template.md Section 1** for XML structure.

#### 4.2: Generate Bus Interface (if applicable)

Determine bus type from Step 2.3 extraction:
- **APB (Advanced Peripheral Bus)**: `vendor="AMBA" library="AMBA4" name="APB4" version="r0p0"`
- **AXI4-Lite**: `vendor="AMBA" library="AMBA4" name="AXI4-Lite" version="r0p0"`
- **AXI4**: `vendor="AMBA" library="AMBA4" name="AXI4" version="r0p0"`

Configure as slave or master with memory map reference.

See **register-template.md Section 2** for XML structure.

#### 4.3: Generate Memory Map

Use extracted address block information from Step 2.2:
- `[MEMORY_MAP_NAME]`: Descriptive name (e.g., "RegisterMap", "ControlRegisters")
- `[BLOCK_NAME]`: Address block name (e.g., "MainBlock", "ControlBlock")
- `[BASE_ADDRESS]`: Starting address in hex (typically `0x0` for device-relative addressing)
- `[RANGE]`: Total address space size in hex (highest register offset + register size, rounded to next power of 2)
- `[WIDTH]`: Data bus width in bits (typically `32`)

See **register-template.md Section 3** for XML structure.

#### 4.4: Generate Register Definitions

**MANDATORY**: Create `<ipxact:register>` element for **EVERY** register extracted in Step 2.2, **regardless of whether they have side-effects or not**.

For EACH register, generate register definition with:
- Basic properties: name, addressOffset, size, access type
- Volatile flag (true for hardware-updated registers, false for control registers)
- Reset value and mask
- **CRITICAL**: Comprehensive `<ipxact:description>` including:
  - Functional purpose
  - Read side-effects (from Step 2.4.3) - if none, explicitly state "No read side-effects"
  - Write side-effects (from Step 2.4.4) - if none, explicitly state "No write side-effects"
  - Cross-register dependencies (from Step 2.4.2) - if none, omit this section
  - Lock/protection constraints (from Step 2.4.2) - if none, omit this section

**Important**: Do NOT skip registers without side-effects. Simple control/status registers still need full register definitions with descriptions stating they have no side-effects.

See **register-template.md Section 4** for XML structure and examples.

#### 4.5: Generate Field Definitions

For EACH field within EACH register (from Step 2.2), generate field definition with:
- bitOffset = LSB of bit range
- bitWidth = (MSB - LSB + 1)
- Access type (may differ from register-level)
- **CRITICAL**: Field-level `<ipxact:description>` including:
  - Field purpose
  - Field-specific side-effects (from Step 2.4.5)
  - Conditions (e.g., "ignored if locked", "write 1 to clear")
  - Cross-register effects
- Enumerated values (if defined in Step 2.2)

See **register-template.md Section 4.2-4.3** for XML structure and examples by behavior type.

#### 4.6: Generate Port Definitions (if applicable)

For EACH I/O signal extracted in Step 2.3:
- Scalar ports (1-bit): clock, reset, interrupt, enable signals
- Vector ports (multi-bit): data buses, address lines, status signals
- Direction: in, out, or inout
- Wire type: std_logic (scalar) or std_logic_vector (vector)

See **register-template.md Section 5** for XML structure.

---

#### 4.7: Validate and Finalize XML

Before saving, validate your XML against **Section 2** of `templates/validation-checklist.md` (**reference only - do not edit that file**):

**Quick self-check** (see validation-checklist.md for comprehensive criteria):
- XML structure complete (component, busInterfaces, memoryMaps, ports)
- Every register and field has comprehensive description
- All side-effects and cross-dependencies documented
- All data accurate (addresses, sizes, access types, reset values)
- No placeholder values remaining

**Note**: validation-checklist.md is a reference guide. You verify against it, but the XML file itself is your output.

**Output**: Create file `[device-name]-registers.xml` in the same directory as SPEC_FILE.

Then immediately proceed to Step 5 to commit.

---

### Step 5: MANDATORY Git Commit

**Execute this step after completing Step 3 (spec.md) OR Step 4 (XML)**

**CRITICAL**: Execute these commands using run_in_terminal tool. Do NOT skip this step.

Stage and commit changes:
```bash
cd [SPECS_DIR]
git add spec.md
# If XML was generated:
git add [device-name]-registers.xml
git commit -m "specify: [feature-name] - [description]"
```

**Verify commit**:
```bash
git log --oneline -1
```

**Commit Message Examples**:
- After step 3: `"specify: watchdog-timer - initial hardware specification"`
- After step 4: `"specify: watchdog-timer - added IP-XACT register XML with side-effects"`
- After updates: `"specify: watchdog-timer - clarified interrupt behavior"`

**Purpose**: Creates audit trail for tracking specification evolution, decision rationale, and enabling version rollback.

Then proceed to Step 6 to report completion.

---

### Step 6: Report Completion

Report completion with:
- Branch name
- Spec file path
- XML file path (if generated)
- Number of `[NEEDS CLARIFICATION]` markers (if any)
- Readiness for the next phase (`/plan`)
- **Git commit hash**

**Example completion message**:
```
✅ Hardware specification complete for watchdog-timer

Branch: 001-watchdog-timer
Spec: .kiro/specs/001-watchdog-timer/spec.md
XML: .kiro/specs/001-watchdog-timer/watchdog-timer-registers.xml

Status: Ready for planning (0 clarifications needed)
Git Commit: abc1234 - specify: watchdog-timer - initial hardware specification

Next step: Use /plan to generate technical implementation plan
```

---

## Key Principles for Hardware IP Specification

**Core Philosophy**: Document WHAT the hardware does (functional behavior), not HOW to implement it (DML/code details).

### 1. Hardware Behavior Focus
- Describe observable device behaviors from software perspective
- Document state machines, transitions, and operational flows
- Specify register side-effects and cross-dependencies explicitly
- Define timing requirements and ordering constraints

### 2. Software Visibility
- Emphasize what software CAN observe: register values, interrupt signals, output pins
- Clarify what software CANNOT observe: internal FSM states, clock dividers, intermediate states
- Document software/hardware interaction sequences (initialization, interrupt handling, error recovery)

### 3. Side-Effect Documentation
- Thoroughly document ALL register read/write side-effects
- Cross-reference sections: side-effects often appear in flows, not register definitions
- Document register relationships and cross-dependencies bidirectionally
- Specify lock/protection mechanisms, reload/copy behaviors, enable/disable gating

### 4. Testability First
- Every requirement MUST be testable through observable behavior
- Use test-driven thinking: "Can I write a test without guessing?"
- Create complete traceability: Hardware Spec → Requirements → Test Scenarios
- Ensure each state, transition, and flow has at least one test scenario

### 5. Precision Over Assumptions
- Mark ambiguities with [NEEDS CLARIFICATION: specific question]
- NEVER guess or infer unstated requirements
- Provide options when possible to guide clarification
- Document NOT required: cycle-accurate timing, checkpoint/restore, performance (unless specified)

### 6. Comprehensive Coverage
- Extract from ALL hardware specification aspects: registers, interfaces, states, flows, ordering, memory
- Minimum quality bars: 5+ requirements, 3+ test scenarios
- Organize by logical capability groups: core functionality, registers, states, interfaces, errors
- Ensure bidirectional documentation: every requirement validates a behavior, every behavior has a requirement

**Note**: The script creates and checks out the new branch and initializes the spec file before writing.

