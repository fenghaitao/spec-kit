# Simics Integration Guide for Spec-Kit

This guide provides comprehensive instructions for using spec-kit's Simics integration capabilities to develop Intel Simics device models and virtual platforms using specification-driven development methodology.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)  
- [Quick Start](#quick-start)
- [Commands Reference](#commands-reference)
- [Project Structure](#project-structure)
- [Workflow Examples](#workflow-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Simics integration extends spec-kit's specification-driven development approach to support Intel Simics device modeling and virtual platform development. It provides three new commands that generate comprehensive specifications for different aspects of Simics development:

- **`/simics-device`**: Creates device model specifications
- **`/simics-platform`**: Creates virtual platform specifications  
- **`/simics-validate`**: Creates validation framework specifications

These commands work alongside spec-kit's existing `/specify`, `/plan`, and `/tasks` commands to provide a complete development workflow from specification to implementation.

## Prerequisites

### Required Software

- **Spec-Kit**: Latest version with Simics integration support
- **Intel Simics**: Version 6.0 or later (for implementation phase)
- **AI Coding Agent**: One of the supported agents:
  - [Claude Code](https://www.anthropic.com/claude-code)
  - [GitHub Copilot](https://code.visualstudio.com/)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli)
  - [Cursor](https://cursor.sh/)
  - [Qwen Code](https://github.com/QwenLM/qwen-code)
  - [opencode](https://opencode.ai/)

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.11 or later
- **Git**: For version control and branch management
- **Shell**: Bash (Linux/macOS) or PowerShell (Windows)

### Knowledge Prerequisites

- Basic understanding of hardware device modeling
- Familiarity with Simics concepts (devices, interfaces, memory spaces)
- Understanding of specification-driven development principles

## Quick Start

### 1. Initialize a Simics Project

```bash
# Create a new project with Simics support
specify init my-simics-project --ai claude

# Navigate to project directory
cd my-simics-project
```

### 2. Create a Device Model Specification

```bash
# In your AI coding agent, use the simics-device command
/simics-device Create a UART controller device with standard register interface, interrupt support, and configurable baud rate
```

This will:
- Create a new branch (e.g., `1234567890-uart-controller-123`)
- Generate a comprehensive device specification
- Set up project structure with contracts and implementation details
- Prepare for implementation planning

### 3. Generate Implementation Plan

```bash
# Use the standard plan command to create implementation plan
/plan Focus on DML register model with Python callbacks for complex logic
```

### 4. Generate Implementation Tasks

```bash  
# Use the standard tasks command to create actionable tasks
/tasks
```

### 5. Execute Implementation

Follow the generated tasks to implement your device model using Simics DML and Python.

## Commands Reference

### `/simics-device` Command

**Purpose**: Generate comprehensive device model specifications for Simics development.

**Usage**:
```
/simics-device <device_description>
```

**Examples**:
```bash
# UART Controller
/simics-device Create a 16550-compatible UART controller with FIFO support, interrupt generation, and configurable baud rates

# Timer Device  
/simics-device Implement a multi-channel timer device with microsecond resolution, compare match interrupts, and PWM output capability

# Memory Controller
/simics-device Design a DDR4 memory controller with ECC support, bank interleaving, and performance monitoring counters
```

**Generated Artifacts**:
- Device behavioral specification
- Register interface definitions
- Memory interface requirements
- Simics interface specifications
- Validation scenarios

### `/simics-platform` Command

**Purpose**: Generate virtual platform specifications for system-level Simics development.

**Usage**:
```
/simics-platform <platform_description>
```

**Examples**:
```bash
# ARM Development Platform
/simics-platform Create an ARM Cortex-A53 based development platform with 4GB DDR4, Ethernet, UART, and GPIO peripherals

# Embedded IoT Platform
/simics-platform Design a Cortex-M4 based IoT platform with low-power features, sensor interfaces, and wireless connectivity

# Server Platform
/simics-platform Build a dual-socket x86-64 server platform with PCIe expansion, multiple network interfaces, and RAID storage
```

**Generated Artifacts**:
- System architecture specification
- Device integration requirements
- Memory map definitions
- Configuration management
- Platform validation scenarios

### `/simics-validate` Command

**Purpose**: Generate validation framework specifications for comprehensive testing.

**Usage**:
```
/simics-validate <validation_requirements>
```

**Examples**:
```bash
# Device Validation
/simics-validate Create comprehensive validation framework for UART controller including functional tests, performance benchmarks, and regression testing

# Platform Validation  
/simics-validate Design system-level validation suite for ARM development platform with boot testing, device integration, and software compatibility validation

# Performance Validation
/simics-validate Implement performance validation framework with throughput measurement, latency analysis, and scalability testing
```

**Generated Artifacts**:
- Validation strategy and objectives
- Test scenario specifications
- Coverage requirements
- Performance criteria
- Automation framework design

## Project Structure

### Enhanced Directory Layout

When using Simics integration, your project structure is enhanced with additional directories and files:

```
my-simics-project/
├── .specify/                          # Spec-kit configuration
│   ├── templates/
│   │   ├── commands/
│   │   │   ├── simics-device.md       # Device command template
│   │   │   ├── simics-platform.md     # Platform command template
│   │   │   └── simics-validate.md     # Validation command template
│   │   └── simics/                    # Simics-specific templates
│   │       └── projects/              # Project templates
│   └── scripts/
│       ├── bash/
│       │   ├── setup-simics-device.sh
│       │   ├── setup-simics-platform.sh
│       │   └── setup-simics-validate.sh
│       └── powershell/
│           ├── setup-simics-device.ps1
│           ├── setup-simics-platform.ps1
│           └── setup-simics-validate.ps1
├── specs/
│   └── [branch-name]/                 # Feature specifications
│       ├── spec.md                    # Core specification
│       ├── plan.md                    # Implementation plan
│       ├── tasks.md                   # Implementation tasks
│       ├── contracts/                 # Interface contracts
│       │   ├── register-interface.md
│       │   ├── memory-interface.md
│       │   └── simics-interface.md
│       ├── simics/                    # Simics-specific artifacts
│       │   ├── device-config.md
│       │   └── integration-tests.md
│       └── implementation-details/    # Technical specifications
│           ├── dml-specification.md
│           ├── python-interface.md
│           └── performance-targets.md
└── [implementation files]             # Generated code
```

### File Purposes

| File | Purpose | Content |
|------|---------|---------|
| `spec.md` | Core specification | Device/platform behavioral requirements |
| `plan.md` | Implementation plan | Technical approach and architecture |
| `tasks.md` | Implementation tasks | Step-by-step implementation guide |
| `contracts/register-interface.md` | Register contracts | Register map and access patterns |
| `contracts/memory-interface.md` | Memory contracts | Address space and memory behavior |
| `contracts/simics-interface.md` | Simics contracts | Required Simics interfaces |
| `simics/device-config.md` | Device configuration | Simics device configuration spec |
| `simics/integration-tests.md` | Test scenarios | Integration and validation tests |
| `implementation-details/dml-specification.md` | DML details | Detailed DML implementation spec |
| `implementation-details/python-interface.md` | Python details | Python callback implementations |
| `implementation-details/performance-targets.md` | Performance specs | Timing and performance requirements |

## Workflow Examples

### Example 1: UART Controller Development

#### Step 1: Create Device Specification
```bash
/simics-device Create a 16550-compatible UART controller with FIFO buffers, interrupt generation for receive/transmit events, configurable baud rates from 9600 to 115200, and support for hardware flow control
```

**Generated specification includes**:
- UART behavioral model (transmit/receive logic)
- Register interface (THR, RBR, IER, IIR, FCR, LCR, MCR, LSR, MSR)
- Memory interface (8-byte register space at configurable base address)
- Simics interfaces (int_register, processor_info_v2)
- Validation scenarios (register access, data transmission, interrupt handling)

#### Step 2: Create Implementation Plan
```bash
/plan Implement using DML for register model and state machine, Python callbacks for FIFO management and timing, integrate with system interrupt controller
```

**Generated plan includes**:
- DML register bank definition
- Python FIFO implementation
- Interrupt handling strategy
- System integration approach

#### Step 3: Generate Implementation Tasks
```bash
/tasks
```

**Generated tasks include**:
- T001: Create DML device template with register bank
- T002: Implement FIFO management in Python
- T003: Add interrupt generation logic
- T004: Create register access validation tests
- T005: Implement data transmission tests
- T006: Add performance benchmarks

### Example 2: ARM Development Platform

#### Step 1: Create Platform Specification
```bash
/simics-platform Create an ARM Cortex-A53 quad-core development platform with 4GB DDR4 memory, GICv3 interrupt controller, UART console, Ethernet controller, GPIO expander, and SD card interface for storage
```

**Generated specification includes**:
- System architecture (quad-core ARM Cortex-A53)
- Device integration (GICv3, UART, Ethernet, GPIO, SD card)
- Memory map (DDR4 space, device registers, boot ROM)
- Configuration management (CPU frequency, memory size, device enables)
- Platform validation (boot sequence, device interactions, performance)

#### Step 2: Create Implementation Plan
```bash
/plan Focus on Simics system configuration with ARM CPU model, implement custom devices for GPIO and SD card, use existing Simics models for standard peripherals
```

#### Step 3: Generate Implementation Tasks
```bash
/tasks
```

### Example 3: Validation Framework

#### Step 1: Create Validation Specification
```bash
/simics-validate Create comprehensive validation framework for the ARM development platform including functional testing of all devices, performance benchmarking, boot sequence validation, Linux kernel compatibility testing, and automated regression testing
```

**Generated specification includes**:
- Validation strategy (functional, performance, integration, regression)
- Test scenarios (boot tests, device tests, system tests)
- Coverage requirements (feature coverage, interface coverage)
- Performance criteria (boot time, throughput, latency)
- Automation framework (CI/CD integration, result reporting)

## Best Practices

### Specification Writing

1. **Be Specific About Behavior**: Clearly describe what the device or platform does, not how to implement it
2. **Define Clear Interfaces**: Specify register layouts, memory maps, and interface requirements precisely
3. **Include Validation Scenarios**: Always include comprehensive test scenarios for validation
4. **Mark Ambiguities**: Use `[NEEDS CLARIFICATION: question]` for unclear requirements

### Implementation Planning

1. **Start with Interfaces**: Plan Simics interface implementations first
2. **Separate Concerns**: Keep register models in DML, complex logic in Python
3. **Plan for Testing**: Include test implementation in your planning
4. **Consider Performance**: Address timing and performance requirements early

### Task Execution

1. **Follow TDD**: Write tests before implementation
2. **Incremental Development**: Implement and test one feature at a time
3. **Regular Validation**: Run validation tests frequently during development
4. **Document Changes**: Keep specifications updated as implementation evolves

### Project Organization

1. **Use Branches**: Each device/platform gets its own feature branch
2. **Maintain Contracts**: Keep interface contracts updated and synchronized
3. **Version Control**: Commit specifications and implementation together
4. **Review Process**: Use pull requests for specification and implementation review

## Troubleshooting

### Common Issues

#### 1. Script Execution Errors

**Problem**: Simics setup scripts fail with permission errors
**Solution**: 
```bash
# On Linux/macOS
chmod +x scripts/bash/setup-simics-*.sh

# On Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Branch Creation Failures

**Problem**: Git branch creation fails
**Solution**:
```bash
# Ensure you're in a git repository
git init
git add .
git commit -m "Initial commit"

# Then retry the Simics command
```

#### 3. Template Processing Issues

**Problem**: Templates not found or corrupted
**Solution**:
```bash
# Reinitialize project with latest templates
specify init --here --ai your-agent --ignore-agent-tools
```

#### 4. JSON Output Parsing Errors

**Problem**: Scripts produce invalid JSON
**Solution**:
```bash
# Test script manually with debug output
./scripts/bash/setup-simics-device.sh --debug "test device"

# Check PowerShell execution policy
Get-ExecutionPolicy
```

### Getting Help

1. **Check Documentation**: Review this guide and template documentation
2. **Validate Setup**: Use `specify check` to verify tool installation
3. **Debug Scripts**: Run scripts with `--debug` flag for detailed output
4. **Community Support**: Report issues on the spec-kit GitHub repository

### Performance Optimization

1. **Specification Size**: Keep specifications focused and concise
2. **Template Reuse**: Leverage existing templates rather than creating custom ones
3. **Incremental Updates**: Update specifications incrementally rather than complete rewrites
4. **Parallel Development**: Use parallel task execution where possible

## Advanced Usage

### Custom Templates

You can create custom templates for specific device types or platform architectures:

```bash
# Create custom device template
cp templates/simics/projects/device-spec-template.md templates/simics/projects/custom-device-template.md

# Modify the template for your specific needs
# Update command templates to reference custom template
```

### Integration with CI/CD

Integrate Simics validation into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
name: Simics Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Validation Tests
        run: |
          # Execute validation framework
          ./scripts/bash/run-validation-suite.sh
```

### Multi-Platform Support

Develop platforms targeting multiple architectures:

```bash
# ARM platform
/simics-platform ARM Cortex-A78 server platform with PCIe, DDR5, and network acceleration

# x86 platform  
/simics-platform Intel Xeon server platform with multiple sockets, high-speed I/O, and hardware security features

# RISC-V platform
/simics-platform RISC-V RV64GC development platform with vector extensions and custom acceleration units
```

This completes the comprehensive Simics integration guide for spec-kit.