# Simics Enhanced Project Structure

This document defines the enhanced project structure for spec-kit projects with Simics integration support.

## Standard Spec-Kit Structure (Preserved)

```
project-root/
├── .specify/
│   ├── memory/
│   │   ├── constitution.md
│   │   └── constitution_update_checklist.md
│   ├── scripts/
│   │   ├── bash/
│   │   └── powershell/
│   └── templates/
│       ├── commands/
│       ├── agent-file-template.md
│       ├── plan-template.md
│       ├── spec-template.md
│       └── tasks-template.md
├── specs/
│   └── [###-feature-name]/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── contracts/
└── [implementation files]
```

## Simics Integration Enhancements

### Enhanced Template Structure

```
.specify/
└── templates/
    ├── commands/
    │   ├── specify.md              # Core command (existing)
    │   ├── plan.md                 # Core command (existing)
    │   ├── tasks.md                # Core command (existing)
    │   ├── simics-device.md        # NEW: Device specification command
    │   ├── simics-platform.md      # NEW: Platform specification command
    │   └── simics-validate.md      # NEW: Validation framework command
    ├── simics/                     # NEW: Simics-specific templates
    │   ├── projects/
    │   │   ├── device-spec-template.md
    │   │   ├── platform-spec-template.md
    │   │   └── validation-template.md
    │   ├── commands/
    │   │   └── [reserved for future command templates]
    │   └── examples/
    │       └── [example specifications and configurations]
    └── [existing core templates]
```

### Enhanced Scripts Structure

```
.specify/
└── scripts/
    ├── bash/
    │   ├── [existing core scripts]
    │   ├── setup-simics-device.sh     # NEW: Device project setup
    │   ├── setup-simics-platform.sh   # NEW: Platform project setup
    │   └── setup-simics-validate.sh   # NEW: Validation framework setup
    └── powershell/
        ├── [existing core scripts]
        ├── setup-simics-device.ps1    # NEW: Device project setup
        ├── setup-simics-platform.ps1  # NEW: Platform project setup
        └── setup-simics-validate.ps1  # NEW: Validation framework setup
```

### Enhanced Specification Structure

For Simics device modeling projects, the specification structure is enhanced:

```
specs/
└── [###-device-name]/              # or [###-platform-name] or [###-validation-name]
    ├── spec.md                     # Core specification (enhanced for Simics)
    ├── plan.md                     # Implementation plan (enhanced for Simics)
    ├── tasks.md                    # Task list (enhanced for Simics)
    ├── contracts/                  # Interface contracts
    │   ├── register-interface.md   # NEW: Register interface specifications
    │   ├── memory-interface.md     # NEW: Memory interface specifications
    │   └── simics-interface.md     # NEW: Simics API interface contracts
    ├── simics/                     # NEW: Simics-specific artifacts
    │   ├── device-config.md        # NEW: Device configuration specification
    │   ├── platform-config.md      # NEW: Platform configuration specification
    │   ├── validation-config.md    # NEW: Validation configuration specification
    │   └── integration-tests.md    # NEW: Simics-specific integration tests
    └── implementation-details/     # Detailed technical specifications
        ├── dml-specification.md    # NEW: DML implementation details
        ├── python-interface.md     # NEW: Python interface implementation
        └── performance-targets.md  # NEW: Performance and timing specifications
```

## Project Type Detection and Structure Selection

### Detection Logic

The enhanced project structure selection depends on specification content analysis:

**Device Model Project** (uses device-enhanced structure):
- Specification contains device behavioral descriptions
- Register interface requirements present
- Simics interface implementation needs identified
- Single device focus with validation scenarios

**Virtual Platform Project** (uses platform-enhanced structure):
- Specification contains system architecture descriptions
- Multiple device integration requirements
- Memory map and address space definitions
- System-level validation scenarios

**Validation Framework Project** (uses validation-enhanced structure):
- Specification focuses on testing and validation
- Test scenario definitions and coverage requirements
- Performance and compliance validation needs
- Automation and reporting requirements

### Structure Adaptation Rules

1. **Preserve Core Structure**: Always maintain spec-kit's core directory structure and workflow
2. **Additive Enhancement**: Add Simics-specific directories and files without removing existing ones
3. **Conditional Inclusion**: Include only relevant Simics directories based on project type
4. **Template Inheritance**: Simics templates extend core templates rather than replace them

## Implementation Guidelines

### Template Processing Priority

1. **Core Templates First**: Process standard spec-kit templates
2. **Simics Enhancement**: Apply Simics-specific template enhancements
3. **Project Type Adaptation**: Select appropriate Simics template variant
4. **Content Integration**: Merge Simics content with core specifications

### File Generation Rules

1. **Core Files**: Always generate standard spec.md, plan.md, tasks.md
2. **Enhanced Content**: Extend core files with Simics-specific sections when applicable
3. **Simics-Specific Files**: Generate additional files in simics/ directory based on project type
4. **Contract Files**: Generate interface contracts in contracts/ directory

### Backward Compatibility

1. **Existing Projects**: Continue to work without modification
2. **New Projects**: Automatically detect Simics integration needs
3. **Mixed Projects**: Support both standard and Simics features in same project
4. **Migration Path**: Provide clear upgrade path for existing projects

## Usage Examples

### Device Model Project Structure

```
specs/001-uart-controller/
├── spec.md                         # Device behavioral specification
├── plan.md                         # DML/Python implementation plan
├── tasks.md                        # Device implementation tasks
├── contracts/
│   ├── register-interface.md       # UART register specifications
│   ├── memory-interface.md         # Memory access patterns
│   └── simics-interface.md         # processor_info_v2, int_register interfaces
├── simics/
│   ├── device-config.md            # UART device configuration
│   └── integration-tests.md        # Device integration test scenarios
└── implementation-details/
    ├── dml-specification.md        # DML register model details
    ├── python-interface.md         # Python callback implementations
    └── performance-targets.md      # Timing and performance requirements
```

### Virtual Platform Project Structure

```
specs/002-arm-development-platform/
├── spec.md                         # Platform architectural specification
├── plan.md                         # System integration implementation plan
├── tasks.md                        # Platform assembly and configuration tasks
├── contracts/
│   ├── system-architecture.md      # Component topology and connections
│   ├── memory-map.md               # Global address space organization
│   └── device-interfaces.md        # Inter-device communication contracts
├── simics/
│   ├── platform-config.md          # System configuration specification
│   └── integration-tests.md        # Platform-level test scenarios
└── implementation-details/
    ├── system-configuration.md     # Simics system configuration details
    ├── device-instantiation.md     # Device model instantiation and connection
    └── boot-sequence.md            # Platform boot and initialization sequence
```

This enhanced project structure maintains full backward compatibility while providing comprehensive support for Simics device modeling and virtual platform development workflows.