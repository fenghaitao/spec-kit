---
description: Execute the implementation planning workflow for Simics device models using DML 1.4. Reads hardware specification and generates design artifacts for device modeling.
handoffs:
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a checklist for the following domain...
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `{SCRIPT}` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH.

2. **Load context**: Read FEATURE_SPEC (hardware specification), register XML file (`[SPECS_DIR]/[device-name]-register.xml`), and `/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute workflow**: Follow IMPL_PLAN template structure:
   - Fill Technical Context (mark unknowns "NEEDS CLARIFICATION")
   - Fill Constitution Check, evaluate gates
   - **Phase 0**: Discovery MCP tools → Architectural RAG queries (1-2 max) → research.md → Git commit
   - **Phase 1**: data-model.md (DML patterns) + contracts/ + test-scenarios.md → Agent context update → Git commit

4. **Report**: Branch, artifacts, ready for /tasks command.

## Core Principles

1. **Sequential phases** - Complete Phase 0 before Phase 1
2. **Minimal RAG queries** - Phase 0: 1-2 architectural; Phase 1: 1-2 pattern RAG queries
3. **Validate each phase** - Verify files exist before proceeding
4. **Design only** - No implementation MCP tools (create_simics_project, etc.)

## Common Pitfalls

- Skipping Discovery MCP tools (get_simics_version, list_installed_packages, list_simics_platforms)
- Too many RAG queries (limit: 1-2 per phase)
- Leaving NEEDS CLARIFICATION unresolved
- Using MCP tool syntax in test-scenarios.md (use generic Simics CLI descriptions instead)
- Executing implementation MCP tools during planning (reserved for Phase 3)
- Not validating file existence before completion

## Phases

### Phase 0: Outline & Research

**Steps**:

1. **Identify unknowns** from Technical Context (NEEDS CLARIFICATION items)

2. **Discovery MCP Tools** (MANDATORY):
   - `get_simics_version()` → Simics Version
   - `list_installed_packages()` → Required Packages
   - `list_simics_platforms()` → Available Platforms

3. **Architectural RAG** (1-2 queries MAX):
   - Identify device category (timer, UART, PCI, DMA, etc.)
   - Query high-level architecture overview only
   - Example: `"DML timer device architecture counter overflow interrupt concepts"`
   - Extract: Architecture, design patterns, key concepts, **example code snippets**
   - Skip: Detailed implementations, callbacks, test code, error handling

4. **Create research.md** (see plan-template.md for structure):
   - DML Learning Prerequisites
   - Environment Discovery (Simics version, packages, platforms)
   - Device Architecture Context
   - Architecture Decisions (resolved NEEDS CLARIFICATION)
   - Implementation Strategy
   - **Example Code References** (code snippets from RAG for implementation reference)

5. **Update plan.md**: Replace all "NEEDS CLARIFICATION" with discovered values

6. **Validate**:
   ```bash
   ls -la [SPECS_DIR]/research.md
   grep "NEEDS CLARIFICATION" [SPECS_DIR]/plan.md  # Should return nothing
   ```

7. **Git commit**: `git commit -m "plan: [feature] - Phase 0 Research"`

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites**: research.md complete, Phase 0 validated

**Steps**:

1. **Create data-model.md** (see plan-template.md for structure):
   - **Extract registers from XML**: Parse `[SPECS_DIR]/[device-name]-register.xml` for register definitions (names, offsets, sizes, access types, bit fields, reset values, side-effects)
   - **Supplement from spec.md**: Add register purposes, operations, interfaces, and functional descriptions
   - **Add DML details**: Document side effects, access callbacks, state dependencies
   - **Execute 1-2 DML pattern RAG queries** (e.g., `"DML register bank implementation pattern"`, `"DML interrupt generation pattern"`)
   - **Document patterns** in "Implementation Patterns" section with the **example code snippets** from RAG results

2. **Create contracts/**: Register/interface behavior specifications
   - `contracts/register-access.md` - Read/write behavior
   - `contracts/interface-behavior.md` - Interface method contracts

3. **Create test-scenarios.md** (see plan-template.md for structure):
   - Extract from spec.md "User Scenarios & Testing"
   - Map: Acceptance Scenarios → Validation Steps, Edge Cases → Troubleshooting
   - Use generic Simics CLI descriptions, placeholders: `[DEVICE_NAME]`, `[REGISTER_NAME]`
   - **Execute 1-2 RAG queries** for test scenario patterns if needed (e.g., `"Simics dev_util register access pattern"`, `"Simics python object for testing"`)
   - **Document patterns** with example code snippets from RAG results in "Implementation Patterns" section if applicable

4. **Update agent context**: Run `{AGENT_SCRIPT}` to add DML/Simics technology

5. **Re-evaluate Constitution Check**: Review data-model.md, refactor if violations found

6. **Validate**:
   ```bash
   ls -la [SPECS_DIR]/data-model.md [SPECS_DIR]/test-scenarios.md [SPECS_DIR]/contracts/
   ```

7. **Git commit**: `git commit -m "plan: [feature] - Phase 1 Design"`

**Output**: data-model.md, contracts/*, test-scenarios.md

## Completion Validation

Before reporting completion, verify:

### Phase 0
```bash
ls -la [SPECS_DIR]/research.md
grep "NEEDS CLARIFICATION" [SPECS_DIR]/plan.md  # Should return nothing
```
- [ ] research.md >= 50 lines with MCP outputs (Simics version, packages, platforms) and architecture context
- [ ] Technical Context has NO "NEEDS CLARIFICATION"

### Phase 1
```bash
ls -la [SPECS_DIR]/data-model.md [SPECS_DIR]/test-scenarios.md [SPECS_DIR]/contracts/
```
- [ ] data-model.md has register/interface definitions + "Implementation Patterns" section
- [ ] contracts/ has >= 1 file (register-access.md, interface-behavior.md)
- [ ] test-scenarios.md uses generic Simics CLI (no MCP syntax)
- [ ] Constitution Check: PASS

### Report Format

```
✅ /plan command complete

**Branch**: [branch_name]
**Feature**: [device_name]
**Date**: [YYYY-MM-DD]

**Files Created**:
- ✅ plan.md (resolved Technical Context)
- ✅ research.md ([X] lines - Simics env, DML patterns)
- ✅ data-model.md ([X] registers, [X] interfaces, [X] states)
- ✅ test-scenarios.md ([X] scenarios)
- ✅ contracts/ ([X] files)

**Ready For**: /tasks command
```

## Key Rules

- Use absolute paths
- ERROR on unresolved NEEDS CLARIFICATION or constitution violations
- Git commit after each phase
- NO implementation MCP tools during planning
- Verify file existence before completion
