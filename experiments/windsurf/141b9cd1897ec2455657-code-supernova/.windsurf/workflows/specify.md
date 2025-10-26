---
description: Create or update the feature specification from a natural language feature description.
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. Run the script `.specify/scripts/bash/create-new-feature.sh --json "$ARGUMENTS"` from repo root and parse its JSON output for BRANCH_NAME and SPEC_FILE. All file paths must be absolute.
  **IMPORTANT** You must only ever run this script once. The JSON is provided in the terminal as output - always refer to it to get the actual content you're looking for.

2. Load `.specify/templates/spec-template.md` to understand required sections.

3. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.
   - **⚠️ CRITICAL**: After writing/updating the spec file, immediately create a git commit (see step 4)

4. **MANDATORY: Git Version Control - Commit After Each Major Update**:
   - **WHEN**: After completing the specification or making significant updates
   - **WHAT**: Stage and commit the spec file and any related changes
   - **HOW**: Use these exact commands:
     ```bash
     git add -A
     git commit -m "specify: <feature-name> - <section/update-description>"
     ```
   - **EXAMPLES**:
     - Initial spec: `git commit -m "specify: device-name - initial specification created"`
     - Updated requirements: `git commit -m "specify: device-name - updated functional requirements"`
     - Added clarifications: `git commit -m "specify: device-name - added clarifications section"`
   - **WHY**: This creates a clear audit trail of specification evolution, making it easy to:
     - Track how requirements evolved
     - Understand decision rationale
     - Review specification history
     - Revert to previous specification versions if needed
   - **CRITICAL**: Always commit specification changes to maintain project history

5. Report completion with branch name, spec file path, and readiness for the next phase.

Note: The script creates and checks out the new branch and initializes the spec file before writing.
