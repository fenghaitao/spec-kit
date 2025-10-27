# Spec as Parser: Hardware Specification Transformation

**Status**: Design Clarification  
**Date**: 2025-01-22  
**Context**: Clarifying the role of /specify phase in parsing external hardware specifications

---

## Key Insight

**The /specify phase is a PARSER, not a summarizer.**

It transforms external hardware specifications (PDFs, Word docs, datasheets) into structured spec.md format that preserves ALL semantic information needed by downstream phases.

---

## Information Flow

```
External Hardware Spec (1000 pages, unstructured)
    ↓
    [PDF, Word, Datasheet format]
    [Vendor-specific terminology]
    [Mixed organization]
    ↓
/specify (PARSER PHASE)
    ↓
    Parses and structures:
    - Extract register definitions
    - Parse bit field layouts
    - Capture operational semantics
    - Document side effects
    - Standardize terminology
    ↓
spec.md (Structured, complete)
    ↓
    [Spec-kit markdown format]
    [Standardized tables]
    [Complete register semantics]
    [All information preserved]
    ↓
/plan (TRANSFORMER PHASE)
    ↓
    Transforms to DML format:
    - spec.md registers → DML register definitions
    - Bit fields → DML field declarations
    - Behaviors → DML methods
    - Add DML-specific details
    ↓
data-model.md (DML-ready)
    ↓
    [DML 1.4 structures]
    [Implementation-ready]
    ↓
/tasks → /implement
```

---

## The Problem with "Summary" Approach

### ❌ **What I Initially Proposed (WRONG)**

```markdown
### Hardware Specification (in spec.md)

**Register Summary**:
- Total registers: ~20 registers
- See hardware_specification.md for details

**Key Capabilities**:
- Enable/disable device
- Configure timeout
```

**Problem**: Loses critical information!
- ❌ No register offsets
- ❌ No bit field layouts
- ❌ No operational semantics
- ❌ No side effects
- ❌ /plan phase has no information to work with

---

## The Right Approach: Complete Parsing

### ✅ **What Should Happen (CORRECT)**

```markdown
### Hardware Specification (in spec.md)

**Register Map**:

| Offset | Name | Size | Access | Reset | Purpose |
|--------|------|------|--------|-------|---------|
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control |
| 0x04 | STATUS | 32-bit | R/O | 0x0001 | Device status |

**CONTROL Register (0x00)** bit fields:
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupts
- Bit 0: DEVICE_ENABLE (R/W) - Enable device

**Operational Behavior**:
- **Initialization**: Write 0x1 to CONTROL.DEVICE_ENABLE
- **Normal Operation**: Write data, set CONTROL.START
- **Error Handling**: STATUS.ERROR set on failure
```

**Benefits**: Preserves all information!
- ✅ Register offsets, sizes, access types
- ✅ Bit field layouts with descriptions
- ✅ Operational semantics (what happens when)
- ✅ Side effects (error handling, state changes)
- ✅ /plan phase has complete information

---

## Why This Matters

### **Semantic Information Must Flow**

The /plan phase needs to know:

1. **Register Semantics**
   - What does writing to CONTROL.DEVICE_ENABLE do?
   - What side effects occur?
   - What state changes happen?

2. **Bit Field Semantics**
   - What does each bit control?
   - What are valid values?
   - What happens on read vs write?

3. **Operational Semantics**
   - What's the initialization sequence?
   - What's the normal operation flow?
   - How are errors handled?

4. **Side Effects**
   - Does writing to one register affect another?
   - Are there timing constraints?
   - Are there ordering requirements?

**Without this information in spec.md, the /plan phase cannot create accurate data-model.md.**

---

## Spec.md as Structured Intermediate Format

### **Role of spec.md**

spec.md is the **structured intermediate representation** between:
- **Input**: Unstructured external hardware spec (vendor format)
- **Output**: DML-specific data-model.md (implementation format)

### **Transformation Stages**

```
Stage 1: Parse (/ specify)
    External Spec → spec.md
    - Vendor format → Spec-kit format
    - Unstructured → Structured tables
    - Vendor terms → Standard terms
    - Scattered info → Organized sections

Stage 2: Transform (/plan)
    spec.md → data-model.md
    - Spec-kit format → DML format
    - Register tables → DML register declarations
    - Bit fields → DML field declarations
    - Behaviors → DML methods
```

---

## Comparison: Spec vs Plan

### **spec.md (Hardware Specification)**

**Purpose**: Structured representation of hardware requirements

**Format**: Spec-kit markdown with tables

**Content**:
```markdown
**CONTROL Register (0x00)** bit fields:
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupt generation
- Bit 0: DEVICE_ENABLE (R/W) - Master enable for device

**Operational Behavior**:
- Initialization: Write 0x1 to CONTROL.DEVICE_ENABLE
- Normal Operation: Write data to DATA, set CONTROL.START
```

**Audience**: Developers, architects (human-readable)

---

### **data-model.md (DML Design)**

**Purpose**: DML-specific implementation design

**Format**: DML-ready structures

**Content**:
```markdown
### Register: CONTROL
- **Offset**: 0x00
- **Size**: 32-bit
- **Access**: R/W
- **Reset Value**: 0x00000000
- **Purpose**: Device control and enable flags
- **Fields**:
  - Bit 7: INTERRUPT_ENABLE (R/W)
    * DML template: `simple_storage`
    * On write: Enable interrupt generation
    * On read: Return current enable state
  - Bit 0: DEVICE_ENABLE (R/W)
    * DML template: `simple_storage`
    * On write: Enable device, trigger initialization
    * On read: Return current enable state
    * Side effect: Writing 1 triggers device initialization sequence

**DML Implementation Notes**:
- Use `register` declaration with `@ 0x00`
- Use `field` declarations for INTERRUPT_ENABLE and DEVICE_ENABLE
- Implement `write` method for DEVICE_ENABLE to trigger initialization
```

**Audience**: Implementation phase (DML code generation)

---

## Updated Template Design

### **spec-template.md Changes**

**Before** (Summary approach - WRONG):
```markdown
**Register Map**:
| Register Name | Purpose |
| CONTROL | Device enable |
```

**After** (Complete parsing - CORRECT):
```markdown
**Register Map**:
| Offset | Name | Size | Access | Reset | Purpose |
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control |

**CONTROL Register (0x00)** bit fields:
- Bit 7: INTERRUPT_ENABLE (R/W) - Enable interrupts
- Bit 0: DEVICE_ENABLE (R/W) - Enable device

**Operational Behavior**:
- Initialization: Write 0x1 to CONTROL.DEVICE_ENABLE
```

---

### **plan-template.md Changes**

**Execution Flow**:
```markdown
1. Load feature spec from spec.md
   → Extract complete Hardware Specification section
   → Parse register table (offsets, sizes, access, reset values)
   → Parse bit field definitions
   → Parse operational behaviors
   
2. Transform to DML format in data-model.md
   → For each register in spec.md:
      * Create DML register definition
      * Add DML-specific implementation details
      * Reference research.md for DML patterns
      * Add DML templates and methods
```

---

## Handling Large Hardware Specs

### **Problem**: External spec is 1000+ pages

### **Solution**: Hierarchical parsing with sub-features

```
External Hardware Spec (1000 pages)
    ↓
/specify [device-core]
    ↓
    Parse high-level structure
    Identify register categories
    Create sub-feature boundaries
    ↓
specs/[001-device-core]/spec.md (20 pages - architecture)
specs/[001-device-core]/sub-features.md (decomposition plan)
    ↓
/specify [001.1-control-registers]
    ↓
    Parse control register section (pages 10-50 of external spec)
    Extract 20 control registers
    Parse bit fields and behaviors
    ↓
specs/[001.1-control-registers]/spec.md (40 pages - complete)
    ↓
    Contains ALL information for 20 control registers:
    - Register table with offsets, sizes, access
    - Bit field breakdowns
    - Operational behaviors
    - Side effects
```

### **Key Point**: Each sub-feature spec.md is complete

Each sub-feature's spec.md contains:
- ✅ Complete register definitions for that sub-feature
- ✅ All bit field layouts
- ✅ All operational semantics
- ✅ All side effects
- ✅ Everything /plan needs for that sub-feature

---

## Benefits of This Approach

### 1. **Complete Information Flow**
- ✅ No information lost between phases
- ✅ /plan has everything it needs
- ✅ Semantic information preserved

### 2. **Structured Intermediate Format**
- ✅ Standardized spec-kit format
- ✅ Easy to parse and transform
- ✅ Human-readable and reviewable

### 3. **Scalable with Sub-Features**
- ✅ Each sub-feature spec.md is complete
- ✅ Manageable size per sub-feature
- ✅ Can be processed independently

### 4. **Clear Separation of Concerns**
- ✅ /specify = Parse external spec
- ✅ /plan = Transform to DML format
- ✅ /implement = Generate DML code

---

## Example: Watchdog Timer

### **External Hardware Spec (Input)**
```
Vendor Datasheet (PDF, 50 pages)
- Section 3.2: Register Map (pages 15-25)
- Section 4.1: Control Register (page 16)
  * Address: 0x1000
  * Size: 32 bits
  * Bit 7: INT_EN - Interrupt Enable
  * Bit 0: WDT_EN - Watchdog Enable
- Section 5.3: Initialization (page 30)
  * Write 0x81 to Control Register to enable
```

### **/specify Output (spec.md)**
```markdown
### Hardware Specification

**Register Map**:
| Offset | Name | Size | Access | Reset | Purpose |
| 0x00 | CONTROL | 32-bit | R/W | 0x0000 | Device control |

**CONTROL Register (0x00)** bit fields:
- Bit 7: INT_EN (R/W) - Interrupt Enable
- Bit 0: WDT_EN (R/W) - Watchdog Enable

**Operational Behavior**:
- Initialization: Write 0x81 to CONTROL (enables both INT_EN and WDT_EN)
```

### **/plan Output (data-model.md)**
```markdown
### Register: CONTROL
- **Offset**: 0x00
- **Size**: 32-bit
- **Access**: R/W
- **Reset Value**: 0x00000000
- **Fields**:
  - Bit 7: INT_EN (R/W)
    * DML template: `simple_storage`
    * On write: Enable/disable interrupt generation
  - Bit 0: WDT_EN (R/W)
    * DML template: `simple_storage`
    * On write: Enable/disable watchdog timer
    * Side effect: Starts countdown when enabled

**DML Implementation**:
```dml
register CONTROL @ 0x00 size 4 {
    field INT_EN @ [7] is (simple_storage);
    field WDT_EN @ [0] is (simple_storage) {
        method write(uint64 value) {
            default(value);
            if (value == 1) {
                // Start watchdog countdown
                start_timer();
            }
        }
    }
}
```
```

---

## Conclusion

**The /specify phase is a parser that transforms external hardware specifications into structured spec.md format, preserving all semantic information needed by downstream phases.**

Key takeaways:
1. ✅ spec.md contains complete register information (offsets, bit fields, behaviors)
2. ✅ /plan transforms spec.md into DML-specific data-model.md
3. ✅ Information flows completely from external spec → spec.md → data-model.md → implementation
4. ✅ For large specs, use hierarchical sub-features with complete parsing per sub-feature

This approach ensures that critical semantic information (register behaviors, side effects, operational sequences) is preserved throughout the workflow and available to all phases that need it.
