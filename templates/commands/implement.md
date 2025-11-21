---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files in the checklists/ directory
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
     - Completed items: Lines matching `- [X]` or `- [x]`
     - Incomplete items: Lines matching `- [ ]`
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists have incomplete items

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing
     - If user says "no" or "wait" or "stop", halt execution
     - If user says "yes" or "proceed" or "continue", proceed to step 3

   - **If all checklists are complete**:
     - Display the table showing all checklists passed
     - Automatically proceed to step 3

3. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read spec.md and data-model.md for entities and relationships
   - **IF EXISTS**: Read test-scenarios.md and contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints

4. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files based on actual project setup:

   **Detection & Creation Logic**:
   - Check if the following command succeeds to determine if the repository is a git repo (create/verify .gitignore if so):

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   **If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only
   **If ignore file missing**: Create with full pattern set for detected technology

5. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

6. Execute implementation following the task plan:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion before proceeding
   - **⚠️ CRITICAL**: After EVERY build or test command, immediately create a git commit (see step 7)

7. **MANDATORY: Git Version Control - Execute After EVERY Build, Test, Initialization, or Major Update**:
   - **WHEN**:
     - Immediately after EVERY build attempt (successful or failed)
     - Immediately after EVERY test run (pass or fail)
     - **Immediately after project initialization** (Setup phase completion)
     - **Immediately after each major DML implementation update** (e.g., completed register bank, completed device method, completed state machine logic)
   - **WHAT**: Stage and commit ALL modified files (source code, tests, configs, DML files, etc.)
   - **HOW**: Execute using run_in_terminal tool with these exact commands:
     ```bash
     cd <FEATURE_DIR>
     git add -A
     git commit -m "implement: <task-id> - <step-description> - <result>"
     git log --oneline -1
     ```
   - **EXAMPLES**:
     - After initialization: `git commit -m "implement: T001-T005 - project initialization - SUCCESS"`
     - After DML update: `git commit -m "implement: T015 - register bank implementation - COMPLETED"`
     - After failed build: `git commit -m "implement: T024 - build validation - FAILED: syntax error in registers.dml"`
     - After successful build: `git commit -m "implement: T024 - build validation - SUCCESS"`
     - After failed test: `git commit -m "implement: T031 - comprehensive tests - FAILED: register access error"`
     - After passed test: `git commit -m "implement: T031 - comprehensive tests - PASSED"`
   - **WHY**: This creates a detailed history of the development process, making it easy to:
     - Track what changes caused failures
     - Revert to working states
     - Review the implementation journey
     - Debug issues by comparing commits
     - **Recover from build failures by reverting to last working state**
   - **CRITICAL**: Do NOT skip commits even if the build/test failed - failed attempts are valuable history
   - **VERIFICATION**: After each git commit, verify with `git log --oneline -1` to confirm commit was created

8. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

9. Progress tracking and error handling:
   - Report progress after each completed task
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT** For completed tasks, make sure to mark the task off as [X] in the tasks file.

10. **Error Recovery Strategy**:

   ### Build Error Recovery (DML Compilation Failures)

   When `build_simics_project()` or `check_with_dmlc()` fails:

   1. **Track build failure count**:
      - Maintain a counter for consecutive build failures on the same task
      - Reset counter to 0 when build succeeds
      - **CRITICAL**: If build fails 3 times consecutively on the same implementation attempt:
        - **STOP execution immediately**
        - Display failure summary:
          ```
          ⚠️ BUILD FAILURE THRESHOLD REACHED (3 consecutive failures)

          Current approach is not working. Options:
          1. Revert to simpler DML implementation (recommended)
          2. Continue debugging current approach
          3. Request human assistance

          Failure history:
          - Attempt 1: <error summary>
          - Attempt 2: <error summary>
          - Attempt 3: <error summary>

          Last successful commit: <git hash>
          ```
        - **MANDATORY**: Ask user: "How would you like to proceed? (1/2/3 or provide guidance)"
        - **Wait for user response** before continuing
        - If user chooses option 1, revert to last successful commit and implement simpler approach
        - If user chooses option 2, continue with current debugging approach
        - If user chooses option 3 or provides guidance, follow user instructions

   2. **Capture and analyze the error**:
      - Use `check_with_dmlc()` for AI-enhanced diagnostics (if not already called)
      - Extract: error type (syntax, semantic, undefined symbol, etc.)
      - Identify: file location, line number, specific construct causing failure

   3. **Review knowledge sources**:
      - Check `.specify/memory/DML_Device_Development_Best_Practices.md` for relevant patterns
      - Check `.specify/memory/DML_grammar.md` for correct syntax
      - Review research.md for similar issues previously resolved
      - Review data-model.md for intended design

   4. **Execute targeted RAG query** (if knowledge insufficient):
      - Include specific error message in query
      - Example: `perform_rag_query("DML error: undefined method write_register how to fix", source_type="dml")`
      - Document RAG results in research.md

   5. **Apply fix**:
      - Make minimal changes to address the specific error
      - Follow DML best practices from knowledge sources
      - Add comments explaining the fix if non-obvious

   6. **Re-validate**:
      - Run `check_with_dmlc()` → `build_simics_project()` again
      - **Increment failure counter** if still failing
      - **Check if failure count >= 3**, if so, execute step 1 (user intervention)
      - If passing, reset failure counter to 0 and proceed to git commit

   7. **Git commit** (MANDATORY even if failed):
      ```bash
      cd <FEATURE_DIR>
      git add -A
      git commit -m "implement: <task-id> - error recovery attempt <N> - <result>"
      git log --oneline -1
      ```

   8. **Document solution**:
      - Add error pattern and solution to research.md under "## Build Error Solutions"
      - Include: error message, root cause, fix applied, RAG query used (if any)

   ### Test Error Recovery (Runtime Failures)

   When `run_simics_test()` fails:

   1. **Analyze test failure**:
      - Review test output for assertion failures, exceptions, timeouts
      - Identify: which test failed, expected vs actual behavior
      - Check: register values, state transitions, interface responses

   2. **Debug with Simics**:
      - Review test code to understand expected behavior
      - Check device implementation for logic errors
      - Compare with spec.md requirements and test-scenarios.md

   3. **Review knowledge sources**:
      - Check `.specify/memory/DML_Device_Development_Best_Practices.md` for common pitfalls
      - Review data-model.md for register side-effects and state dependencies
      - Check research.md for similar runtime issues

   4. **Execute targeted RAG query** (if needed):
      - Include test failure details
      - Example: `perform_rag_query("DML register read returns wrong value state machine", source_type="dml")`
      - Example: `perform_rag_query("Simics test assertion failure interrupt not triggered", source_type="python")`
      - Document RAG results in research.md

   5. **Apply fix**:
      - Fix device logic based on test requirements
      - Ensure side-effects are implemented correctly
      - Verify state transitions match spec.md

   6. **Re-validate**:
      - Run `check_with_dmlc()` → `build_simics_project()` (ensure still compiles)
      - Run `run_simics_test()` again
      - If still failing, repeat from step 1
      - If passing, proceed to git commit

   7. **Git commit** (MANDATORY even if failed):
      ```bash
      git add -A
      git commit -m "implement: <task-id> - test fix - <result>"
      ```

   8. **Document solution**:
      - Add test failure pattern and solution to research.md under "## Runtime Error Solutions"
      - Include: test scenario, failure reason, fix applied, RAG query used (if any)

   ### General Recovery Guidelines

   - **Iterate incrementally**: Make one fix at a time, validate after each change
   - **Commit frequently**: Commit after each fix attempt (success or failure) for history tracking
   - **Document learnings**: Always update research.md with error patterns and solutions
   - **Use RAG wisely**: Execute targeted queries with specific error context, not generic questions
   - **Check dependencies**: Some errors may be caused by missing/incorrect earlier implementations
   - **Consult examples**: RAG query results often include working code examples - adapt them carefully
   - **Don't skip validation**: Always run check_with_dmlc + build after DML changes, tests after logic fixes

11. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/speckit.tasks` first to regenerate the task list.
