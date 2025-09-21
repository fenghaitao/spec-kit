#!/usr/bin/env bash
# check-task-prerequisites.sh - Check task prerequisites with workflow enforcement
set -e

# Load common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Function to validate tasks phase prerequisites
validate_tasks_prerequisites() {
    debug_log "Validating tasks phase prerequisites"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local state_file="$spec_kit_dir/workflow-state.json"
    local plan_marker="$spec_kit_dir/phase-markers/plan.complete"
    
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
    
    # Check if planning phase is completed
    if [[ ! -f "$plan_marker" ]]; then
        # Check which phases are missing
        local product_marker="$spec_kit_dir/phase-markers/product.complete"
        local specify_marker="$spec_kit_dir/phase-markers/specify.complete"
        
        local missing_phases=()
        local next_command=""
        
        if [[ ! -f "$product_marker" ]]; then
            missing_phases+=("product (/simics-platform)")
            next_command="/simics-platform"
        elif [[ ! -f "$specify_marker" ]]; then
            missing_phases+=("specify (/specify)")
            next_command="/specify"
        else
            missing_phases+=("plan (/plan)")
            next_command="/plan"
        fi
        
        local missing_list=$(IFS=', '; echo "${missing_phases[*]}")
        
        if [[ "$JSON_MODE" == "true" ]]; then
            echo "{\"error\": \"Tasks phase requires all previous phases to be completed. Missing phases: $missing_list\", \"success\": false, \"missing_phases\": [$(printf '\"%s\",' "${missing_phases[@]}" | sed 's/,$//g')], \"next_command\": \"$next_command\"}"
            exit 1
        else
            echo "Error: Tasks phase requires all previous phases to be completed." >&2
            echo "Missing phases: $missing_list" >&2
            echo "Please run the $next_command command next." >&2
            exit 1
        fi
    fi
    
    # Validate plan context availability
    if [[ -f "$state_file" ]]; then
        local has_plan_context=$(python3 -c "
import json
import sys
try:
    with open('$state_file', 'r') as f:
        state = json.load(f)
    plan_data = state.get('phaseData', {}).get('plan', {})
    print('true' if plan_data else 'false')
except:
    print('false')
" 2>/dev/null || echo "false")
        
        if [[ "$has_plan_context" != "true" ]]; then
            if [[ "$JSON_MODE" == "true" ]]; then
                echo '{"error": "Plan context not found. Planning phase may not have been completed properly.", "success": false, "missing_phase": "plan", "next_command": "/plan"}'
                exit 1
            else
                echo "Error: Plan context not found." >&2
                echo "Planning phase may not have been completed properly. Please run /plan command." >&2
                exit 1
            fi
        fi
    fi
    
    debug_log "Tasks phase prerequisites validated successfully"
}

# Function to load plan context for tasks integration
load_plan_context() {
    debug_log "Loading plan context for tasks integration"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local state_file="$spec_kit_dir/workflow-state.json"
    
    if [[ -f "$state_file" ]]; then
        python3 -c "
import json
import sys
try:
    with open('$state_file', 'r') as f:
        state = json.load(f)
    plan_data = state.get('phaseData', {}).get('plan', {})
    print(json.dumps(plan_data, indent=2))
except Exception as e:
    print('{}', file=sys.stderr)
" 2>/dev/null || echo "{}"
    else
        echo "{}"
    fi
}

# Function to complete tasks phase
complete_tasks_phase() {
    debug_log "Completing tasks phase - workflow sequence finished"
    
    local spec_kit_dir="$(pwd)/.spec-kit"
    local phase_markers_dir="$spec_kit_dir/phase-markers"
    local state_file="$spec_kit_dir/workflow-state.json"
    
    # Create tasks phase completion marker
    touch "$phase_markers_dir/tasks.complete"
    
    # Store tasks completion and mark phase as completed
    python3 -c "
import json
import sys

# Read current state
with open('$state_file', 'r') as f:
    state = json.load(f)

# Store tasks context
tasks_context = {
    'workflow_completed': True,
    'all_phases_completed': ['product', 'specify', 'plan', 'tasks'],
    'final_phase': 'tasks',
    'metadata': {
        'completed_at': '$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)',
        'workflow_sequence': 'product -> specify -> plan -> tasks'
    }
}

state.setdefault('phaseData', {})['tasks'] = tasks_context

# Mark tasks phase as completed
if 'tasks' not in state.get('completedPhases', []):
    state.setdefault('completedPhases', []).append('tasks')
state['currentPhase'] = None
state['lastUpdated'] = '$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'
state['workflowCompleted'] = True

# Write updated state
with open('$state_file', 'w') as f:
    json.dump(state, f, indent=2)
" 2>/dev/null || {
        debug_log "Python not available for state update"
    }
    
    debug_log "Tasks phase marked as complete - full workflow enforcement sequence finished"
}

JSON_MODE=false
for arg in "$@"; do 
    case "$arg" in 
        --json) JSON_MODE=true ;; 
        --help|-h) echo "Usage: $0 [--json]"; exit 0 ;; 
    esac
done

# Validate workflow prerequisites for tasks phase
validate_tasks_prerequisites

# Load plan context for integration
PLAN_CONTEXT=$(load_plan_context)
eval $(get_feature_paths)
check_feature_branch "$CURRENT_BRANCH" || exit 1

if [[ ! -d "$FEATURE_DIR" ]]; then 
    echo "ERROR: Feature directory not found: $FEATURE_DIR" 
    echo "Run /specify first."
    exit 1
fi

if [[ ! -f "$IMPL_PLAN" ]]; then 
    echo "ERROR: plan.md not found in $FEATURE_DIR" 
    echo "Run /plan first."
    exit 1
fi

# Complete tasks phase after successful validation
complete_tasks_phase
if $JSON_MODE; then
  docs=()
  [[ -f "$RESEARCH" ]] && docs+=("research.md")
  [[ -f "$DATA_MODEL" ]] && docs+=("data-model.md")
  ([[ -d "$CONTRACTS_DIR" ]] && [[ -n "$(ls -A "$CONTRACTS_DIR" 2>/dev/null)" ]]) && docs+=("contracts/")
  [[ -f "$QUICKSTART" ]] && docs+=("quickstart.md")
  
  json_docs=$(printf '"%s",' "${docs[@]}")
  json_docs="[${json_docs%,}]"
  
  printf '{"FEATURE_DIR":"%s","AVAILABLE_DOCS":%s,"workflow":{"phase_completed":"tasks","workflow_completed":true,"enforcement_active":true,"plan_context_integrated":true,"full_sequence_completed":"product->specify->plan->tasks"}}\n' "$FEATURE_DIR" "$json_docs"
else
  echo "FEATURE_DIR:$FEATURE_DIR"
  echo "AVAILABLE_DOCS:"
  check_file "$RESEARCH" "research.md"
  check_file "$DATA_MODEL" "data-model.md"
  check_dir "$CONTRACTS_DIR" "contracts/"
  check_file "$QUICKSTART" "quickstart.md"
  echo ""
  echo "=== WORKFLOW ENFORCEMENT ==="
  echo "✓ Tasks phase completed successfully"
  echo "✓ Plan context integrated into tasks"
  echo "✓ Full workflow sequence completed: product -> specify -> plan -> tasks"
  echo "✓ Enhanced workflow enforcement successfully executed"
fi
