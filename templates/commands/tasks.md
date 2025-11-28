---
description: Generate an actionable, dependency-ordered tasks.md for Simics DML 1.4 device model implementation based on available design artifacts.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Workflow

### 1. Setup
Run `{SCRIPT}` from repo root → parse FEATURE_DIR and AVAILABLE_DOCS. All paths must be absolute.

### 2. Load Design Documents

**Required**: plan.md, spec.md, [device-name]-registers.xml
**Optional**: research.md, data-model.md, contracts/, test-scenarios.md

**Extract from spec.md**:
- **Hardware Spec**: Register map (ALL registers + side-effects), external signals, device states, memory interface
- **Functional Requirements**: User stories, acceptance criteria → map to test tasks
- **Test Scenarios**: Map to test implementation tasks

### 3. Generate tasks.md

Use `.specify/templates/tasks-template.md` as structure. Fill with device name from plan.md.

**Phase Structure**:
- **Phase 1**: Setup (project creation, register definitions)
- **Phase 2**: Foundational (knowledge + base tests) ⚠️ BLOCKS all requirements
- **Phase 3-N**: Per-Requirement (each requirement = Tests → Implementation → Validation → Commit)
- **Phase N-1**: Integration (memory, interrupts, checkpointing)
- **Phase N**: Polish (performance, docs, final validation)

### 4. Coverage Validation (BEFORE finalizing)

```
[ ] ALL registers (functional + ID/configuration)
[ ] ALL external signals (interrupts + resets)
[ ] ALL device states + transitions
[ ] ALL memory interface validation (width, alignment, burst, error)
[ ] ALL functional requirements → implementation + test tasks
```

**Gap Analysis**: If ANY unchecked → ADD missing tasks before finalizing.

### 5. Git Commit

```bash
cd [FEATURE_DIR]
git add tasks.md
git commit -m "tasks: [feature-name] - Generated implementation tasks ([X] tasks, [Y] phases)"
git log --oneline -1
```

### 6. Report

Output: path, task count per phase, coverage summary, git commit hash.

---

## Task Generation Rules

### Checklist Format (REQUIRED)

```text
- [ ] [TaskID] [P?] Description with file path
```

- **Checkbox**: `- [ ]` (required)
- **Task ID**: T001, T002... (sequential)
- **[P]**: Only if parallelizable
- **Description**: Action + exact file path

**Examples**:
- ✅ `- [ ] T001 Verify connection: get_simics_version()`
- ✅ `- [ ] T015 [P] Implement interrupt handling in simics-project/modules/device-name/device-name.dml`
- ❌ `- [ ] Create register tests` (missing ID, path)

### Task Coverage Mapping

| Source | Task Focus |
|--------|------------|
| Hardware Spec Registers | Side-effects, callbacks, state updates (NOT basic definitions - Phase 1 handles those) |
| Hardware Spec Signals | Signal interfaces, assertion/clear logic, timing |
| Hardware Spec Memory | Width/alignment/burst validation, error responses |
| Functional Requirements | Implementation tasks + test tasks |
| Device States | State variables, transition logic |
| Test Scenarios | Test implementation tasks [P] |

### Critical Requirements

1. **MCP Absolute Paths**: ALL MCP tool calls use absolute paths
2. **No Separate Build Tasks**: `check_with_dmlc` + `build_simics_project` are validation steps, not tasks
3. **Test File Naming**: Simics tests use `s-` prefix (e.g., `s-register-access.py`), NOT `test_`
4. **Knowledge Check**: Review research.md, data-model.md before RAG queries
5. **Git Commits**: Each requirement phase ends with mandatory commit
