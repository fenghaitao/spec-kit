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

## Workflow Overview

The `/plan` command executes a 2-phase planning workflow for Simics device modeling:

1. **Setup & Context Loading** - Initialize environment and load specifications
2. **Phase 0: Outline & Research** - Discover environment, query architecture, create research.md
3. **Phase 1: Design & Contracts** - Create data-model.md, contracts/, test-scenarios.md
4. **Completion Validation & Report** - Verify artifacts and report readiness for /tasks

**Key Outputs**: plan.md (filled), research.md, data-model.md, contracts/, test-scenarios.md

---

## Detailed Steps

### Step 1: Setup & Context Loading

**Actions**:
1. Run `{SCRIPT}` from repository root
2. Parse JSON output for: FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH
3. Read FEATURE_SPEC (hardware specification at `[SPECS_DIR]/spec.md`)
4. Read register XML file (`[SPECS_DIR]/[device-name]-register.xml`)
5. Read constitution file (`/memory/constitution.md`)
6. Load IMPL_PLAN template (already copied to `[SPECS_DIR]/plan.md`)

**Deliverable**: Environment configured, context loaded, ready for planning

### Step 2: Fill Technical Context & Constitution Check

**Actions**:
1. Extract technical details from spec.md and mark unknowns as "NEEDS CLARIFICATION"
2. Fill Technical Context section in plan.md:
   - Language/Version: DML 1.4
   - Simics Version: Mark NEEDS CLARIFICATION (will be resolved in Phase 0)
   - Required Packages: Mark NEEDS CLARIFICATION (will be resolved in Phase 0)
   - Available Platforms: Mark NEEDS CLARIFICATION (will be resolved in Phase 0)
   - Device Type, Hardware Interfaces, Performance Goals, Constraints, Scale/Scope
3. Evaluate constitution gates (complexity, architecture, dependencies)
4. Document gate results (PASS/FAIL) and justify violations if any

**Deliverable**: plan.md Technical Context filled, Constitution Check completed

### Step 3: Execute Phase 0 (Outline & Research)

**Actions**:
1. Identify all "NEEDS CLARIFICATION" items from Technical Context
2. Execute Discovery MCP Tools (MANDATORY):
   - `get_simics_version()` → Simics Version
   - `list_installed_packages()` → Required Packages
   - `list_simics_platforms()` → Available Platforms
3. Execute Architectural RAG queries (3-4 MAX):
   - Query 1: Architectural Overview
   - Query 2: Key Design Concepts
   - Query 3: Common Patterns (with code snippets)
   - Query 4: Device-specific patterns (optional)
4. Create research.md with structure from plan-template.md
5. Update plan.md: Replace all "NEEDS CLARIFICATION" with discovered values
6. Validate Phase 0 completion
7. Git commit Phase 0 artifacts

**Deliverable**: research.md, plan.md (fully resolved)

### Step 4: Execute Phase 1 (Design & Contracts)

**Actions**:
1. Create data-model.md:
   - Extract registers from XML and spec.md
   - Execute 1-2 DML pattern RAG queries
   - Document Implementation Patterns with code snippets
2. Create contracts/ directory with register-access.md and interface-behavior.md
3. Create test-scenarios.md from spec.md "User Scenarios & Testing"
4. Update agent context with DML/Simics technology
5. Re-evaluate Constitution Check
6. Validate Phase 1 completion
7. Git commit Phase 1 artifacts

**Deliverable**: data-model.md, contracts/, test-scenarios.md

### Step 5: Validate Completion & Report

**Actions**:
1. Execute validation checks for Phase 0 and Phase 1
2. Verify all files exist with required content
3. Confirm no "NEEDS CLARIFICATION" remains
4. Generate completion report with file details

**Deliverable**: Completion report, ready for /tasks command

---

## Core Principles

### 1. Sequential Phase Execution
- **Complete Phase 0 before Phase 1** - Research findings inform design decisions
- **No skipping steps** - Each phase builds on previous phase outputs
- **Validate before proceeding** - Use validation commands to confirm phase completion
- **Rationale**: Architectural understanding from Phase 0 prevents design rework in Phase 1

### 2. Minimal, Targeted RAG Queries
- **Phase 0 Limit: 3-4 architectural queries** - Focus on overview, concepts, patterns
- **Phase 1 Limit: 1-2 queries per pattern** - Only for specific DML/test patterns needed
- **Query Purpose**: Architectural guidance and code snippets, NOT detailed implementations
- **Rationale**: Excessive RAG queries dilute context and slow planning; detailed patterns gathered during implementation

### 3. Complete Resolution of Unknowns
- **Mark unknowns as "NEEDS CLARIFICATION"** in Technical Context during initial fill
- **Resolve ALL unknowns in Phase 0** using Discovery MCP tools and architectural RAG
- **ERROR if any remain** - No unresolved NEEDS CLARIFICATION before Phase 1
- **Rationale**: Ambiguity in planning leads to implementation blockers and rework

### 4. Design-Only Workflow
- **NO implementation MCP tools** - create_simics_project, add_dml_code, etc. reserved for Phase 3 (tasks)
- **Use ONLY**: get_simics_version, list_installed_packages, list_simics_platforms, RAG queries
- **Focus on artifacts**: research.md, data-model.md, contracts/, test-scenarios.md
- **Rationale**: Separation of planning (design) from execution (implementation) ensures complete understanding before coding

### 5. Validate Each Deliverable
- **File existence checks** - Verify files created before marking phase complete
- **Content validation** - Confirm minimum line counts, required sections present
- **Constitution compliance** - Re-check gates after design artifacts created
- **Rationale**: Early validation catches incomplete work before downstream dependencies fail

### 6. Git Commit Per Phase
- **Phase 0 commit** - After research.md created and plan.md updated
- **Phase 1 commit** - After data-model.md, contracts/, test-scenarios.md created
- **Commit messages** - Use format: `"plan: [feature] - Phase X [Name]"`
- **Rationale**: Phase-level commits provide clear audit trail and enable rollback if needed

## Common Pitfalls

- Skipping Discovery MCP tools (get_simics_version, list_installed_packages, list_simics_platforms)
- Too many RAG queries (limit: 3-4 in Phase 0 for architecture/concepts/patterns)
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

3. **Architectural RAG** (3-4 queries MAX):
   - **Query 1 - Architectural Overview**: Identify device category and query architecture
     * Example: `"DML timer device architecture counter overflow interrupt concepts"`
     * Extract: High-level architecture, components, typical registers/interfaces
   - **Query 2 - Key Design Concepts**: Query specific design concepts for device type
     * Example: `"DML timer counter overflow interrupt handling key concepts"`
     * Extract: Core concepts, state management, operational semantics
   - **Query 3 - Common Patterns**: Query implementation patterns for device category
     * Example: `"DML timer device common implementation patterns register bank events"`
     * Extract: Typical DML patterns (io_memory, signals, events), **example code snippets**
   - **Optional Query 4**: Additional device-specific pattern if needed
     * Example: `"DML periodic event scheduling timer pattern"`
   - Skip: Detailed implementations, callbacks, test code, error handling

4. **Create research.md** (see plan-template.md for structure):
   - DML Learning Prerequisites
   - Environment Discovery (Simics version, packages, platforms)
   - Device Architecture Context:
     * Architectural Overview (from Query 1)
     * Key Design Concepts (from Query 2)
     * Common Patterns for This Device Type (from Query 3)
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

Before reporting completion, verify all Phase 0 and Phase 1 requirements:

### Phase 0 Validation
- [ ] research.md >= 50 lines with MCP outputs (Simics version, packages, platforms) and architecture context
- [ ] Technical Context in plan.md has NO "NEEDS CLARIFICATION"
- [ ] Validation commands from Phase 0 passed successfully

### Phase 1 Validation
- [ ] data-model.md has register/interface definitions + "Implementation Patterns" section
- [ ] contracts/ has >= 1 file (register-access.md, interface-behavior.md)
- [ ] test-scenarios.md uses generic Simics CLI (no MCP syntax)
- [ ] Constitution Check: PASS
- [ ] Validation commands from Phase 1 passed successfully

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
