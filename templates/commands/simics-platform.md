---
description: Create comprehensive virtual platform specification for Simics platform development (Product Phase Entry Point)
scripts:
  sh: scripts/bash/setup-simics-platform.sh --json "{ARGS}"
  ps: scripts/powershell/setup-simics-platform.ps1 -Json "{ARGS}"
---

Given the platform description provided as an argument, do this:

**WORKFLOW ENFORCEMENT - PRODUCT PHASE**
This command initiates the enhanced workflow enforcement system. Before proceeding:
- Initialize workflow state tracking for the product definition phase
- Validate that this is the proper entry point for the feature development workflow
- Prepare for context capture and transfer to subsequent specification phase

1. **Initialize Workflow State**:
   - Create .spec-kit directory structure if not exists
   - Initialize workflow state management
   - Mark product phase as started
   - Validate workspace readiness for workflow enforcement

2. Run the script `{SCRIPT}` from repo root and parse its JSON output for BRANCH_NAME, SPEC_FILE, PLATFORM_TYPE, COMPONENT_LIST, and TARGET_SYSTEM. All file paths must be absolute.

2. Load the Simics platform specification template:
   - Read `templates/simics/projects/platform-spec-template.md` to understand required sections
   - The template provides comprehensive structure for virtual platform specifications

3. Generate the platform specification using the template structure:
   - Replace [PLATFORM_NAME] with the platform name extracted from arguments
   - Fill in platform description from arguments in the Input field
   - Execute the template's main() execution flow steps 1-11
   - Replace placeholders with concrete details derived from the platform description
   - Preserve all section headings and structure from the template
   - Focus on system architecture, device integration, and validation requirements
   - Mark any ambiguous areas with [NEEDS CLARIFICATION: specific question]

4. Write the complete specification to SPEC_FILE maintaining:
   - All mandatory sections (Platform Overview, System Architecture, Device Integration, Memory Map, Timing Model, Configuration Management, Validation Scenarios)
   - Optional sections only when relevant to the platform type
   - Clear separation between architectural requirements and implementation details
   - Comprehensive validation scenarios for platform testing

5. Validate the generated specification:
   - Ensure no implementation details (Simics configuration scripts, Python setup code)
   - Verify all [NEEDS CLARIFICATION] markers are justified
   - Check that device integration and memory map are adequately specified
   - Confirm validation scenarios cover system-level and integration testing

6. **Capture Product Context for Workflow**:
   - Extract and store product vision, success criteria, and constraints
   - Identify stakeholder requirements and technical constraints
   - Store product context in workflow state for specification phase transfer
   - Calculate context integrity hash for validation
   - Mark product phase as completed

7. Report completion with:
   - Branch name and platform type
   - Specification file path (absolute)
   - Summary of key system characteristics identified
   - List of main component devices and their roles
   - Any areas requiring clarification for implementation
   - **Workflow Status**: Product phase completed, ready for specification phase
   - **Next Step**: Use `/specify` command to proceed to specification phase with captured product context
   - **Enforcement Note**: Attempting to skip to `/plan` or `/tasks` will be blocked until specification phase is completed

**WORKFLOW ENFORCEMENT NOTES**:
- This command serves as the **Product Phase Entry Point** in the enhanced workflow enforcement system
- Product context captured here will automatically flow to the specification phase
- All subsequent phases (specify, plan, tasks) will validate prerequisites before execution
- Skipping phases will result in clear error messages with guidance to complete missing phases

Note: This command creates virtual platform specifications that serve as the foundation for Simics system configuration and integration. The specification focuses on WHAT the platform provides rather than HOW to configure it in Simics.

Use absolute paths with the repository root for all file operations to avoid path issues.