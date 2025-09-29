# Simics MCP Server Integration - Phase 1

## Overview

This document describes the Phase 1 integration between spec-kit and simics-mcp-server. The integration enhances spec-kit's templates with MCP tool references, enabling automated Simics project setup, building, and testing workflows.

## What Changed

### `templates/plan-template.md` Updates

#### 1. Enhanced Technical Context (Lines 53-58)
Added Simics-specific context fields:
- **Simics Version**: References `get_simics_version()` MCP tool
- **Required Packages**: References `search_packages()` and `install_simics_package()` MCP tools
- **MCP Server**: Notes integration availability
- **Device Type**: Hardware device classification
- **Hardware Interfaces**: Register-level interface definitions

#### 2. Updated Project Structure Comments (Lines 121-125)
Replaced manual project creation with MCP tool workflow:
```markdown
# Use MCP tools for automated project creation:
# 1. `create_simics_project(project_name=DEVICE_NAME, project_path=".")` → generates base structure
# 2. `add_dml_device_skeleton(project_path=".", device_name=DEVICE_NAME)` → adds device modeling files
# 3. `build_simics_project(project_path=".")` → validates build system
# The structure shown below will be created automatically during Phase 3.1 Setup.
```

#### 3. Enhanced Research Tasks (Lines 170-173)
Added MCP-specific research tasks:
- Verify simics-mcp-server connection using `get_simics_version()` MCP tool
- Research available Simics packages using `search_packages()` MCP tool
- Validate required packages using `list_installed_packages()` MCP tool
- Research simics-mcp-server MCP tools for project automation and build management

### `templates/tasks-template.md` Updates

#### 1. MCP-Powered Setup Phase (Lines 53-57)
Replaced manual setup with automated MCP tool calls:
- **T001**: Verify connection with `get_simics_version()`
- **T002**: Create project structure with `create_simics_project(project_name="DEVICE_NAME", project_path=".")`
- **T003**: Install packages with `install_simics_package(package_name, version)`
- **T004**: Add device skeleton with `add_dml_device_skeleton(project_path=".", device_name="DEVICE_NAME")`
- **T005**: Verify build system with `build_simics_project(project_path=".")`

#### 2. Enhanced TDD Phase (Lines 67-70)
Updated test setup with MCP validation:
- **T009**: Set up and validate test environment using `run_simics_test(project_path=".", suite=None)`

#### 3. Build-Integrated Implementation (Lines 82-90)
Added continuous build validation:
- **T013**: Build device module using `build_simics_project(project_path=".", module="DEVICE_NAME")`
- **T018**: Incremental build validation using `build_simics_project(project_path=".")`

#### 4. Comprehensive Integration Testing (Lines 99-104)
Enhanced integration phase with validation:
- **T023**: Validate integration with `build_simics_project(project_path=".")`
- **T024**: Run comprehensive tests using `run_simics_test(project_path=".", suite="all")`

#### 5. Enhanced Task Generation Rules (Lines 154-156)
Updated ordering strategy:
- **Simics**: MCP Setup → Tests → Registers → Interfaces → Device → Integration → Validation → Polish
- **Simics MCP Tools**: Use at each validation step for continuous integration

#### 6. Simics-Specific Validation (Lines 168-173)
Added validation checklist for MCP integration:
- All MCP tool calls specify correct project_path
- Build validation tasks after implementation changes
- Test execution tasks use appropriate suite parameter
- Package installation tasks specify version when known
- Device name consistently used across MCP tool calls

## MCP Tools Referenced

The templates now reference these simics-mcp-server MCP tools:

### Project Management
- `get_simics_version()` - Verify installation and get version info
- `create_simics_project(project_name, project_path)` - Create project structure
- `add_dml_device_skeleton(project_path, device_name)` - Add device modeling files

### Package Management  
- `search_packages(query)` - Search available packages
- `list_installed_packages()` - List installed packages
- `install_simics_package(package_name, version)` - Install packages

### Build & Testing
- `build_simics_project(project_path, module=None)` - Build project or specific module
- `run_simics_test(project_path, suite=None)` - Run test suites

## How to Use

### Prerequisites
1. **simics-mcp-server running**: The MCP server must be accessible
2. **Simics installed**: Valid Simics installation required
3. **MCP client**: Tool to communicate with simics-mcp-server

### Workflow Changes

#### Planning Phase
When using `/plan` command with `Project Type = simics`:
1. Research tasks will include MCP tool verification
2. Technical context will reference MCP tools for package management
3. Project structure comments explain automated setup

#### Task Generation Phase  
When using `/tasks` command on Simics projects:
1. Setup tasks use MCP tools instead of manual commands
2. Build validation integrated throughout implementation
3. Test execution automated with MCP tools

#### Implementation Phase
When executing generated tasks:
1. Run MCP tool calls as specified in task descriptions
2. Validate each step with build/test commands
3. Use continuous integration approach with frequent validation

### Example Usage

#### Research Phase
```bash
# Instead of manual research, tasks will include:
# - "Verify simics-mcp-server connection using `get_simics_version()` MCP tool"
# - "Research available Simics packages using `search_packages()` MCP tool"  
```

#### Setup Phase
```bash
# Instead of manual project creation, tasks will specify:
# - T001: Verify simics-mcp-server connection and Simics installation using `get_simics_version()`
# - T002: Create Simics project structure using `create_simics_project(project_name="DEVICE_NAME", project_path=".")`
```

#### Implementation Phase
```bash
# Build validation integrated into development cycle:
# - T013: Build device module using `build_simics_project(project_path=".", module="DEVICE_NAME")`
# - T018: Incremental build validation using `build_simics_project(project_path=".")`
```

## Benefits

### 1. **Automated Project Setup**
- No more manual project structure creation
- Consistent project layout via MCP tools
- Reduced setup errors and time

### 2. **Continuous Build Validation**
- Build errors caught early in development
- Module-specific and full-project validation
- Integration with TDD workflow

### 3. **Integrated Testing**
- Automated test execution with appropriate suites
- Test environment validation
- Comprehensive integration testing

### 4. **Package Management**
- Automated dependency installation
- Version compatibility checking
- Package discovery and research

### 5. **Structured Development**
- Clear separation of manual vs automated tasks
- Validated progression through development phases
- Consistent tooling across projects

## Future Enhancements (Phase 2+)

This Phase 1 integration provides the foundation for:
- **Phase 2**: Simics AI assistant option in spec-kit CLI
- **Phase 3**: Full MCP client integration with automated tool execution
- **Phase 4**: Real-time project monitoring and validation

## Implementation Notes

- All MCP tool references use exact function signatures from simics-mcp-server
- Tool calls include proper parameter specifications (project_path, device_name, etc.)
- Templates maintain backward compatibility with non-Simics projects
- Validation rules ensure consistent MCP tool usage across tasks

This integration significantly enhances the development experience for Simics device modeling while maintaining the structured, specification-driven approach of spec-kit.