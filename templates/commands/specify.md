---
description: Create or update the feature specification from a natural language feature description with workflow enforcement
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

Given the feature description provided as an argument, do this:

**WORKFLOW ENFORCEMENT - SPECIFICATION PHASE**
This command operates within the enhanced workflow enforcement system:
- Validates that the product phase has been completed
- Loads and integrates product context from the previous phase
- Ensures proper context flow from product → specification
- Marks specification phase as completed upon successful execution

1. **Validate Phase Prerequisites**:
   - Check that product phase is completed
   - Verify product context availability
   - Block execution if prerequisites not met with guidance to complete missing phases
   - Load product context for integration into specification

2. Run the script `{SCRIPT}` from repo root and parse its JSON output for BRANCH_NAME and SPEC_FILE. All file paths must be absolute.

3. **Load Product Context and Templates**:
   - Load `templates/spec-template.md` to understand required sections
   - Retrieve product context (vision, requirements, constraints, stakeholders) from workflow state
   - Prepare context injection points for specification generation

4. **Generate Specification with Product Context Integration**:
   - Write the specification to SPEC_FILE using the template structure
   - Inject product vision into specification overview
   - Map product requirements to technical specifications
   - Incorporate constraints and stakeholder information
   - Replace placeholders with concrete details derived from feature description AND product context
   - Preserve section order and headings while ensuring product traceability
   - Mark any areas requiring clarification with [NEEDS CLARIFICATION: specific question]

5. **Validate Specification Completeness**:
   - Ensure all product requirements are addressed in technical specifications
   - Verify traceability from product vision to technical details
   - Check that all [NEEDS CLARIFICATION] markers are justified
   - Validate specification completeness against quality criteria

6. **Complete Specification Phase**:
   - Store specification context for plan phase transfer
   - Mark specification phase as completed in workflow state
   - Calculate and store content integrity hash

7. Report completion with:
   - Branch name and spec file path
   - **Product Context Integration**: Summary of how product vision was incorporated
   - **Traceability Status**: Mapping from product requirements to technical specifications
   - **Workflow Status**: Specification phase completed, ready for planning phase
   - **Next Step**: Use `/plan` command to proceed to planning phase with captured specification context
   - **Enforcement Note**: Attempting to skip to `/tasks` will be blocked until planning phase is completed

**WORKFLOW ENFORCEMENT NOTES**:
- This command requires the **Product Phase** to be completed first
- Product context automatically flows into specification generation
- All subsequent phases (plan, tasks) will validate this specification completion
- Skipping phases will result in clear error messages with guidance

Note: The script creates and checks out the new branch and initializes the spec file before writing.
