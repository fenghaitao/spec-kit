# Simics Integration Summary

This document summarizes the integration of Simics model development capabilities into the spec-kit system.

## Overview

The Simics Device Implementation Guidelines from `docs/simics-model-development-guide.md` have been fully integrated into the spec-kit workflow through template enhancements. This allows hardware device modeling projects to seamlessly use the existing `/specify`, `/plan`, and `/tasks` commands while receiving Simics-specific guidance and structure.

## Integration Approach

The integration was implemented by enhancing the core templates that the commands use, rather than modifying the command files themselves. This preserves existing functionality while adding comprehensive Simics support.

## Files Modified

### 1. Specification Template (`templates/spec-template.md`)

**Changes:**
- Added **Hardware Specification** section for Simics projects
- Updated section requirements to include Simics-specific guidance
- Added detection note for hardware device modeling projects

**New Section Added:**
```markdown
### Hardware Specification *(Simics projects only)*
- **Device Type**: [e.g., Network controller, Storage device, Memory controller]
- **Register Map**: [High-level register categories and their purposes]
- **External Interfaces**: [Ports, connections, and protocols the device supports]
- **Software Visibility**: [What aspects of the device software can observe/control]
```

### 2. Implementation Plan Template (`templates/plan-template.md`)

**Changes:**
- Enhanced **Technical Context** section with Simics-specific examples:
  - Language: DML 1.4
  - Dependencies: Simics API
  - Testing: Simics test scripts
  - Platform: Simics 6.x
  - Project Type: Added `simics` option
  - Performance Goals: functional accuracy
  - Constraints: software-visible behavior
  - Scale/Scope: register count/complexity

- Added **Simics project structure** option:
```
# Option 4: Simics device project
device-name/
├── device-name.dml          # Main device implementation
├── registers.dml            # Register definitions
├── interfaces.dml           # External interfaces
├── utility.dml             # Common utilities
└── tests/
    ├── unit/               # DML unit tests
    └── integration/        # System-level tests
```

- Enhanced **Phase 0 Research** with Simics-specific research tasks:
  - Research DML syntax and device modeling patterns
  - Research Simics API for memory operations and interfaces
  - Analyze hardware specification for register mapping
  - Research similar device implementations for reference

- Updated **Phase 1 Design** to include:
  - Register definitions, interfaces, and device state in data-model.md
  - Register access contracts and interface specifications
  - Register read/write behavior tests
  - Device operational workflow tests

- Updated execution flow to detect `simics=hardware device` projects

### 3. Tasks Template (`templates/tasks-template.md`)

**Changes:**
- Added **Simics path conventions**: `device-name/`, `device-name/tests/` at repository root

- Added comprehensive **Simics examples** for all phases:

**Setup Example:**
```
- [ ] T001 Create device directory structure (device-name/, tests/)
- [ ] T002 Initialize DML project with Simics module dependencies
- [ ] T003 [P] Configure DML syntax checking and validation tools
```

**TDD Example:**
```
- [ ] T004 [P] Register access test in device-name/tests/unit/test_registers.py
- [ ] T005 [P] Interface behavior test in device-name/tests/unit/test_interfaces.py
- [ ] T006 [P] Device workflow test in device-name/tests/integration/test_device_ops.py
- [ ] T007 [P] Memory operation test in device-name/tests/integration/test_memory.py
```

**Implementation Example:**
```
- [ ] T008 [P] Register definitions in device-name/registers.dml
- [ ] T009 [P] Interface declarations in device-name/interfaces.dml
- [ ] T010 [P] Utility methods in device-name/utility.dml
- [ ] T011 Main device structure in device-name/device-name.dml
- [ ] T012 Register read/write logic implementation
- [ ] T013 Device state management and attributes
- [ ] T014 Error handling and logging for device operations
```

**Integration Example:**
```
- [ ] T015 Connect device to memory interface using transact() methods
- [ ] T016 Implement interrupt line connections and events
- [ ] T017 Add external port communications and protocols
- [ ] T018 Integrate with Simics checkpointing and state management
```

- Updated **Task Generation Rules** with Simics patterns:
  - Each register interface → register test task [P]
  - Each register group → DML file task [P]
  - Each device workflow → operational test [P]
  - Ordering: Setup → Tests → Registers → Interfaces → Device → Integration → Polish

- Enhanced **execution flow** to handle Simics document loading:
  - Extract register definitions → DML file tasks

## Files Unchanged

The following command files were intentionally left unchanged to preserve existing functionality:
- `templates/commands/specify.md`
- `templates/commands/plan.md`
- `templates/commands/tasks.md`
- `templates/agent-file-template.md`

## How It Works

### Automatic Detection
The system automatically detects Simics projects through:
1. **Project type detection**: `simics=hardware device` in technical context
2. **Template sections**: Hardware Specification section in spec template
3. **Content analysis**: Device-related keywords in feature descriptions

### Workflow Integration
When working on a Simics device project:

1. **`/specify`**: Creates specification with Hardware Specification section if device modeling is detected
2. **`/plan`**: 
   - Sets project type to `simics`
   - Uses Simics-specific technical context examples
   - Generates Simics project structure
   - Includes Simics research and design tasks
3. **`/tasks`**: 
   - Creates DML-specific task structure
   - Follows hardware development TDD patterns
   - Generates register, interface, and device implementation tasks

### Key Benefits

✅ **Seamless Integration**: Simics projects work within existing workflow  
✅ **No Breaking Changes**: Existing software projects unaffected  
✅ **Comprehensive Coverage**: All phases from specification through implementation  
✅ **Expert Guidance**: Incorporates hardware engineering best practices  
✅ **Flexible Detection**: Automatically adapts to project type  

## Best Practices Integrated

The following Simics best practices from the development guide are now embedded in the templates:

### Core Principles
- **Software-Visible Behavior Focus**: Model only externally visible functionality
- **Register Accuracy**: All registers must be 100% specification-compliant
- **Functional Simulation**: Internal hardware details may be abstracted
- **Information Fidelity**: Base decisions on provided specifications only

### DML Implementation Patterns
- Use `register`s, `attribute`s, and side effects to reflect device behavior
- Implement side effects in `write_register()` and `read_register()` methods
- Use `attribute`s for internal states, configuration, and checkpointing
- Implement `interface`s in `connect` blocks for device communication
- Use `template`s to minimize redundant code
- Implement `event`s for asynchronous handling
- Ensure correct state management for checkpointing

### Development Process
- **Phase 1**: Foundation and Planning (register analysis, interface definition)
- **Phase 2**: Structure Definition (DML declarations with `unimpl`)
- **Phase 3**: Logic Implementation (register operations and side effects)
- **Phase 4**: Validation and Refinement (syntax checking, behavioral compliance)

## Usage Examples

### Example 1: Network Controller
```bash
/specify "Implement a Gigabit Ethernet controller device model for Simics with transmit/receive functionality, interrupt generation, and register-based configuration"
```

This would automatically:
- Include Hardware Specification section in spec
- Set project type to `simics` in plan
- Generate network controller specific tasks

### Example 2: Memory Controller
```bash
/specify "Create a DDR4 memory controller simulation with timing models, refresh logic, and performance counters"
```

This would:
- Detect hardware device modeling
- Plan with DML/Simics technical context
- Generate memory controller implementation tasks

## Conclusion

The Simics integration provides comprehensive support for hardware device modeling within the existing spec-kit framework. The integration maintains backward compatibility while adding sophisticated hardware development capabilities, making the system suitable for both software and hardware engineering projects.