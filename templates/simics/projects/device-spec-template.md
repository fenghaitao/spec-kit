# Device Model Specification: [DEVICE_NAME]

**Feature Branch**: `[###-device-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: Device description: "$ARGUMENTS"

## Execution Flow (simics-device)
```
1. Parse device description from Input
   → If empty: ERROR "No device description provided"
2. Extract device characteristics from description
   → Identify: device type, interfaces, behavioral requirements, performance constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill Device Behavioral Model section
   → If no clear behavior: ERROR "Cannot determine device functionality"
5. Generate Register Interface Specifications
   → Each register must be clearly defined
   → Mark ambiguous register definitions
6. Define Memory Interface Requirements
7. Specify Simics Interface Implementation needs
8. Generate Validation Scenarios
9. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
10. Return: SUCCESS (device spec ready for implementation planning)
```

---

## ⚡ Device Modeling Guidelines
- ✅ Focus on BEHAVIOR and INTERFACES the device provides
- ❌ Avoid HOW to implement in DML/Python (no code structure, specific API calls)
- 🔧 Written for hardware architects and simulation developers

### Section Requirements
- **Mandatory sections**: Must be completed for every device model
- **Optional sections**: Include only when relevant to the device
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a device description:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption needed
2. **Don't guess interface details**: If description doesn't specify register layout, mark it
3. **Think like a validator**: Every vague requirement should fail the "testable and unambiguous" check
4. **Common underspecified areas**:
   - Register bit field definitions and access patterns
   - Memory address space requirements
   - Interface timing and synchronization requirements
   - Reset and initialization behavior
   - Error handling and exception conditions
   - Performance and power requirements

---

## Device Overview *(mandatory)*

### Device Type and Purpose
[Describe what this device is and its role in the target system]

### Target System Context
- **System Architecture**: [Target hardware platform/architecture]
- **Simulation Purpose**: [Software development/validation/research/education]
- **Abstraction Level**: [Functional/Cycle-accurate/Mixed-level modeling]

### Integration Requirements
- **Required Simics Interfaces**: [processor_info_v2, int_register, memory_space, etc.]
- **System Interconnections**: [Bus connections, memory mappings, interrupt lines]
- **Dependencies**: [Other device models, system components]

## Device Behavioral Model *(mandatory)*

### Core Functionality
[Describe the primary functions this device performs in natural language]

### State Management
- **Device States**: [Operational states the device can be in]
- **State Transitions**: [What triggers state changes]
- **Reset Behavior**: [How device responds to system reset]

### Data Processing
- **Input Data**: [What data the device receives and from where]
- **Processing Logic**: [How the device transforms or processes data]
- **Output Generation**: [What outputs the device produces]

## Register Interface Specifications *(mandatory)*

### Register Map Overview
| Offset | Name | Width | Access | Description |
|--------|------|-------|--------|-------------|
| [0x00] | [REG_NAME] | [32-bit] | [RW/RO/WO] | [Register function] |

*Example of marking unclear register definitions:*
- **Control Register**: [NEEDS CLARIFICATION: specific control bits not defined]
- **Status Register**: [NEEDS CLARIFICATION: status bit meanings not specified]

### Register Bit Fields
#### [REGISTER_NAME] (Offset: [0xXX])
| Bits | Field | Access | Reset | Description |
|------|-------|--------|-------|-------------|
| [31:24] | [FIELD_NAME] | [RW] | [0x00] | [Field function] |

### Access Patterns and Restrictions
- **Byte Access**: [Supported/Not supported]
- **Unaligned Access**: [Behavior when accessing unaligned addresses]
- **Read/Write Ordering**: [Any ordering requirements or side effects]

## Memory Interface Requirements *(mandatory)*

### Address Space Requirements
- **Base Address**: [Required base address or address range]
- **Address Space Size**: [Total memory space needed]
- **Address Decoding**: [How addresses map to internal resources]

### Memory Access Patterns
- **Read Behavior**: [Normal reads, side effects, caching implications]
- **Write Behavior**: [Write effects, write-through/write-back, buffering]
- **Access Timing**: [Setup/hold times, wait states, burst capabilities]

### Cache and Memory Coherency
- **Cacheable Regions**: [Which address ranges can be cached]
- **Coherency Requirements**: [Memory coherency protocol participation]
- **DMA Capabilities**: [Direct memory access support if applicable]

## Simics Interface Implementation *(mandatory)*

### Required Simics Interfaces
#### processor_info_v2 Interface
- **Methods to Implement**: [get_processor_info, get_current_context, etc.]
- **Context Management**: [How device manages execution contexts]
- **Exception Handling**: [Exception generation and handling]

#### int_register Interface  
- **Register Access Methods**: [read_register, write_register implementations]
- **Register Banking**: [Multiple register banks if applicable]
- **Access Validation**: [Permission checking, reserved bit handling]

#### memory_space Interface
- **Memory Operation Methods**: [read, write, get_physical_address]
- **Address Translation**: [Virtual to physical address mapping]
- **Memory Protection**: [Access control and protection mechanisms]

### Event Handling Requirements
- **Interrupt Generation**: [When and how device generates interrupts]
- **Event Scheduling**: [Timed events, periodic operations]
- **Callback Registration**: [External event notifications]

## Integration and Connectivity *(include if device has external interfaces)*

### System Bus Connections
- **Bus Type**: [AHB, AXI, PCIe, custom bus protocol]
- **Bus Width**: [Data bus width and addressing capabilities]
- **Transfer Types**: [Supported transfer modes and protocols]

### Interrupt Handling
- **Interrupt Lines**: [Number and types of interrupt outputs]
- **Interrupt Conditions**: [Events that trigger interrupts]
- **Interrupt Priorities**: [Priority levels and arbitration]

### Clock and Reset Interfaces
- **Clock Domains**: [Clock inputs and frequency requirements]
- **Reset Signals**: [Reset types and reset sequence requirements]
- **Power Management**: [Power states and transitions if applicable]

## Validation and Testing Scenarios *(mandatory)*

### Functional Validation
1. **Register Access Validation**
   - **Given** device is initialized, **When** reading each register, **Then** default values returned
   - **Given** device is operational, **When** writing valid data to writable registers, **Then** data is stored correctly
   - **Given** device is operational, **When** writing to read-only registers, **Then** writes are ignored

2. **Behavioral Validation**
   - **Given** [specific device state], **When** [triggering condition], **Then** [expected behavior]
   - **Given** [input condition], **When** [device processes], **Then** [expected output]

3. **Integration Validation**
   - **Given** device connected to system, **When** system boot sequence, **Then** device initializes correctly
   - **Given** multiple devices present, **When** inter-device communication, **Then** protocols work correctly

### Performance Validation
- **Throughput Requirements**: [Expected data processing rates]
- **Latency Requirements**: [Response time expectations]
- **Resource Usage**: [Memory footprint, CPU utilization in simulation]

### Error Scenario Testing
- **Invalid Access Patterns**: [How device handles invalid register accesses]
- **Boundary Conditions**: [Behavior at maximum/minimum operational limits]
- **Fault Injection**: [Response to simulated hardware faults]

---

## Review & Acceptance Checklist
*GATE: Automated checks run during simics-device execution*

### Device Model Completeness
- [ ] No implementation details (DML code, Python classes, Simics API calls)
- [ ] Focused on device behavior and interface requirements
- [ ] Written for hardware architects and simulation developers
- [ ] All mandatory sections completed for device type

### Interface Specification Quality
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Register specifications are complete and unambiguous
- [ ] Memory interface requirements are clearly defined
- [ ] Simics interface requirements are specified
- [ ] Validation scenarios cover functional and integration testing

### Simics Integration Readiness
- [ ] Required Simics interfaces identified
- [ ] Interface method requirements specified
- [ ] Integration points with system clearly defined
- [ ] Validation approach addresses simulation-specific concerns

---

## Execution Status
*Updated by simics-device main() during processing*

- [ ] Device description parsed
- [ ] Device characteristics extracted
- [ ] Ambiguities marked
- [ ] Behavioral model defined
- [ ] Register interface specified
- [ ] Memory requirements defined
- [ ] Simics interfaces identified
- [ ] Validation scenarios generated
- [ ] Review checklist passed

---