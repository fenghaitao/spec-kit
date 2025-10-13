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

5. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

   **For Simics Device Implementation Tasks:**
   - **Critical Principles**:
     * Focus on software-visible behaviors (Simics is functional simulator)
     * Omit low-level hardware logic irrelevant to software
     * ALL registers MUST be 100% correct (visible to software/outside world)
     * DO NOT use your own knowledge - refer to MCP tool documentation
     * Memory read/write MUST use `transact()` method
     * Simplify internal behavior as long as external state is correct
   
   - **Implementation Process**:
     1. Use MCP tools (pageindex_rag_query_drm, pageindex_rag_query_model_builder) to learn Simics/DML
     2. Declare ALL `register`s, `port`s, `connect`s with spec references in comments
     3. Separate register declarations from logic implementation
     4. Leave side effects unimplemented initially (use `unimpl`) with comments
     5. List unclear/questionable spec parts in top file comment
     6. Implement register-specific logic in `write_register()`/`read_register()` methods
     7. Use `attribute`s for internal state, runtime config, checkpointing
     8. Implement `interface`s in `connect` for device communication
     9. Use `template`s from "utility.dml" to minimize redundancy
     10. Define `event`s for asynchronous/deferred operations
     11. Complete clearly stated side effects with spec references
     12. Leave unclear logic as `TODO` in top comment - DO NOT implement unclear parts
     13. Build with `build_simics_project()` after each major change
     14. Fix syntax errors iteratively
     15. Write Python tests with spec references (test only clear implementations)
   
   - **YOU MUST**: Implement ALL registers - this is mandatory
   - **Remember**: Remind yourself of Simics concepts/DML syntax before each task

6. Progress tracking and error handling:
   - Report progress after each completed task
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT** For completed tasks, make sure to mark the task off as [X] in the tasks file.

7. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/tasks` first to regenerate the task list.