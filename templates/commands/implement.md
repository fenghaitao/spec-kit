---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

The user input can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

1. Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.
   **CRITICAL**: Store your current working directory as `WORKING_DIR` for use with MCP tool calls.

2. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

3. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

4. Execute implementation following the task plan:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together  
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion before proceeding
   - **⚠️ CRITICAL**: After EVERY build or test command, immediately create a git commit (see step 7)

5. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation
   - **⚠️ After each build/test**: Run `git add -A && git commit -m "implement: <task> - <result>"`
   - **⚠️ MCP Tool Paths**: When calling MCP tools (like `build_simics_project`, `run_simics_test`), replace any `<ABSOLUTE_PATH_TO_PROJECT>` placeholder with your actual `WORKING_DIR` path. Example: if `WORKING_DIR=/home/user/myproject`, use `project_path="/home/user/myproject/simics-project"` NOT `project_path="./simics-project"`

6. Progress tracking and error handling:
   - Report progress after each completed task
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT** For completed tasks, make sure to mark the task off as [X] in the tasks file.

7. **MANDATORY: Git Version Control - Execute After EVERY Build or Test**:
   - **WHEN**: Immediately after EVERY build attempt (successful or failed) and EVERY test run (pass or fail)
   - **WHAT**: Stage and commit ALL modified files (source code, tests, configs, DML files, etc.)
   - **HOW**: Use these exact commands:
     ```bash
     git add -A
     git commit -m "implement: <task-id> - <step-description> - <result>"
     ```
   - **EXAMPLES**:
     - After failed build: `git commit -m "implement: T024 - build validation - FAILED: syntax error in registers.dml"`
     - After successful build: `git commit -m "implement: T024 - build validation - SUCCESS"`
     - After failed test: `git commit -m "implement: T031 - comprehensive tests - FAILED: register access error"`
     - After passed test: `git commit -m "implement: T031 - comprehensive tests - PASSED"`
   - **WHY**: This creates a detailed history of the development process, making it easy to:
     - Track what changes caused failures
     - Revert to working states
     - Review the implementation journey
     - Debug issues by comparing commits
   - **CRITICAL**: Do NOT skip commits even if the build/test failed - failed attempts are valuable history

8. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/tasks` first to regenerate the task list.