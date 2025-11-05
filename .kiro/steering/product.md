# Product Overview

## Spec Kit

Spec Kit is a framework for **Specification-Driven Development (SDD)** - a methodology that inverts traditional software development by making specifications executable rather than just documentation.

### Core Concept

Instead of writing code first and documentation second, SDD treats specifications as the primary artifact that generates implementation. The workflow is:

1. **Constitution** → Project principles and architectural guidelines
2. **Specification** → What to build and why (tech-agnostic)
3. **Plan** → Technical implementation approach with chosen tech stack
4. **Tasks** → Executable task breakdown
5. **Implementation** → Code generation from specifications

### Key Features

- **Slash Commands**: Structured workflow commands (`/constitution`, `/specify`, `/plan`, `/tasks`, `/implement`)
- **Template-Driven**: Enforces quality through structured templates that guide LLM behavior
- **Constitutional Governance**: Immutable architectural principles ensure consistency
- **Multi-Agent Support**: Works with Claude Code, GitHub Copilot, Cursor, Windsurf, and others
- **Simics Integration**: Specialized support for hardware device modeling with Simics simulator

### Target Users

- Development teams practicing AI-assisted development
- Organizations building hardware simulation models (Simics)
- Teams wanting structured, repeatable AI-driven development workflows
- Projects requiring specification-first, test-driven development

### Philosophy

Specifications don't serve code—code serves specifications. The gap between intent and implementation is eliminated by making specifications precise enough to generate working systems.
