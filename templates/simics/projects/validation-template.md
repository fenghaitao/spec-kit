# Validation Framework: [MODEL_NAME]

**Feature Branch**: `[###-validation-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: Validation requirements: "$ARGUMENTS"

## Execution Flow (simics-validate)
```
1. Parse validation requirements from Input
   → If empty: ERROR "No validation requirements provided"
2. Extract validation scope from requirements
   → Identify: model type, test scenarios, coverage requirements, performance targets
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill Validation Strategy section
   → If no clear strategy: ERROR "Cannot determine validation approach"
5. Generate Test Scenario Specifications
   → Each test must be executable and verifiable
   → Mark ambiguous test requirements
6. Define Coverage Requirements and Metrics
7. Specify Performance Validation Criteria
8. Generate Test Environment Setup Requirements
9. Define Validation Automation Strategy
10. Run Review Checklist
    → If any [NEEDS CLARIFICATION]: WARN "Validation spec has uncertainties"
    → If implementation details found: ERROR "Remove tool-specific details"
11. Return: SUCCESS (validation spec ready for test implementation)
```

---

## ⚡ Validation Framework Guidelines
- ✅ Focus on WHAT to validate and HOW to measure success
- ❌ Avoid HOW to implement tests (no specific Simics commands, test scripts)
- 🧪 Written for validation engineers and test developers

### Section Requirements
- **Mandatory sections**: Must be completed for every validation framework
- **Optional sections**: Include only when relevant to the validation scope
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from validation requirements:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption needed
2. **Don't guess test details**: If requirements don't specify coverage metrics, mark it
3. **Think like a test engineer**: Every vague requirement should fail the "measurable and verifiable" check
4. **Common underspecified areas**:
   - Test coverage requirements and metrics definitions
   - Performance criteria and acceptance thresholds
   - Test data generation and input specification
   - Pass/fail criteria for complex behavioral tests
   - Test environment configuration and dependencies
   - Regression testing scope and frequency

---

## Validation Overview *(mandatory)*

### Validation Scope and Objectives
[Describe what is being validated and why validation is needed]

### Model Under Test
- **Model Type**: [Device Model/Virtual Platform/System Component]
- **Model Name**: [Specific model or platform being validated]
- **Validation Focus**: [Functional/Performance/Integration/Compliance]
- **Validation Depth**: [Unit/Integration/System-level testing]

### Success Criteria
- **Primary Objectives**: [What must be demonstrated for validation success]
- **Acceptance Thresholds**: [Quantitative criteria for validation completion]
- **Quality Gates**: [Checkpoints that must be passed during validation]

## Validation Strategy *(mandatory)*

### Testing Approach
- **Testing Philosophy**: [Black-box/White-box/Gray-box testing approach]
- **Test Methodology**: [Test-driven validation, specification-based testing]
- **Validation Stages**: [Progressive validation stages and their objectives]

### Test Categories and Priorities
| Category | Priority | Objective | Coverage Target |
|----------|----------|-----------|-----------------|
| [Functional] | [High] | [Verify basic functionality] | [100% of features] |
| [Performance] | [Medium] | [Validate performance requirements] | [Key scenarios] |
| [Integration] | [High] | [Verify system integration] | [All interfaces] |
| [Regression] | [Medium] | [Prevent quality degradation] | [Critical paths] |

### Risk-Based Testing Focus
- **High-Risk Areas**: [Components or scenarios with highest failure risk]
- **Critical Paths**: [Essential functionality that must work correctly]
- **Edge Cases**: [Boundary conditions and unusual scenarios]

## Test Scenario Specifications *(mandatory)*

### Functional Validation Test Scenarios

#### Core Functionality Tests
1. **Basic Operation Validation**
   - **Test ID**: FV-001
   - **Objective**: Verify basic device/platform operation
   - **Given**: [Initial test conditions]
   - **When**: [Test actions performed]
   - **Then**: [Expected results and verification criteria]
   - **Pass Criteria**: [Specific measurable outcomes]

2. **Interface Validation**
   - **Test ID**: FV-002
   - **Objective**: Verify interface compliance and behavior
   - **Test Steps**: [Detailed test procedure]
   - **Expected Results**: [Interface behavior verification]
   - **Verification Method**: [How results are checked]

*Example of marking unclear test requirements:*
- **Register Access Test**: [NEEDS CLARIFICATION: specific register addresses not defined]
- **Performance Test**: [NEEDS CLARIFICATION: performance thresholds not specified]

#### Behavioral Validation Tests
1. **State Transition Validation**
   - **Test Scope**: [Device state machine validation]
   - **Test Cases**: [Valid and invalid state transitions]
   - **Verification**: [State consistency checks]

2. **Error Handling Validation**
   - **Error Scenarios**: [Invalid inputs, fault conditions]
   - **Expected Behavior**: [Error detection and recovery]
   - **Recovery Validation**: [System recovery verification]

### Integration Validation Test Scenarios

#### Device Integration Tests
1. **Multi-Device Interaction**
   - **Test Configuration**: [Multiple device setup]
   - **Interaction Scenarios**: [Device-to-device communication]
   - **Verification Points**: [Data integrity, timing, synchronization]

2. **System-Level Integration**
   - **System Configuration**: [Complete system setup]
   - **Integration Scenarios**: [End-to-end system workflows]
   - **Success Metrics**: [System-level performance and functionality]

#### Software Integration Tests
1. **Driver Compatibility**
   - **Software Stack**: [OS and driver versions]
   - **Compatibility Tests**: [Driver installation and operation]
   - **Functionality Verification**: [Software-hardware interaction]

2. **Application Software Tests**
   - **Target Applications**: [Key application software]
   - **Usage Scenarios**: [Typical application workflows]
   - **Performance Validation**: [Application performance on platform]

## Coverage Requirements and Metrics *(mandatory)*

### Functional Coverage Requirements
- **Feature Coverage**: [Percentage of features that must be tested]
- **Interface Coverage**: [Percentage of interface scenarios to validate]
- **Use Case Coverage**: [Percentage of user scenarios to test]

### Structural Coverage Requirements
- **Code Coverage**: [If applicable, code coverage targets]
- **State Coverage**: [Percentage of device states to exercise]
- **Transition Coverage**: [Percentage of state transitions to validate]

### Test Coverage Metrics
| Coverage Type | Target Percentage | Measurement Method | Reporting Frequency |
|---------------|-------------------|-------------------|-------------------|
| [Functional] | [95%] | [Feature checklist] | [Daily] |
| [Interface] | [100%] | [Interface matrix] | [Weekly] |
| [Performance] | [80%] | [Benchmark suite] | [Per build] |

### Coverage Analysis and Reporting
- **Coverage Measurement Tools**: [Tools for measuring test coverage]
- **Coverage Gap Analysis**: [Process for identifying untested areas]
- **Coverage Improvement Process**: [How to address coverage gaps]

## Performance Validation Criteria *(include if performance is critical)*

### Performance Requirements
| Metric | Requirement | Measurement Method | Acceptance Criteria |
|--------|-------------|--------------------|-------------------|
| [Throughput] | [Value + Units] | [Test procedure] | [Pass/fail threshold] |
| [Latency] | [Value + Units] | [Measurement technique] | [Acceptable range] |
| [Resource Usage] | [Limits] | [Monitoring approach] | [Maximum limits] |

### Performance Test Scenarios
1. **Nominal Performance Testing**
   - **Test Conditions**: [Normal operational conditions]
   - **Performance Metrics**: [Throughput, latency, resource usage]
   - **Measurement Duration**: [Test execution time]

2. **Stress Testing**
   - **Stress Conditions**: [High load, extreme conditions]
   - **Stress Scenarios**: [Maximum throughput, minimum latency]
   - **Degradation Limits**: [Acceptable performance degradation]

3. **Scalability Testing**
   - **Scaling Parameters**: [System size, load levels]
   - **Scalability Metrics**: [Performance vs. scale relationship]
   - **Scaling Limits**: [Maximum supported scale]

### Performance Regression Prevention
- **Baseline Performance**: [Reference performance measurements]
- **Regression Thresholds**: [Acceptable performance variation]
- **Performance Monitoring**: [Continuous performance tracking]

## Test Environment Setup Requirements *(mandatory)*

### Test Environment Configuration
- **Hardware Requirements**: [Host system specifications]
- **Software Dependencies**: [Required software versions]
- **Simics Configuration**: [Simics version and setup requirements]
- **Test Data Requirements**: [Test datasets, configuration files]

### Test Infrastructure
- **Test Automation Framework**: [Automated test execution requirements]
- **Results Collection**: [Test result gathering and storage]
- **Test Reporting**: [Test report generation and distribution]

### Test Environment Management
- **Environment Setup**: [Steps to configure test environment]
- **Environment Maintenance**: [Keeping test environment current]
- **Environment Verification**: [Validating test environment correctness]

## Validation Automation Strategy *(mandatory)*

### Automation Scope
- **Automated Tests**: [Which tests will be automated]
- **Manual Tests**: [Which tests require manual execution]
- **Automation Priorities**: [Order of automation implementation]

### Test Execution Strategy
- **Continuous Integration**: [Integration with CI/CD pipelines]
- **Scheduled Testing**: [Regular automated test execution]
- **On-Demand Testing**: [Manual test triggering capabilities]

### Test Result Management
- **Result Collection**: [Automated result gathering methods]
- **Result Analysis**: [Automated analysis and trending]
- **Failure Investigation**: [Process for investigating test failures]

## Validation Deliverables and Timeline *(include if project has specific deliverable requirements)*

### Validation Deliverables
| Deliverable | Description | Due Date | Success Criteria |
|-------------|-------------|----------|------------------|
| [Test Plan] | [Detailed test plan document] | [Date] | [Approval criteria] |
| [Test Cases] | [Complete test case suite] | [Date] | [Coverage targets met] |
| [Test Results] | [Validation execution results] | [Date] | [Pass/fail criteria met] |

### Validation Timeline
1. **Test Planning Phase**: [Duration and key milestones]
2. **Test Development Phase**: [Test implementation timeline]
3. **Test Execution Phase**: [Validation execution schedule]
4. **Results Analysis Phase**: [Analysis and reporting timeline]

### Success Milestones
- **Planning Complete**: [Test plan approved and baseline established]
- **Infrastructure Ready**: [Test environment operational]
- **Tests Developed**: [All test cases implemented and verified]
- **Execution Complete**: [All validation tests executed]
- **Validation Passed**: [Success criteria met and documented]

---

## Review & Acceptance Checklist
*GATE: Automated checks run during simics-validate execution*

### Validation Framework Completeness
- [ ] No implementation details (specific test scripts, Simics commands)
- [ ] Focused on validation requirements and success criteria
- [ ] Written for validation engineers and test developers
- [ ] All mandatory sections completed for validation scope

### Test Specification Quality
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Test scenarios are complete and executable
- [ ] Coverage requirements are clearly defined and measurable
- [ ] Performance criteria are specific and verifiable
- [ ] Success criteria are unambiguous and achievable

### Validation Process Readiness
- [ ] Test environment requirements specified
- [ ] Automation strategy defined and feasible
- [ ] Deliverables and timeline are realistic
- [ ] Risk mitigation approaches identified

---

## Execution Status
*Updated by simics-validate main() during processing*

- [ ] Validation requirements parsed
- [ ] Validation scope extracted
- [ ] Ambiguities marked
- [ ] Validation strategy defined
- [ ] Test scenarios specified
- [ ] Coverage requirements defined
- [ ] Performance criteria specified
- [ ] Test environment requirements defined
- [ ] Automation strategy defined
- [ ] Review checklist passed

---