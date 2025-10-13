# RAG Documentation Search Integration

## Overview

This document describes the integration of RAG (Retrieval-Augmented Generation) documentation search into spec-kit templates. The `perform_rag_query` tool enables agents to search Simics documentation during planning, task generation, and implementation phases.

## What Changed

### `templates/plan-template.md` Updates

#### 1. Enhanced Phase 0 Research (Lines 191-202)
Added RAG documentation search capability alongside MCP tools:
- **RAG documentation search**: Use `perform_rag_query(query, source_type, match_count)` to search Simics documentation
- **Source types available**:
  * `source_type="dml"` - Search DML documentation only
  * `source_type="python"` - Search Python API documentation only
  * `source_type="source"` - Search both DML and Python sources
  * `source_type="docs"` - Search general Simics documentation
  * `source_type="all"` - Search all available sources

#### 2. Updated Research Output (Lines 204-211)
Enhanced research.md consolidation to include RAG findings:
- **RAG findings**: Document relevant code examples, API patterns, and best practices discovered
- **Output**: research.md with all NEEDS CLARIFICATION resolved, MCP tool outputs, and RAG documentation search results documented

#### 3. Enhanced Phase 1 Design (Line 227)
Added RAG support for contract generation:
- **RAG support**: Use `perform_rag_query("register interface patterns", source_type="source")` for additional implementation examples

#### 4. Progress Tracking (Lines 355-362)
Added RAG Documentation Search Status checklist:
- [ ] `perform_rag_query()` used for DML-specific research (source_type="dml")
- [ ] `perform_rag_query()` used for Python API research (source_type="python")
- [ ] `perform_rag_query()` used for implementation patterns (source_type="source")
- [ ] `perform_rag_query()` used for architectural guidance (source_type="docs")
- [ ] RAG search results documented in research.md
- [ ] Code examples and patterns extracted from RAG results
- [ ] Best practices identified and incorporated into design decisions

### `templates/tasks-template.md` Updates

#### 1. Enhanced Setup Phase (Lines 62-65)
Added RAG search tasks to documentation access phase:
- **T010**: `perform_rag_query("DML device implementation patterns", source_type="source", match_count=5)` for additional examples
- **T011**: `perform_rag_query("Simics register modeling", source_type="dml", match_count=5)` for register-specific guidance
- **T012**: Study and document retrieved documentation, examples, DML template, and RAG search results
- **T013**: Validate that documentation, examples, and RAG searches have been successfully retrieved

#### 2. Enhanced TDD Phase (Lines 75-79)
Added RAG search for test patterns:
- **T014**: `perform_rag_query("Simics Python test patterns", source_type="python", match_count=3)` for test examples
- Test tasks now reference both device examples and RAG results for patterns

#### 3. Enhanced Implementation Phase (Lines 91, 97)
Added RAG searches during implementation:
- **T019**: `perform_rag_query("DML register implementation", source_type="dml", match_count=3)` for implementation patterns
- **T025**: `perform_rag_query("device state management Simics", source_type="source", match_count=3)` for state handling patterns

#### 4. Enhanced Integration Phase (Line 110)
Added RAG search for integration patterns:
- **T030**: `perform_rag_query("Simics device interface integration", source_type="docs", match_count=3)` for integration patterns

#### 5. Updated Dependencies (Lines 135-144)
Enhanced Simics dependency chain to include RAG searches:
- Documentation access (T005-T009) before RAG searches (T010-T011)
- RAG searches (T010-T011) before study phase (T012)
- Validation (T013) before test RAG search (T014)
- Test RAG search (T014) before register tests (T015-T018)
- Register tests before implementation RAG searches (T019, T025)
- Implementation RAG searches before actual implementation
- Device implementation before integration RAG search (T030)
- Integration RAG search before integration tasks

#### 6. Enhanced Validation Checklist (Lines 200-202)
Added RAG-specific validation:
- [ ] RAG searches use appropriate source_type for each phase
- [ ] RAG search results documented before proceeding to implementation
- [ ] match_count parameter set appropriately (3-5 results typical)

#### 7. Updated Critical Gate (Lines 213-216, 219-224, 227-232)
Enhanced Pre-Test Phase Gate to include RAG:
- **GATE T010**: `perform_rag_query()` executed for DML device patterns with valid results
- **GATE T011**: `perform_rag_query()` executed for Simics register modeling with valid results
- **GATE T012**: Retrieved documentation, examples, DML template, and RAG search results studied
- **GATE T013**: Validation confirms all MCP tools and RAG searches returned valid content

Updated execution validation rules:
- RAG searches MUST be called immediately when encountered
- Use appropriate source_type and match_count (3-5 results typical)
- No Phase 3.2+ tasks can proceed until ALL setup MCP tools and RAG searches are executed

Added common execution failures:
- ❌ "Let's search with RAG" without actually invoking
- ❌ Wrong source_type (using "all" when specific type would be better)

## RAG Tool Reference

### Function Signature
```python
perform_rag_query(query: str, source_type: str = "all", match_count: int = 5)
```

### Parameters

#### `query` (required)
The search query string. Should be specific and focused.

**Examples:**
- "DML device implementation patterns"
- "Simics register modeling"
- "Python test patterns for devices"
- "device state management"
- "register interface patterns"

#### `source_type` (optional, default: "all")
Specifies which documentation sources to search:

| Source Type | Description | Use Case |
|------------|-------------|----------|
| `"dml"` | Simics DML device modeling examples | DML device implementations, modeling patterns, register definitions |
| `"python"` | Simics device Python test cases | Python test examples, test patterns, device testing code |
| `"source"` | Both DML and Python sources | Combined implementation and test examples |
| `"docs"` | General Simics documentation | Architecture, concepts, integration, reference manuals |
| `"all"` | All available sources | Broad research, initial exploration |

#### `match_count` (optional, default: 5)
Number of results to return. **Recommended: 5** for all searches to get comprehensive results.

## Usage Patterns by Phase

### Phase 0: Research (Planning)
**Goal**: Gather architectural information and design patterns

```python
# DML device modeling examples
perform_rag_query("DML device implementation examples", source_type="dml", match_count=5)

# Python test case examples
perform_rag_query("device Python test examples", source_type="python", match_count=5)

# Combined implementation and test examples
perform_rag_query("register implementation patterns", source_type="source", match_count=5)

# Documentation and architectural guidance
perform_rag_query("device interface design", source_type="docs", match_count=5)
```

### Phase 1: Design & Contracts (Planning)
**Goal**: Find specific implementation patterns for design decisions

```python
# Contract patterns
perform_rag_query("register interface patterns", source_type="source", match_count=5)
```

### Phase 3.1: Setup (Tasks)
**Goal**: Gather comprehensive documentation before implementation

```python
# Device patterns
perform_rag_query("DML device implementation patterns", source_type="source", match_count=5)

# Register modeling
perform_rag_query("Simics register modeling", source_type="dml", match_count=5)
```

### Phase 3.2: Tests (Tasks)
**Goal**: Find test patterns and examples

```python
# Test patterns
perform_rag_query("Simics Python test patterns", source_type="python", match_count=5)
```

### Phase 3.3: Implementation (Tasks)
**Goal**: Find specific implementation guidance during coding

```python
# Register implementation
perform_rag_query("DML register implementation", source_type="dml", match_count=5)

# State management
perform_rag_query("device state management Simics", source_type="source", match_count=5)
```

### Phase 3.4: Integration (Tasks)
**Goal**: Find integration patterns and best practices

```python
# Integration patterns
perform_rag_query("Simics device interface integration", source_type="docs", match_count=5)
```

## Best Practices

### 1. Choose Appropriate source_type
- **Use specific types** (`dml`, `python`, `source`) when you know what you're looking for
- **Use `docs`** for conceptual/architectural information
- **Use `all`** only for initial broad exploration

### 2. Set Reasonable match_count
- **5 results**: Standard for all queries (recommended)
- Provides comprehensive results without overwhelming output
- Consistent across all phases and use cases

### 3. Document Results
- Always document RAG findings in research.md or task notes
- Extract specific code examples and patterns
- Note which queries were most useful for future reference

### 4. Timing
- **Research phase**: Use RAG early to inform design decisions
- **Setup phase**: Execute RAG searches before writing tests
- **Implementation phase**: Use RAG for specific technical questions
- **Never skip**: RAG searches are part of the critical gate

### 5. Query Formulation
- Be specific: "DML register implementation" not "registers"
- Include context: "Simics Python test patterns" not "test patterns"
- Focus on patterns: "device state management" not "state"

## Integration with MCP Tools

RAG complements MCP tools by providing:
- **Broader context**: MCP tools provide specific examples, RAG provides patterns
- **Documentation search**: RAG searches indexed docs, MCP tools retrieve specific files
- **Pattern discovery**: RAG finds similar implementations across codebase
- **Best practices**: RAG surfaces recommended approaches from documentation

### Workflow
1. **MCP tools first**: Get environment info (`get_simics_version`, `list_installed_packages`)
2. **MCP documentation**: Retrieve specific docs (`get_simics_dml_1_4_reference_manual`)
3. **MCP examples**: Get concrete examples (`get_simics_device_example_i2c`)
4. **RAG searches**: Find patterns and additional examples
5. **Study phase**: Analyze all gathered information together
6. **Implementation**: Use both MCP tools and RAG results as reference

## Validation

### Pre-Implementation Checklist
- [ ] RAG searches executed for each phase
- [ ] Results documented in research.md or task notes
- [ ] Appropriate source_type used for each query
- [ ] match_count set based on query specificity
- [ ] Code examples extracted and analyzed
- [ ] Patterns identified and incorporated into design

### Common Issues
- **Empty results**: Query too specific or wrong source_type
- **Too many results**: Increase specificity or reduce match_count
- **Irrelevant results**: Refine query or use more specific source_type
- **Missing context**: Use broader source_type or increase match_count

## Examples

### Example 1: DML Device Research
```python
# Phase 0: Research
perform_rag_query("DML device modeling basics", source_type="dml", match_count=5)
# → Returns: DML syntax, device structure patterns, attribute definitions

# Phase 3.1: Setup
perform_rag_query("DML device implementation patterns", source_type="source", match_count=5)
# → Returns: Complete device implementations, register patterns, interface examples

# Phase 3.3: Implementation
perform_rag_query("DML register implementation", source_type="dml", match_count=5)
# → Returns: Specific register read/write implementations, bank definitions
```

### Example 2: Python Test Case Research
```python
# Phase 0: Research
perform_rag_query("device Python test examples", source_type="python", match_count=5)
# → Returns: Python test case examples, test structure, device testing patterns

# Phase 3.2: Tests
perform_rag_query("Simics Python test patterns", source_type="python", match_count=5)
# → Returns: Test case implementations, assertions, device testing code
```

### Example 3: Integration Research
```python
# Phase 1: Design
perform_rag_query("register interface patterns", source_type="source", match_count=5)
# → Returns: Interface definitions, register access patterns

# Phase 3.4: Integration
perform_rag_query("Simics device interface integration", source_type="docs", match_count=5)
# → Returns: Integration concepts, interface connections, best practices
```

## Troubleshooting

### Issue: No Results
**Cause**: Query too specific or wrong source_type
**Solution**: 
- Try broader query terms
- Use `source_type="all"` for initial search
- Check spelling and terminology

### Issue: Too Many Irrelevant Results
**Cause**: Query too broad or wrong source_type
**Solution**:
- Add more specific terms to query
- Use more specific source_type
- Reduce match_count

### Issue: Results Not Helpful
**Cause**: Query doesn't match documentation structure
**Solution**:
- Reformulate query using documentation terminology
- Try different source_type
- Combine with MCP tool results for better context

## Future Enhancements

Potential improvements to RAG integration:
1. **Semantic search**: Enhanced query understanding
2. **Result ranking**: Better relevance scoring
3. **Cross-reference**: Link RAG results with MCP tool outputs
4. **Caching**: Store frequently used queries
5. **Feedback loop**: Learn from which queries are most useful

---

**Integration Status**: ✅ Complete
**Last Updated**: 2025-10-13
**Version**: 1.0.0
