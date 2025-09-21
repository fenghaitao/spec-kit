---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts with workflow enforcement
scripts:
  sh: scripts/bash/check-task-prerequisites.sh --json
  ps: scripts/powershell/check-task-prerequisites.ps1 -Json
---

Given the context provided as an argument, do this:

**WORKFLOW ENFORCEMENT - TASKS PHASE**
This command operates within the enhanced workflow enforcement system:
- Validates that the planning phase has been completed
- Loads and integrates plan context from the previous phase
- Ensures proper context flow from plan → tasks
- Marks tasks phase as completed upon successful execution
- Completes the full workflow sequence: product → specify → plan → tasks

1. **Validate Phase Prerequisites**:
   - Check that planning phase is completed
   - Verify plan context availability
   - Block execution if prerequisites not met with guidance to complete missing phases
   - Load plan context for integration into task generation

2. Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

3. **Load Plan Context and Analyze Design Artifacts**:
   - Load and analyze available design documents:
     - Always read plan.md for tech stack and libraries
     - IF EXISTS: Read data-model.md for entities
     - IF EXISTS: Read contracts/ for API endpoints
     - IF EXISTS: Read research.md for technical decisions
     - IF EXISTS: Read quickstart.md for test scenarios
   - Integrate plan context (implementation strategy, technology stack, milestones, dependencies)
   - Ensure traceability from plan to implementation tasks

   Note: Not all projects have all documents. For example:
   - CLI tools might not have contracts/
   - Simple libraries might not need data-model.md
   - Generate tasks based on what's available

4. **Generate Tasks with Plan Context Integration**:
   - Use `/templates/tasks-template.md` as the base
   - Inject plan context into task generation
   - Replace example tasks with actual tasks based on:
     * **Setup tasks**: Project init, dependencies, linting (from technology stack)
     * **Test tasks [P]**: One per contract, one per integration scenario
     * **Core tasks**: One per entity, service, CLI command, endpoint
     * **Integration tasks**: DB connections, middleware, logging
     * **Polish tasks [P]**: Unit tests, performance, docs
   - Ensure tasks align with implementation strategy from plan
   - Include technology stack and dependency information from plan context

5. **Task generation rules with Plan Traceability**:
   - Each contract file → contract test task marked [P]
   - Each entity in data-model → model creation task marked [P]
   - Each endpoint → implementation task (not parallel if shared files)
   - Each user story → integration test marked [P]
   - Each milestone from plan → corresponding implementation tasks
   - Different files = can be parallel [P]
   - Same file = sequential (no [P])

6. **Order tasks by dependencies from Plan**:
   - Setup before everything
   - Tests before implementation (TDD)
   - Models before services
   - Services before endpoints
   - Core before integration
   - Everything before polish
   - Respect dependency order from plan context

7. Include parallel execution examples:
   - Group [P] tasks that can run together
   - Show actual Task agent commands

8. **Complete Tasks Phase**:
   - Store tasks context (completion of workflow sequence)
   - Mark tasks phase as completed in workflow state
   - Calculate and store content integrity hash

9. Create FEATURE_DIR/tasks.md with:
   - Correct feature name from implementation plan
   - Numbered tasks (T001, T002, etc.)
   - Clear file paths for each task
   - Dependency notes
   - Parallel execution guidance
   - **Plan Integration**: Reference to implementation strategy and technology stack
   - **Traceability**: Clear connection from plan milestones to implementation tasks

10. Report completion with:
    - Feature directory and tasks file path
    - **Plan Context Integration**: Summary of how plan was incorporated
    - **Traceability Status**: Mapping from plan to implementation tasks
    - **Workflow Status**: Tasks phase completed, full workflow sequence finished
    - **Achievement**: Complete product → specify → plan → tasks workflow execution
    - **Enforcement Summary**: All phases completed with proper context flow

**WORKFLOW ENFORCEMENT NOTES**:
- This command requires the **Planning Phase** to be completed first
- Plan context automatically flows into task generation
- This completes the full workflow enforcement sequence
- All prerequisite phases (product, specify, plan) have been validated

Context for task generation: {ARGS}

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.
