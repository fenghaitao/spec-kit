"""
Context Transfer Utilities for Enhanced Workflow Enforcement.

This module provides utilities for transferring context and data between
workflow phases (product → specify → plan → tasks) while maintaining
traceability and integrity.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from .workflow_state import WorkflowPhase, WorkflowStateManager


class ContextType(Enum):
    """Types of context that can be transferred between phases."""
    PRODUCT_VISION = "product_vision"
    REQUIREMENTS = "requirements"
    CONSTRAINTS = "constraints"
    STAKEHOLDER_INFO = "stakeholder_info"
    TECHNICAL_SPECS = "technical_specs"
    ARCHITECTURE_DECISIONS = "architecture_decisions"
    DESIGN_ARTIFACTS = "design_artifacts"
    IMPLEMENTATION_PLAN = "implementation_plan"


@dataclass
class ContextItem:
    """Represents a single piece of context information."""
    type: ContextType
    content: str
    source_phase: WorkflowPhase
    metadata: Dict[str, Any]
    created_at: str
    hash: Optional[str] = None


@dataclass
class ProductContext:
    """Context data from the product phase."""
    vision: str
    success_criteria: List[str]
    constraints: List[str]
    stakeholders: List[Dict[str, str]]
    requirements: List[Dict[str, str]]
    metadata: Dict[str, Any]


@dataclass
class SpecificationContext:
    """Context data from the specification phase."""
    technical_requirements: List[Dict[str, str]]
    architecture_decisions: List[Dict[str, str]]
    design_constraints: List[str]
    interfaces: List[Dict[str, str]]
    validation_criteria: List[str]
    clarifications_resolved: List[str]
    metadata: Dict[str, Any]


@dataclass
class PlanContext:
    """Context data from the plan phase."""
    implementation_strategy: str
    technology_stack: List[str]
    resource_allocation: Dict[str, Any]
    milestones: List[Dict[str, str]]
    dependencies: List[str]
    risk_analysis: List[Dict[str, str]]
    design_artifacts: List[str]
    metadata: Dict[str, Any]


class ContextTransferManager:
    """
    Manages context transfer between workflow phases.
    
    This class handles extraction, transformation, and injection of context
    data as it flows through the product → specify → plan → tasks sequence.
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize the context transfer manager.
        
        Args:
            workspace_path: Path to the workspace root.
        """
        self.workspace_path = Path(workspace_path or ".")
        self.state_manager = WorkflowStateManager(workspace_path)
    
    def extract_product_context(self, product_spec_path: Union[str, Path]) -> ProductContext:
        """
        Extract product context from product specification document.
        
        Args:
            product_spec_path: Path to the product specification file.
            
        Returns:
            Extracted product context.
        """
        spec_path = Path(product_spec_path)
        if not spec_path.exists():
            raise FileNotFoundError(f"Product specification not found: {spec_path}")
        
        content = spec_path.read_text()
        
        # Extract structured information from product specification
        vision = self._extract_section(content, "Product Vision", "Vision")
        success_criteria = self._extract_list_section(content, "Success Criteria", "Criteria")
        constraints = self._extract_list_section(content, "Technical Constraints", "Constraints")
        stakeholders = self._extract_stakeholders(content)
        requirements = self._extract_requirements(content)
        
        return ProductContext(
            vision=vision,
            success_criteria=success_criteria,
            constraints=constraints,
            stakeholders=stakeholders,
            requirements=requirements,
            metadata={
                "source_file": str(spec_path),
                "extracted_at": self._get_timestamp(),
                "sections_found": self._count_sections(content)
            }
        )
    
    def extract_specification_context(self, spec_path: Union[str, Path]) -> SpecificationContext:
        """
        Extract specification context from specification document.
        
        Args:
            spec_path: Path to the specification file.
            
        Returns:
            Extracted specification context.
        """
        spec_file = Path(spec_path)
        if not spec_file.exists():
            raise FileNotFoundError(f"Specification not found: {spec_file}")
        
        content = spec_file.read_text()
        
        # Extract technical specification elements
        tech_requirements = self._extract_technical_requirements(content)
        arch_decisions = self._extract_architecture_decisions(content)
        design_constraints = self._extract_list_section(content, "Design Constraints")
        interfaces = self._extract_interfaces(content)
        validation_criteria = self._extract_list_section(content, "Validation Criteria")
        clarifications = self._extract_resolved_clarifications(content)
        
        return SpecificationContext(
            technical_requirements=tech_requirements,
            architecture_decisions=arch_decisions,
            design_constraints=design_constraints,
            interfaces=interfaces,
            validation_criteria=validation_criteria,
            clarifications_resolved=clarifications,
            metadata={
                "source_file": str(spec_file),
                "extracted_at": self._get_timestamp(),
                "completeness_score": self._calculate_completeness_score(content)
            }
        )
    
    def extract_plan_context(self, plan_path: Union[str, Path]) -> PlanContext:
        """
        Extract plan context from implementation plan document.
        
        Args:
            plan_path: Path to the plan file.
            
        Returns:
            Extracted plan context.
        """
        plan_file = Path(plan_path)
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan not found: {plan_file}")
        
        content = plan_file.read_text()
        
        # Extract implementation plan elements
        strategy = self._extract_section(content, "Implementation Strategy", "Strategy")
        technology = self._extract_list_section(content, "Technology Stack", "Technologies")
        resources = self._extract_resource_allocation(content)
        milestones = self._extract_milestones(content)
        dependencies = self._extract_list_section(content, "Dependencies")
        risks = self._extract_risk_analysis(content)
        artifacts = self._extract_design_artifacts(content)
        
        return PlanContext(
            implementation_strategy=strategy,
            technology_stack=technology,
            resource_allocation=resources,
            milestones=milestones,
            dependencies=dependencies,
            risk_analysis=risks,
            design_artifacts=artifacts,
            metadata={
                "source_file": str(plan_file),
                "extracted_at": self._get_timestamp(),
                "plan_complexity": self._assess_plan_complexity(content)
            }
        )
    
    def inject_product_context_into_spec(self, product_context: ProductContext, 
                                       spec_template_path: Union[str, Path]) -> str:
        """
        Inject product context into specification template.
        
        Args:
            product_context: Product context to inject.
            spec_template_path: Path to specification template.
            
        Returns:
            Specification content with injected product context.
        """
        template_path = Path(spec_template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Specification template not found: {template_path}")
        
        template_content = template_path.read_text()
        
        # Replace placeholders with product context
        injected_content = template_content
        
        # Inject product vision
        injected_content = injected_content.replace(
            "{{PRODUCT_VISION}}", product_context.vision
        )
        
        # Inject success criteria
        criteria_text = "\n".join(f"- {criterion}" for criterion in product_context.success_criteria)
        injected_content = injected_content.replace(
            "{{SUCCESS_CRITERIA}}", criteria_text
        )
        
        # Inject constraints
        constraints_text = "\n".join(f"- {constraint}" for constraint in product_context.constraints)
        injected_content = injected_content.replace(
            "{{TECHNICAL_CONSTRAINTS}}", constraints_text
        )
        
        # Inject requirements
        requirements_text = self._format_requirements(product_context.requirements)
        injected_content = injected_content.replace(
            "{{REQUIREMENTS}}", requirements_text
        )
        
        # Inject stakeholder information
        stakeholders_text = self._format_stakeholders(product_context.stakeholders)
        injected_content = injected_content.replace(
            "{{STAKEHOLDERS}}", stakeholders_text
        )
        
        return injected_content
    
    def inject_spec_context_into_plan(self, spec_context: SpecificationContext,
                                    plan_template_path: Union[str, Path]) -> str:
        """
        Inject specification context into plan template.
        
        Args:
            spec_context: Specification context to inject.
            plan_template_path: Path to plan template.
            
        Returns:
            Plan content with injected specification context.
        """
        template_path = Path(plan_template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Plan template not found: {template_path}")
        
        template_content = template_path.read_text()
        
        # Replace placeholders with specification context
        injected_content = template_content
        
        # Inject technical requirements
        tech_req_text = self._format_technical_requirements(spec_context.technical_requirements)
        injected_content = injected_content.replace(
            "{{TECHNICAL_REQUIREMENTS}}", tech_req_text
        )
        
        # Inject architecture decisions
        arch_text = self._format_architecture_decisions(spec_context.architecture_decisions)
        injected_content = injected_content.replace(
            "{{ARCHITECTURE_DECISIONS}}", arch_text
        )
        
        # Inject design constraints
        constraints_text = "\n".join(f"- {constraint}" for constraint in spec_context.design_constraints)
        injected_content = injected_content.replace(
            "{{DESIGN_CONSTRAINTS}}", constraints_text
        )
        
        # Inject interfaces
        interfaces_text = self._format_interfaces(spec_context.interfaces)
        injected_content = injected_content.replace(
            "{{INTERFACES}}", interfaces_text
        )
        
        return injected_content
    
    def inject_plan_context_into_tasks(self, plan_context: PlanContext,
                                     tasks_template_path: Union[str, Path]) -> str:
        """
        Inject plan context into tasks template.
        
        Args:
            plan_context: Plan context to inject.
            tasks_template_path: Path to tasks template.
            
        Returns:
            Tasks content with injected plan context.
        """
        template_path = Path(tasks_template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Tasks template not found: {template_path}")
        
        template_content = template_path.read_text()
        
        # Replace placeholders with plan context
        injected_content = template_content
        
        # Inject implementation strategy
        injected_content = injected_content.replace(
            "{{IMPLEMENTATION_STRATEGY}}", plan_context.implementation_strategy
        )
        
        # Inject technology stack
        tech_text = "\n".join(f"- {tech}" for tech in plan_context.technology_stack)
        injected_content = injected_content.replace(
            "{{TECHNOLOGY_STACK}}", tech_text
        )
        
        # Inject milestones
        milestones_text = self._format_milestones(plan_context.milestones)
        injected_content = injected_content.replace(
            "{{MILESTONES}}", milestones_text
        )
        
        # Inject dependencies
        deps_text = "\n".join(f"- {dep}" for dep in plan_context.dependencies)
        injected_content = injected_content.replace(
            "{{DEPENDENCIES}}", deps_text
        )
        
        return injected_content
    
    def store_context_for_phase(self, phase: WorkflowPhase, context: Union[ProductContext, SpecificationContext, PlanContext]) -> None:
        """
        Store context data for a specific phase.
        
        Args:
            phase: The workflow phase.
            context: Context data to store.
        """
        context_data = asdict(context)
        self.state_manager.store_phase_data(phase, context_data)
    
    def retrieve_context_for_phase(self, phase: WorkflowPhase) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored context data for a specific phase.
        
        Args:
            phase: The workflow phase.
            
        Returns:
            Context data or None if not found.
        """
        return self.state_manager.get_phase_data(phase)
    
    def validate_context_flow(self) -> Dict[str, Any]:
        """
        Validate context flow across all completed phases.
        
        Returns:
            Validation results including any issues found.
        """
        completed_phases = self.state_manager.get_completed_phases()
        issues = []
        
        # Check product → specify flow
        if WorkflowPhase.SPECIFY in completed_phases:
            product_data = self.retrieve_context_for_phase(WorkflowPhase.PRODUCT)
            if not product_data:
                issues.append("Missing product context for specification phase")
        
        # Check specify → plan flow
        if WorkflowPhase.PLAN in completed_phases:
            spec_data = self.retrieve_context_for_phase(WorkflowPhase.SPECIFY)
            if not spec_data:
                issues.append("Missing specification context for plan phase")
        
        # Check plan → tasks flow
        if WorkflowPhase.TASKS in completed_phases:
            plan_data = self.retrieve_context_for_phase(WorkflowPhase.PLAN)
            if not plan_data:
                issues.append("Missing plan context for tasks phase")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "completed_phases": [phase.value for phase in completed_phases]
        }
    
    # Helper methods for content extraction and formatting
    
    def _extract_section(self, content: str, *section_names: str) -> str:
        """Extract content from a markdown section."""
        for section_name in section_names:
            pattern = rf"#{1,6}\s*{re.escape(section_name)}.*?\n(.*?)(?=\n#{1,6}|\Z)"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
    
    def _extract_list_section(self, content: str, *section_names: str) -> List[str]:
        """Extract list items from a markdown section."""
        section_content = self._extract_section(content, *section_names)
        if not section_content:
            return []
        
        lines = section_content.split("\n")
        items = []
        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                items.append(line[2:].strip())
            elif line.startswith("1. ") or re.match(r"^\d+\.", line):
                items.append(re.sub(r"^\d+\.\s*", "", line).strip())
        
        return items
    
    def _extract_stakeholders(self, content: str) -> List[Dict[str, str]]:
        """Extract stakeholder information."""
        stakeholders = []
        section_content = self._extract_section(content, "Stakeholders", "Stakeholder")
        
        # Simple extraction - can be enhanced based on actual format
        lines = section_content.split("\n")
        for line in lines:
            if ":" in line and (line.startswith("- ") or line.startswith("* ")):
                parts = line[2:].split(":", 1)
                if len(parts) == 2:
                    stakeholders.append({
                        "name": parts[0].strip(),
                        "role": parts[1].strip()
                    })
        
        return stakeholders
    
    def _extract_requirements(self, content: str) -> List[Dict[str, str]]:
        """Extract requirements information."""
        requirements = []
        section_content = self._extract_section(content, "Requirements", "Requirement")
        
        # Extract requirements with IDs and descriptions
        lines = section_content.split("\n")
        for line in lines:
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                req_text = line.strip()[2:]
                # Simple format: "REQ-001: Description"
                if ":" in req_text:
                    parts = req_text.split(":", 1)
                    requirements.append({
                        "id": parts[0].strip(),
                        "description": parts[1].strip()
                    })
                else:
                    requirements.append({
                        "id": f"REQ-{len(requirements) + 1:03d}",
                        "description": req_text
                    })
        
        return requirements
    
    def _extract_technical_requirements(self, content: str) -> List[Dict[str, str]]:
        """Extract technical requirements."""
        return self._extract_requirements(content)  # Reuse requirements extraction
    
    def _extract_architecture_decisions(self, content: str) -> List[Dict[str, str]]:
        """Extract architecture decisions."""
        decisions = []
        section_content = self._extract_section(content, "Architecture", "Design Decisions")
        
        lines = section_content.split("\n")
        for line in lines:
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                decision_text = line.strip()[2:]
                decisions.append({
                    "decision": decision_text,
                    "rationale": ""  # Could be enhanced to extract rationale
                })
        
        return decisions
    
    def _extract_interfaces(self, content: str) -> List[Dict[str, str]]:
        """Extract interface definitions."""
        interfaces = []
        section_content = self._extract_section(content, "Interfaces", "API")
        
        lines = section_content.split("\n")
        for line in lines:
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                interface_text = line.strip()[2:]
                interfaces.append({
                    "name": interface_text,
                    "description": ""
                })
        
        return interfaces
    
    def _extract_resolved_clarifications(self, content: str) -> List[str]:
        """Extract resolved clarifications."""
        # Look for resolved [NEEDS CLARIFICATION] items
        resolved = []
        lines = content.split("\n")
        
        for line in lines:
            if "[RESOLVED]" in line or "[CLARIFIED]" in line:
                resolved.append(line.strip())
        
        return resolved
    
    def _extract_resource_allocation(self, content: str) -> Dict[str, Any]:
        """Extract resource allocation information."""
        section_content = self._extract_section(content, "Resources", "Resource Allocation")
        
        # Simple extraction - can be enhanced
        return {
            "team_size": self._extract_number_from_text(section_content, "team"),
            "timeline": self._extract_timeline(section_content),
            "budget": self._extract_number_from_text(section_content, "budget")
        }
    
    def _extract_milestones(self, content: str) -> List[Dict[str, str]]:
        """Extract milestone information."""
        milestones = []
        section_content = self._extract_section(content, "Milestones", "Timeline")
        
        lines = section_content.split("\n")
        for line in lines:
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                milestone_text = line.strip()[2:]
                milestones.append({
                    "name": milestone_text,
                    "date": ""  # Could be enhanced to extract dates
                })
        
        return milestones
    
    def _extract_risk_analysis(self, content: str) -> List[Dict[str, str]]:
        """Extract risk analysis information."""
        risks = []
        section_content = self._extract_section(content, "Risks", "Risk Analysis")
        
        lines = section_content.split("\n")
        for line in lines:
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                risk_text = line.strip()[2:]
                risks.append({
                    "risk": risk_text,
                    "mitigation": ""
                })
        
        return risks
    
    def _extract_design_artifacts(self, content: str) -> List[str]:
        """Extract design artifact references."""
        artifacts = []
        
        # Look for file references and diagrams
        lines = content.split("\n")
        for line in lines:
            if ".md" in line or ".png" in line or ".jpg" in line or "diagram" in line.lower():
                artifacts.append(line.strip())
        
        return artifacts
    
    def _format_requirements(self, requirements: List[Dict[str, str]]) -> str:
        """Format requirements for injection."""
        if not requirements:
            return ""
        
        formatted = []
        for req in requirements:
            formatted.append(f"- {req.get('id', '')}: {req.get('description', '')}")
        
        return "\n".join(formatted)
    
    def _format_stakeholders(self, stakeholders: List[Dict[str, str]]) -> str:
        """Format stakeholders for injection."""
        if not stakeholders:
            return ""
        
        formatted = []
        for stakeholder in stakeholders:
            formatted.append(f"- {stakeholder.get('name', '')}: {stakeholder.get('role', '')}")
        
        return "\n".join(formatted)
    
    def _format_technical_requirements(self, tech_requirements: List[Dict[str, str]]) -> str:
        """Format technical requirements for injection."""
        return self._format_requirements(tech_requirements)
    
    def _format_architecture_decisions(self, decisions: List[Dict[str, str]]) -> str:
        """Format architecture decisions for injection."""
        if not decisions:
            return ""
        
        formatted = []
        for decision in decisions:
            formatted.append(f"- {decision.get('decision', '')}")
            if decision.get('rationale'):
                formatted.append(f"  - Rationale: {decision.get('rationale')}")
        
        return "\n".join(formatted)
    
    def _format_interfaces(self, interfaces: List[Dict[str, str]]) -> str:
        """Format interfaces for injection."""
        if not interfaces:
            return ""
        
        formatted = []
        for interface in interfaces:
            formatted.append(f"- {interface.get('name', '')}")
            if interface.get('description'):
                formatted.append(f"  - {interface.get('description')}")
        
        return "\n".join(formatted)
    
    def _format_milestones(self, milestones: List[Dict[str, str]]) -> str:
        """Format milestones for injection."""
        if not milestones:
            return ""
        
        formatted = []
        for milestone in milestones:
            formatted.append(f"- {milestone.get('name', '')}")
            if milestone.get('date'):
                formatted.append(f"  - Due: {milestone.get('date')}")
        
        return "\n".join(formatted)
    
    def _count_sections(self, content: str) -> int:
        """Count the number of sections in content."""
        return len(re.findall(r"^#{1,6}\s", content, re.MULTILINE))
    
    def _calculate_completeness_score(self, content: str) -> float:
        """Calculate completeness score for specification."""
        required_sections = [
            "technical requirements", "architecture", "interfaces", 
            "validation", "constraints"
        ]
        
        found_sections = 0
        for section in required_sections:
            if self._extract_section(content, section):
                found_sections += 1
        
        return found_sections / len(required_sections)
    
    def _assess_plan_complexity(self, content: str) -> str:
        """Assess plan complexity."""
        word_count = len(content.split())
        
        if word_count < 500:
            return "low"
        elif word_count < 1500:
            return "medium"
        else:
            return "high"
    
    def _extract_number_from_text(self, text: str, context: str) -> Optional[int]:
        """Extract numeric value from text based on context."""
        pattern = rf"{context}.*?(\d+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _extract_timeline(self, text: str) -> Optional[str]:
        """Extract timeline information from text."""
        timeline_patterns = [
            r"(\d+\s*weeks?)",
            r"(\d+\s*months?)",
            r"(\d+\s*days?)"
        ]
        
        for pattern in timeline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()