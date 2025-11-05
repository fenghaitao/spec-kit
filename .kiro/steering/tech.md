# Technology Stack

## Core Technologies

### Language & Runtime
- **Python 3.11+**: Primary implementation language
- **uv**: Package manager and tool installer (replaces pip/pipx)

### CLI Tool
- **Typer**: Command-line interface framework
- **Rich**: Terminal formatting and output
- **httpx**: HTTP client with SOCKS support
- **platformdirs**: Cross-platform directory paths
- **readchar**: Interactive terminal input
- **truststore**: SSL/TLS certificate handling

### Build System
- **Hatchling**: PEP 517 build backend
- **pyproject.toml**: Project configuration and dependencies

## Project Structure

```
spec-kit/
├── src/specify_cli/          # CLI implementation
├── templates/                 # Spec, plan, and task templates
│   ├── commands/             # Slash command definitions
│   ├── spec-template.md
│   ├── plan-template.md
│   └── tasks-template.md
├── scripts/                   # Automation scripts
│   ├── bash/                 # Linux/macOS scripts
│   └── powershell/           # Windows scripts
├── memory/                    # Constitutional documents
│   ├── constitution.md
│   ├── DML_grammar.md
│   └── DML_Device_Development_Best_Practices.md
├── docs/                      # Documentation
└── experiments/               # AI agent experiments
```

## Common Commands

### Installation
```bash
# Install as persistent tool (recommended)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# One-time usage
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>
```

### Development
```bash
# Install dependencies
uv sync

# Run CLI locally
uv run specify --help

# Test CLI functionality
uv run specify check
uv run specify init test-project --ai claude
```

### Project Initialization
```bash
# Create new project
specify init <project-name>

# Initialize in current directory
specify init . --ai claude
specify init --here --ai copilot

# Force merge into non-empty directory
specify init . --force --ai claude

# Skip git initialization
specify init <project-name> --no-git

# Debug mode
specify init <project-name> --debug
```

### System Checks
```bash
# Verify prerequisites
specify check

# Check for AI agent tools (git, claude, gemini, code, cursor, etc.)
```

## Supported AI Agents

The CLI integrates with multiple AI coding assistants:
- Claude Code (`--ai claude`)
- GitHub Copilot (`--ai copilot`)
- Cursor (`--ai cursor`)
- Windsurf (`--ai windsurf`)
- Gemini CLI (`--ai gemini`)
- Qwen Code (`--ai qwen`)
- opencode (`--ai opencode`)
- Codex CLI (`--ai codex`)
- Kilo Code (`--ai kilocode`)
- Auggie CLI (`--ai auggie`)
- Roo Code (`--ai roo`)

## Simics Integration

### MCP Server
- **simics-mcp-server**: Model Context Protocol server for Simics automation
- Provides tools for project creation, building, and testing
- Integrated into plan and task templates for hardware device modeling

### Key MCP Tools
- `get_simics_version()` - Version verification
- `create_simics_project()` - Project structure creation
- `add_dml_device_skeleton()` - Device modeling scaffolding
- `build_simics_project()` - Build automation
- `run_simics_test()` - Test execution
- `search_packages()` - Package discovery
- `list_installed_packages()` - Package management

## Environment Variables

### SPECIFY_FEATURE
Override feature detection for non-Git repositories:
```bash
export SPECIFY_FEATURE="001-photo-albums"
```
Must be set in the AI agent context before using `/plan` or follow-up commands.

### GitHub Authentication
```bash
export GH_TOKEN="ghp_your_token_here"
export GITHUB_TOKEN="ghp_your_token_here"
```
Used for API requests, helpful in corporate environments.

## Script Variants

### Bash Scripts (`scripts/bash/`)
- `check-prerequisites.sh` - Verify system requirements
- `common.sh` - Shared utilities
- `create-new-feature.sh` - Feature branch creation
- `setup-plan.sh` - Plan initialization
- `update-agent-context.sh` - Agent context management

### PowerShell Scripts (`scripts/powershell/`)
- Same functionality as bash scripts
- Cross-platform Windows support
- Use `--script ps` flag during initialization

## Testing Approach

- Manual testing with AI agents in real workflows
- CLI functionality validation with sample projects
- Template validation through agent execution
- Integration testing with supported AI coding assistants
