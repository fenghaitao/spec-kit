# Project Structure & Organization

## Repository Layout

### Core Directories

**`src/specify_cli/`** - CLI implementation
- Main entry point for the `specify` command
- Handles project initialization, system checks, and template management

**`templates/`** - Specification and workflow templates
- `spec-template.md` - Feature specification structure
- `plan-template.md` - Technical implementation plan structure
- `tasks-template.md` - Task breakdown structure
- `agent-file-template.md` - Agent context file template
- `commands/` - Slash command definitions for AI agents
  - `constitution.md`, `specify.md`, `clarify.md`, `plan.md`, `tasks.md`, `analyze.md`, `implement.md`

**`memory/`** - Constitutional and reference documents
- `constitution.md` - Core architectural principles (Simics-focused)
- `DML_grammar.md` - Device Modeling Language syntax reference
- `DML_Device_Development_Best_Practices.md` - Simics development patterns

**`scripts/`** - Automation utilities
- `bash/` - Linux/macOS shell scripts
- `powershell/` - Windows PowerShell scripts
- Used by AI agents during feature creation and project setup

**`docs/`** - User-facing documentation
- Installation guides, quickstart, integration examples
- Simics-specific documentation

**`experiments/`** - AI agent testing and validation
- Organized by agent type (vscode, windsurf)
- Contains real-world usage examples and test projects

## Generated Project Structure

When `specify init` runs, it creates this structure in the target project:

```
project-name/
├── .specify/
│   ├── memory/
│   │   ├── constitution.md          # Project principles
│   │   ├── DML_grammar.md           # (Simics projects)
│   │   └── DML_Device_Development_Best_Practices.md
│   ├── scripts/
│   │   └── bash/ or powershell/     # Automation scripts
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   └── tasks-template.md
│   └── specs/
│       └── 001-feature-name/        # Feature-specific directory
│           ├── spec.md              # Requirements and user stories
│           ├── plan.md              # Technical implementation plan
│           ├── tasks.md             # Task breakdown
│           ├── data-model.md        # Data structures
│           ├── research.md          # Technical research
│           ├── quickstart.md        # Validation scenarios
│           └── contracts/           # API specs, interfaces
└── AGENT.md                         # Agent context file (e.g., CLAUDE.md)
```

## Feature Organization

### Branch-Based Features
- Each feature gets a numbered branch: `001-feature-name`, `002-next-feature`
- Feature number auto-increments based on existing specs
- Branch name derived from feature description

### Feature Directory Contents

**`spec.md`** (Required)
- User stories and acceptance criteria
- Tech-agnostic requirements
- Marked with `[NEEDS CLARIFICATION]` for ambiguities

**`plan.md`** (Required)
- Technical implementation approach
- Technology choices with rationale
- Phase-based implementation strategy
- Constitutional compliance gates

**`tasks.md`** (Required)
- Executable task list derived from plan
- Dependency tracking and parallel execution markers
- TDD workflow integration

**`data-model.md`** (Optional)
- Entity definitions and relationships
- Database schemas or register maps (Simics)
- State management structures

**`contracts/`** (Optional)
- API specifications (OpenAPI, GraphQL)
- Interface definitions (DML interfaces for Simics)
- Message formats and protocols

**`research.md`** (Optional)
- Technical investigation results
- Library comparisons and benchmarks
- Package compatibility research

**`quickstart.md`** (Optional)
- Key validation scenarios
- Manual testing procedures
- Integration verification steps

## Naming Conventions

### Files
- Templates: `*-template.md`
- Commands: Lowercase, no extension in `commands/` directory
- Scripts: Kebab-case with appropriate extension (`.sh`, `.ps1`)
- Specs: Lowercase with hyphens (`spec.md`, `data-model.md`)

### Directories
- Feature specs: `NNN-feature-description` (e.g., `001-watchdog-timer`)
- Lowercase with hyphens for multi-word names
- Numbered sequentially starting from 001

### Branches
- Feature branches: `NNN-feature-description`
- Matches the spec directory name
- Created automatically by `/specify` command

## Constitutional Governance

### Memory Files
The `memory/` directory contains immutable principles that govern all development:

**`constitution.md`**
- Nine articles defining architectural principles
- Device-first, interface-first, test-first mandates
- Simplicity and anti-abstraction rules
- Version controlled with amendment process

**Domain-Specific References**
- `DML_grammar.md` - Language syntax for Simics projects
- `DML_Device_Development_Best_Practices.md` - Patterns and practices

### Template Enforcement
Templates operationalize constitutional principles through:
- Structured sections that prevent premature implementation details
- Checklists that enforce completeness
- Gates that validate architectural compliance
- Explicit markers for ambiguities and clarifications

## Workflow Integration

### Slash Commands
AI agents access commands from `templates/commands/`:
- `/constitution` - Create/update project principles
- `/specify` - Generate feature specification
- `/clarify` - Structured requirement clarification
- `/plan` - Create technical implementation plan
- `/tasks` - Generate executable task breakdown
- `/analyze` - Cross-artifact consistency check
- `/implement` - Execute implementation tasks

### Script Automation
Scripts in `scripts/bash/` or `scripts/powershell/`:
- `create-new-feature.sh` - Feature branch and directory setup
- `setup-plan.sh` - Plan initialization
- `update-agent-context.sh` - Sync agent context files
- `check-prerequisites.sh` - Validate system requirements
- `common.sh` - Shared utilities

## Simics-Specific Structure

For Simics hardware modeling projects:

```
project-name/
├── modules/
│   └── device-name/              # Device module
│       ├── device-name.dml       # Main device file
│       ├── registers.dml         # Register definitions
│       ├── interfaces.dml        # Interface declarations
│       ├── utility.dml           # Helper methods
│       └── test/                 # Device tests
│           ├── test_registers.py
│           ├── test_interfaces.py
│           └── s-device-name.py  # Main test file
├── bt/                           # Build tree (generated)
└── linux64/                      # Platform binaries (generated)
```

## Best Practices

### File Organization
- Keep templates in `templates/` - never modify in generated projects
- Constitutional documents in `memory/` are reference-only
- Feature specs in `specs/NNN-name/` are working documents
- Scripts are utilities, not implementation code

### Version Control
- Commit constitution changes with clear rationale
- Feature branches contain only feature-specific changes
- Template updates require testing with multiple AI agents
- Document breaking changes in CHANGELOG.md

### Documentation
- README.md for user-facing instructions
- spec-driven.md for methodology deep-dive
- CONTRIBUTING.md for contributor guidelines
- Domain-specific docs in `docs/` directory
