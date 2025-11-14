---
description: Create or update the feature specification from a natural language feature description.
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

The text the user typed after `/specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. Run the script `{SCRIPT}` from repo root and parse its JSON output for BRANCH_NAME and SPEC_FILE. All file paths must be absolute.
  **IMPORTANT** You must only ever run this script once. The JSON is provided in the terminal as output - always refer to it to get the actual content you're looking for.

2. Load `templates/spec-template.md` to understand required sections.

3. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.
   - **After completing the specification**, immediately proceed to step 5 to commit

4. **MANDATORY: Generate IP-XACT Register Description XML**:
   - Load `templates/register-template.md` and follow the complete "Hardware Specification Analysis Process"
   - Create separate file: `[feature-name]-registers.xml` in the same directory as SPEC_FILE
   - **After completing the XML file**, immediately proceed to step 5 to commit

5. **MANDATORY: Git Commit After Each Major Update**:
   - **Execute this step after completing step 3 OR step 4**
   - Stage and commit changes:
     ```bash
     git add -A
     git commit -m "specify: <feature-name> - <section/update-description>"
     ```
   - **Examples**:
     - After step 3: `"specify: device-name - initial specification created"`
     - After step 4: `"specify: device-name - added IP-XACT register XML"`
     - After updates: `"specify: device-name - updated functional requirements"`
   - **Purpose**: Creates audit trail for tracking specification evolution, decision rationale, and enabling version rollback
   - **Continue**: After committing, proceed to next step or report completion

6. Report completion with branch name, spec file path, XML file path (if generated), and readiness for the next phase.

Note: The script creates and checks out the new branch and initializes the spec file before writing.
