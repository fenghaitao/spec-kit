#!/bin/bash
# setup-simics-validate.sh - Initialize Simics validation framework project
# Usage: setup-simics-validate.sh --json "{validation_requirements}"

set -euo pipefail

# Default values
VALIDATION_REQUIREMENTS=""
JSON_OUTPUT=false
DEBUG=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            VALIDATION_REQUIREMENTS="$2"
            JSON_OUTPUT=true
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        *)
            VALIDATION_REQUIREMENTS="$1"
            shift
            ;;
    esac
done

# Function to log debug messages
debug_log() {
    if [[ "$DEBUG" == "true" ]]; then
        echo "[DEBUG] $1" >&2
    fi
}

# Function to generate unique branch name
generate_branch_name() {
    local model_name="$1"
    local timestamp=$(date +%s)
    local random_suffix=$(( RANDOM % 1000 ))
    local clean_name=$(echo "$model_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    echo "${timestamp}-validate-${clean_name}-${random_suffix}"
}

# Function to extract model name from requirements
extract_model_name() {
    local requirements="$1"
    # Look for model names in validation requirements
    if echo "$requirements" | grep -qi "uart\|serial"; then
        echo "uart-controller"
    elif echo "$requirements" | grep -qi "timer"; then
        echo "timer-device"
    elif echo "$requirements" | grep -qi "platform\|system"; then
        echo "virtual-platform"
    elif echo "$requirements" | grep -qi "processor\|cpu"; then
        echo "processor-model"
    elif echo "$requirements" | grep -qi "memory\|ddr"; then
        echo "memory-controller"
    elif echo "$requirements" | grep -qi "network\|ethernet"; then
        echo "network-device"
    else
        # Fallback: extract first meaningful word
        echo "$requirements" | head -n1 | tr ' ' '\n' | grep -v '^$' | head -n1 | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g' || echo "model"
    fi
}

# Function to determine model type from requirements
determine_model_type() {
    local requirements="$1"
    if echo "$requirements" | grep -qi "device\|controller\|peripheral"; then
        echo "device"
    elif echo "$requirements" | grep -qi "platform\|system"; then
        echo "platform"
    elif echo "$requirements" | grep -qi "processor\|cpu"; then
        echo "processor"
    elif echo "$requirements" | grep -qi "component\|module"; then
        echo "component"
    else
        echo "generic"
    fi
}

# Function to determine validation scope from requirements
determine_validation_scope() {
    local requirements="$1"
    local scopes=()
    
    # Look for validation scope indicators
    if echo "$requirements" | grep -qi "functional\|function\|behavior"; then
        scopes+=("functional")
    fi
    if echo "$requirements" | grep -qi "performance\|speed\|throughput\|latency"; then
        scopes+=("performance")
    fi
    if echo "$requirements" | grep -qi "integration\|system"; then
        scopes+=("integration")
    fi
    if echo "$requirements" | grep -qi "compliance\|standard\|specification"; then
        scopes+=("compliance")
    fi
    if echo "$requirements" | grep -qi "regression\|compatibility"; then
        scopes+=("regression")
    fi
    if echo "$requirements" | grep -qi "stress\|load\|robustness"; then
        scopes+=("stress")
    fi
    
    # Default to functional if no specific scope identified
    if [[ ${#scopes[@]} -eq 0 ]]; then
        scopes+=("functional")
    fi
    
    # Join array with commas
    IFS=','
    echo "${scopes[*]}"
}

# Function to extract test categories from requirements
extract_test_categories() {
    local requirements="$1"
    local categories=()
    
    # Look for test category indicators
    if echo "$requirements" | grep -qi "unit\|component"; then
        categories+=("unit")
    fi
    if echo "$requirements" | grep -qi "integration\|interface"; then
        categories+=("integration")
    fi
    if echo "$requirements" | grep -qi "system\|end.*to.*end"; then
        categories+=("system")
    fi
    if echo "$requirements" | grep -qi "acceptance\|validation"; then
        categories+=("acceptance")
    fi
    if echo "$requirements" | grep -qi "performance\|benchmark"; then
        categories+=("performance")
    fi
    if echo "$requirements" | grep -qi "security\|safety"; then
        categories+=("security")
    fi
    
    # Default to basic categories if none identified
    if [[ ${#categories[@]} -eq 0 ]]; then
        categories+=("functional" "integration")
    fi
    
    # Join array with commas
    IFS=','
    echo "${categories[*]}"
}

# Main execution
main() {
    debug_log "Starting Simics validation project setup"
    debug_log "Validation requirements: $VALIDATION_REQUIREMENTS"
    
    if [[ -z "$VALIDATION_REQUIREMENTS" ]]; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo '{"error": "No validation requirements provided", "success": false}'
            exit 1
        else
            echo "Error: No validation requirements provided" >&2
            exit 1
        fi
    fi
    
    # Extract validation information
    local model_name=$(extract_model_name "$VALIDATION_REQUIREMENTS")
    local model_type=$(determine_model_type "$VALIDATION_REQUIREMENTS")
    local validation_scope=$(determine_validation_scope "$VALIDATION_REQUIREMENTS")
    local test_categories=$(extract_test_categories "$VALIDATION_REQUIREMENTS")
    local branch_name=$(generate_branch_name "$model_name")
    
    debug_log "Extracted model name: $model_name"
    debug_log "Determined model type: $model_type"
    debug_log "Validation scope: $validation_scope"
    debug_log "Test categories: $test_categories"
    debug_log "Generated branch name: $branch_name"
    
    # Create project directory structure
    local project_root=$(pwd)
    local specs_dir="$project_root/specs/$branch_name"
    local spec_file="$specs_dir/spec.md"
    local contracts_dir="$specs_dir/contracts"
    local simics_dir="$specs_dir/simics"
    local impl_details_dir="$specs_dir/implementation-details"
    local tests_dir="$specs_dir/tests"
    
    debug_log "Creating directory structure"
    mkdir -p "$specs_dir"
    mkdir -p "$contracts_dir"
    mkdir -p "$simics_dir"
    mkdir -p "$impl_details_dir"
    mkdir -p "$tests_dir"
    
    # Create git branch if in a git repository
    if [[ -d ".git" ]]; then
        debug_log "Creating git branch: $branch_name"
        git checkout -b "$branch_name" 2>/dev/null || true
    fi
    
    # Initialize spec file with template header
    cat > "$spec_file" << EOF
# Validation Framework: $model_name

**Feature Branch**: \`$branch_name\`  
**Created**: $(date +%Y-%m-%d)  
**Status**: Draft  
**Input**: Validation requirements: "$VALIDATION_REQUIREMENTS"

<!-- This file will be populated by the simics-validate command -->
<!-- Template: templates/simics/projects/validation-template.md -->

EOF
    
    debug_log "Created spec file: $spec_file"
    
    # Create placeholder contract files
    echo "# Test Interface Specifications" > "$contracts_dir/test-interfaces.md"
    echo "# Validation Criteria Contracts" > "$contracts_dir/validation-criteria.md"
    echo "# Test Environment Contracts" > "$contracts_dir/test-environment.md"
    
    # Create placeholder simics files
    echo "# Validation Configuration Specification" > "$simics_dir/validation-config.md"
    echo "# Test Execution Framework" > "$simics_dir/test-execution.md"
    echo "# Results Analysis and Reporting" > "$simics_dir/results-analysis.md"
    
    # Create placeholder implementation details
    echo "# Test Implementation Specifications" > "$impl_details_dir/test-implementation.md"
    echo "# Automation Framework Details" > "$impl_details_dir/automation-framework.md"
    echo "# Performance Measurement Details" > "$impl_details_dir/performance-measurement.md"
    
    # Create placeholder test directories
    echo "# Functional Test Cases" > "$tests_dir/functional-tests.md"
    echo "# Performance Test Cases" > "$tests_dir/performance-tests.md"
    echo "# Integration Test Cases" > "$tests_dir/integration-tests.md"
    
    debug_log "Created project structure successfully"
    
    # Output results
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        cat << EOF
{
    "success": true,
    "branch_name": "$branch_name",
    "spec_file": "$spec_file",
    "model_name": "$model_name",
    "model_type": "$model_type",
    "validation_scope": "$validation_scope",
    "test_categories": "$test_categories",
    "specs_dir": "$specs_dir",
    "contracts_dir": "$contracts_dir",
    "simics_dir": "$simics_dir",
    "implementation_details_dir": "$impl_details_dir",
    "tests_dir": "$tests_dir"
}
EOF
    else
        echo "Simics validation project created successfully!"
        echo "Branch: $branch_name"
        echo "Model: $model_name ($model_type)"
        echo "Validation Scope: $validation_scope"
        echo "Test Categories: $test_categories"
        echo "Spec file: $spec_file"
        echo "Ready for validation framework specification."
    fi
}

# Run main function
main "$@"