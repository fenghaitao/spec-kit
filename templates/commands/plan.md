---
description: Execute the implementation planning workflow using the plan template to generate design artifacts with workflow enforcement
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
---

Given the implementation details provided as an argument, do this:

**WORKFLOW ENFORCEMENT - PLANNING PHASE**
This command operates within the enhanced workflow enforcement system:
- Validates that the specification phase has been completed
- Loads and integrates specification context from the previous phase
- Ensures proper context flow from specify → plan
- Marks planning phase as completed upon successful execution

1. **Validate Phase Prerequisites**:
   - Check that specification phase is completed
   - Verify specification context availability
   - Block execution if prerequisites not met with guidance to complete missing phases
   - Load specification context for integration into planning

2. Run `{SCRIPT}` from the repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. All future file paths must be absolute.

3. **Load Specification Context and Analyze Requirements**:
   - Read and analyze the feature specification to understand:
     - The feature requirements and user stories
     - Functional and non-functional requirements
     - Success criteria and acceptance criteria
     - Any technical constraints or dependencies mentioned
   - Integrate specification context (technical requirements, architecture decisions, design constraints)
   - Ensure traceability from specification to implementation plan

4. Read the constitution at `/memory/constitution.md` to understand constitutional requirements.

5. **Execute Implementation Plan with Specification Context Integration**:
   - Load `/templates/plan-template.md` (already copied to IMPL_PLAN path)
   - Set Input path to FEATURE_SPEC
   - Inject specification context into plan generation
   - Run the Execution Flow (main) function steps 1-9
   - The template is self-contained and executable
   - Follow error handling and gate checks as specified
   - Let the template guide artifact generation in $SPECS_DIR:
     * Phase 0 generates research.md
     * Phase 1 generates data-model.md, contracts/, quickstart.md
     * Phase 2 generates tasks.md
   - Incorporate user-provided details from arguments into Technical Context: {ARGS}
   - Ensure specification requirements are reflected in all design artifacts
   - Update Progress Tracking as you complete each phase

6. **Validate Plan Completeness and Traceability**:
   - Check Progress Tracking shows all phases complete
   - Ensure all required artifacts were generated
   - Confirm no ERROR states in execution
   - Verify traceability from specification to implementation plan
   - Validate that all specification requirements are addressed

7. **Complete Planning Phase**:
   - Store plan context for tasks phase transfer
   - Mark planning phase as completed in workflow state
   - Calculate and store content integrity hash

8. Report results with:
   - Branch name and file paths
   - Generated artifacts
   - **Specification Context Integration**: Summary of how specification was incorporated
   - **Traceability Status**: Mapping from specification to implementation plan
   - **Workflow Status**: Planning phase completed, ready for tasks phase
   - **Next Step**: Use `/tasks` command to proceed to tasks phase with captured plan context
   - **Enforcement Note**: All prerequisite phases (product, specify) have been completed

**WORKFLOW ENFORCEMENT NOTES**:
- This command requires the **Specification Phase** to be completed first
- Specification context automatically flows into plan generation
- The tasks phase will validate this planning completion
- Skipping phases will result in clear error messages with guidance

Use absolute paths with the repository root for all file operations to avoid path issues.
