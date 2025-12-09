# Simics Model Development Constitution

## Core Principles

### I. Device-First Development
Every hardware component starts as a standalone device model—no exceptions. This forces modular design from the start:

- Device models must be self-contained DML modules
- Each device model is independently testable in isolation
- Clear hardware abstraction boundaries with well-defined interfaces
- Device models expose functionality through standardized Simics interfaces
- No monolithic system models - compose from discrete device components

### II. Interface-First Architecture
All device components communicate through well-defined, testable hardware interfaces:

- DML Interface: Registers, ports, and connections defined before logic implementation
- Hardware interfaces specified before behavioral modeling
- Memory-mapped interfaces with clear address space definitions
- Inter-device communication through standardized Simics interfaces
- Register maps documented before register implementation
- Signal and bus protocols defined before device logic

### III. Test-First Development (NON-NEGOTIABLE)
TDD mandatory for all Simics device development:

- Specification tests written → Hardware behavior verified → Tests fail → Then implement DML
- Register access tests, device behavior tests, integration tests with other devices
- Functional simulation validation against hardware specification
- Test vectors derived from hardware specification documents
- Red-Green-Refactor cycle: Test → Fail → Implement → Pass → Refactor
- Behavior verification before implementation complexity

### IV. Specification-Driven Implementation
Base all implementation decisions strictly on provided hardware specifications:

- Hardware specifications drive register definitions and device behavior
- Software-visible behavior must match specification exactly
- Internal implementation may be simplified if not software-visible
- Mark unclear hardware behaviors with [NEEDS CLARIFICATION] and implement as TODO
- No assumptions beyond documented hardware specification
- Reference specification sections in DML comments

### V. Integration Testing Focus
Focus on real-world hardware integration scenarios:

- Device-to-device communication testing
- Software driver compatibility testing
- Platform integration validation
- Memory subsystem interaction testing
- Bus protocol compliance verification
- Interrupt handling and timing validation

### VI. Observability and Transparency
Everything must be inspectable and debuggable in simulation:

- Register states must be inspectable at runtime
- Device state changes must be traceable
- Simulation events must be observable
- Debug interfaces for device inspection
- Comprehensive logging of device operations
- State visibility through Simics CLI and debugging tools

### VII. Versioning and Evolution
MAJOR.MINOR.BUILD format with clear compatibility contracts:

- Device model versioning aligned with hardware specification versions
- Register interface changes require version increment
- Simulation compatibility maintained across device model versions
- Backward compatibility for simulation checkpoints
- Clear migration paths for specification updates

### VIII. Simplicity and Incremental Development
Start simple, add complexity only when proven necessary:

- Model only software-visible behaviors initially
- Add internal complexity only when required for accuracy
- Prefer functional correctness over implementation detail accuracy
- Implement clear abstractions before detailed behaviors
- YAGNI principles for device features - implement what's specified
- Single responsibility per device model and register

### IX. Simics Excellence
Leverage Simics domain expertise and best practices:

- Follow DML coding standards and patterns
- Use Simics templates and utility functions
- Implement proper state management for checkpointing
- Ensure timing and event handling accuracy
- Optimize for simulation performance while maintaining accuracy
- Leverage Simics debugging and inspection capabilities

## Constitutional Compliance Framework

### Specification Phase
- All device projects begin with hardware specification templates
- Device specifications include register maps, interface definitions, and behavioral requirements
- Mark ambiguities with [NEEDS CLARIFICATION] for hardware specification gaps

### Planning Phase
- Constitutional compliance verification for Simics device development
- Technical translation from hardware specifications to DML implementation plans
- Behavioral testing strategy focused on software-visible device functionality

### Implementation Phase
- Simics-specific task generation following device modeling best practices
- Adherence to DML standards while maintaining constitutional principles
- Consistent documentation and validation approaches across all device models

## Amendment Process

Modifications to this constitution require:
- Explicit documentation of the rationale for change
- Review and approval by Simics development team
- Backwards compatibility assessment with existing device models
- Update of all dependent templates and documentation

## Governance

This constitution supersedes all other Simics device development practices. All specification, planning, task generation, and implementation must verify constitutional compliance. When specific device requirements conflict with constitutional principles, the constitution takes precedence unless explicitly documented and justified.

**Version**: 4.0.0 | **Ratified**: 2024-12-19 | **Last Amended**: 2024-12-19

*Major version increment reflects focus on Simics model development as the primary methodology.*