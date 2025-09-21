"""
Traceability Verification System for Enhanced Workflow Enforcement.

This module provides comprehensive traceability validation across all workflow
phases to ensure proper context flow and requirement continuity throughout
the product → specify → plan → tasks sequence.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass

from .workflow_state import WorkflowPhase, WorkflowStateManager
from .context_transfer import ContextTransferManager
from .validation_framework import ValidationLevel, ValidationIssue, ValidationResult


@dataclass 
class TraceabilityLink:
    """Represents a traceability link between phases."""
    source_phase: WorkflowPhase
    target_phase: WorkflowPhase
    source_element: str
    target_element: str
    confidence: float  # 0.0 to 1.0
    link_type: str  # "requirement", "constraint", "decision", etc.


@dataclass
class TraceabilityMatrix:
    """Matrix showing traceability coverage across phases."""
    source_phase: WorkflowPhase
    target_phase: WorkflowPhase
    total_elements: int
    traced_elements: int
    coverage: float  # traced_elements / total_elements
    links: List[TraceabilityLink]


class TraceabilityValidator:
    """
    Validates traceability across all workflow phases.
    
    This validator ensures proper context flow and requirement traceability
    throughout the product → specify → plan → tasks sequence.
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize the traceability validator."""
        self.state_manager = WorkflowStateManager(workspace_path)
        self.context_manager = ContextTransferManager(workspace_path)
        self.workspace_path = workspace_path or "."
    
    def validate_full_traceability(self) -> ValidationResult:
        """
        Validate traceability across the entire workflow.
        
        Returns:
            Validation result for full workflow traceability.
        """
        issues = []
        details = {}
        
        # Get workflow status
        workflow_status = self.state_manager.get_workflow_status()
        completed_phases = [WorkflowPhase(phase) for phase in workflow_status.get("completedPhases", [])]
        
        if len(completed_phases) < 2:
            return ValidationResult(
                valid=True,
                score=1.0,
                issues=[],
                summary="✅ Insufficient phases completed for traceability validation",
                details={"completed_phases": len(completed_phases)}
            )
        
        # Validate context flow
        context_flow_issues, context_score = self._validate_context_flow(completed_phases)
        issues.extend(context_flow_issues)
        details["context_flow_score"] = context_score
        
        # Validate requirement traceability
        req_trace_issues, req_score = self._validate_requirement_traceability(completed_phases)
        issues.extend(req_trace_issues)
        details["requirement_traceability_score"] = req_score
        
        # Validate consistency across phases
        consistency_issues, consistency_score = self._validate_phase_consistency(completed_phases)
        issues.extend(consistency_issues)
        details["consistency_score"] = consistency_score
        
        # Generate traceability matrices
        matrices = self._generate_traceability_matrices(completed_phases)
        details["traceability_matrices"] = [
            {
                "source": matrix.source_phase.value,
                "target": matrix.target_phase.value,
                "coverage": matrix.coverage,
                "traced_elements": matrix.traced_elements,
                "total_elements": matrix.total_elements
            }
            for matrix in matrices
        ]
        
        # Calculate overall score
        scores = [context_score, req_score, consistency_score]
        overall_score = sum(scores) / len(scores)
        
        # Determine validity
        valid = overall_score >= 0.8 and not any(issue.level == ValidationLevel.ERROR for issue in issues)
        
        # Generate summary
        summary = self._generate_traceability_summary(valid, overall_score, completed_phases, issues)
        
        return ValidationResult(
            valid=valid,
            score=overall_score,
            issues=issues,
            summary=summary,
            details=details
        )
    
    def _validate_context_flow(self, completed_phases: List[WorkflowPhase]) -> Tuple[List[ValidationIssue], float]:
        """Validate context flow between phases."""
        issues = []
        flow_scores = []
        
        # Check product → specify flow
        if WorkflowPhase.SPECIFY in completed_phases:
            product_context = self.context_manager.retrieve_context_for_phase(WorkflowPhase.PRODUCT)
            if not product_context:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="context_flow",
                    message="Missing product context for specification phase",
                    suggestion="Ensure product phase properly captures and stores context"
                ))
                flow_scores.append(0.0)
            else:
                flow_scores.append(1.0)
        
        # Check specify → plan flow
        if WorkflowPhase.PLAN in completed_phases:
            spec_context = self.context_manager.retrieve_context_for_phase(WorkflowPhase.SPECIFY)
            if not spec_context:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="context_flow",
                    message="Missing specification context for planning phase",
                    suggestion="Ensure specification phase properly captures and stores context"
                ))
                flow_scores.append(0.0)
            else:
                flow_scores.append(1.0)
        
        # Check plan → tasks flow
        if WorkflowPhase.TASKS in completed_phases:
            plan_context = self.context_manager.retrieve_context_for_phase(WorkflowPhase.PLAN)
            if not plan_context:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="context_flow",
                    message="Missing plan context for tasks phase",
                    suggestion="Ensure planning phase properly captures and stores context"
                ))
                flow_scores.append(0.0)
            else:
                flow_scores.append(1.0)
        
        # Calculate context flow score
        context_score = sum(flow_scores) / max(len(flow_scores), 1)
        
        return issues, context_score
    
    def _validate_requirement_traceability(self, completed_phases: List[WorkflowPhase]) -> Tuple[List[ValidationIssue], float]:
        """Validate requirement traceability across phases."""
        issues = []
        
        if len(completed_phases) < 2:
            return issues, 1.0  # Not enough phases to validate traceability
        
        # Check if all phases maintain requirement context
        phase_contexts = {}
        missing_contexts = []
        
        for phase in completed_phases:
            context = self.context_manager.retrieve_context_for_phase(phase)
            if context:
                phase_contexts[phase] = context
            else:
                missing_contexts.append(phase)
        
        if missing_contexts:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="requirement_traceability",
                message=f"Missing context for phases: {[p.value for p in missing_contexts]}",
                suggestion="Ensure all phases capture and store context properly"
            ))
        
        # Validate specific traceability links
        if WorkflowPhase.PRODUCT in phase_contexts and WorkflowPhase.SPECIFY in phase_contexts:
            product_req_issues = self._check_product_to_spec_traceability(
                phase_contexts[WorkflowPhase.PRODUCT],
                phase_contexts[WorkflowPhase.SPECIFY]
            )
            issues.extend(product_req_issues)
        
        if WorkflowPhase.SPECIFY in phase_contexts and WorkflowPhase.PLAN in phase_contexts:
            spec_plan_issues = self._check_spec_to_plan_traceability(
                phase_contexts[WorkflowPhase.SPECIFY],
                phase_contexts[WorkflowPhase.PLAN]
            )
            issues.extend(spec_plan_issues)
        
        # Calculate requirement traceability score
        req_score = len(phase_contexts) / len(completed_phases) if completed_phases else 1.0
        
        # Reduce score based on traceability issues
        traceability_issues = [i for i in issues if i.category == "requirement_traceability"]
        if traceability_issues:
            req_score *= max(0.5, 1.0 - len(traceability_issues) * 0.1)
        
        return issues, req_score
    
    def _validate_phase_consistency(self, completed_phases: List[WorkflowPhase]) -> Tuple[List[ValidationIssue], float]:
        """Validate consistency across phases."""
        issues = []
        
        # Check phase completion markers
        missing_markers = []
        for phase in completed_phases:
            marker_file = self.state_manager.phase_markers_dir / f"{phase.value}.complete"
            if not marker_file.exists():
                missing_markers.append(phase)
        
        if missing_markers:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="consistency",
                message=f"Missing completion markers for phases: {[p.value for p in missing_markers]}",
                suggestion="Ensure all completed phases have proper completion markers"
            ))
        
        # Check state file consistency
        try:
            workflow_status = self.state_manager.get_workflow_status()
            stated_completed = set(workflow_status.get("completedPhases", []))
            actual_completed = set(p.value for p in completed_phases)
            
            if stated_completed != actual_completed:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="consistency",
                    message="Workflow state inconsistency detected",
                    suggestion="Reconcile workflow state with actual phase completion"
                ))
        except Exception as e:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="consistency",
                message=f"Could not verify workflow state consistency: {e}",
                suggestion="Check workflow state file integrity"
            ))
        
        # Calculate consistency score
        consistency_score = max(0.0, 1.0 - len(missing_markers) * 0.2 - 
                               len([i for i in issues if i.level == ValidationLevel.ERROR]) * 0.5)
        
        return issues, consistency_score
    
    def _check_product_to_spec_traceability(self, product_context: Dict[str, Any], 
                                          spec_context: Dict[str, Any]) -> List[ValidationIssue]:
        """Check traceability from product to specification phase."""
        issues = []
        
        # Check if product requirements are addressed in specification
        product_requirements = product_context.get("requirements", [])
        if product_requirements:
            # This is a simplified check - in practice, you would analyze 
            # the actual specification document content
            spec_reqs = spec_context.get("technical_requirements", [])
            
            if len(spec_reqs) < len(product_requirements) * 0.8:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="requirement_traceability",
                    message="Specification may not address all product requirements",
                    suggestion="Ensure all product requirements are covered in technical specifications"
                ))
        
        # Check if product constraints are considered
        product_constraints = product_context.get("constraints", [])
        if product_constraints:
            spec_constraints = spec_context.get("design_constraints", [])
            
            if len(spec_constraints) < len(product_constraints) * 0.7:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="requirement_traceability",
                    message="Not all product constraints reflected in specification",
                    suggestion="Ensure product constraints are considered in design constraints"
                ))
        
        return issues
    
    def _check_spec_to_plan_traceability(self, spec_context: Dict[str, Any], 
                                       plan_context: Dict[str, Any]) -> List[ValidationIssue]:
        """Check traceability from specification to plan phase."""
        issues = []
        
        # Check if technical requirements are addressed in plan
        tech_requirements = spec_context.get("technical_requirements", [])
        if tech_requirements:
            # Check if plan has corresponding implementation strategy
            impl_strategy = plan_context.get("implementation_strategy", "")
            
            if not impl_strategy or len(impl_strategy.split()) < 50:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="requirement_traceability",
                    message="Implementation plan may not adequately address technical requirements",
                    suggestion="Ensure implementation strategy covers all technical requirements"
                ))
        
        # Check if architecture decisions are reflected in plan
        arch_decisions = spec_context.get("architecture_decisions", [])
        if arch_decisions:
            tech_stack = plan_context.get("technology_stack", [])
            
            if not tech_stack:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="requirement_traceability",
                    message="Technology stack not specified in plan",
                    suggestion="Define technology stack based on architecture decisions"
                ))
        
        return issues
    
    def _generate_traceability_matrices(self, completed_phases: List[WorkflowPhase]) -> List[TraceabilityMatrix]:
        """Generate traceability matrices for phase relationships."""
        matrices = []
        
        # Generate matrices for each phase pair
        phase_pairs = [
            (WorkflowPhase.PRODUCT, WorkflowPhase.SPECIFY),
            (WorkflowPhase.SPECIFY, WorkflowPhase.PLAN),
            (WorkflowPhase.PLAN, WorkflowPhase.TASKS)
        ]
        
        for source, target in phase_pairs:
            if source in completed_phases and target in completed_phases:
                matrix = self._create_traceability_matrix(source, target)
                matrices.append(matrix)
        
        return matrices
    
    def _create_traceability_matrix(self, source_phase: WorkflowPhase, 
                                  target_phase: WorkflowPhase) -> TraceabilityMatrix:
        """Create a traceability matrix between two phases."""
        # Get contexts for both phases
        source_context = self.context_manager.retrieve_context_for_phase(source_phase)
        target_context = self.context_manager.retrieve_context_for_phase(target_phase)
        
        # This is a simplified implementation - in practice, you would analyze
        # actual document content to create detailed traceability links
        
        if not source_context or not target_context:
            return TraceabilityMatrix(
                source_phase=source_phase,
                target_phase=target_phase,
                total_elements=0,
                traced_elements=0,
                coverage=0.0,
                links=[]
            )
        
        # Simplified traceability calculation
        source_elements = self._count_traceable_elements(source_context)
        target_elements = self._count_traceable_elements(target_context)
        
        # Estimate traceability based on context overlap
        traced_elements = min(source_elements, target_elements)
        coverage = traced_elements / max(source_elements, 1)
        
        # Create sample links (in practice, these would be derived from content analysis)
        links = self._create_sample_links(source_phase, target_phase, traced_elements)
        
        return TraceabilityMatrix(
            source_phase=source_phase,
            target_phase=target_phase,
            total_elements=source_elements,
            traced_elements=traced_elements,
            coverage=coverage,
            links=links
        )
    
    def _count_traceable_elements(self, context: Dict[str, Any]) -> int:
        """Count traceable elements in a context."""
        count = 0
        
        # Count requirements
        if "requirements" in context:
            count += len(context["requirements"])
        
        # Count constraints
        if "constraints" in context:
            count += len(context["constraints"])
        
        # Count technical requirements
        if "technical_requirements" in context:
            count += len(context["technical_requirements"])
        
        # Count architecture decisions
        if "architecture_decisions" in context:
            count += len(context["architecture_decisions"])
        
        return max(count, 1)  # Ensure at least 1 to avoid division by zero
    
    def _create_sample_links(self, source_phase: WorkflowPhase, target_phase: WorkflowPhase, 
                           count: int) -> List[TraceabilityLink]:
        """Create sample traceability links."""
        links = []
        
        for i in range(min(count, 5)):  # Limit to 5 sample links
            link = TraceabilityLink(
                source_phase=source_phase,
                target_phase=target_phase,
                source_element=f"{source_phase.value}_element_{i+1}",
                target_element=f"{target_phase.value}_element_{i+1}",
                confidence=0.8 + (i * 0.05),  # Sample confidence
                link_type="requirement" if i % 2 == 0 else "constraint"
            )
            links.append(link)
        
        return links
    
    def _generate_traceability_summary(self, valid: bool, score: float, 
                                     completed_phases: List[WorkflowPhase], 
                                     issues: List[ValidationIssue]) -> str:
        """Generate traceability validation summary."""
        phase_names = [p.value for p in completed_phases]
        
        if valid:
            summary = f"✅ Traceability validation passed (score: {score:.2f})"
        else:
            summary = f"❌ Traceability validation failed (score: {score:.2f})"
        
        summary += f" - Phases: {' → '.join(phase_names)}"
        
        error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in issues if i.level == ValidationLevel.WARNING])
        
        if error_count > 0:
            summary += f" - {error_count} errors"
        if warning_count > 0:
            summary += f" - {warning_count} warnings"
        
        return summary
    
    def generate_traceability_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive traceability report.
        
        Returns:
            Dictionary containing detailed traceability information.
        """
        validation_result = self.validate_full_traceability()
        
        # Get workflow status
        workflow_status = self.state_manager.get_workflow_status()
        completed_phases = [WorkflowPhase(phase) for phase in workflow_status.get("completedPhases", [])]
        
        # Generate detailed report
        report = {
            "validation_result": {
                "valid": validation_result.valid,
                "score": validation_result.score,
                "summary": validation_result.summary,
                "issue_count": len(validation_result.issues)
            },
            "workflow_status": {
                "completed_phases": [p.value for p in completed_phases],
                "total_phases": len(WorkflowPhase),
                "progress": len(completed_phases) / len(WorkflowPhase)
            },
            "traceability_matrices": validation_result.details.get("traceability_matrices", []),
            "context_flow": {
                "score": validation_result.details.get("context_flow_score", 0.0),
                "status": "passing" if validation_result.details.get("context_flow_score", 0.0) >= 0.8 else "failing"
            },
            "requirement_traceability": {
                "score": validation_result.details.get("requirement_traceability_score", 0.0),
                "status": "passing" if validation_result.details.get("requirement_traceability_score", 0.0) >= 0.8 else "failing"
            },
            "consistency": {
                "score": validation_result.details.get("consistency_score", 0.0),
                "status": "passing" if validation_result.details.get("consistency_score", 0.0) >= 0.8 else "failing"
            },
            "issues": [
                {
                    "level": issue.level.value,
                    "category": issue.category,
                    "message": issue.message,
                    "suggestion": issue.suggestion
                }
                for issue in validation_result.issues
            ]
        }
        
        return report


def validate_workflow_traceability(workspace_path: Optional[str] = None) -> ValidationResult:
    """
    Convenience function to validate workflow traceability.
    
    Args:
        workspace_path: Path to the workspace root.
        
    Returns:
        Validation result.
    """
    validator = TraceabilityValidator(workspace_path)
    return validator.validate_full_traceability()


def generate_traceability_report(workspace_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to generate traceability report.
    
    Args:
        workspace_path: Path to the workspace root.
        
    Returns:
        Traceability report.
    """
    validator = TraceabilityValidator(workspace_path)
    return validator.generate_traceability_report()


if __name__ == "__main__":
    # Command-line interface for traceability validation
    import argparse
    
    parser = argparse.ArgumentParser(description="Traceability validation utility")
    parser.add_argument("--workspace", help="Workspace path", default=".")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    
    args = parser.parse_args()
    
    if args.report:
        report = generate_traceability_report(args.workspace)
        print(json.dumps(report, indent=2))
    else:
        result = validate_workflow_traceability(args.workspace)
        print(result.summary)
        print(f"Score: {result.score:.2f}")
        
        if result.issues:
            print("\\nIssues:")
            for issue in result.issues:
                level_icon = "❌" if issue.level == ValidationLevel.ERROR else "⚠️" if issue.level == ValidationLevel.WARNING else "ℹ️"
                print(f"  {level_icon} {issue.message}")
                if issue.suggestion:
                    print(f"     💡 {issue.suggestion}")
        
        exit(0 if result.valid else 1)