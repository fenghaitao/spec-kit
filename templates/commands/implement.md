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

## Workflow

### 1. Setup
Run `{SCRIPT}` from repo root → parse FEATURE_DIR and AVAILABLE_DOCS. All paths must be absolute.

### 2. Checklist Verification (if checklists/ exists)
- Count `- [ ]` (incomplete) and `- [X]` (complete) in each checklist file
- If ANY incomplete: Display table, ask user "Proceed anyway? (yes/no)", wait for response
- If ALL complete: Auto-proceed

### 3. Load Context
- **REQUIRED**: tasks.md (task list), plan.md (architecture)
- **IF EXISTS**: spec.md, data-model.md, test-scenarios.md, contracts/, research.md

### 4. Project Setup
- Verify/create .gitignore if git repo detected (`git rev-parse --git-dir`)

### 5. Execute Tasks

**Execution Rules**:
- Phase-by-phase, respect dependencies
- Sequential tasks in order; parallel [P] tasks can run together
- TDD: test tasks before implementation tasks
- Tasks affecting same files run sequentially

**Code Update Strategy**:
- **CRITICAL**: For DML files (.dml) and test files (.py), use `apply_git_diff` tool to apply targeted patches
  - Generate git diff format patches for specific changes
  - Preserves existing code structure and comments
  - Reduces risk of overwriting unrelated code
- **ONLY** use `write_file` with `overwrite=True` for:
  - New files (no existing content)
  - Complete file replacement explicitly required
  - Small files where full rewrite is clearer
- **NEVER** use `write_file` with `overwrite=True` on existing DML or test files unless absolutely necessary

**After EACH Task**:
1. **Mark complete**: `- [ ] T###` → `- [X] T###` in tasks.md (use replace_string_in_file)
2. **Git commit**:
   ```bash
   cd <FEATURE_DIR>
   git add -A
   git commit -m "implement: <task-id> - <description> - <result>"
   git log --oneline -1
   ```

**Progress Tracking**:
- Report after each task
- Halt on non-parallel task failure
- For [P] tasks: continue with successful, report failed

---

## Error Recovery

### Build Failures (`check_with_dmlc` / `build_simics_project`)

**3-Strike Rule**: If 3 consecutive failures on same task:
- STOP and display failure summary with options:
  1. Revert to simpler implementation
  2. Continue debugging
  3. Request human assistance
- Wait for user response before continuing

**Recovery Steps**:
1. Capture error (type, file, line)
2. Review: DML_Device_Development_Best_Practices.md, DML_grammar.md, research.md
3. RAG query if needed: `perform_rag_query("<error message>", source_type="dml")`
4. Apply minimal fix using `apply_git_diff` (generate targeted patch for error location)
5. Re-validate: `check_with_dmlc()` → `build_simics_project()`
6. Git commit (even if failed): `"implement: <task-id> - error recovery attempt <N> - <result>"`
7. Document in research.md under "## Build Error Solutions"

### Test Failures (`run_simics_test`)

**Recovery Steps**:
1. Analyze: which test, expected vs actual, register values, state transitions
2. Review: DML best practices, data-model.md, research.md
3. RAG query if needed (DML or Python source_type)
4. Fix device logic or test using `apply_git_diff` (targeted patches)
5. Re-validate: build → test
6. Git commit
7. Document in research.md under "## Runtime Error Solutions"

### General Guidelines
- One fix at a time, validate after each
- Commit after every attempt (success/failure)
- Document learnings in research.md
- Targeted RAG queries with specific error context

---

## Completion

Verify:
- All tasks marked `- [X]` in tasks.md
- Features match spec.md
- Tests pass

Report:
- Total tasks: [N], Completed: [X], Failed: [Y]
- Task completion rate: [X/N * 100]%

**Note**: If tasks.md incomplete, run `/speckit.tasks` first.
