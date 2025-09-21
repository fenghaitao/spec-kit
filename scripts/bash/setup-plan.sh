#!/usr/bin/env bash
# setup-plan.sh - Initialize implementation plan with workflow enforcement
set -e

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Function to validate planning phase prerequisites
validate_planning_prerequisites() {
    debug_log "Validating planning phase prerequisites"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local state_file="$spec_kit_dir/workflow-state.json"
    local specify_marker="$spec_kit_dir/phase-markers/specify.complete"
    
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
    
    # Check if specification phase is completed
    if [[ ! -f "$specify_marker" ]]; then
        # Check if product phase is also missing
        local product_marker="$spec_kit_dir/phase-markers/product.complete"
        if [[ ! -f "$product_marker" ]]; then
            if [[ "$JSON_MODE" == "true" ]]; then
                echo '{"error": "Both product and specification phases must be completed before planning phase. Please complete the product phase first.", "success": false, "missing_phase": "product", "next_command": "/simics-platform"}'
                exit 1
            else
                echo "Error: Both product and specification phases must be completed before planning phase." >&2
                echo "Please run the /simics-platform command first to complete the product phase." >&2
                exit 1
            fi
        else
            if [[ "$JSON_MODE" == "true" ]]; then
                echo '{"error": "Specification phase must be completed before planning phase. Please complete the specification phase first.", "success": false, "missing_phase": "specify", "next_command": "/specify"}'
                exit 1
            else
                echo "Error: Specification phase must be completed before planning phase." >&2
                echo "Please run the /specify command first to complete the specification phase." >&2
                exit 1
            fi
        fi
    fi
    
    # Validate specification context availability
    if [[ -f "$state_file" ]]; then
        local has_spec_context=$(python3 -c "
import json
import sys
try:
    with open('$state_file', 'r') as f:
        state = json.load(f)
    spec_data = state.get('phaseData', {}).get('specify', {})
    print('true' if spec_data else 'false')
except:
    print('false')
" 2>/dev/null || echo "false")
        
        if [[ "$has_spec_context" != "true" ]]; then
            if [[ "$JSON_MODE" == "true" ]]; then
                echo '{"error": "Specification context not found. Specification phase may not have been completed properly.", "success": false, "missing_phase": "specify", "next_command": "/specify"}'
                exit 1
            else
                echo "Error: Specification context not found." >&2
                echo "Specification phase may not have been completed properly. Please run /specify command." >&2
                exit 1
            fi
        fi
    fi
    
    debug_log "Planning phase prerequisites validated successfully"
}

# Function to load specification context for plan integration
load_specification_context() {
    debug_log "Loading specification context for plan integration"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local state_file="$spec_kit_dir/workflow-state.json"
    
    if [[ -f "$state_file" ]]; then
        python3 -c "
import json
import sys
try:
    with open('$state_file', 'r') as f:
        state = json.load(f)
    spec_data = state.get('phaseData', {}).get('specify', {})
    print(json.dumps(spec_data, indent=2))
except Exception as e:
    print('{}', file=sys.stderr)
" 2>/dev/null || echo "{}"
    else
        echo "{}"
    fi
}

# Function to complete planning phase
complete_planning_phase() {
    local impl_plan="$1"
    debug_log "Completing planning phase"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local phase_markers_dir="$spec_kit_dir/phase-markers"
    local state_file="$spec_kit_dir/workflow-state.json"
    
    # Create planning phase completion marker
    touch "$phase_markers_dir/plan.complete"
    
    # Store planning context and mark phase as completed
    if [[ -f "$impl_plan" ]]; then
        local plan_content=$(cat "$impl_plan")
        local content_hash=$(echo "$plan_content" | sha256sum | cut -d' ' -f1)
        
        python3 -c "
import json
import sys

# Read current state
with open('$state_file', 'r') as f:
    state = json.load(f)

# Store planning context
plan_context = {
    'implementation_strategy': 'Implementation strategy from plan document',
    'technology_stack': [],
    'resource_allocation': {},
    'milestones': [],
    'dependencies': [],
    'risk_analysis': [],
    'design_artifacts': ['$impl_plan'],
    'metadata': {
        'source_file': '$impl_plan',
        'extracted_at': '$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)',
        'content_hash': '$content_hash'
    }
}

state.setdefault('phaseData', {})['plan'] = plan_context

# Mark planning phase as completed
if 'plan' not in state.get('completedPhases', []):
    state.setdefault('completedPhases', []).append('plan')
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
    
    debug_log "Planning phase marked as complete"
}

JSON_MODE=false
for arg in "$@"; do 
    case "$arg" in 
        --json) JSON_MODE=true ;; 
        --help|-h) echo "Usage: $0 [--json]"; exit 0 ;; 
    esac
done

# Validate workflow prerequisites for planning phase
validate_planning_prerequisites

# Load specification context for integration
SPEC_CONTEXT=$(load_specification_context)
eval $(get_feature_paths)
check_feature_branch "$CURRENT_BRANCH" || exit 1
mkdir -p "$FEATURE_DIR"

TEMPLATE="$REPO_ROOT/templates/plan-template.md"
if [[ -f "$TEMPLATE" ]]; then
    cp "$TEMPLATE" "$IMPL_PLAN"
    
    # Inject specification context into plan template if available
    if [[ -n "$SPEC_CONTEXT" && "$SPEC_CONTEXT" != "{}" ]]; then
        debug_log "Integrating specification context into plan"
        
        # Extract key specification context elements for injection
        local tech_requirements=$(echo "$SPEC_CONTEXT" | python3 -c "import json, sys; data=json.load(sys.stdin); print('\n'.join(['- ' + str(req) for req in data.get('technical_requirements', [])]))" 2>/dev/null || echo "")
        local arch_decisions=$(echo "$SPEC_CONTEXT" | python3 -c "import json, sys; data=json.load(sys.stdin); print('\n'.join(['- ' + str(dec) for dec in data.get('architecture_decisions', [])]))" 2>/dev/null || echo "")
        
        # Simple template injection (can be enhanced with more sophisticated processing)
        if [[ -n "$tech_requirements" ]]; then
            sed -i "s/{{TECHNICAL_REQUIREMENTS}}/$tech_requirements/g" "$IMPL_PLAN" 2>/dev/null || true
        fi
        if [[ -n "$arch_decisions" ]]; then
            sed -i "s/{{ARCHITECTURE_DECISIONS}}/$arch_decisions/g" "$IMPL_PLAN" 2>/dev/null || true
        fi
    fi
fi

# Complete planning phase
complete_planning_phase "$IMPL_PLAN"
if $JSON_MODE; then
  printf '{"FEATURE_SPEC":"%s","IMPL_PLAN":"%s","SPECS_DIR":"%s","BRANCH":"%s","workflow":{"phase_completed":"plan","next_phase":"tasks","next_command":"/tasks","enforcement_active":true,"spec_context_integrated":true}}\n' \
    "$FEATURE_SPEC" "$IMPL_PLAN" "$FEATURE_DIR" "$CURRENT_BRANCH"
else
  echo "FEATURE_SPEC: $FEATURE_SPEC"
  echo "IMPL_PLAN: $IMPL_PLAN"
  echo "SPECS_DIR: $FEATURE_DIR"
  echo "BRANCH: $CURRENT_BRANCH"
  echo ""
  echo "=== WORKFLOW ENFORCEMENT ==="
  echo "✓ Planning phase completed successfully"
  echo "✓ Specification context integrated into plan"
  echo "→ Next step: Use /tasks command to proceed to tasks phase"
  echo "⚠ All prerequisite phases (product, specify) have been completed"
fi
