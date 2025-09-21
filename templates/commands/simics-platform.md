---
description: Create comprehensive virtual platform specification for Simics platform development
scripts:
  sh: scripts/bash/setup-simics-platform.sh --json "{ARGS}"
  ps: scripts/powershell/setup-simics-platform.ps1 -Json "{ARGS}"
---

Given the platform description provided as an argument, do this:

1. Run the script `{SCRIPT}` from repo root and parse its JSON output for BRANCH_NAME, SPEC_FILE, PLATFORM_TYPE, COMPONENT_LIST, and TARGET_SYSTEM. All file paths must be absolute.

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

6. Report completion with:
   - Branch name and platform type
   - Specification file path (absolute)
   - Summary of key system characteristics identified
   - List of main component devices and their roles
   - Any areas requiring clarification for implementation
   - Readiness for implementation planning phase

Note: This command creates virtual platform specifications that serve as the foundation for Simics system configuration and integration. The specification focuses on WHAT the platform provides rather than HOW to configure it in Simics.

Use absolute paths with the repository root for all file operations to avoid path issues.