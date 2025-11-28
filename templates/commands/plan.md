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

**Outputs**: plan.md (filled), research.md, data-model.md, contracts/, test-scenarios.md

---

## Steps

### 1. Setup & Context Loading
1. Run `{SCRIPT}` from repo root → parse FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH
2. Read: spec.md, [device-name]-registers.xml, /memory/constitution.md
3. Load plan.md template

### 2. Fill Technical Context
1. Extract details from spec.md, mark unknowns as "NEEDS CLARIFICATION"
2. Fill plan.md Technical Context (DML 1.4, device type, interfaces, constraints)
3. Evaluate constitution gates (PASS/FAIL)

### 3. Phase 0 - Research

**Discovery MCP Tools** (MANDATORY):
- `get_simics_version()`, `list_installed_packages()`, `list_simics_platforms()`

**Read DML References** (MANDATORY):
- `.specify/memory/DML_grammar.md`, `.specify/memory/DML_Device_Development_Best_Practices.md`, `.specify/memory/Simics_Model_Test_Best_Practices.md`

**RAG Queries** (3-4 MAX):
1. Architectural Overview (device category, components)
2. Key Design Concepts (state management, semantics)
3. Common Patterns (DML patterns, code snippets)
4. Device-specific patterns (optional)

**Create research.md**:
- Environment Discovery, Architecture Context, Example Code References, Implementation Notes

**Update plan.md**: Replace ALL "NEEDS CLARIFICATION" with discovered values

**Git commit**:
```bash
cd [SPECS_DIR]
git add research.md plan.md
git commit -m "plan: [feature-name] - Phase 0: Research and environment discovery"
```

### 4. Phase 1 - Design & Contracts

**Create data-model.md**:
- Extract registers from XML + spec.md
- Execute 1-2 DML pattern RAG queries
- Document Implementation Patterns with code snippets

**Create contracts/**:
- `register-access.md` (read/write behavior)
- `interface-behavior.md` (interface contracts)

**Create test-scenarios.md**:
- Extract from spec.md "User Scenarios & Testing"
- Use generic Simics CLI (no MCP syntax), placeholders: `[DEVICE_NAME]`, `[REGISTER_NAME]`

**Update agent context**: Run `{AGENT_SCRIPT}`

**Git commit**:
```bash
cd [SPECS_DIR]
git add data-model.md contracts/ test-scenarios.md
git commit -m "plan: [feature-name] - Phase 1: Design artifacts and contracts"
```

### 5. Completion Validation

**Phase 0**:
- [ ] research.md >= 50 lines with environment discovery
- [ ] plan.md has NO "NEEDS CLARIFICATION"
- [ ] Git commit verified

**Phase 1**:
- [ ] data-model.md has registers + Implementation Patterns
- [ ] contracts/ has >= 1 file
- [ ] test-scenarios.md uses generic Simics CLI
- [ ] Git commit verified

**Report**:
```
✅ /plan command complete
Branch: [branch_name] | Feature: [device_name]
Files: plan.md, research.md, data-model.md, test-scenarios.md, contracts/
Git Commits: Phase 0 [hash], Phase 1 [hash]
Ready For: /tasks command
```

---

## Core Principles

1. **Sequential Execution**: Complete Phase 0 before Phase 1 (research informs design)
2. **Minimal RAG**: Phase 0: 3-4 queries, Phase 1: 1-2 per pattern
3. **Resolve Unknowns**: ERROR if any "NEEDS CLARIFICATION" remains after Phase 0
4. **Design-Only**: NO implementation MCP tools (reserved for /implement)
5. **Git Commits**: After each phase for audit trail

## Common Pitfalls

- Skipping Discovery MCP tools
- Too many RAG queries
- Leaving NEEDS CLARIFICATION unresolved
- Using MCP tool syntax in test-scenarios.md
- Executing implementation MCP tools during planning
