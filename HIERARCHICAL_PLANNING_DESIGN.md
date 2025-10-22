# Hierarchical Planning Design for Large Hardware Specifications

**Status**: Design Proposal  
**Date**: 2025-01-22  
**Context**: Addressing scalability issues with large hardware specifications (1000+ pages) and context window limits

---

## Problem Statement

### Current Issues

1. **Context Window Overflow**
   - Hardware specifications can exceed 1000 pages (~500K tokens)
   - Plan phase accumulates: spec.md + research.md + data-model.md + contracts/
   - Total context can reach 800+ pages (~400K tokens)
   - Exceeds most model context limits (128K-200K tokens)

2. **Cannot Re-run /plan**
   - Once plan.md is large, re-running /plan loads too much context
   - Iterative refinement becomes impossible
   - Changes require starting from scratch

3. **Long Execution Times**
   - /implement phase must load all previous artifacts
   - Processing 1000+ pages takes 30+ minutes
   - Timeout issues and poor user experience

4. **Monolithic Approach Doesn't Scale**
   ```
   /specify → spec.md (50 pages)
       ↓
   /plan → plan.md (200 pages) + research.md (100 pages) + data-model.md (150 pages)
       ↓ [Context: 500 pages = ~250K tokens]
   /tasks → tasks.md (300 pages)
       ↓ [Context: 800 pages = ~400K tokens] ❌ EXCEEDS LIMITS
   /implement → Must load all above + code
       ↓ [Context: 1000+ pages] ❌ IMPOSSIBLE
   ```

---

## Solution: Hierarchical Feature Decomposition

### Core Concept

Break large features into **manageable sub-features** that can be planned and implemented independently, while maintaining architectural coherence through a parent feature.

### Key Principles

1. **Hierarchical Structure**: Parent feature defines architecture, sub-features implement components
2. **Context Inheritance**: Sub-features inherit research and architecture from parent
3. **Focused Scope**: Each sub-feature has manageable context (<100 pages)
4. **Independent Execution**: Sub-features can be planned/implemented separately
5. **Incremental Progress**: Complete sub-features one at a time

---

## Proposed Architecture

### Directory Structure

```
specs/
├── [001-device-core]/              # Parent feature (main)
│   ├── spec.md                     # High-level device specification
│   ├── plan.md                     # Architecture overview (~20 pages)
│   ├── research.md                 # Research findings (~50 pages)
│   └── sub-features.md             # Sub-feature decomposition
│
├── [001.1-control-registers]/      # Sub-feature 1
│   ├── spec.md                     # Control register requirements (~10 pages)
│   ├── plan.md                     # Control register design (~30 pages)
│   ├── data-model.md               # Register definitions (~20 pages)
│   ├── contracts/                  # Register contracts
│   ├── tasks.md                    # Implementation tasks (~40 pages)
│   └── [implementation files]
│
├── [001.2-status-registers]/       # Sub-feature 2
│   ├── spec.md                     # Status register requirements (~8 pages)
│   ├── plan.md                     # Status register design (~25 pages)
│   ├── data-model.md               # Register definitions (~15 pages)
│   ├── contracts/                  # Register contracts
│   ├── tasks.md                    # Implementation tasks (~30 pages)
│   └── [implementation files]
│
├── [001.3-data-path]/              # Sub-feature 3
│   ├── spec.md                     # Data path requirements (~15 pages)
│   ├── plan.md                     # Data path design (~40 pages)
│   ├── data-model.md               # Register definitions (~30 pages)
│   ├── contracts/                  # Data path contracts
│   ├── tasks.md                    # Implementation tasks (~50 pages)
│   └── [implementation files]
│
└── [001.4-integration]/            # Sub-feature 4
    ├── spec.md                     # Integration requirements (~12 pages)
    ├── plan.md                     # Integration design (~30 pages)
    ├── tasks.md                    # Integration tasks (~40 pages)
    └── [implementation files]
```

### Context Size Comparison

#### Before (Monolithic)
```
/plan [device-core]
├── spec.md (50 pages)
├── hardware_specification/ (1000 pages) ❌
├── research.md (100 pages)
├── data-model.md (150 pages)
└── Total: ~1300 pages ❌ IMPOSSIBLE
```

#### After (Hierarchical)
```
/plan [001.1-control-registers]
├── specs/[001.1-control-registers]/spec.md (10 pages)
├── specs/[001-device-core]/research.md (50 pages, inherited)
├── specs/[001-device-core]/plan.md (20 pages, architecture)
└── Total: ~80 pages ✅ MANAGEABLE

/plan [001.2-status-registers]
├── specs/[001.2-status-registers]/spec.md (8 pages)
├── specs/[001-device-core]/research.md (50 pages, inherited)
├── specs/[001-device-core]/plan.md (20 pages, architecture)
├── specs/[001.1-control-registers]/plan.md (30 pages, dependency)
└── Total: ~108 pages ✅ MANAGEABLE
```

---

## Workflow

### Phase 1: Parent Feature Specification

```bash
/specify [device-core]
```

**Output**: `specs/[001-device-core]/spec.md`

```markdown
# Feature Specification: Device Core

## Device Purpose
[High-level description of the complete device]

## Sub-Features
This device is decomposed into the following sub-features:

1. **[001.1-control-registers]**: Control and configuration registers
   - Scope: ~20 registers (0x00-0x4C)
   - Purpose: Device enable, mode selection, configuration
   - Dependencies: None
   
2. **[001.2-status-registers]**: Status and monitoring registers
   - Scope: ~15 registers (0x50-0x8C)
   - Purpose: Device state, error flags, diagnostics
   - Dependencies: Control Registers
   
3. **[001.3-data-path]**: Data transfer and buffering
   - Scope: ~30 registers (0x90-0x12C)
   - Purpose: Data I/O, DMA, buffering
   - Dependencies: Control + Status Registers
   
4. **[001.4-integration]**: System integration
   - Scope: System-level integration
   - Purpose: Interrupt handling, bus interface, platform integration
   - Dependencies: All above sub-features

## Integration Requirements
[How sub-features work together]

## Hardware Specification Summary
- Total registers: ~65 registers
- Register address range: 0x00-0x12C
- See sub-feature specs for detailed register maps

## Constraints and Requirements
[Overall device constraints]
```

### Phase 2: Parent Feature Planning

```bash
/plan [device-core]
```

**Output**: `specs/[001-device-core]/plan.md` + `research.md`

```markdown
# Implementation Plan: Device Core

## Architecture Overview
[High-level architecture diagram and decisions]

## Sub-Feature Breakdown

### Sub-Feature 1: Control Registers [001.1]
- **Scope**: Registers 0x00-0x4C (20 registers)
- **Dependencies**: None (can start immediately)
- **Estimated Size**: ~100 pages total artifacts
- **Priority**: 1 (must complete first)

### Sub-Feature 2: Status Registers [001.2]
- **Scope**: Registers 0x50-0x8C (15 registers)
- **Dependencies**: Control Registers (needs device state)
- **Estimated Size**: ~80 pages total artifacts
- **Priority**: 2

### Sub-Feature 3: Data Path [001.3]
- **Scope**: Registers 0x90-0x12C (30 registers)
- **Dependencies**: Control + Status Registers
- **Estimated Size**: ~140 pages total artifacts
- **Priority**: 3

### Sub-Feature 4: Integration [001.4]
- **Scope**: System-level integration
- **Dependencies**: All above sub-features
- **Estimated Size**: ~90 pages total artifacts
- **Priority**: 4 (must complete last)

## Execution Order
1. Control Registers (001.1) - Start immediately
2. Status Registers (001.2) - Start after 001.1 complete
3. Data Path (001.3) - Start after 001.1 + 001.2 complete
4. Integration (001.4) - Start after all above complete

## Phase 0: Research (DONE ONCE)
[Research findings that apply to all sub-features]
- Simics version, packages, platforms
- DML patterns and examples
- Test patterns
- Device examples from RAG queries

## Phase 1: Architecture Design
[High-level design decisions that apply to all sub-features]
- Register address allocation strategy
- Naming conventions
- Interface design patterns
- Error handling approach

## Next Steps
1. Create sub-features.md with detailed decomposition
2. Run /specify for each sub-feature
3. Run /plan for each sub-feature in dependency order
4. Run /tasks and /implement for each sub-feature
5. Run /integrate to combine all sub-features
```

### Phase 3: Sub-Feature Specification

```bash
/specify [001.1-control-registers]
```

**Output**: `specs/[001.1-control-registers]/spec.md`

```markdown
# Feature Specification: Control Registers

**Parent Feature**: [001-device-core]  
**Sub-Feature ID**: 001.1  
**Dependencies**: None

## Scope
This sub-feature implements control and configuration registers (0x00-0x4C).

## Register Map

| Register Name | Offset | Purpose | Software Operations |
|---------------|--------|---------|---------------------|
| CONTROL | 0x00 | Device enable and mode | Write to enable/configure |
| CONFIG1 | 0x04 | Configuration set 1 | Write to configure |
| CONFIG2 | 0x08 | Configuration set 2 | Write to configure |
| MODE_SELECT | 0x0C | Operating mode selection | Write to select mode |
[... 16 more registers ...]

## Functional Requirements
[Specific to control registers only]

FR-001: System MUST allow software to enable/disable device via CONTROL register
FR-002: System MUST support 4 operating modes via MODE_SELECT register
[... more requirements ...]

## Integration Points
- Status registers will read device state from control registers
- Data path will check enable status from CONTROL register
- Integration layer will use MODE_SELECT for platform-specific behavior

## Constraints
- Register access must be atomic (32-bit aligned)
- Configuration changes take effect within 10 clock cycles
- Mode changes require device to be disabled first
```

### Phase 4: Sub-Feature Planning

```bash
/plan [001.1-control-registers]
```

**Output**: `specs/[001.1-control-registers]/plan.md` + `data-model.md` + `contracts/`

```markdown
# Implementation Plan: Control Registers

**Parent Feature**: [001-device-core]  
**Sub-Feature ID**: 001.1  
**Input**: specs/[001.1-control-registers]/spec.md

## Context Inheritance

### Inherited from Parent Feature
- **Research**: ../[001-device-core]/research.md (no need to repeat)
- **Architecture**: ../[001-device-core]/plan.md (follow architecture decisions)
- **Patterns**: Use DML patterns from parent research

### Focused Scope
- Only 20 control registers
- Estimated artifacts: ~100 pages total
- Context per phase: <80 pages

## Phase 0: Research (INHERITED)
Reference: ../[001-device-core]/research.md

No additional research needed. All DML patterns, Simics tools, and device examples
are already documented in parent feature research.

## Phase 1: Design

### data-model.md (FOCUSED - ~20 pages)
Only 20 registers with detailed definitions:
- CONTROL (0x00)
- CONFIG1 (0x04)
- CONFIG2 (0x08)
[... 17 more registers ...]

### contracts/ (FOCUSED)
Only control register contracts:
- contracts/control_register_access.md
- contracts/configuration_behavior.md
- contracts/mode_selection.md

### quickstart.md (FOCUSED)
Test only control register functionality:
- Enable device via CONTROL
- Configure via CONFIG1/CONFIG2
- Select mode via MODE_SELECT
- Verify configuration
```

### Phase 5: Sub-Feature Tasks

```bash
/tasks [001.1-control-registers]
```

**Output**: `specs/[001.1-control-registers]/tasks.md`

```markdown
# Implementation Tasks: Control Registers

**Parent Feature**: [001-device-core]  
**Sub-Feature ID**: 001.1

## Task Breakdown

### Phase 3.1: Setup (T001-T004)
- [ ] T001: Create Simics project structure (if not exists)
- [ ] T002: Add control registers module skeleton
- [ ] T003: Set up build system for control registers
- [ ] T004: Verify build system

### Phase 3.2: TDD - Control Register Tests (T005-T008)
- [ ] T005: Write CONTROL register access tests
- [ ] T006: Write CONFIG1/CONFIG2 register tests
- [ ] T007: Write MODE_SELECT register tests
- [ ] T008: Set up test environment

### Phase 3.3: Implementation - Control Registers (T009-T020)
- [ ] T009: Implement CONTROL register (0x00)
- [ ] T010: Implement CONFIG1 register (0x04)
- [ ] T011: Implement CONFIG2 register (0x08)
- [ ] T012: Implement MODE_SELECT register (0x0C)
[... T013-T020: remaining 16 registers ...]

### Phase 3.4: Integration (T021-T024)
- [ ] T021: Integrate all control registers
- [ ] T022: Validate register interactions
- [ ] T023: Run comprehensive tests
- [ ] T024: Document control register API

Total tasks: 24 (manageable for focused implementation)
```

### Phase 6: Sub-Feature Implementation

```bash
/implement [001.1-control-registers]
```

**Context loaded**:
- ✅ specs/[001.1-control-registers]/spec.md (~10 pages)
- ✅ specs/[001.1-control-registers]/plan.md (~30 pages)
- ✅ specs/[001.1-control-registers]/tasks.md (~40 pages)
- ✅ specs/[001-device-core]/research.md (~50 pages, inherited)
- **Total: ~130 pages** ✅ Manageable!

### Phase 7: Repeat for Other Sub-Features

```bash
# After 001.1 is complete
/specify [001.2-status-registers]
/plan [001.2-status-registers]
/tasks [001.2-status-registers]
/implement [001.2-status-registers]

# After 001.2 is complete
/specify [001.3-data-path]
/plan [001.3-data-path]
/tasks [001.3-data-path]
/implement [001.3-data-path]

# After all sub-features complete
/specify [001.4-integration]
/plan [001.4-integration]
/tasks [001.4-integration]
/implement [001.4-integration]
```

---

## Template Changes Required

### 1. New Template: `sub-features-template.md`

```markdown
# Sub-Features: [FEATURE NAME]

**Parent Feature**: [###-feature-name]  
**Created**: [DATE]  
**Status**: [Planning | In Progress | Complete]

## Decomposition Strategy

### Size Analysis
- Total estimated pages: [X] pages
- Threshold for decomposition: 100 pages
- Decision: Decompose into [N] sub-features

### Decomposition Criteria
- Logical component boundaries (e.g., register categories)
- Dependency relationships
- Size balance (~100 pages per sub-feature)
- Implementation order

## Sub-Features

### [###.1-sub-feature-name]
- **Scope**: [What this sub-feature covers]
- **Size Estimate**: [X] pages
- **Register Count**: [N] registers
- **Address Range**: [0xXX-0xYY]
- **Dependencies**: [None | Other sub-features]
- **Priority**: [1-5]
- **Status**: [Not Started | In Progress | Complete]
- **Estimated Effort**: [X] weeks

### [###.2-sub-feature-name]
- **Scope**: [What this sub-feature covers]
- **Size Estimate**: [X] pages
- **Register Count**: [N] registers
- **Address Range**: [0xXX-0xYY]
- **Dependencies**: [###.1]
- **Priority**: [1-5]
- **Status**: [Not Started | In Progress | Complete]
- **Estimated Effort**: [X] weeks

[Repeat for each sub-feature]

## Execution Order

### Phase 1: Foundation
1. [###.1-sub-feature-name] (no dependencies)

### Phase 2: Core Functionality
2. [###.2-sub-feature-name] (depends on ###.1)
3. [###.3-sub-feature-name] (depends on ###.1)

### Phase 3: Integration
4. [###.4-sub-feature-name] (depends on all above)

## Integration Plan

### Integration Points
- [How sub-features interact]
- [Shared interfaces]
- [Data flow between sub-features]

### Integration Testing
- [How to test integrated system]
- [Validation criteria]

### Completion Criteria
- [ ] All sub-features implemented
- [ ] Integration tests pass
- [ ] System-level validation complete
- [ ] Documentation complete
```

### 2. Update `spec-template.md`

Add after the Quick Guidelines section:

```markdown
## Feature Size Check (for Hardware Specifications)

**MANDATORY for Simics projects**: Before completing specification, estimate feature size:

### Size Estimation
1. **Count registers**: [N] registers
2. **Estimate pages per register**: ~2 pages (definition + tests)
3. **Total register pages**: [N × 2] pages
4. **Add overhead**: +50 pages (research, architecture, integration)
5. **Total estimate**: [N × 2 + 50] pages

### Decomposition Decision
- **If total < 100 pages**: Single feature (proceed normally)
- **If total > 100 pages**: **DECOMPOSE into sub-features**

### Decomposition Guidelines
If decomposition is required:
1. Create logical component boundaries (e.g., register categories)
2. Aim for ~20-30 registers per sub-feature (~100 pages)
3. Define clear dependencies between sub-features
4. Create sub-features.md with decomposition plan
5. Run /specify for each sub-feature separately

### Example Decomposition
For a device with 65 registers (~180 pages total):
- Sub-feature 1: Control Registers (20 registers, ~90 pages)
- Sub-feature 2: Status Registers (15 registers, ~80 pages)
- Sub-feature 3: Data Path (30 registers, ~110 pages)
- Sub-feature 4: Integration (system-level, ~40 pages)
```

### 3. Update `plan-template.md`

Add at the beginning of Execution Flow:

```markdown
## Feature Type Detection

**MANDATORY**: Determine if this is a parent feature or sub-feature:

### Parent Feature
- No parent feature reference in spec.md
- May have sub-features.md
- Executes full planning workflow
- Creates research.md (Phase 0)

### Sub-Feature
- Has "Parent Feature: [###-feature-name]" in spec.md
- Inherits research from parent
- Focuses on sub-feature scope only
- References parent architecture

## Execution Flow (/plan command scope)

### For Parent Features:
```
1. Load feature spec from Input path
   → Extract: Functional Requirements, Hardware Specification summary
2. Check feature size (from spec.md size estimation)
   → If > 100 pages: Verify sub-features.md exists
   → If sub-features exist: Create architecture overview only
3. Fill Technical Context
4. Execute Phase 0 → research.md (FULL RESEARCH)
5. Execute Phase 1 → Architecture design only
6. Stop - Sub-features will do detailed design
```

### For Sub-Features:
```
1. Load sub-feature spec from Input path
   → Extract: Parent Feature reference
   → Load parent feature's research.md and plan.md
2. Fill Technical Context (inherit from parent)
3. Skip Phase 0 (inherit parent's research.md)
4. Execute Phase 1 → Detailed design for this sub-feature only
   → data-model.md (focused on sub-feature registers)
   → contracts/ (focused on sub-feature contracts)
   → quickstart.md (focused on sub-feature validation)
5. Stop - Ready for /tasks
```

## Context Inheritance (for Sub-Features)

If this is a sub-feature (has parent feature reference):

### Inherited Context
1. **Research**: Load ../[parent-feature]/research.md
   - Simics version, packages, platforms
   - DML patterns and examples
   - Test patterns
   - DO NOT repeat research

2. **Architecture**: Load ../[parent-feature]/plan.md
   - Follow architecture decisions
   - Use naming conventions
   - Follow design patterns

3. **Dependencies**: Load dependent sub-feature plans
   - If sub-feature depends on [###.1], load [###.1]/plan.md
   - Extract interface definitions
   - Understand integration points

### Focused Scope
- Only plan components in this sub-feature's scope
- Reference parent and dependencies, don't duplicate
- Keep artifacts small and focused (<100 pages total)
```

### 4. Update `tasks-template.md`

Add at the beginning:

```markdown
## Sub-Feature Context

**If this is a sub-feature**:

### Parent Feature
- **Parent**: [###-parent-feature-name]
- **Sub-Feature ID**: [###.N]
- **Dependencies**: [List of other sub-features this depends on]

### Scope Boundaries
- **In Scope**: [What this sub-feature implements]
- **Out of Scope**: [What other sub-features implement]
- **Integration Points**: [How this connects to other sub-features]

### Task Numbering
- Use sub-feature prefix: T[###.N]-001, T[###.N]-002, etc.
- Example: T[001.1]-001 for first task in sub-feature 001.1
```

---

## Benefits

### 1. Scalable Context Management
- ✅ Each sub-feature has manageable context (<100 pages)
- ✅ Can always re-run /plan on any sub-feature
- ✅ No context window overflow
- ✅ Faster execution times (5-10 minutes per sub-feature)

### 2. Incremental Progress
- ✅ Complete sub-features one at a time
- ✅ See progress incrementally
- ✅ Can pause and resume work
- ✅ Easier to track completion

### 3. Parallel Development
- ✅ Independent sub-features can be developed in parallel
- ✅ Multiple developers/agents can work simultaneously
- ✅ Faster overall completion

### 4. Better Organization
- ✅ Clear component boundaries
- ✅ Focused documentation
- ✅ Easier to understand and maintain
- ✅ Better code organization

### 5. Flexible Iteration
- ✅ Can revise individual sub-features without affecting others
- ✅ Can add new sub-features later
- ✅ Can reorder sub-features if dependencies allow
- ✅ Easier to handle changes

---

## Implementation Checklist

### Phase 1: Template Creation
- [ ] Create `sub-features-template.md`
- [ ] Update `spec-template.md` with size check
- [ ] Update `plan-template.md` with context inheritance
- [ ] Update `tasks-template.md` with sub-feature context

### Phase 2: Workflow Updates
- [ ] Update `/specify` command to support sub-features
- [ ] Update `/plan` command to detect parent vs sub-feature
- [ ] Update `/tasks` command to handle sub-feature scope
- [ ] Update `/implement` command to load correct context

### Phase 3: Documentation
- [ ] Document decomposition guidelines
- [ ] Create examples of decomposed features
- [ ] Update user guides
- [ ] Create troubleshooting guide

### Phase 4: Testing
- [ ] Test with small feature (no decomposition)
- [ ] Test with large feature (requires decomposition)
- [ ] Test sub-feature planning
- [ ] Test sub-feature implementation
- [ ] Test integration of sub-features

---

## Example: Complete Workflow

### Device with 65 Registers (~180 pages)

```bash
# Step 1: Create parent feature spec
/specify "Create a network controller device with 65 registers"
# Output: specs/[001-network-controller]/spec.md
# Includes: Sub-features decomposition (4 sub-features)

# Step 2: Create parent feature plan (architecture only)
/plan [001-network-controller]
# Output: specs/[001-network-controller]/plan.md (~20 pages)
# Output: specs/[001-network-controller]/research.md (~50 pages)
# Output: specs/[001-network-controller]/sub-features.md

# Step 3: Create sub-feature 1 spec
/specify [001.1-control-registers]
# Output: specs/[001.1-control-registers]/spec.md (~10 pages)

# Step 4: Create sub-feature 1 plan
/plan [001.1-control-registers]
# Context: spec.md (10) + parent research (50) + parent plan (20) = 80 pages ✅
# Output: specs/[001.1-control-registers]/plan.md (~30 pages)

# Step 5: Create sub-feature 1 tasks
/tasks [001.1-control-registers]
# Context: spec (10) + plan (30) + parent research (50) = 90 pages ✅
# Output: specs/[001.1-control-registers]/tasks.md (~40 pages)

# Step 6: Implement sub-feature 1
/implement [001.1-control-registers]
# Context: spec (10) + plan (30) + tasks (40) + parent research (50) = 130 pages ✅
# Output: Implementation files

# Step 7-9: Repeat for sub-features 2, 3, 4
/specify [001.2-status-registers]
/plan [001.2-status-registers]
/tasks [001.2-status-registers]
/implement [001.2-status-registers]

# ... and so on

# Step 10: Integration
/specify [001.4-integration]
/plan [001.4-integration]
/tasks [001.4-integration]
/implement [001.4-integration]
```

**Total time**: ~2 hours (vs 30+ minutes timeout with monolithic approach)  
**Context per phase**: Always <150 pages ✅  
**Re-run capability**: Can re-run /plan on any sub-feature ✅

---

## Future Enhancements

### 1. Automatic Decomposition
- Agent automatically suggests decomposition based on size
- Proposes logical boundaries
- Estimates effort per sub-feature

### 2. Dependency Visualization
- Generate dependency graph
- Show execution order
- Highlight parallel opportunities

### 3. Progress Tracking
- Dashboard showing sub-feature completion
- Overall progress percentage
- Estimated time remaining

### 4. Smart Context Loading
- Load only necessary dependencies
- Lazy load on-demand
- Cache frequently accessed artifacts

---

## Conclusion

Hierarchical feature decomposition solves the fundamental scalability issues with large hardware specifications:

- ✅ **Context window limits**: Each sub-feature stays under 150 pages
- ✅ **Re-run capability**: Can always re-run /plan on sub-features
- ✅ **Execution time**: 5-10 minutes per sub-feature vs 30+ minutes timeout
- ✅ **Incremental progress**: Complete sub-features one at a time
- ✅ **Better organization**: Clear component boundaries and focused documentation

This design enables spec-kit to scale to arbitrarily large hardware specifications while maintaining usability and performance.
