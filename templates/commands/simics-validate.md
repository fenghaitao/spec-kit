---
description: Create comprehensive validation framework specification for Simics model validation
scripts:
  sh: scripts/bash/setup-simics-validate.sh --json "{ARGS}"
  ps: scripts/powershell/setup-simics-validate.ps1 -Json "{ARGS}"
---

Given the validation requirements provided as an argument, do this:

1. Run the script `{SCRIPT}` from repo root and parse its JSON output for BRANCH_NAME, SPEC_FILE, MODEL_TYPE, VALIDATION_SCOPE, and TEST_CATEGORIES. All file paths must be absolute.

2. Load the Simics validation framework template:
   - Read `templates/simics/projects/validation-template.md` to understand required sections
   - The template provides comprehensive structure for validation framework specifications

3. Generate the validation specification using the template structure:
   - Replace [MODEL_NAME] with the model name extracted from arguments
   - Fill in validation requirements from arguments in the Input field
   - Execute the template's main() execution flow steps 1-11
   - Replace placeholders with concrete details derived from the validation requirements
   - Preserve all section headings and structure from the template
   - Focus on validation strategy, test scenarios, and success criteria
   - Mark any ambiguous areas with [NEEDS CLARIFICATION: specific question]

4. Write the complete specification to SPEC_FILE maintaining:
   - All mandatory sections (Validation Overview, Strategy, Test Scenarios, Coverage Requirements, Test Environment, Automation Strategy)
   - Optional sections only when relevant to the validation scope
   - Clear separation between validation requirements and implementation details
   - Comprehensive test scenarios covering functional, performance, and integration validation

5. Validate the generated specification:
   - Ensure no implementation details (specific test scripts, Simics commands)
   - Verify all [NEEDS CLARIFICATION] markers are justified
   - Check that test scenarios and coverage requirements are adequately specified
   - Confirm validation approach addresses both functional and non-functional requirements

6. Report completion with:
   - Branch name and validation scope
   - Specification file path (absolute)
   - Summary of key validation objectives identified
   - List of main test categories and coverage targets
   - Any areas requiring clarification for test implementation
   - Readiness for test development and execution phases

Note: This command creates validation framework specifications that serve as the foundation for comprehensive Simics model testing. The specification focuses on WHAT to validate and success criteria rather than HOW to implement the tests.

Use absolute paths with the repository root for all file operations to avoid path issues.