"""
Command Integration Module for Enhanced Workflow Enforcement.

This module provides command-level integration utilities that enable
existing commands to easily integrate with the workflow enforcement system.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Add the parent directory to sys.path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from workflow_state import (
    WorkflowStateManager, 
    WorkflowPhase, 
    PhasePrerequisiteError, 
    StateValidationError
)
from context_transfer import (
    ContextTransferManager,
    ProductContext,
    SpecificationContext,
    PlanContext
)


@dataclass
class CommandExecutionContext:
    """Context information for command execution."""
    command_name: str
    target_phase: WorkflowPhase
    workspace_path: str
    arguments: Dict[str, Any]
    prerequisites_met: bool = False
    product_context: Optional[ProductContext] = None
    spec_context: Optional[SpecificationContext] = None
    plan_context: Optional[PlanContext] = None


class WorkflowCommandIntegrator:
    """
    Integrates workflow enforcement into existing commands.
    
    This class provides a unified interface for commands to validate prerequisites,
    load context, and complete phases within the workflow enforcement system.
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize the command integrator.
        
        Args:
            workspace_path: Path to the workspace root.
        """
        self.workspace_path = workspace_path or os.getcwd()
        self.state_manager = WorkflowStateManager(workspace_path)
        self.context_manager = ContextTransferManager(workspace_path)
    
    def validate_command_prerequisites(self, command_name: str, target_phase: WorkflowPhase) -> Tuple[bool, Optional[str]]:
        """
        Validate prerequisites for command execution.
        
        Args:
            command_name: Name of the command being executed.
            target_phase: Target workflow phase for the command.
            
        Returns:
            Tuple of (prerequisites_met, error_message).
        """
        try:
            # Skip validation for product phase (entry point)
            if target_phase == WorkflowPhase.PRODUCT:
                return True, None
            
            # Validate phase prerequisites
            self.state_manager.validate_phase_prerequisites(target_phase)
            return True, None
            
        except PhasePrerequisiteError as e:
            # Generate helpful error message with guidance
            error_msg = self._generate_prerequisite_error_message(target_phase, str(e))
            return False, error_msg
        
        except Exception as e:
            return False, f"Workflow validation failed: {e}"
    
    def _generate_prerequisite_error_message(self, target_phase: WorkflowPhase, error_details: str) -> str:
        """
        Generate helpful error message for prerequisite failures.
        
        Args:
            target_phase: The phase that failed validation.
            error_details: Detailed error information.
            
        Returns:
            Formatted error message with guidance.
        """
        phase_guidance = {
            WorkflowPhase.SPECIFY: {
                "missing": "product",
                "command": "/simics-platform",
                "description": "Create a platform specification to define the product context"
            },
            WorkflowPhase.PLAN: {
                "missing": "specify", 
                "command": "/specify",
                "description": "Create a feature specification to define technical requirements"
            },
            WorkflowPhase.TASKS: {
                "missing": "plan",
                "command": "/plan", 
                "description": "Create an implementation plan to define the approach and design"
            }
        }
        
        guidance = phase_guidance.get(target_phase)
        if guidance:
            return (
                f"❌ Cannot proceed to {target_phase.value} phase.\n\n"
                f"🔍 Missing prerequisite: {guidance['missing']} phase must be completed first.\n"
                f"📋 Required action: Run {guidance['command']} command to {guidance['description']}.\n\n"
                f"💡 The enhanced workflow enforcement ensures proper sequence:\n"
                f"   product → specify → plan → tasks\n\n"
                f"Details: {error_details}"
            )
        else:
            return f"Workflow prerequisite error: {error_details}"
    
    def load_phase_context(self, phase: WorkflowPhase) -> Optional[Dict[str, Any]]:
        """
        Load context data for a specific phase.
        
        Args:
            phase: The phase to load context for.
            
        Returns:
            Context data or None if not available.
        """
        try:
            return self.context_manager.retrieve_context_for_phase(phase)
        except Exception as e:
            print(f"Warning: Failed to load {phase.value} context: {e}", file=sys.stderr)
            return None
    
    def prepare_command_context(self, command_name: str, target_phase: WorkflowPhase, 
                              arguments: Dict[str, Any]) -> CommandExecutionContext:
        """
        Prepare execution context for a command.
        
        Args:
            command_name: Name of the command.
            target_phase: Target workflow phase.
            arguments: Command arguments.
            
        Returns:
            Command execution context.
        """
        # Validate prerequisites
        prerequisites_met, error_msg = self.validate_command_prerequisites(command_name, target_phase)
        
        context = CommandExecutionContext(
            command_name=command_name,
            target_phase=target_phase,
            workspace_path=self.workspace_path,
            arguments=arguments,
            prerequisites_met=prerequisites_met
        )
        
        if not prerequisites_met:
            # Return context with error for handling by command
            context.error_message = error_msg
            return context
        
        # Load available contexts based on target phase
        if target_phase in [WorkflowPhase.SPECIFY, WorkflowPhase.PLAN, WorkflowPhase.TASKS]:
            product_data = self.load_phase_context(WorkflowPhase.PRODUCT)
            if product_data:
                try:
                    context.product_context = ProductContext(**product_data)
                except TypeError:
                    # Handle case where data structure doesn't match exactly
                    pass
        
        if target_phase in [WorkflowPhase.PLAN, WorkflowPhase.TASKS]:
            spec_data = self.load_phase_context(WorkflowPhase.SPECIFY)
            if spec_data:
                try:
                    context.spec_context = SpecificationContext(**spec_data)
                except TypeError:
                    pass
        
        if target_phase == WorkflowPhase.TASKS:
            plan_data = self.load_phase_context(WorkflowPhase.PLAN)
            if plan_data:
                try:
                    context.plan_context = PlanContext(**plan_data)
                except TypeError:
                    pass
        
        return context
    
    def start_phase_execution(self, phase: WorkflowPhase) -> None:
        """
        Mark the start of phase execution.
        
        Args:
            phase: The phase being started.
        """
        try:
            self.state_manager.start_phase(phase)
        except Exception as e:
            print(f"Warning: Failed to start phase {phase.value}: {e}", file=sys.stderr)
    
    def complete_phase_execution(self, phase: WorkflowPhase, output_content: Optional[str] = None,
                                context_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark the completion of phase execution.
        
        Args:
            phase: The phase being completed.
            output_content: Content generated for integrity checking.
            context_data: Context data to store for next phase.
        """
        try:
            # Store phase context if provided
            if context_data:
                self.state_manager.store_phase_data(phase, context_data)
            
            # Complete the phase
            self.state_manager.complete_phase(phase, output_content)
            
        except Exception as e:
            print(f"Warning: Failed to complete phase {phase.value}: {e}", file=sys.stderr)
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get current workflow status.
        
        Returns:
            Workflow status information.
        """
        try:
            return self.state_manager.get_workflow_status()
        except Exception as e:
            return {
                "error": f"Failed to get workflow status: {e}",
                "currentPhase": None,
                "completedPhases": [],
                "nextPhase": None
            }
    
    def generate_command_guidance(self, target_phase: WorkflowPhase) -> Dict[str, str]:
        """
        Generate guidance for command execution.
        
        Args:
            target_phase: Target phase for guidance.
            
        Returns:
            Guidance information.
        """
        completed_phases = self.state_manager.get_completed_phases()
        
        guidance = {
            "phase": target_phase.value,
            "status": "ready" if target_phase == WorkflowPhase.PRODUCT else "pending",
            "next_command": "",
            "description": ""
        }
        
        if target_phase == WorkflowPhase.PRODUCT:
            guidance.update({
                "status": "ready",
                "description": "Start the workflow by defining the product context",
                "notes": "This is the entry point for the enhanced workflow enforcement"
            })
        elif target_phase == WorkflowPhase.SPECIFY:
            if WorkflowPhase.PRODUCT in completed_phases:
                guidance.update({
                    "status": "ready", 
                    "description": "Create technical specification from product context",
                    "notes": "Product context will be automatically integrated"
                })
            else:
                guidance.update({
                    "status": "blocked",
                    "next_command": "/simics-platform",
                    "description": "Complete product phase first",
                    "notes": "Product context is required for specification generation"
                })
        elif target_phase == WorkflowPhase.PLAN:
            if WorkflowPhase.SPECIFY in completed_phases:
                guidance.update({
                    "status": "ready",
                    "description": "Create implementation plan from specification",
                    "notes": "Specification context will be automatically integrated"
                })
            else:
                missing_phases = []
                if WorkflowPhase.PRODUCT not in completed_phases:
                    missing_phases.append("product (/simics-platform)")
                if WorkflowPhase.SPECIFY not in completed_phases:
                    missing_phases.append("specify (/specify)")
                
                guidance.update({
                    "status": "blocked",
                    "next_command": f"/{missing_phases[0].split(' ')[0]}" if missing_phases else "",
                    "description": f"Complete missing phases: {', '.join(missing_phases)}",
                    "notes": "All previous phases must be completed in sequence"
                })
        elif target_phase == WorkflowPhase.TASKS:
            if WorkflowPhase.PLAN in completed_phases:
                guidance.update({
                    "status": "ready",
                    "description": "Generate implementation tasks from plan",
                    "notes": "Plan context will be automatically integrated"
                })
            else:
                missing_phases = []
                if WorkflowPhase.PRODUCT not in completed_phases:
                    missing_phases.append("product (/simics-platform)")
                if WorkflowPhase.SPECIFY not in completed_phases:
                    missing_phases.append("specify (/specify)")
                if WorkflowPhase.PLAN not in completed_phases:
                    missing_phases.append("plan (/plan)")
                
                guidance.update({
                    "status": "blocked", 
                    "next_command": f"/{missing_phases[0].split(' ')[0]}" if missing_phases else "",
                    "description": f"Complete missing phases: {', '.join(missing_phases)}",
                    "notes": "All previous phases must be completed in sequence"
                })
        
        return guidance
    
    def inject_context_into_template(self, template_path: str, target_phase: WorkflowPhase,
                                   context: CommandExecutionContext) -> str:
        """
        Inject context into template based on target phase.
        
        Args:
            template_path: Path to the template file.
            target_phase: Target workflow phase.
            context: Command execution context.
            
        Returns:
            Template content with injected context.
        """
        try:
            if target_phase == WorkflowPhase.SPECIFY and context.product_context:
                return self.context_manager.inject_product_context_into_spec(
                    context.product_context, template_path
                )
            elif target_phase == WorkflowPhase.PLAN and context.spec_context:
                return self.context_manager.inject_spec_context_into_plan(
                    context.spec_context, template_path
                )
            elif target_phase == WorkflowPhase.TASKS and context.plan_context:
                return self.context_manager.inject_plan_context_into_tasks(
                    context.plan_context, template_path
                )
            else:
                # Fallback: return template as-is
                with open(template_path, 'r') as f:
                    return f.read()
        except Exception as e:
            print(f"Warning: Context injection failed: {e}", file=sys.stderr)
            # Fallback: return template as-is
            try:
                with open(template_path, 'r') as f:
                    return f.read()
            except:
                return ""
    
    def validate_workflow_integrity(self) -> Dict[str, Any]:
        """
        Validate overall workflow integrity.
        
        Returns:
            Validation results.
        """
        try:
            return self.context_manager.validate_context_flow()
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Workflow integrity check failed: {e}"],
                "completed_phases": []
            }


def create_workflow_integrator(workspace_path: Optional[str] = None) -> WorkflowCommandIntegrator:
    """
    Factory function to create a workflow integrator instance.
    
    Args:
        workspace_path: Path to the workspace root.
        
    Returns:
        Workflow command integrator instance.
    """
    return WorkflowCommandIntegrator(workspace_path)


# Convenience functions for script integration

def validate_phase_prerequisites(phase_name: str, workspace_path: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate prerequisites for a phase.
    
    Args:
        phase_name: Name of the phase ("product", "specify", "plan", "tasks").
        workspace_path: Path to the workspace root.
        
    Returns:
        Tuple of (prerequisites_met, error_message).
    """
    try:
        phase = WorkflowPhase(phase_name)
        integrator = create_workflow_integrator(workspace_path)
        return integrator.validate_command_prerequisites(phase_name, phase)
    except ValueError:
        return False, f"Invalid phase name: {phase_name}"
    except Exception as e:
        return False, f"Validation failed: {e}"


def get_phase_context(phase_name: str, workspace_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get context data for a phase.
    
    Args:
        phase_name: Name of the phase ("product", "specify", "plan", "tasks").
        workspace_path: Path to the workspace root.
        
    Returns:
        Context data or None if not available.
    """
    try:
        phase = WorkflowPhase(phase_name)
        integrator = create_workflow_integrator(workspace_path)
        return integrator.load_phase_context(phase)
    except ValueError:
        return None
    except Exception:
        return None


def complete_phase(phase_name: str, output_content: Optional[str] = None,
                  context_data: Optional[Dict[str, Any]] = None,
                  workspace_path: Optional[str] = None) -> bool:
    """
    Mark a phase as completed.
    
    Args:
        phase_name: Name of the phase ("product", "specify", "plan", "tasks").
        output_content: Content generated for integrity checking.
        context_data: Context data to store for next phase.
        workspace_path: Path to the workspace root.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        phase = WorkflowPhase(phase_name)
        integrator = create_workflow_integrator(workspace_path)
        integrator.complete_phase_execution(phase, output_content, context_data)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Command-line interface for workflow operations
    import argparse
    
    parser = argparse.ArgumentParser(description="Workflow enforcement utility")
    parser.add_argument("operation", choices=["validate", "status", "context"], 
                       help="Operation to perform")
    parser.add_argument("--phase", help="Phase name for validation or context operations")
    parser.add_argument("--workspace", help="Workspace path")
    
    args = parser.parse_args()
    
    if args.operation == "validate":
        if not args.phase:
            print("Error: --phase required for validate operation", file=sys.stderr)
            sys.exit(1)
        
        success, error = validate_phase_prerequisites(args.phase, args.workspace)
        if success:
            print(f"✅ {args.phase} phase prerequisites met")
            sys.exit(0)
        else:
            print(f"❌ {error}", file=sys.stderr)
            sys.exit(1)
    
    elif args.operation == "status":
        integrator = create_workflow_integrator(args.workspace)
        status = integrator.get_workflow_status()
        
        print(f"Current Phase: {status.get('currentPhase', 'None')}")
        print(f"Completed Phases: {', '.join(status.get('completedPhases', []))}")
        print(f"Next Phase: {status.get('nextPhase', 'None')}")
    
    elif args.operation == "context":
        if not args.phase:
            print("Error: --phase required for context operation", file=sys.stderr)
            sys.exit(1)
        
        context = get_phase_context(args.phase, args.workspace)
        if context:
            import json
            print(json.dumps(context, indent=2))
        else:
            print(f"No context available for {args.phase} phase")
            sys.exit(1)