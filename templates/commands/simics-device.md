---
description: Create comprehensive device model specification for Simics device development
scripts:
  sh: scripts/bash/setup-simics-device.sh --json "{ARGS}"
  ps: scripts/powershell/setup-simics-device.ps1 -Json "{ARGS}"
---

Given the device description provided as an argument, do this:

1. Run the script `{SCRIPT}` from repo root and parse its JSON output for BRANCH_NAME, SPEC_FILE, DEVICE_TYPE, and SIMICS_VERSION. All file paths must be absolute.

2. Load the Simics device specification template:
   - Read `templates/simics/projects/device-spec-template.md` to understand required sections
   - The template provides comprehensive structure for device modeling specifications

3. Generate the device specification using the template structure:
   - Replace [DEVICE_NAME] with the device name extracted from arguments
   - Fill in device description from arguments in the Input field
   - Execute the template's main() execution flow steps 1-10
   - Replace placeholders with concrete details derived from the device description
   - Preserve all section headings and structure from the template
   - Focus on device behavior, interfaces, and validation requirements
   - Mark any ambiguous areas with [NEEDS CLARIFICATION: specific question]

4. Write the complete specification to SPEC_FILE maintaining:
   - All mandatory sections (Device Overview, Behavioral Model, Register Interface, Memory Interface, Simics Interface, Validation Scenarios)
   - Optional sections only when relevant to the device type
   - Clear separation between behavioral requirements and implementation details
   - Comprehensive validation scenarios for device testing

5. Validate the generated specification:
   - Ensure no implementation details (DML code, Python classes, Simics API calls)
   - Verify all [NEEDS CLARIFICATION] markers are justified
   - Check that register and memory interfaces are adequately specified
   - Confirm validation scenarios cover functional and integration testing

6. Report completion with:
   - Branch name and device type
   - Specification file path (absolute)
   - Summary of key device characteristics identified
   - Any areas requiring clarification for implementation
   - Readiness for implementation planning phase

Note: This command creates device model specifications that serve as the foundation for Simics DML/Python implementation. The specification focuses on WHAT the device does rather than HOW to implement it.

Use absolute paths with the repository root for all file operations to avoid path issues.