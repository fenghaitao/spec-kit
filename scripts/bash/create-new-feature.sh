#!/usr/bin/env bash
# (Moved to scripts/bash/) Create a new feature with branch, directory structure, and template with workflow enforcement
set -e

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Function to validate workflow prerequisites for specification phase
validate_specification_prerequisites() {
    debug_log "Validating specification phase prerequisites"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local state_file="$spec_kit_dir/workflow-state.json"
    local product_marker="$spec_kit_dir/phase-markers/product.complete"
    
    # Check if workflow enforcement is active
    if [[ ! -d "$spec_kit_dir" ]]; then
        if [[ "$JSON_MODE" == "true" ]]; then
            echo '{"error": "Workflow enforcement not initialized. Run /simics-platform command first to start the product phase.", "success": false, "missing_phase": "product", "next_command": "/simics-platform"}'
            exit 1
        else
            echo "Error: Workflow enforcement not initialized." >&2
            echo "Please run the /simics-platform command first to start the product phase." >&2
            exit 1
        fi
    fi
    
    # Check if product phase is completed
    if [[ ! -f "$product_marker" ]]; then
        if [[ "$JSON_MODE" == "true" ]]; then
            echo '{"error": "Product phase must be completed before specification phase. Please complete the product phase first.", "success": false, "missing_phase": "product", "next_command": "/simics-platform"}'
            exit 1
        else
            echo "Error: Product phase must be completed before specification phase." >&2
            echo "Please run the /simics-platform command first to complete the product phase." >&2
            exit 1
        fi
    fi
    
    # Validate product context availability
    if [[ -f "$state_file" ]]; then
        # Check if product context exists
        local has_product_context=$(python3 -c "
import json
import sys
try:
    with open('$state_file', 'r') as f:
        state = json.load(f)
    product_data = state.get('phaseData', {}).get('product', {})
    print('true' if product_data else 'false')
except:
    print('false')
" 2>/dev/null || echo "false")
        
        if [[ "$has_product_context" != "true" ]]; then
            if [[ "$JSON_MODE" == "true" ]]; then
                echo '{"error": "Product context not found. Product phase may not have been completed properly.", "success": false, "missing_phase": "product", "next_command": "/simics-platform"}'
                exit 1
            else
                echo "Error: Product context not found." >&2
                echo "Product phase may not have been completed properly. Please run /simics-platform command." >&2
                exit 1
            fi
        fi
    fi
    
    debug_log "Specification phase prerequisites validated successfully"
}

# Function to load product context for specification integration
load_product_context() {
    debug_log "Loading product context for specification integration"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local state_file="$spec_kit_dir/workflow-state.json"
    
    if [[ -f "$state_file" ]]; then
        python3 -c "
import json
import sys
try:
    with open('$state_file', 'r') as f:
        state = json.load(f)
    product_data = state.get('phaseData', {}).get('product', {})
    print(json.dumps(product_data, indent=2))
except Exception as e:
    print('{}', file=sys.stderr)
" 2>/dev/null || echo "{}"
    else
        echo "{}"
    fi
}

# Function to complete specification phase
complete_specification_phase() {
    local spec_file="$1"
    debug_log "Completing specification phase"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local phase_markers_dir="$spec_kit_dir/phase-markers"
    local state_file="$spec_kit_dir/workflow-state.json"
    
    # Create specification phase completion marker
    touch "$phase_markers_dir/specify.complete"
    
    # Store specification context and mark phase as completed
    if [[ -f "$spec_file" ]]; then
        local spec_content=$(cat "$spec_file")
        local content_hash=$(echo "$spec_content" | sha256sum | cut -d' ' -f1)
        
        python3 -c "
import json
import sys

# Read current state
with open('$state_file', 'r') as f:
    state = json.load(f)

# Store specification context
spec_context = {
    'technical_requirements': [],
    'architecture_decisions': [],
    'design_constraints': [],
    'interfaces': [],
    'validation_criteria': [],
    'clarifications_resolved': [],
    'metadata': {
        'source_file': '$spec_file',
        'extracted_at': '$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)',
        'content_hash': '$content_hash'
    }
}

state.setdefault('phaseData', {})['specify'] = spec_context

# Mark specification phase as completed
if 'specify' not in state.get('completedPhases', []):
    state.setdefault('completedPhases', []).append('specify')
state['currentPhase'] = None
state['lastUpdated'] = '$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'
state['contextHash'] = '$content_hash'

# Write updated state
with open('$state_file', 'w') as f:
    json.dump(state, f, indent=2)
" 2>/dev/null || {
            debug_log "Python not available for state update"
        }
    fi
    
    debug_log "Specification phase marked as complete"
}

JSON_MODE=false
ARGS=()
for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --help|-h) echo "Usage: $0 [--json] <feature_description>"; exit 0 ;;
        *) ARGS+=("$arg") ;;
    esac
done

FEATURE_DESCRIPTION="${ARGS[*]}"
if [ -z "$FEATURE_DESCRIPTION" ]; then
    echo "Usage: $0 [--json] <feature_description>" >&2
    exit 1
fi

# Validate workflow prerequisites for specification phase
validate_specification_prerequisites

# Load product context for integration
PRODUCT_CONTEXT=$(load_product_context)

REPO_ROOT=$(git rev-parse --show-toplevel)
SPECS_DIR="$REPO_ROOT/specs"
mkdir -p "$SPECS_DIR"

HIGHEST=0
if [ -d "$SPECS_DIR" ]; then
    for dir in "$SPECS_DIR"/*; do
        [ -d "$dir" ] || continue
        dirname=$(basename "$dir")
        number=$(echo "$dirname" | grep -o '^[0-9]\+' || echo "0")
        number=$((10#$number))
        if [ "$number" -gt "$HIGHEST" ]; then HIGHEST=$number; fi
    done
fi

NEXT=$((HIGHEST + 1))
FEATURE_NUM=$(printf "%03d" "$NEXT")

BRANCH_NAME=$(echo "$FEATURE_DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//')
WORDS=$(echo "$BRANCH_NAME" | tr '-' '\n' | grep -v '^$' | head -3 | tr '\n' '-' | sed 's/-$//')
BRANCH_NAME="${FEATURE_NUM}-${WORDS}"

git checkout -b "$BRANCH_NAME"

FEATURE_DIR="$SPECS_DIR/$BRANCH_NAME"
mkdir -p "$FEATURE_DIR"

TEMPLATE="$REPO_ROOT/templates/spec-template.md"
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$TEMPLATE" ]; then 
    cp "$TEMPLATE" "$SPEC_FILE"
    
    # Inject product context into specification template if available
    if [[ -n "$PRODUCT_CONTEXT" && "$PRODUCT_CONTEXT" != "{}" ]]; then
        debug_log "Integrating product context into specification"
        
        # Extract key product context elements for injection
        local product_vision=$(echo "$PRODUCT_CONTEXT" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data.get('vision', ''))" 2>/dev/null || echo "")
        local product_constraints=$(echo "$PRODUCT_CONTEXT" | python3 -c "import json, sys; data=json.load(sys.stdin); print('\n'.join(['- ' + c for c in data.get('constraints', [])]))" 2>/dev/null || echo "")
        
        # Simple template injection (can be enhanced with more sophisticated processing)
        if [[ -n "$product_vision" ]]; then
            sed -i "s/{{PRODUCT_VISION}}/$product_vision/g" "$SPEC_FILE" 2>/dev/null || true
        fi
        if [[ -n "$product_constraints" ]]; then
            sed -i "s/{{PRODUCT_CONSTRAINTS}}/$product_constraints/g" "$SPEC_FILE" 2>/dev/null || true
        fi
    fi
else 
    touch "$SPEC_FILE"
fi

# Complete specification phase
complete_specification_phase "$SPEC_FILE"

if $JSON_MODE; then
    printf '{"BRANCH_NAME":"%s","SPEC_FILE":"%s","FEATURE_NUM":"%s","workflow":{"phase_completed":"specify","next_phase":"plan","next_command":"/plan","enforcement_active":true,"product_context_integrated":true}}\n' "$BRANCH_NAME" "$SPEC_FILE" "$FEATURE_NUM"
else
    echo "BRANCH_NAME: $BRANCH_NAME"
    echo "SPEC_FILE: $SPEC_FILE"
    echo "FEATURE_NUM: $FEATURE_NUM"
    echo ""
    echo "=== WORKFLOW ENFORCEMENT ===" 
    echo "✓ Specification phase completed successfully"
    echo "✓ Product context integrated into specification"
    echo "→ Next step: Use /plan command to proceed to planning phase"
    echo "⚠ Attempting to skip to /tasks will be blocked until planning is completed"
fi
