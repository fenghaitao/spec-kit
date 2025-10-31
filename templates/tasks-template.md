# Tasks: [FEATURE NAME]

**Status**: No## Format: `[ID] [P?] Description`
**[P]** = Can run in parallel (different files, no dependencies)
Include exact file paths in descriptions

**⚠️ CRITICAL - MCP Tool Paths (SSE Transport)**:
- **ALWAYS use ABSOLUTE paths** for MCP tools: `create_simics_project()`, `build_simics_project()`, `run_simics_test()`
- **NEVER use relative paths** like `"./simics-project"` or `"../project"`
- **WHY**: SSE transport MCP servers run in different process/directory context
- **HOW**: Use `os.getcwd()` or workspace root to construct: `"/full/path/to/workspace/simics-project"`
- **Example**: `create_simics_project(project_path="/home/user/workspace/simics-project")`tarted | In Progress | Completed | Blocked
**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md → Extract: DML version, Simics API, device type, register map
2. Load design docs:
   → data-model.md: Extract registers, interfaces, state variables → DML implementation tasks
   → contracts/: Each contract file → test tasks (register-access.md, interface-behavior.md)
   → research.md: Extract MCP tool outputs, architecture decisions, device patterns
3. Generate tasks by category:
   → Setup: MCP tools (get_simics_version, create_simics_project, add_dml_device_skeleton, checkout_and_build_dmlc)
   → **Knowledge Gates** (before tests/implementation):
     • Research Review: Read research.md → extract MCP outputs, architecture decisions, patterns
     • Test RAG Queries: Get test patterns before writing tests
     • DML Learning Gate: Read DML_grammar.md before DML implementation
   → Tests: Contract tests (register access, interface behavior, device workflows)
   → Core: Register definitions, interface declarations, device logic, state management
   → Integration: Memory mapping, interrupt/reset signals, checkpointing
   → Polish: Performance validation, documentation, final tests
4. Apply task rules:
   → Different files = mark [P] for parallel (registers.dml vs interfaces.dml)
   → Same file = sequential (no [P])
   → Research review before tests/implementation
   → Test RAG queries before writing tests
   → Tests before DML learning (TDD)
   → DML learning before DML implementation
   → Optional RAG queries: LLM checks knowledge first, uses RAG if needed
   → check_with_dmlc + build_simics_project after EVERY implementation task (not separate tasks)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All registers have DML implementations?
   → All interfaces declared?
   → Research review task before tests?
   → Test RAG queries before test writing?
   → DML learning gate before DML implementation?
   → CRITICAL BUILD REQUIREMENT mentions checking knowledge before RAG?
   → No separate check_with_dmlc/build_simics_project tasks?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Project structure**: `./simics-project/modules/device-name/`, `./simics-project/modules/device-name/test/` at repository root
- **DML files**: `device-name.dml`, `registers.dml`, `interfaces.dml` in module directory
- **Test files**: `test_*.py` in module test directory

## Phase 3.1: Setup

- [ ] T001 Verify connection: `get_simics_version()`
- [ ] T002 Create project: `create_simics_project(project_path="/absolute/path/to/workspace/simics-project")` ⚠️ ABSOLUTE PATH
- [ ] T003 Add skeleton: `add_dml_device_skeleton(project_path="/absolute/path/to/workspace/simics-project", device_name="DEVICE_NAME")` ⚠️ ABSOLUTE PATH
- [ ] T004 Checkout DMLC: `checkout_and_build_dmlc(project_path="/absolute/path/to/workspace/simics-project")` ⚠️ ABSOLUTE PATH
- [ ] T005 [P] Verify build: `build_simics_project(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` ⚠️ ABSOLUTE PATH

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [ ] T006 **GATE**: Read research.md → extract architecture decisions, MCP tool outputs, design patterns → document in implementation notes
- [ ] T007 [P] **RAG Query**: Execute `perform_rag_query("Simics Python device testing register read write verification patterns", source_type="python", match_count=10)` for test patterns
- [ ] T008 [P] Register access test - implement using RAG patterns
- [ ] T009 [P] Interface behavior test - implement using RAG patterns
- [ ] T010 [P] Device workflow test - implement using RAG patterns
- [ ] T011 [P] Validate test environment: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test")` ⚠️ ABSOLUTE PATH

## Phase 3.3: Core Implementation (ONLY after tests are failing)

**⚠️ CRITICAL BUILD REQUIREMENT**:
Before implementing EACH task in this phase:
1. Check if you have sufficient knowledge from research.md, data-model.md, and study notes
2. If knowledge is insufficient, execute `perform_rag_query()` to get missing patterns
3. Then proceed with implementation

After implementing EACH task:
1. `check_with_dmlc(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` for AI-enhanced diagnostics
2. `build_simics_project(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` to verify compilation

Do NOT mark task done until build succeeds. Do NOT proceed to next task if build fails.

**Note**: Do NOT create separate tasks for check_with_dmlc/build_simics_project calls - they are mandatory validation steps after EVERY implementation task, not standalone tasks.

- [ ] T012 **GATE**: Read .specify/memory/DML_grammar.md → document in implementation notes
- [ ] T013 **GATE**: Review study notes
- [ ] T014 **GATE**: Read device skeleton
- [ ] T015 [P] Register definitions in registers.dml (apply grammar + best practices + RAG if needed) [Then check_with_dmlc + build per CRITICAL BUILD REQUIREMENT]
- [ ] T016 [P] Interface declarations in interfaces.dml (apply grammar + best practices + RAG if needed) [Then check_with_dmlc + build per CRITICAL BUILD REQUIREMENT]
- [ ] T017-T020 Register logic, state management, error handling, validation (check_with_dmlc + build after EACH)

## Phase 3.4: Integration

- [ ] T021 Connect device to memory interface using transact() methods (check knowledge, use RAG if needed) [Then check_with_dmlc + build per CRITICAL BUILD REQUIREMENT]
- [ ] T022 Implement interrupt line connections and events (check knowledge, use RAG if needed) [Then check_with_dmlc + build per CRITICAL BUILD REQUIREMENT]
- [ ] T023 Add external port communications and protocols (check knowledge, use RAG if needed) [Then check_with_dmlc + build per CRITICAL BUILD REQUIREMENT]
- [ ] T024 Integrate with Simics checkpointing and state management (check knowledge, use RAG if needed) [Then check_with_dmlc + build per CRITICAL BUILD REQUIREMENT]
- [ ] T025 [P] Run comprehensive tests: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test")` ⚠️ ABSOLUTE PATH

## Phase 3.5: Polish

- [ ] T026 [P] Performance validation (<1% simulation overhead)
- [ ] T027 [P] Code review and cleanup (DML grammar compliance, error handling, logging)
- [ ] T028 [P] Update device documentation (README.md with usage examples)
- [ ] T029 [P] Update test documentation
- [ ] T030 Final validation: `run_simics_test(project_path="/absolute/path/to/workspace/simics-project")` ⚠️ ABSOLUTE PATH

## Dependencies

**Task Flow**:
- T001-T005 (Setup) → T006 (Research Review) → T007-T011 (Test RAG + Tests) → T012-T014 (DML Learning) → T015+ (Implementation with optional RAG) → T021-T025 (Integration with optional RAG) → T026-T030 (Polish)

**Critical Path**:
- Setup → Research review → Test RAG + Tests → DML learning → Implementation (with optional RAG) → Integration (with optional RAG) → Polish

**Parallel Opportunities**:
- T007-T008 (Test RAG queries - if multiple query categories)
- T008-T010 (Test file creation - different files)
- T015-T016 (Register and interface files - different files)
- T026-T029 (Polish tasks - documentation and validation)

## Parallel Example

**Test Creation (After T007 RAG query)**:
```bash
# Can run T008-T010 in parallel (different test files):
Task T008: "Register access test - implement using RAG patterns"
Task T009: "Interface behavior test - implement using RAG patterns"
Task T010: "Device workflow test - implement using RAG patterns"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**: Each contract file → contract test tasks [P] (register access, interface behavior)
2. **From Data Model**: Each register → DML implementation task, each interface → DML declaration task
3. **From User Stories**: Each workflow → integration test [P], quickstart steps → validation tasks
4. **Ordering**: Setup → Research Review → Test RAG Query → Tests → DML Learning → Implementation (with optional RAG) → Integration (with optional RAG) → Polish

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task
- [ ] **All MCP tool calls use ABSOLUTE paths** (SSE transport requirement)
- [ ] All MCP tool calls specify correct project_path parameter
- [ ] **No separate tasks for check_with_dmlc/build_simics_project** (they are validation steps in CRITICAL BUILD REQUIREMENT, not standalone tasks)
- [ ] Test execution tasks use appropriate suite parameter
- [ ] Device name consistently used across MCP tool calls
- [ ] RAG queries placed before test writing tasks
- [ ] Implementation tasks mention checking knowledge before using RAG

## Critical Gates

### Research Review Gate:
- [ ] Read research.md completely
- [ ] Extract and document in implementation notes:
  - **Architecture Decisions**: Key design choices, rationale
  - **Device Architecture Context**: High-level device patterns
  - **Patterns & Best Practices**: Coding patterns, conventions
  - **Constraints**: Technical limitations, requirements
  - **Dependencies**: Libraries, versions, compatibility notes
  - **MCP Tool Outputs**: Simics version, packages, platform info
- [ ] Verify comprehensive notes before writing tests

**What's in research.md**:
- Environment discovery results (MCP tool outputs)
- High-level device architecture overview (1-2 RAG queries for context)
- Architecture decisions from spec.md analysis
- Design implications for implementation

**What's NOT in research.md** (gathered during implementation):
- Detailed register implementation patterns → Use RAG during implementation
- Specific callback/method code → Use RAG during error recovery
- Test code examples → Use RAG before writing tests
- Error handling details → Use RAG during debugging

### DML Learning Gate:
- [ ] Read DML_grammar.md completely
- [ ] Document learnings in implementation notes: "## DML Grammar Study Notes"
- [ ] Verify comprehensive notes before starting DML implementation

**Note**: Tests are written using RAG query patterns first, and don't require deep DML study yet

## Execution Rules
1. **Prerequisites**: Verify plan.md and data-model.md exist
2. **Research Review**: Read research.md BEFORE writing tests or implementation
3. **RAG Before Tests**: Execute RAG queries BEFORE implementing tests
4. **RAG During Implementation**: Check knowledge first, use RAG only if needed
5. **DML Learning**: DML learning gate before ANY DML implementation
6. **Tests First**: Tests written using RAG patterns, before DML learning
7. **Study Notes**: Must reference in all DML tasks
8. **MCP Absolute Paths**: ALWAYS use absolute paths for `create_simics_project()`, `build_simics_project()`, `run_simics_test()` (SSE transport requirement)
9. **Validation Workflow**: After EVERY DML implementation task: check knowledge → use RAG if needed → implement → `check_with_dmlc()` → `build_simics_project()` → mark task done (NOT separate tasks)

## Common Failures
- ❌ Skip research.md review before tests/implementation
- ❌ Skip DML learning gate
- ❌ Incomplete study notes
- ❌ Ignore study notes during implementation
- ❌ Test after DML learning (should be before)
- ❌ Skip RAG queries before test writing
- ❌ Create separate RAG query tasks for implementation (should check knowledge first)
- ❌ **Use relative paths for MCP tools** (must be absolute for SSE transport)
- ❌ **Create separate tasks for check_with_dmlc/build_simics_project** (they are validation steps, not tasks)
- ✅ **Correct**: Setup → Research review → RAG query → tests → DML learning → implementation (check knowledge, use RAG if needed, then check_with_dmlc + build after each) → absolute paths for all MCP calls

## Error Recovery

**CRITICAL**: DO NOT guess fixes. Always use RAG queries with error-specific query strings to get solutions and examples.

### Build Errors

**Step 1: Extract Error Information**
**REQUIRED**: Use `check_with_dmlc(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")` to get AI-enhanced diagnostics.

From the diagnostic output, identify:
- **Error type**: syntax | semantic | template | pattern
- **Error keyword**: Core error term (e.g., "expected ';'", "unknown attribute")
- **Error context**: Affected construct (e.g., "register declaration", "interface method")
- **Error location**: File path + line number
- **AI suggestions**: Review any automatic fix suggestions provided by the tool

**Step 2: Check Study Notes (If Available)**
If DML study notes exist from learning gate:
1. Search "DML Grammar Study Notes" → syntax/declaration issues
2. On match → Apply pattern, skip to Step 6
3. On no match → Continue to Step 3

**Step 3: Query for Solution (Max 2 Attempts)**

**Attempt 1 - Specific Query:**
```python
perform_rag_query(
    query=f"DML 1.4 {error_keyword} {error_context} fix solution example",
    source_type="dml",  # or "docs" for grammar/syntax errors
    match_count=10
)
```

**If no relevant results, Attempt 2 - Broadened Query:**
```python
perform_rag_query(
    query=f"DML 1.4 {error_type} common issues examples",
    source_type="docs",
    match_count=15
)
```

**Query Pattern Examples:**
- `"syntax error: expected ';'"` → `"DML 1.4 register declaration semicolon syntax"`
- `"unknown attribute"` → `"DML 1.4 attribute declarations scoping"`
- `"template not found"` → `"DML 1.4 template inheritance interface"`

**Step 4: Review RAG Results**
- Examine code examples showing correct usage
- Identify pattern differences from your implementation
- Note relevant documentation excerpts

**Step 5: Apply Fix**
- Use examples as reference (adapt, don't copy blindly)
- Ensure fix aligns with Grammar study notes (if available)
- Apply to your specific use case

**Step 6: Verify & Iterate**
```bash
build_simics_project(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")
```
- ✅ **Build succeeds** → Continue to Step 7
- ❌ **Same error** → Try Attempt 2 query or escalate
- ⚠️ **New error** → Return to Step 1 with new error

**Step 7: Document Solution (Only If Build Succeeded)**
Append to `.specify/dml_diagnostics.md`:
```markdown
## [Error Type]: [Error Keyword] - [Date]

**Location**: `[file:line]`  
**Fix**: [One-line summary of what was changed]

### Problem
[2-3 sentences: What was wrong, why it failed]

### Solution
**Source**: [AI suggestion | RAG pattern | Study notes reference]  
**Changes**:
```dml
// Before (incorrect)
[Brief code snippet showing the error]

// After (corrected)
[Brief code snippet showing the fix]
```

**Key Lesson**: [One sentence about the pattern/rule to remember]

---
```
Then mark task complete.

**Example Entry**:
```markdown
## Syntax Error: Expected semicolon - 2025-10-31

**Location**: `registers.dml:45`  
**Fix**: Added semicolon after register declaration

### Problem
Register declaration was missing terminating semicolon. DML grammar requires semicolon after param declarations inside register body.

### Solution
**Source**: DML Grammar Study Notes (register declaration syntax)  
**Changes**:
```dml
// Before (incorrect)
register control @ 0x00 {
    param size = 4
}

// After (corrected)
register control @ 0x00 {
    param size = 4;
}
```

**Key Lesson**: All param declarations must end with semicolon in DML 1.4

---
```

### Test Failures

**Step 1: Identify Test Failure Type**
- Register access test → read/write/reset behavior
- Interface behavior test → method calls/return values
- Device workflow test → state transitions/events
- Python test framework → assertions/setup/teardown

**Step 2: Query for Solution (Max 2 Attempts)**
```python
# Attempt 1 - Specific
perform_rag_query(
    query=f"Simics Python test {test_scenario} example working code",
    source_type="python",
    match_count=10
)
```

**Query Pattern Examples:**
- `"register read returns wrong value"` → `"Simics Python test register read write verification"`
- `"interface method not found"` → `"Simics Python test interface method invocation"`
- `"device state transition failed"` → `"Simics Python test device state workflow"`

**Step 3: Review RAG Results**
- Examine working test examples
- Identify differences from your test implementation
- Note test patterns and assertions

**Step 4: Apply Fix**
- Adapt test patterns to your specific scenario
- Ensure test aligns with device behavior from spec.md

**Step 5: Verify**
```bash
run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test")
```

### Runtime Errors

**Step 1: Identify Runtime Issue Type**
- Device behavior → unexpected state/response
- Interface errors → connection/communication failures
- Memory errors → access violations/unmapped regions
- Event/timing → callback/sequence issues

**Step 2: Check Study Notes (If Available)**
If DML study notes exist:
1. Search "DML Best Practices Study Notes" → device behavior patterns
2. On match → Apply pattern, skip to Step 5
3. On no match → Continue to Step 3

**Step 3: Query for Solution (Max 2 Attempts)**
```python
# Attempt 1 - Specific
perform_rag_query(
    query=f"DML 1.4 {error_scenario} {error_context} runtime fix example",
    source_type="dml",
    match_count=10
)
```

**Query Pattern Examples:**
- `"device not responding to memory write"` → `"DML 1.4 memory mapped IO write handler"`
- `"interrupt not firing"` → `"DML 1.4 interrupt signal raise event trigger"`
- `"state not preserved"` → `"DML 1.4 checkpoint state serialization"`

**Step 4: Review RAG Results**
- Examine correct implementation patterns
- Identify behavioral differences
- Note state management approaches

**Step 5: Apply Fix**
- Adapt patterns to your device implementation
- Ensure behavior matches spec.md requirements

**Step 6: Verify**
```bash
build_simics_project(project_path="/absolute/path/to/workspace/simics-project", module="DEVICE_NAME")
run_simics_test(project_path="/absolute/path/to/workspace/simics-project", suite="modules/DEVICE_NAME/test")
```
