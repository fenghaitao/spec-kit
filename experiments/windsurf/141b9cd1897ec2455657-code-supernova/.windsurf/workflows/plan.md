---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

Given the implementation details provided as an argument, do this:

1. Run `.specify/scripts/bash/setup-plan.sh --json` from the repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. All future file paths must be absolute.
   - BEFORE proceeding, inspect FEATURE_SPEC for a `## Clarifications` section with at least one `Session` subheading. If missing or clearly ambiguous areas remain (vague adjectives, unresolved critical choices), PAUSE and instruct the user to run `/clarify` first to reduce rework. Only continue if: (a) Clarifications exist OR (b) an explicit user override is provided (e.g., "proceed without clarification"). Do not attempt to fabricate clarifications yourself.
2. Read and analyze the feature specification to understand:
   - The feature requirements and user stories
   - Functional and non-functional requirements
   - Success criteria and acceptance criteria
   - Any technical constraints or dependencies mentioned

3. Read the constitution at `.specify/memory/constitution.md` to understand constitutional requirements.

4. Execute the implementation plan template:
   - Load `.specify/templates/plan-template.md` (already copied to IMPL_PLAN path)
   - Set Input path to FEATURE_SPEC
   - Run the Execution Flow (main) function steps 1-9
   - The template is self-contained and executable
   - Follow error handling and gate checks as specified
   - Let the template guide artifact generation in $SPECS_DIR:
     * Phase 0 generates research.md
     * Phase 1 generates data-model.md, contracts/, quickstart.md
     * Phase 2 generates tasks.md
   - Incorporate user-provided details from arguments into Technical Context: $ARGUMENTS
   - Update Progress Tracking as you complete each phase
   - **⚠️ CRITICAL**: After completing EACH phase (Phase 0, Phase 1, Phase 2), immediately create a git commit (see step 6)

5. **MANDATORY: Git Version Control - Commit After Each Phase**:
   - **WHEN**: After completing each planning phase (Phase 0, Phase 1, Phase 2) and creating artifacts
   - **WHAT**: Stage and commit all generated artifacts for that phase
   - **HOW**: Use these exact commands:
     ```bash
     git add -A
     git commit -m "plan: <feature-name> - <phase-name> - <artifacts-created>"
     ```
   - **EXAMPLES**:
     - After Phase 0: `git commit -m "plan: device-name - Phase 0 Research - created research.md"`
     - After Phase 1: `git commit -m "plan: device-name - Phase 1 Design - created data-model.md, contracts/, quickstart.md"`
     - After Phase 2: `git commit -m "plan: device-name - Phase 2 Tasks - created tasks.md"`
     - Updated plan: `git commit -m "plan: device-name - updated technical context with MCP tools info"`
   - **WHY**: This creates a clear audit trail of the planning process, making it easy to:
     - Track which artifacts were created in each phase
     - Understand the design evolution
     - Review planning decisions
     - Revert to previous planning states if needed
   - **CRITICAL**: Always commit after each phase completion to maintain clear project history

6. Verify execution completed:
   - Check Progress Tracking shows all phases complete
   - Ensure all required artifacts were generated
   - Confirm no ERROR states in execution

7. Report results with branch name, file paths, and generated artifacts.

Use absolute paths with the repository root for all file operations to avoid path issues.
