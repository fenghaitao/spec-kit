#!/bin/bash
# setup-simics-platform.sh - Initialize Simics virtual platform project
# Usage: setup-simics-platform.sh --json "{platform_description}"

set -euo pipefail

# Default values
PLATFORM_DESCRIPTION=""
JSON_OUTPUT=false
DEBUG=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            PLATFORM_DESCRIPTION="$2"
            JSON_OUTPUT=true
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        *)
            PLATFORM_DESCRIPTION="$1"
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
    local platform_name="$1"
    local timestamp=$(date +%s)
    local random_suffix=$(( RANDOM % 1000 ))
    local clean_name=$(echo "$platform_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    echo "${timestamp}-${clean_name}-${random_suffix}"
}

# Function to extract platform name from description
extract_platform_name() {
    local description="$1"
    # Simple extraction - look for common platform patterns
    if echo "$description" | grep -qi "arm\|cortex"; then
        echo "arm-platform"
    elif echo "$description" | grep -qi "x86\|intel"; then
        echo "x86-platform"
    elif echo "$description" | grep -qi "risc\|riscv"; then
        echo "riscv-platform"
    elif echo "$description" | grep -qi "embedded\|mcu"; then
        echo "embedded-platform"
    elif echo "$description" | grep -qi "server"; then
        echo "server-platform"
    elif echo "$description" | grep -qi "mobile\|phone"; then
        echo "mobile-platform"
    elif echo "$description" | grep -qi "automotive\|car"; then
        echo "automotive-platform"
    elif echo "$description" | grep -qi "iot"; then
        echo "iot-platform"
    else
        # Fallback: extract first meaningful word
        echo "$description" | head -n1 | tr ' ' '\n' | grep -v '^$' | head -n1 | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g' || echo "generic-platform"
    fi
}

# Function to determine platform type from description
determine_platform_type() {
    local description="$1"
    if echo "$description" | grep -qi "server\|datacenter"; then
        echo "server"
    elif echo "$description" | grep -qi "embedded\|mcu\|microcontroller"; then
        echo "embedded"
    elif echo "$description" | grep -qi "mobile\|phone\|tablet"; then
        echo "mobile"
    elif echo "$description" | grep -qi "automotive\|car\|vehicle"; then
        echo "automotive"
    elif echo "$description" | grep -qi "iot\|sensor"; then
        echo "iot"
    elif echo "$description" | grep -qi "desktop\|workstation"; then
        echo "desktop"
    elif echo "$description" | grep -qi "development\|dev\|prototype"; then
        echo "development"
    else
        echo "generic"
    fi
}

# Function to extract component list from description
extract_component_list() {
    local description="$1"
    local components=()
    
    # Look for common components
    if echo "$description" | grep -qi "cpu\|processor\|core"; then
        components+=("processor")
    fi
    if echo "$description" | grep -qi "memory\|ram\|ddr"; then
        components+=("memory")
    fi
    if echo "$description" | grep -qi "uart\|serial"; then
        components+=("uart")
    fi
    if echo "$description" | grep -qi "timer"; then
        components+=("timer")
    fi
    if echo "$description" | grep -qi "interrupt\|irq"; then
        components+=("interrupt-controller")
    fi
    if echo "$description" | grep -qi "ethernet\|network"; then
        components+=("network")
    fi
    if echo "$description" | grep -qi "gpio"; then
        components+=("gpio")
    fi
    if echo "$description" | grep -qi "i2c"; then
        components+=("i2c")
    fi
    if echo "$description" | grep -qi "spi"; then
        components+=("spi")
    fi
    
    # Join array with commas
    IFS=','
    echo "${components[*]}"
}

# Function to determine target system from description
determine_target_system() {
    local description="$1"
    if echo "$description" | grep -qi "arm.*cortex.*a[0-9]"; then
        echo "ARM Cortex-A"
    elif echo "$description" | grep -qi "arm.*cortex.*m[0-9]"; then
        echo "ARM Cortex-M"
    elif echo "$description" | grep -qi "x86.*64\|amd64"; then
        echo "x86-64"
    elif echo "$description" | grep -qi "x86.*32\|i386"; then
        echo "x86-32"
    elif echo "$description" | grep -qi "risc.*v"; then
        echo "RISC-V"
    elif echo "$description" | grep -qi "mips"; then
        echo "MIPS"
    else
        echo "Generic"
    fi
}

# Main execution
main() {
    debug_log "Starting Simics platform project setup"
    debug_log "Platform description: $PLATFORM_DESCRIPTION"
    
    if [[ -z "$PLATFORM_DESCRIPTION" ]]; then
        if [[ "$JSON_OUTPUT" == "true" ]]; then
            echo '{"error": "No platform description provided", "success": false}'
            exit 1
        else
            echo "Error: No platform description provided" >&2
            exit 1
        fi
    fi
    
    # Extract platform information
    local platform_name=$(extract_platform_name "$PLATFORM_DESCRIPTION")
    local platform_type=$(determine_platform_type "$PLATFORM_DESCRIPTION")
    local component_list=$(extract_component_list "$PLATFORM_DESCRIPTION")
    local target_system=$(determine_target_system "$PLATFORM_DESCRIPTION")
    local branch_name=$(generate_branch_name "$platform_name")
    
    debug_log "Extracted platform name: $platform_name"
    debug_log "Determined platform type: $platform_type"
    debug_log "Component list: $component_list"
    debug_log "Target system: $target_system"
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
# Virtual Platform Specification: $platform_name

**Feature Branch**: \`$branch_name\`  
**Created**: $(date +%Y-%m-%d)  
**Status**: Draft  
**Input**: Platform description: "$PLATFORM_DESCRIPTION"

<!-- This file will be populated by the simics-platform command -->
<!-- Template: templates/simics/projects/platform-spec-template.md -->

EOF
    
    debug_log "Created spec file: $spec_file"
    
    # Create placeholder contract files
    echo "# System Architecture Specification" > "$contracts_dir/system-architecture.md"
    echo "# Memory Map Specification" > "$contracts_dir/memory-map.md"
    echo "# Device Interface Specifications" > "$contracts_dir/device-interfaces.md"
    
    # Create placeholder simics files
    echo "# Platform Configuration Specification" > "$simics_dir/platform-config.md"
    echo "# Integration Test Scenarios" > "$simics_dir/integration-tests.md"
    
    # Create placeholder implementation details
    echo "# System Configuration Implementation" > "$impl_details_dir/system-configuration.md"
    echo "# Device Instantiation and Connection" > "$impl_details_dir/device-instantiation.md"
    echo "# Boot Sequence and Initialization" > "$impl_details_dir/boot-sequence.md"
    
    debug_log "Created project structure successfully"
    
    # Output results
    if [[ "$JSON_OUTPUT" == "true" ]]; then
        cat << EOF
{
    "success": true,
    "branch_name": "$branch_name",
    "spec_file": "$spec_file",
    "platform_name": "$platform_name",
    "platform_type": "$platform_type",
    "component_list": "$component_list",
    "target_system": "$target_system",
    "specs_dir": "$specs_dir",
    "contracts_dir": "$contracts_dir",
    "simics_dir": "$simics_dir",
    "implementation_details_dir": "$impl_details_dir"
}
EOF
    else
        echo "Simics platform project created successfully!"
        echo "Branch: $branch_name"
        echo "Platform: $platform_name ($platform_type)"
        echo "Target System: $target_system"
        echo "Components: $component_list"
        echo "Spec file: $spec_file"
        echo "Ready for specification generation."
    fi
}

# Run main function
main "$@"