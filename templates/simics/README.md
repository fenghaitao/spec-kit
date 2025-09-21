# Simics Integration Templates

This directory contains templates for Intel Simics device modeling integration with spec-kit.

## Template Structure

### Commands (`commands/`)
- Device model specification commands
- Platform specification commands  
- Validation workflow commands

### Projects (`projects/`)
- Device model project templates
- Virtual platform project templates
- Testing and validation templates

### Examples (`examples/`)
- Sample device specifications
- Platform integration examples
- Validation scenario examples

## Usage

These templates are automatically included when initializing a spec-kit project with Simics support. They extend the core spec-kit workflow to support hardware device modeling and simulation development.

## Integration Points

- Extends `/specify` command for device specifications
- Enhances `/plan` command for implementation planning
- Augments `/tasks` command for validation workflows