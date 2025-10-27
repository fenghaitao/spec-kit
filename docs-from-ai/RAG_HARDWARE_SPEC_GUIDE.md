# RAG Query Guide for Hardware Specifications

**Purpose**: Guide for using RAG queries to fill gaps in hardware specifications during /specify and /plan phases  
**Date**: 2025-01-22

---

## Overview

When parsing external hardware specifications (PDFs, datasheets, manuals), information may be:
- **Incomplete**: Some register details missing
- **Unclear**: Ambiguous descriptions
- **Scattered**: Information spread across multiple sections
- **Implicit**: Behavior not explicitly documented

**Solution**: Use RAG (Retrieval-Augmented Generation) to query the original hardware specification documents.

---

## When to Use RAG

### During /specify Phase

Use RAG when parsing external hardware spec into spec.md:

1. **Missing Register Information**
   - Register offset not found
   - Bit field layout unclear
   - Access type (R/W/RO) not specified
   - Reset value not documented

2. **Unclear Operational Behavior**
   - Initialization sequence not clear
   - Side effects not documented
   - State transitions ambiguous
   - Error handling not specified

3. **Incomplete Interface Details**
   - Interrupt behavior unclear
   - DMA requirements not specified
   - Bus protocol details missing
   - Timing constraints not documented

### During /plan Phase

Use RAG when transforming spec.md into data-model.md:

1. **Implementation Details Needed**
   - DML-specific patterns for register type
   - Similar device examples
   - Best practices for specific behavior
   - Error handling patterns

2. **Clarifying Ambiguities**
   - Resolving [NEEDS CLARIFICATION] markers
   - Filling [RAG QUERY NEEDED] gaps
   - Verifying assumptions
   - Cross-referencing related sections

---

## Marking Strategy

### Two Types of Markers

#### 1. **[NEEDS CLARIFICATION: ...]** 
For questions that require **human decision** or **external input**

**Use when**:
- Design decision needed (e.g., "Should we use PCI or memory-mapped I/O?")
- Requirement not specified (e.g., "What should timeout range be?")
- Multiple valid options (e.g., "Which interrupt line to use?")

**Example**:
```markdown
**Base Address**: [NEEDS CLARIFICATION: Is this PCI BAR-based or fixed memory-mapped?]
```

**Resolution**: Human must decide or provide requirement

---

#### 2. **[RAG QUERY NEEDED: ...]**
For information that **exists in hardware spec** but wasn't captured during initial parsing

**Use when**:
- Information exists but wasn't found initially
- Details are in a different section of the spec
- Need to cross-reference multiple sections
- Clarification available in spec but unclear

**Example**:
```markdown
**CONTROL Register (0x00)** bit fields:
- Bits [7:6]: [RAG QUERY NEEDED: Purpose of bits 6-7 in CONTROL register]
- Bit 5: MODE_SELECT (R/W) - Operating mode selection
```

**Resolution**: Execute RAG query to find information in hardware spec

---

## RAG Query Patterns

### Pattern 1: Missing Register Details

**Scenario**: Register mentioned but details missing

**Marker**:
```markdown
| 0x08 | CONFIG | 32-bit | [RAG QUERY NEEDED: Access type for CONFIG register] | 0x0000 | Configuration |
```

**RAG Query**:
```python
perform_rag_query(
    "CONFIG register access type read write permissions",
    source_type="docs",
    filter="hardware_specification.pdf",
    match_count=5
)
```

**Update spec.md**:
```markdown
| 0x08 | CONFIG | 32-bit | R/W | 0x0000 | Configuration |
```

---

### Pattern 2: Missing Bit Field Layout

**Scenario**: Register defined but bit fields not detailed

**Marker**:
```markdown
**STATUS Register (0x04)** bit fields:
[RAG QUERY NEEDED: Complete bit field layout for STATUS register]
```

**RAG Query**:
```python
perform_rag_query(
    "STATUS register bit field definitions and layout",
    source_type="docs",
    filter="hardware_specification.pdf",
    match_count=5
)
```

**Update spec.md**:
```markdown
**STATUS Register (0x04)** bit fields:
- Bit 7: ERROR (R/O) - Error condition detected
- Bit 6: BUSY (R/O) - Device busy processing
- Bits [5:1]: Reserved
- Bit 0: READY (R/O) - Device ready
```

---

### Pattern 3: Unclear Operational Behavior

**Scenario**: Register purpose known but usage unclear

**Marker**:
```markdown
**Operational Behavior**:
- **Initialization**: [RAG QUERY NEEDED: Device initialization sequence and register write order]
```

**RAG Query**:
```python
perform_rag_query(
    "device initialization sequence register configuration order",
    source_type="docs",
    filter="hardware_specification.pdf",
    match_count=10
)
```

**Update spec.md**:
```markdown
**Operational Behavior**:
- **Initialization**: 
  1. Write 0x0 to CONTROL to disable device
  2. Write configuration to CONFIG register
  3. Write 0x1 to CONTROL.ENABLE to enable device
  4. Poll STATUS.READY until set
```

---

### Pattern 4: Missing Side Effects

**Scenario**: Register write behavior not documented

**Marker**:
```markdown
**CONTROL Register (0x00)** bit fields:
- Bit 0: DEVICE_ENABLE (R/W) - Enable device
  [RAG QUERY NEEDED: Side effects of writing to DEVICE_ENABLE bit]
```

**RAG Query**:
```python
perform_rag_query(
    "DEVICE_ENABLE bit side effects state changes behavior",
    source_type="docs",
    filter="hardware_specification.pdf",
    match_count=5
)
```

**Update spec.md**:
```markdown
**CONTROL Register (0x00)** bit fields:
- Bit 0: DEVICE_ENABLE (R/W) - Enable device
  * Side effects: Writing 1 triggers device initialization, resets COUNTER to 0, clears STATUS.ERROR
```

---

### Pattern 5: Scattered Information

**Scenario**: Information spread across multiple sections

**Marker**:
```markdown
**External Interfaces**:
- **Interrupt Lines**: [RAG QUERY NEEDED: Interrupt line assignment and behavior from sections 3.2 and 5.4]
```

**RAG Query**:
```python
perform_rag_query(
    "interrupt line assignment IRQ number interrupt behavior",
    source_type="docs",
    filter="hardware_specification.pdf",
    match_count=10
)
```

**Update spec.md**:
```markdown
**External Interfaces**:
- **Interrupt Lines**: IRQ 5 for timeout events, IRQ 6 for error conditions
  * Interrupt fires when STATUS.INTERRUPT_PENDING set
  * Clear by reading STATUS register
  * Edge-triggered, active high
```

---

## RAG Query Best Practices

### 1. **Be Specific in Queries**

❌ **Bad**: "register information"  
✅ **Good**: "CONTROL register bit 7 interrupt enable function and behavior"

❌ **Bad**: "device setup"  
✅ **Good**: "device initialization sequence register write order timing requirements"

### 2. **Use Technical Terms**

Include specific technical terms from the hardware spec:
- Register names (CONTROL, STATUS, CONFIG)
- Bit field names (DEVICE_ENABLE, INTERRUPT_ENABLE)
- Technical concepts (initialization, side effects, timing)

### 3. **Specify Source Type**

```python
# For hardware specification documents
source_type="docs"

# For DML device examples
source_type="dml"

# For Python test examples
source_type="python"

# For combined sources
source_type="source"
```

### 4. **Use Filters When Available**

```python
# Filter to specific document
filter="hardware_specification.pdf"

# Filter to specific section
filter="hardware_specification.pdf section 3"

# Filter to device family
filter="watchdog_timer_family"
```

### 5. **Adjust Match Count**

```python
# For specific information (default)
match_count=5

# For scattered information
match_count=10

# For comprehensive search
match_count=15
```

---

## Workflow Integration

### During /specify Phase

```markdown
## Execution Flow (main)
```
1. Parse user description from Input
2. If external hardware spec provided:
   a. Parse hardware spec document
   b. Extract register definitions
   c. For missing information: Mark with [RAG QUERY NEEDED: ...]
   d. Execute RAG queries to fill gaps
   e. Update spec.md with retrieved information
3. For unclear requirements: Mark with [NEEDS CLARIFICATION: ...]
4. Fill User Scenarios & Testing section
5. Generate Functional Requirements
6. Complete Hardware Specification section
7. Run Review Checklist
8. Return: SUCCESS (spec ready for planning)
```

### During /plan Phase

```markdown
## Phase 1: Design & Contracts

### Step 1.1: Create data-model.md

1. Read Hardware Specification from spec.md
2. Check for [RAG QUERY NEEDED] markers
3. If markers found:
   a. Execute suggested RAG queries
   b. Document results in research.md
   c. Use retrieved information in data-model.md
4. Transform spec.md registers into DML format
5. Add DML-specific implementation details
```

---

## Example: Complete Workflow

### Step 1: Initial Parsing (Incomplete)

**spec.md** (after initial parsing):
```markdown
**Register Map**:
| Offset | Name | Size | Access | Reset | Purpose |
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control |
| 0x04 | STATUS | 32-bit | [RAG QUERY NEEDED: Access type] | 0x0001 | Device status |

**CONTROL Register (0x00)** bit fields:
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupts
- Bits [6:1]: [RAG QUERY NEEDED: Purpose of bits 1-6 in CONTROL register]
- Bit 0: DEVICE_ENABLE (R/W) - Enable device

**Operational Behavior**:
- **Initialization**: [RAG QUERY NEEDED: Device initialization sequence]
```

### Step 2: Execute RAG Queries

**Query 1**: STATUS register access type
```python
result1 = perform_rag_query(
    "STATUS register access type read write permissions",
    source_type="docs",
    filter="hardware_spec.pdf",
    match_count=5
)
# Result: "STATUS register is read-only (R/O)"
```

**Query 2**: CONTROL register bits 1-6
```python
result2 = perform_rag_query(
    "CONTROL register bits 1 through 6 function purpose",
    source_type="docs",
    filter="hardware_spec.pdf",
    match_count=5
)
# Result: "Bits [6:4]: MODE_SELECT, Bits [3:1]: Reserved"
```

**Query 3**: Initialization sequence
```python
result3 = perform_rag_query(
    "device initialization sequence register configuration order",
    source_type="docs",
    filter="hardware_spec.pdf",
    match_count=10
)
# Result: "1. Disable device, 2. Configure mode, 3. Enable device"
```

### Step 3: Update spec.md (Complete)

**spec.md** (after RAG queries):
```markdown
**Register Map**:
| Offset | Name | Size | Access | Reset | Purpose |
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control |
| 0x04 | STATUS | 32-bit | R/O | 0x0001 | Device status |

**CONTROL Register (0x00)** bit fields:
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupts
- Bits [6:4]: MODE_SELECT (R/W) - Operating mode selection (0-7)
- Bits [3:1]: Reserved (must be 0)
- Bit 0: DEVICE_ENABLE (R/W) - Enable device

**Operational Behavior**:
- **Initialization**:
  1. Write 0x0 to CONTROL.DEVICE_ENABLE to disable device
  2. Write desired mode to CONTROL.MODE_SELECT (bits [6:4])
  3. Write 0x1 to CONTROL.DEVICE_ENABLE to enable device
  4. Poll STATUS.READY until set (bit 0)
```

### Step 4: Document in research.md

**research.md**:
```markdown
## RAG Queries Executed During /specify

### Query 1: STATUS Register Access Type
- **Query**: "STATUS register access type read write permissions"
- **Source**: hardware_spec.pdf
- **Result**: STATUS register is read-only (R/O)
- **Applied to**: spec.md Register Map table

### Query 2: CONTROL Register Bits 1-6
- **Query**: "CONTROL register bits 1 through 6 function purpose"
- **Source**: hardware_spec.pdf
- **Result**: Bits [6:4] = MODE_SELECT, Bits [3:1] = Reserved
- **Applied to**: spec.md CONTROL register bit fields

### Query 3: Initialization Sequence
- **Query**: "device initialization sequence register configuration order"
- **Source**: hardware_spec.pdf
- **Result**: Disable → Configure mode → Enable → Poll ready
- **Applied to**: spec.md Operational Behavior section
```

---

## Template Updates Summary

### spec-template.md

Added section:
```markdown
**RAG Query Guidance** *(for incomplete information)*:
If information is missing or unclear during /specify phase, use RAG to query the original hardware specification:
- **Missing register details**: `perform_rag_query("CONTROL register bit field definitions", source_type="docs", filter="hardware_spec.pdf")`
- **Unclear behavior**: `perform_rag_query("device initialization sequence and register write order", source_type="docs")`

Mark areas that need RAG queries with: [RAG QUERY NEEDED: specific question about hardware spec]
```

### plan-template.md

Added to Step 1.1:
```markdown
**If spec.md has [RAG QUERY NEEDED] markers**:
- Execute the suggested RAG queries to fill in missing information
- Update data-model.md with the retrieved information
- Document the RAG query and results in research.md for reference
```

---

## Benefits

### 1. **Complete Information Capture**
- ✅ No information left behind
- ✅ All details from hardware spec captured
- ✅ Gaps filled systematically

### 2. **Traceable Queries**
- ✅ Document what was queried
- ✅ Record where information came from
- ✅ Reproducible process

### 3. **Iterative Refinement**
- ✅ Can add more RAG queries later
- ✅ Can refine queries for better results
- ✅ Can query different sections

### 4. **Clear Distinction**
- ✅ [NEEDS CLARIFICATION] = Human decision needed
- ✅ [RAG QUERY NEEDED] = Information exists, need to find it
- ✅ Clear action items for each marker type

---

## Conclusion

**Use RAG queries as a systematic way to fill gaps in hardware specifications during parsing.**

Key practices:
1. ✅ Mark incomplete information with [RAG QUERY NEEDED: specific question]
2. ✅ Execute RAG queries with specific, technical terms
3. ✅ Update spec.md with retrieved information
4. ✅ Document queries and results in research.md
5. ✅ Distinguish between [NEEDS CLARIFICATION] (human decision) and [RAG QUERY NEEDED] (information exists)

This approach ensures complete, accurate hardware specifications while maintaining traceability and reproducibility.
