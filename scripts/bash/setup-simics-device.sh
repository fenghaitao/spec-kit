#!/bin/bash
# setup-simics-device.sh - Initialize Simics device model project
# Usage: setup-simics-device.sh --json "{device_description}"

set -euo pipefail

# Default values
DEVICE_DESCRIPTION=""
JSON_OUTPUT=false
DEBUG=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            DEVICE_DESCRIPTION="$2"
            JSON_OUTPUT=true
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        *)
            DEVICE_DESCRIPTION="$1"
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
    local device_name="$1"
    local timestamp=$(date +%s)
    local random_suffix=$(( RANDOM % 1000 ))
    local clean_name=$(echo "$device_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    echo "${timestamp}-${clean_name}-${random_suffix}"
}

# Function to extract device name from description
extract_device_name() {
    local description="$1"
    # Simple extraction - look for common device patterns
    if echo "$description" | grep -qi "uart\|serial"; then
        echo "uart-controller"
    elif echo "$description" | grep -qi "timer"; then
        echo "timer-device"
    elif echo "$description" | grep -qi "interrupt\|irq"; then
        echo "interrupt-controller"    
    elif echo "$description" | grep -qi "memory\|ddr\|ram"; then
        echo "memory-controller"
    elif echo "$description" | grep -qi "ethernet\|network"; then
        echo "network-controller"
    elif echo "$description" | grep -qi "gpio"; then
        echo "gpio-controller"
    elif echo "$description" | grep -qi "i2c"; then
        echo "i2c-controller"
    elif echo "$description" | grep -qi "spi"; then
        echo "spi-controller"
    else
        # Fallback: extract first meaningful word
        echo "$description" | head -n1 | tr ' ' '\n' | grep -v '^$' | head -n1 | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g' || echo "generic-device"
    fi
}

# Function to determine device type from description
determine_device_type() {
    local description="$1"
    if echo "$description" | grep -qi "processor\|cpu\|core"; then
        echo "processor"
    elif echo "$description" | grep -qi "memory\|ddr\|ram\|cache"; then
        echo "memory"
    elif echo "$description" | grep -qi "uart\|serial\|i2c\|spi\|gpio"; then
        echo "peripheral"
    elif echo "$description" | grep -qi "interrupt\|irq"; then
        echo "controller"
    elif echo "$description" | grep -qi "timer\|clock"; then
        echo "timing"
    elif echo "$description" | grep -qi "network\|ethernet"; then
        echo "network"
    else
        echo "generic"
    fi
}

# Function to determine Simics version (default to latest stable)
determine_simics_version() {
    # In a real implementation, this could check for installed Simics versions
    echo "6.0"
}

# Main execution
main() {
    debug_log "Starting Simics device project setup"
    debug_log "Device description: $DEVICE_DESCRIPTION"
    
    if [[ -z "$DEVICE_DESCRIPTION" ]]; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo '{"error": "No device description provided", "success": false}'
            exit 1
        else
            echo "Error: No device description provided" >&2
            exit 1
        fi
    fi
    
    # Extract device information
    local device_name=$(extract_device_name "$DEVICE_DESCRIPTION")
    local device_type=$(determine_device_type "$DEVICE_DESCRIPTION")
    local simics_version=$(determine_simics_version)
    local branch_name=$(generate_branch_name "$device_name")
    
    debug_log "Extracted device name: $device_name"
    debug_log "Determined device type: $device_type"
    debug_log "Generated branch name: $branch_name"
    
    # Create project directory structure
    local project_root=$(pwd)
    local specs_dir="$project_root/specs/$branch_name"
    local spec_file="$specs_dir/spec.md"
    local contracts_dir="$specs_dir/contracts"
    local simics_dir="$specs_dir/simics"
    local impl_details_dir="$specs_dir/implementation-details"
    
    debug_log "Creating directory structure"
    mkdir -p "$specs_dir"
    mkdir -p "$contracts_dir"
    mkdir -p "$simics_dir"
    mkdir -p "$impl_details_dir"
    
    # Create git branch if in a git repository
    if [[ -d ".git" ]]; then
        debug_log "Creating git branch: $branch_name"
        git checkout -b "$branch_name" 2>/dev/null || true
    fi
    
    # Initialize spec file with template header
    cat > "$spec_file" << EOF
# Device Model Specification: $device_name

**Feature Branch**: \`$branch_name\`  
**Created**: $(date +%Y-%m-%d)  
**Status**: Draft  
**Input**: Device description: "$DEVICE_DESCRIPTION"

<!-- This file will be populated by the simics-device command -->
<!-- Template: templates/simics/projects/device-spec-template.md -->

EOF
    
    debug_log "Created spec file: $spec_file"
    
    # Create placeholder contract files
    echo "# Register Interface Specification" > "$contracts_dir/register-interface.md"
    echo "# Memory Interface Specification" > "$contracts_dir/memory-interface.md"
    echo "# Simics Interface Specification" > "$contracts_dir/simics-interface.md"
    
    # Create placeholder simics files
    echo "# Device Configuration Specification" > "$simics_dir/device-config.md"
    echo "# Integration Test Scenarios" > "$simics_dir/integration-tests.md"
    
    # Create placeholder implementation details
    echo "# DML Implementation Specification" > "$impl_details_dir/dml-specification.md"
    echo "# Python Interface Implementation" > "$impl_details_dir/python-interface.md"
    echo "# Performance and Timing Requirements" > "$impl_details_dir/performance-targets.md"
    
    debug_log "Created project structure successfully"
    
    # Output results
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        cat << EOF
{
    "success": true,
    "branch_name": "$branch_name",
    "spec_file": "$spec_file",
    "device_name": "$device_name",
    "device_type": "$device_type",
    "simics_version": "$simics_version",
    "specs_dir": "$specs_dir",
    "contracts_dir": "$contracts_dir",
    "simics_dir": "$simics_dir",
    "implementation_details_dir": "$impl_details_dir"
}
EOF
    else
        echo "Simics device project created successfully!"
        echo "Branch: $branch_name"
        echo "Device: $device_name ($device_type)"
        echo "Spec file: $spec_file"
        echo "Ready for specification generation."
    fi
}

# Run main function
main "$@"