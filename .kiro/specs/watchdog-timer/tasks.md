# Implementation Tasks

## Overview

This document outlines the incremental implementation tasks for the Simics watchdog timer device. The implementation follows a pragmatic approach: set up the project structure first, then implement core functionality with focused testing on critical behaviors.

The implementation leverages Simics MCP (Model Context Protocol) server tools for project setup, device skeleton generation, compilation, and testing. Tasks are organized to build incrementally, with each phase producing a working, testable device.

## Prerequisites

### Environment Setup

- Verify Simics installation and MCP server availability
- Confirm DML 1.4 compiler (dmlc) version 7.57.0+ is available
- Ensure QSP-x86 platform is accessible for integration testing

### MCP Server Tools

The following MCP server tools will be used throughout implementation:

- `mcp_local_server_create_simics_project`: Create new Simics project
- `mcp_local_server_add_dml_device_skeleton`: Generate DML device skeleton
- `mcp_local_server_build_simics_project`: Compile DML device model
- `mcp_local_server_run_simics_test`: Execute test suites
- `mcp_local_server_check_with_dmlc`: Check DML syntax and semantics
- `mcp_local_server_perform_rag_query`: Query Simics documentation and examples

## Task Breakdown

### Phase 1: Project Setup and Basic Structure

- [ ] 1.1 Create Simics Project and Device Skeleton
  - Use MCP tools to create project at `./watchdog-timer-project`
  - Generate watchdog-timer device skeleton
  - Verify project builds successfully
  - _Requirements: All (project foundation)_

- [ ] 1.2 Query DML Examples and Documentation
  - Query register bank implementation patterns
  - Query port and signal interface examples
  - Query event handling patterns
  - Document findings for reference
  - _Requirements: All (implementation guidance)_

### Phase 2: Register Bank Implementation

- [ ] 2.1 Implement Identification Registers
  - Implement WDOGPERIPHID[4-7] at 0xFD0-0xFDC (values: 0x04, 0x00, 0x00, 0x00)
  - Implement WDOGPERIPHID[0-3] at 0xFE0-0xFEC (values: 0x24, 0xB8, 0x1B, 0x00)
  - Implement WDOGPCELLID[0-3] at 0xFF0-0xFFC (values: 0x0D, 0xF0, 0x05, 0xB1)
  - All registers read-only with hard-coded values
  - _Requirements: 7.1-7.8, 8.1-8.4_

- [ ] 2.2 Implement WDOGLOAD Register
  - Register at offset 0x00, size 4 bytes
  - Reset value 0xFFFFFFFF
  - Read-write access
  - _Requirements: 1.1_

- [ ] 2.3 Implement WDOGVALUE Register
  - Add session variable `counter_value` (uint32, init 0xFFFFFFFF)
  - Register at offset 0x04, size 4 bytes
  - Read-only, returns counter_value
  - _Requirements: 1.4, 1.5_

- [ ] 2.4 Implement WDOGCONTROL Register
  - Register at offset 0x08, size 4 bytes, reset value 0x00000000
  - Field INTEN @ [0] - interrupt enable
  - Field RESEN @ [1] - reset enable
  - Field step_value @ [4:2] - counter step (0-4 valid, 5-7 invalid)
  - _Requirements: 2.1, 3.1, 4.1_

- [ ] 2.5 Implement Status Registers
  - Add session variable `interrupt_pending` (bool, init false)
  - WDOGRIS at offset 0x10, read-only, bit[0] = interrupt_pending
  - WDOGMIS at offset 0x14, read-only, bit[0] = (interrupt_pending AND INTEN)
  - _Requirements: 3.4, 3.5, 3.6_

- [ ] 2.6 Implement WDOGINTCLR Register
  - Register at offset 0x0C, write-only
  - after_write method clears interrupt_pending flag
  - Read returns zero
  - _Requirements: 3.7_

- [ ] 2.7 Implement WDOGLOCK Register
  - Add session variable `is_locked` (bool, init false)
  - Register at offset 0xC00, size 4 bytes
  - after_write: if value == 0x1ACCE551 then unlock, else lock
  - Read returns 0 if unlocked, 1 if locked
  - _Requirements: 5.1-5.5_

- [ ] 2.8 Implement Integration Test Registers
  - Add session variable `test_mode_active` (bool, init false)
  - WDOGITCR at offset 0xF00, bit[0] controls test mode
  - WDOGITOP at offset 0xF04, write-only, bit[1]=wdogint, bit[0]=wdogres
  - _Requirements: 6.1-6.4_

### Phase 3: Lock Protection Implementation

- [ ] 3.1 Implement Lock Protection for Control Registers
  - Add bank-level write method checking is_locked
  - Protect WDOGLOAD, WDOGCONTROL, WDOGINTCLR when locked
  - WDOGLOCK always writable
  - Log warnings for lock violations
  - _Requirements: 5.6, 5.7_

### Phase 4: Output Port Implementation

- [ ] 4.1 Implement Interrupt Port
  - Query DML examples for simple_interrupt interface
  - Implement interrupt_port with simple_interrupt interface
  - Add methods to raise/lower interrupt
  - _Requirements: 10.1, 10.3_

- [ ] 4.2 Implement Reset Port
  - Query DML examples for simple_signal interface
  - Implement reset_port with simple_signal interface
  - Add methods to assert/deassert reset
  - _Requirements: 10.2, 10.4_

### Phase 5: Counter and Event Implementation

- [ ] 5.1 Implement Counter Reload Logic
  - Implement reload_counter() method
  - Call reload_counter() when INTEN transitions 0→1
  - Call reload_counter() when WDOGINTCLR written
  - Update counter_value from WDOGLOAD
  - _Requirements: 1.2, 1.3_

- [ ] 5.2 Implement Counter Event
  - Query DML examples for event implementation
  - Declare counter_event in device
  - Implement event callback method
  - Implement schedule_timeout() method
  - _Requirements: All timeout-related_

- [ ] 5.3 Implement Step Value Calculation
  - Implement get_counter_step() method
  - Map step_value: 0→1, 1→2, 2→4, 3→8, 4→16
  - Invalid values (5-7) return 1 with warning
  - _Requirements: 2.2-2.7_

### Phase 6: Timeout and Interrupt Logic

- [ ] 6.1 Implement First Timeout with Interrupt
  - In counter_event callback, check if counter reached zero
  - If INTEN=1, set interrupt_pending=true and raise wdogint port
  - Update WDOGRIS and WDOGMIS accordingly
  - _Requirements: 3.2, 3.3_

- [ ] 6.2 Implement Interrupt Clear
  - Enhance WDOGINTCLR after_write method
  - Clear interrupt_pending flag
  - Lower wdogint port
  - Reload counter from WDOGLOAD
  - _Requirements: 3.7_

- [ ] 6.3 Implement Second Timeout with Reset
  - In counter_event callback, check if interrupt_pending=true
  - If RESEN=1 and interrupt_pending=true, assert wdogres port
  - No reset if interrupt cleared between timeouts
  - _Requirements: 4.2, 4.3, 4.4, 4.5_

### Phase 7: Integration Test Mode

- [ ] 7.1 Implement Test Mode Entry/Exit
  - Implement WDOGITCR after_write method
  - Update test_mode_active flag
  - Suspend counter operation in test mode
  - Resume normal operation on exit
  - _Requirements: 6.2, 6.3_

- [ ] 7.2 Implement Direct Output Control in Test Mode
  - Implement WDOGITOP after_write method
  - Check test_mode_active before driving outputs
  - Drive wdogint from WDOGITOP bit[1]
  - Drive wdogres from WDOGITOP bit[0]
  - _Requirements: 6.5, 6.6, 6.7_

### Phase 8: Logging and Error Handling

- [ ] 8.1 Implement Comprehensive Logging
  - Add log statements for register writes (info level)
  - Add log statements for register reads (debug level)
  - Add log statements for timeout events (info level)
  - Add log statements for interrupt/reset assertions (info/warning level)
  - Add log statements for lock and test mode transitions (info level)
  - _Requirements: 11.1-11.7_

- [ ] 8.2 Implement Error Handling
  - Add validation in get_counter_step() for invalid step_value
  - Add warning logs in lock protection code
  - Add warning logs for read-only register writes
  - Ensure write-only registers return zero on read
  - _Requirements: 11.1-11.7, 12.1-12.7_

### Phase 9: Platform Integration

- [ ] 9.1 Create Platform Configuration Script
  - Create platform configuration script for QSP-x86
  - Map device to address 0x1000 with 4KB space
  - Connect interrupt_port to platform interrupt controller
  - Connect reset_port to platform reset controller
  - _Requirements: 9.1-9.5_

- [ ]* 9.2 Write Platform Integration Tests
  - Test device accessible at base address 0x1000
  - Test all register offsets accessible
  - Test interrupt delivery to platform
  - Test reset signal propagation
  - _Requirements: 9.1-9.5, 10.1-10.5_

### Phase 10: Functional Scenarios and Documentation

- [ ]* 10.1 Write Functional Scenario Tests
  - Scenario 1: Normal watchdog operation with periodic feeding
  - Scenario 2: Watchdog timeout with reset
  - Scenario 3: Lock protection preventing misconfiguration
  - Scenario 4: Integration test mode verification
  - Scenario 5: Multiple timeout cycles
  - Scenario 6: Step value configuration changes
  - _Requirements: All_

- [ ] 10.2 Create Device Documentation
  - Create README.md with device overview
  - Document register map and bit fields
  - Document usage examples
  - Document platform integration steps
  - _Requirements: All_

### Phase 11: Quality Assurance

- [ ]* 11.1 Run Complete Test Suite
  - Run all implemented tests
  - Verify all tests pass
  - Address any failures
  - _Requirements: All_

- [ ] 11.2 Verify Requirements Traceability
  - Review requirements.md
  - Verify all 12 requirements implemented
  - Verify all acceptance criteria met
  - Document any gaps
  - _Requirements: All_

- [ ] 11.3 Final Code Quality Review
  - Run DML syntax and semantic checks with dmlc
  - Review code for style consistency
  - Check documentation completeness
  - Verify all requirements met
  - _Requirements: 12.1-12.7_

## Task Execution Guidelines

### Implementation Workflow

For each task:

1. **Implement**: Write the DML code for the task
2. **Build**: Compile using MCP build tool
3. **Verify**: Check for compilation errors and warnings
4. **Test** (for non-optional test tasks): Write and run tests
5. **Document**: Update comments and documentation

### MCP Server Usage

Throughout implementation, use MCP server tools:

- **Build frequently**: After each implementation step
  ```
  mcp_local_server_build_simics_project(
      project_path="./watchdog-timer-project",
      module="watchdog-timer"
  )
  ```

- **Check syntax**: Before running tests
  ```
  mcp_local_server_check_with_dmlc(
      project_path="./watchdog-timer-project",
      module="watchdog-timer"
  )
  ```

- **Run tests**: After implementing test tasks
  ```
  mcp_local_server_run_simics_test(
      project_path="./watchdog-timer-project"
  )
  ```

- **Query documentation**: When unsure about DML features
  ```
  mcp_local_server_perform_rag_query(
      query="<your question>",
      source_type="docs",
      match_count=5
  )
  ```

### Testing Strategy

- Optional test tasks (marked with *) focus on comprehensive validation
- Core functionality is validated through compilation and basic integration
- Write tests for critical behaviors: timeouts, interrupts, resets, lock protection
- Test edge cases and error conditions where specified

## Success Criteria

The implementation is complete when:

1. All non-optional tasks completed
2. Device compiles without errors or warnings
3. All 12 requirements from requirements.md implemented
4. Design from design.md followed
5. Core functionality verified (register access, counter operation, interrupts, resets)
6. Platform integration working
7. Documentation complete

## Estimated Effort

- Phase 1: 1 hour (setup)
- Phase 2: 3-4 hours (registers)
- Phase 3-4: 2 hours (lock and ports)
- Phase 5-6: 3-4 hours (counter and timeouts)
- Phase 7-8: 2 hours (test mode and logging)
- Phase 9-10: 2-3 hours (integration and docs)
- Phase 11: 1-2 hours (quality)

**Total estimated effort**: 14-18 hours

## Notes

- Follow constitutional principles from constitution.md
- Use DML 1.4 syntax from DML_grammar.md
- Leverage MCP server tools throughout
- Document as you go
- Use RAG queries when stuck on DML syntax or Simics features
- Optional tasks (marked with *) can be skipped for faster MVP delivery
