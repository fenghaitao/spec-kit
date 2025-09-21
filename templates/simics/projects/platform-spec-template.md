# Virtual Platform Specification: [PLATFORM_NAME]

**Feature Branch**: `[###-platform-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: Platform description: "$ARGUMENTS"

## Execution Flow (simics-platform)
```
1. Parse platform description from Input
   → If empty: ERROR "No platform description provided"
2. Extract system characteristics from description
   → Identify: target hardware, component list, performance requirements, use cases
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill System Architecture section
   → If no clear topology: ERROR "Cannot determine system architecture"
5. Generate Device Integration Requirements
   → Each device connection must be specified
   → Mark ambiguous integration points
6. Define Memory Map and Address Space
7. Specify Timing and Synchronization Model
8. Generate Configuration Management Requirements
9. Define Platform Validation Scenarios
10. Run Review Checklist
    → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
    → If implementation details found: ERROR "Remove tech details"
11. Return: SUCCESS (platform spec ready for implementation planning)
```

---

## ⚡ Virtual Platform Guidelines
- ✅ Focus on SYSTEM ARCHITECTURE and INTEGRATION requirements
- ❌ Avoid HOW to implement in Simics (no configuration scripts, specific API usage)
- 🏗️ Written for system architects and platform developers

### Section Requirements
- **Mandatory sections**: Must be completed for every virtual platform
- **Optional sections**: Include only when relevant to the platform
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a platform description:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption needed
2. **Don't guess system details**: If description doesn't specify component connections, mark it
3. **Think like a system integrator**: Every vague requirement should fail the "implementable and unambiguous" check
4. **Common underspecified areas**:
   - Memory map organization and address assignments
   - Device interconnection topology and protocols
   - Timing relationships and synchronization requirements
   - Configuration parameter ranges and dependencies
   - Performance targets and scalability requirements
   - Boot sequence and initialization ordering

---

## Platform Overview *(mandatory)*

### Target System Description
[Describe the hardware system being modeled and its intended use]

### Simulation Purpose and Scope
- **Primary Use Case**: [Software development/Hardware validation/Education/Research]
- **Target Software**: [OS types, applications, firmware that will run on platform]
- **Abstraction Level**: [Functional/Cycle-accurate/Mixed-level modeling]
- **Simulation Performance Goals**: [Target simulation speed, host resource usage]

### Platform Characteristics
- **System Complexity**: [Number of cores, devices, memory hierarchy levels]
- **Target Accuracy**: [Functional correctness vs. timing accuracy requirements]
- **Extensibility Requirements**: [Ability to add/modify components]

## System Architecture *(mandatory)*

### Component Topology
[Describe the high-level system organization and component relationships]

### Processing Elements
| Component | Type | Quantity | Architecture | Purpose |
|-----------|------|----------|--------------|---------|
| [CPU_NAME] | [Processor] | [Count] | [ISA/Version] | [Primary computation] |
| [DSP_NAME] | [DSP] | [Count] | [Architecture] | [Signal processing] |

### Memory Hierarchy
| Level | Type | Size | Location | Characteristics |
|-------|------|------|----------|-----------------|
| [L1] | [Cache] | [Size] | [On-chip] | [Access time, associativity] |
| [DRAM] | [Main Memory] | [Size] | [External] | [Bandwidth, latency] |

### System Interconnect
- **Primary Bus**: [Bus type, width, protocol]
- **Secondary Buses**: [Additional interconnects for specific subsystems]
- **Bridge Components**: [Bus bridges, protocol converters]
- **Arbitration**: [Bus arbitration mechanisms, priority schemes]

## Device Integration Requirements *(mandatory)*

### Device Component List
| Device | Model/Type | Interfaces | Address Range | Dependencies |
|--------|------------|------------|---------------|--------------|
| [DEVICE_NAME] | [Model] | [Bus, IRQ] | [Base-Size] | [Prerequisites] |

*Example of marking unclear integration requirements:*
- **Network Controller**: [NEEDS CLARIFICATION: specific network interface type not specified]
- **Storage Controller**: [NEEDS CLARIFICATION: SATA/NVMe/eMMC interface not defined]

### Interface Connections
#### Bus Connections
- **System Bus Topology**: [How devices connect to main system bus]
- **Device-to-Device Connections**: [Direct device interconnections]
- **Bus Hierarchy**: [Multi-level bus organization if applicable]

#### Interrupt Routing
- **Interrupt Controller**: [Type and configuration]
- **IRQ Assignments**: [Interrupt line assignments for each device]
- **Priority Levels**: [Interrupt priority organization]

#### Clock Distribution
- **Clock Sources**: [System clock generators and frequencies]
- **Clock Domains**: [Different clock domains and relationships]
- **Clock Gating**: [Power management through clock control]

## Memory Map and Address Space *(mandatory)*

### Global Address Map
| Base Address | End Address | Size | Component | Access Type |
|--------------|-------------|------|-----------|-------------|
| [0x00000000] | [0x0FFFFFFF] | [256MB] | [ROM/Boot] | [RO] |
| [0x10000000] | [0x1FFFFFFF] | [256MB] | [RAM] | [RW] |
| [0x40000000] | [0x4FFFFFFF] | [256MB] | [Devices] | [RW] |

### Device Address Assignments
#### [DEVICE_SUBSYSTEM_NAME]
| Device | Base Address | Size | Register Map |
|--------|--------------|------|--------------|
| [DEVICE] | [0xXXXXXXXX] | [Size] | [Register layout reference] |

### Memory Protection and Access Control
- **Memory Protection Units**: [MPU/MMU configuration if applicable]
- **Access Permissions**: [Read/write/execute permissions by memory region]
- **Secure/Non-secure Regions**: [Security domain assignments if applicable]

## Timing and Synchronization Model *(mandatory)*

### Clock Domain Organization
- **Primary Clock Domain**: [System clock frequency and source]
- **Peripheral Clock Domains**: [Different clock domains for device subsystems]
- **Clock Relationships**: [PLL configurations, divider ratios]

### Synchronization Requirements
- **Bus Synchronization**: [Clock domain crossing handling]
- **Device Synchronization**: [Inter-device timing coordination]
- **Memory Access Timing**: [Memory controller timing parameters]

### Performance Requirements
- **Bus Bandwidth**: [Required data transfer rates]
- **Memory Bandwidth**: [Memory subsystem performance targets]
- **Interrupt Latency**: [Maximum interrupt response times]

## Configuration Management *(mandatory)*

### System Configuration Parameters
| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| [CLOCK_FREQ] | [Integer] | [Range] | [Default] | [System clock frequency] |
| [MEMORY_SIZE] | [Size] | [Range] | [Default] | [Main memory configuration] |

### Runtime Configuration Options
- **Boot Configuration**: [Boot source selection, initialization parameters]
- **Memory Configuration**: [Memory size, timing parameters]
- **Device Configuration**: [Device enable/disable, operational parameters]

### Configuration Dependencies
- **Parameter Constraints**: [Valid parameter combinations]
- **Mutual Exclusions**: [Conflicting configuration options]
- **Validation Rules**: [Configuration validation requirements]

## Boot and Initialization Sequence *(include if platform has specific boot requirements)*

### Boot Process Overview
1. **Power-On Reset**: [Initial system state and reset sequence]
2. **Boot ROM Execution**: [Early boot code execution]
3. **Device Initialization**: [Device discovery and initialization order]
4. **Memory Setup**: [Memory controller configuration]
5. **OS Handoff**: [Transition to operating system]

### Device Initialization Order
| Priority | Device/Subsystem | Initialization Requirements | Dependencies |
|----------|------------------|----------------------------|--------------|
| [1] | [Core Systems] | [Basic system setup] | [None] |
| [2] | [Memory Controller] | [Memory interface setup] | [Core Systems] |

### Boot Configuration Options
- **Boot Source Selection**: [ROM, Flash, Network boot options]
- **Debug Mode Support**: [JTAG, serial debug interfaces]
- **Safe Mode Operation**: [Minimal configuration boot option]

## Platform Validation Scenarios *(mandatory)*

### System-Level Functional Validation
1. **Boot Sequence Validation**
   - **Given** platform is powered on, **When** boot sequence executes, **Then** system reaches operational state
   - **Given** various boot configurations, **When** boot process runs, **Then** appropriate software loads

2. **Device Integration Validation**
   - **Given** all devices are configured, **When** inter-device communication occurs, **Then** data transfers correctly
   - **Given** system under load, **When** multiple devices access memory, **Then** arbitration works correctly

3. **Memory System Validation**
   - **Given** memory hierarchy is configured, **When** software accesses memory, **Then** correct data is returned
   - **Given** memory protection is enabled, **When** invalid accesses occur, **Then** appropriate exceptions generated

### Performance Validation
- **Boot Time**: [Maximum acceptable boot time to operational state]
- **Throughput**: [System-level data processing capabilities]
- **Scalability**: [Performance with different configuration options]

### Integration Validation
- **Multi-Device Scenarios**: [Complex interactions between multiple devices]
- **Stress Testing**: [System behavior under high load conditions]
- **Configuration Validation**: [Testing various system configuration options]

### Software Compatibility Validation
- **Operating System Support**: [Target OS boot and operation validation]
- **Application Software**: [Key application software execution validation]
- **Development Tools**: [Debugger, profiler, development tool support]

---

## Review & Acceptance Checklist
*GATE: Automated checks run during simics-platform execution*

### Platform Architecture Completeness
- [ ] No implementation details (Simics configuration scripts, Python setup code)
- [ ] Focused on system architecture and integration requirements
- [ ] Written for system architects and platform developers
- [ ] All mandatory sections completed for platform type

### Integration Specification Quality
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Device integration requirements are complete and unambiguous
- [ ] Memory map is clearly defined with no conflicts
- [ ] Timing and synchronization requirements are specified
- [ ] Configuration management approach is defined

### Platform Validation Readiness
- [ ] System-level validation scenarios defined
- [ ] Performance requirements specified
- [ ] Software compatibility requirements identified
- [ ] Integration testing approach addresses platform-specific concerns

---

## Execution Status
*Updated by simics-platform main() during processing*

- [ ] Platform description parsed
- [ ] System characteristics extracted
- [ ] Ambiguities marked
- [ ] System architecture defined
- [ ] Device integration specified
- [ ] Memory map defined
- [ ] Timing model specified
- [ ] Configuration management defined
- [ ] Validation scenarios generated
- [ ] Review checklist passed

---