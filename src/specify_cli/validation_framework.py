"""
Validation Framework for Enhanced Workflow Enforcement - Core Validators.

This module provides core validation capabilities for the workflow
enforcement system, including specification and plan validation.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Validation levels for different types of checks."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    level: ValidationLevel
    category: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Results of a validation operation."""
    valid: bool
    score: float  # 0.0 to 1.0
    issues: List[ValidationIssue]
    summary: str
    details: Dict[str, Any]


class SpecificationValidator:
    """
    Validates specification documents for completeness and quality.
    """
    
    def __init__(self):
        """Initialize the specification validator."""
        self.required_sections = [
            "overview", "requirements", "architecture", "technical details", 
            "interfaces", "validation", "constraints"
        ]
        
        self.recommended_sections = [
            "assumptions", "dependencies", "risks", "alternatives", "examples"
        ]
    
    def validate_specification(self, spec_content: str) -> ValidationResult:
        """
        Validate a specification document.
        
        Args:
            spec_content: Content of the specification document.
            
        Returns:
            Validation result.
        """
        issues = []
        details = {}
        
        # Section presence validation
        section_issues, section_score = self._validate_sections(spec_content)
        issues.extend(section_issues)
        details["section_score"] = section_score
        
        # Content quality validation
        quality_issues, quality_score = self._validate_content_quality(spec_content)
        issues.extend(quality_issues)
        details["quality_score"] = quality_score
        
        # Clarity validation
        clarity_issues, clarity_score = self._validate_clarity(spec_content)
        issues.extend(clarity_issues)
        details["clarity_score"] = clarity_score
        
        # Calculate overall score
        overall_score = (section_score + quality_score + clarity_score) / 3.0
        
        # Determine validity
        valid = overall_score >= 0.7 and not any(issue.level == ValidationLevel.ERROR for issue in issues)
        
        # Generate summary
        summary = self._generate_spec_summary(valid, overall_score, issues)
        
        return ValidationResult(
            valid=valid,
            score=overall_score,
            issues=issues,
            summary=summary,
            details=details
        )
    
    def _validate_sections(self, content: str) -> Tuple[List[ValidationIssue], float]:
        """Validate presence of required and recommended sections."""
        issues = []
        found_sections = self._extract_sections(content)
        
        # Check required sections
        missing_required = []
        for section in self.required_sections:
            if not self._section_exists(section, found_sections):
                missing_required.append(section)
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="structure",
                    message=f"Missing required section: {section}",
                    suggestion=f"Add a '{section}' section to the specification"
                ))
        
        # Check recommended sections
        missing_recommended = []
        for section in self.recommended_sections:
            if not self._section_exists(section, found_sections):
                missing_recommended.append(section)
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="structure",
                    message=f"Missing recommended section: {section}",
                    suggestion=f"Consider adding a '{section}' section"
                ))
        
        # Calculate score
        required_score = (len(self.required_sections) - len(missing_required)) / len(self.required_sections)
        recommended_score = (len(self.recommended_sections) - len(missing_recommended)) / len(self.recommended_sections)
        
        section_score = (required_score * 0.8) + (recommended_score * 0.2)
        
        return issues, section_score
    
    def _validate_content_quality(self, content: str) -> Tuple[List[ValidationIssue], float]:
        """Validate content quality metrics."""
        issues = []
        
        # Check for clarification markers
        clarification_count = len(re.findall(r'\\[NEEDS CLARIFICATION[:\\]]', content, re.IGNORECASE))
        if clarification_count > 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="completeness",
                message=f"Found {clarification_count} unresolved clarification markers",
                suggestion="Resolve all [NEEDS CLARIFICATION] items before proceeding"
            ))
        
        # Check content length
        word_count = len(content.split())
        if word_count < 500:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="completeness",
                message=f"Specification is quite short ({word_count} words)",
                suggestion="Consider adding more detail to ensure completeness"
            ))
        
        # Check for technical details
        tech_indicators = ["api", "interface", "protocol", "algorithm", "data", "format"]
        tech_score = sum(1 for indicator in tech_indicators if indicator in content.lower()) / len(tech_indicators)
        if tech_score < 0.3:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="technical_depth",
                message="Limited technical detail detected",
                suggestion="Include more technical specifications and implementation details"
            ))
        
        # Calculate quality score
        clarification_penalty = min(clarification_count * 0.1, 0.3)
        length_bonus = min(word_count / 1000, 0.2)
        
        quality_score = max(0.0, min(1.0, 0.7 + tech_score * 0.3 + length_bonus - clarification_penalty))
        
        return issues, quality_score
    
    def _validate_clarity(self, content: str) -> Tuple[List[ValidationIssue], float]:
        """Validate clarity and readability."""
        issues = []
        
        # Check for overly long sentences
        sentence_lengths = [len(s.split()) for s in re.split(r'[.!?]', content) if s.strip()]
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            long_sentences = sum(1 for length in sentence_lengths if length > 25)
            
            if avg_length > 20:
                issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    category="clarity",
                    message=f"Average sentence length is {avg_length:.1f} words",
                    suggestion="Consider breaking down long sentences for better readability"
                ))
            
            if long_sentences > len(sentence_lengths) * 0.2:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="clarity", 
                    message=f"{long_sentences} very long sentences detected",
                    suggestion="Break down complex sentences for clarity"
                ))
        
        # Calculate clarity score
        clarity_penalties = len([i for i in issues if i.category == "clarity"]) * 0.1
        clarity_score = max(0.0, 1.0 - clarity_penalties)
        
        return issues, clarity_score
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from content."""
        sections = re.findall(r'^#{1,6}\\s+(.+)$', content, re.MULTILINE)
        return [section.lower().strip() for section in sections]
    
    def _section_exists(self, target_section: str, found_sections: List[str]) -> bool:
        """Check if a target section exists in found sections."""
        target_words = set(target_section.lower().split())
        for section in found_sections:
            section_words = set(section.split())
            if target_words.issubset(section_words) or len(target_words.intersection(section_words)) >= len(target_words) / 2:
                return True
        return False
    
    def _generate_spec_summary(self, valid: bool, score: float, issues: List[ValidationIssue]) -> str:
        """Generate validation summary."""
        if valid:
            summary = f"✅ Specification validation passed (score: {score:.2f})"
        else:
            summary = f"❌ Specification validation failed (score: {score:.2f})"
        
        error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in issues if i.level == ValidationLevel.WARNING])
        
        if error_count > 0:
            summary += f" - {error_count} errors"
        if warning_count > 0:
            summary += f" - {warning_count} warnings"
        
        return summary


class PlanValidator:
    """
    Validates implementation plan documents for completeness and feasibility.
    """
    
    def __init__(self):
        """Initialize the plan validator."""
        self.required_elements = [
            "implementation_strategy", "technology_stack", "architecture",
            "milestones", "dependencies", "resources"
        ]
        
        self.recommended_elements = [
            "risk_analysis", "testing_strategy", "deployment_plan",
            "monitoring", "documentation"
        ]
    
    def validate_plan(self, plan_content: str) -> ValidationResult:
        """
        Validate an implementation plan document.
        
        Args:
            plan_content: Content of the plan document.
            
        Returns:
            Validation result.
        """
        issues = []
        details = {}
        
        # Element presence validation
        element_issues, element_score = self._validate_elements(plan_content)
        issues.extend(element_issues)
        details["element_score"] = element_score
        
        # Feasibility validation
        feasibility_issues, feasibility_score = self._validate_feasibility(plan_content)
        issues.extend(feasibility_issues)
        details["feasibility_score"] = feasibility_score
        
        # Detail level validation
        detail_issues, detail_score = self._validate_detail_level(plan_content)
        issues.extend(detail_issues)
        details["detail_score"] = detail_score
        
        # Calculate overall score
        overall_score = (element_score + feasibility_score + detail_score) / 3.0
        
        # Determine validity
        valid = overall_score >= 0.7 and not any(issue.level == ValidationLevel.ERROR for issue in issues)
        
        # Generate summary
        summary = self._generate_plan_summary(valid, overall_score, issues)
        
        return ValidationResult(
            valid=valid,
            score=overall_score,
            issues=issues,
            summary=summary,
            details=details
        )
    
    def _validate_elements(self, content: str) -> Tuple[List[ValidationIssue], float]:
        """Validate presence of required plan elements."""
        issues = []
        content_lower = content.lower()
        
        # Check required elements
        missing_required = []
        for element in self.required_elements:
            element_keywords = element.replace("_", " ").split()
            if not any(keyword in content_lower for keyword in element_keywords):
                missing_required.append(element)
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    category="structure",
                    message=f"Missing required element: {element.replace('_', ' ')}",
                    suggestion=f"Add {element.replace('_', ' ')} to the implementation plan"
                ))
        
        # Check recommended elements
        missing_recommended = []
        for element in self.recommended_elements:
            element_keywords = element.replace("_", " ").split()
            if not any(keyword in content_lower for keyword in element_keywords):
                missing_recommended.append(element)
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="structure",
                    message=f"Missing recommended element: {element.replace('_', ' ')}",
                    suggestion=f"Consider adding {element.replace('_', ' ')} to the plan"
                ))
        
        # Calculate score
        required_score = (len(self.required_elements) - len(missing_required)) / len(self.required_elements)
        recommended_score = (len(self.recommended_elements) - len(missing_recommended)) / len(self.recommended_elements)
        
        element_score = (required_score * 0.8) + (recommended_score * 0.2)
        
        return issues, element_score
    
    def _validate_feasibility(self, content: str) -> Tuple[List[ValidationIssue], float]:
        """Validate plan feasibility."""
        issues = []
        
        # Check for timeline information
        timeline_patterns = [r'\\d+\\s*(days?|weeks?|months?)', r'deadline', r'milestone', r'schedule']
        timeline_mentions = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in timeline_patterns)
        
        if timeline_mentions == 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="feasibility",
                message="No timeline information found",
                suggestion="Include estimated timelines and milestones"
            ))
        
        # Check for resource allocation
        resource_patterns = [r'team', r'developer', r'engineer', r'resource', r'capacity']
        resource_mentions = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in resource_patterns)
        
        if resource_mentions == 0:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="feasibility",
                message="No resource allocation mentioned",
                suggestion="Specify team size and resource requirements"
            ))
        
        # Calculate feasibility score
        feasibility_score = min(1.0, (timeline_mentions * 0.5 + resource_mentions * 0.5) / 10.0)
        
        return issues, feasibility_score
    
    def _validate_detail_level(self, content: str) -> Tuple[List[ValidationIssue], float]:
        """Validate level of detail in the plan."""
        issues = []
        
        word_count = len(content.split())
        if word_count < 800:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="detail",
                message=f"Implementation plan is quite brief ({word_count} words)",
                suggestion="Consider adding more implementation details"
            ))
        
        # Check for specific implementation details
        detail_indicators = ["implement", "create", "develop", "build", "configure", "setup", "deploy"]
        detail_count = sum(len(re.findall(f'\\b{indicator}\\b', content, re.IGNORECASE)) for indicator in detail_indicators)
        
        if detail_count < 5:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="detail",
                message="Limited implementation details",
                suggestion="Include more specific implementation steps and actions"
            ))
        
        # Calculate detail score
        length_factor = min(word_count / 1500, 1.0)
        detail_factor = min(detail_count / 20, 1.0)
        
        detail_score = (length_factor + detail_factor) / 2.0
        
        return issues, detail_score
    
    def _generate_plan_summary(self, valid: bool, score: float, issues: List[ValidationIssue]) -> str:
        """Generate plan validation summary."""
        if valid:
            summary = f"✅ Implementation plan validation passed (score: {score:.2f})"
        else:
            summary = f"❌ Implementation plan validation failed (score: {score:.2f})"
        
        error_count = len([i for i in issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in issues if i.level == ValidationLevel.WARNING])
        
        if error_count > 0:
            summary += f" - {error_count} errors"
        if warning_count > 0:
            summary += f" - {warning_count} warnings"
        
        return summary


def validate_specification_file(file_path: str) -> ValidationResult:
    """
    Convenience function to validate a specification file.
    
    Args:
        file_path: Path to the specification file.
        
    Returns:
        Validation result.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validator = SpecificationValidator()
        return validator.validate_specification(content)
    
    except FileNotFoundError:
        return ValidationResult(
            valid=False,
            score=0.0,
            issues=[ValidationIssue(
                level=ValidationLevel.ERROR,
                category="file_access",
                message=f"Specification file not found: {file_path}",
                suggestion="Ensure the specification file exists"
            )],
            summary="❌ Specification file not found",
            details={}
        )
    except Exception as e:
        return ValidationResult(
            valid=False,
            score=0.0,
            issues=[ValidationIssue(
                level=ValidationLevel.ERROR,
                category="file_access",
                message=f"Error reading specification file: {e}",
                suggestion="Check file permissions and format"
            )],
            summary="❌ Error reading specification file",
            details={}
        )


def validate_plan_file(file_path: str) -> ValidationResult:
    """
    Convenience function to validate a plan file.
    
    Args:
        file_path: Path to the plan file.
        
    Returns:
        Validation result.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validator = PlanValidator()
        return validator.validate_plan(content)
    
    except FileNotFoundError:
        return ValidationResult(
            valid=False,
            score=0.0,
            issues=[ValidationIssue(
                level=ValidationLevel.ERROR,
                category="file_access",
                message=f"Plan file not found: {file_path}",
                suggestion="Ensure the plan file exists"
            )],
            summary="❌ Plan file not found",
            details={}
        )
    except Exception as e:
        return ValidationResult(
            valid=False,
            score=0.0,
            issues=[ValidationIssue(
                level=ValidationLevel.ERROR,
                category="file_access",
                message=f"Error reading plan file: {e}",
                suggestion="Check file permissions and format"
            )],
            summary="❌ Error reading plan file",
            details={}
        )


if __name__ == "__main__":
    # Command-line interface for validation
    import argparse
    
    parser = argparse.ArgumentParser(description="Workflow validation utility")
    parser.add_argument("file_type", choices=["spec", "plan"], 
                       help="Type of file to validate")
    parser.add_argument("file_path", help="Path to the file to validate")
    
    args = parser.parse_args()
    
    if args.file_type == "spec":
        result = validate_specification_file(args.file_path)
    else:
        result = validate_plan_file(args.file_path)
    
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