"""
Workflow State Management for Enhanced Workflow Enforcement.

This module implements the core state management infrastructure for enforcing
the product → specify → plan → tasks workflow sequence in spec-kit.
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class WorkflowPhase(Enum):
    """Enumeration of workflow phases."""
    PRODUCT = "product"
    SPECIFY = "specify" 
    PLAN = "plan"
    TASKS = "tasks"


class WorkflowStateError(Exception):
    """Base exception for workflow state errors."""
    pass


class PhasePrerequisiteError(WorkflowStateError):
    """Exception raised when phase prerequisites are not met."""
    pass


class StateValidationError(WorkflowStateError):
    """Exception raised when state validation fails."""
    pass


class WorkflowStateManager:
    """
    Manages workflow state persistence and validation for the enhanced workflow enforcement.
    
    This class tracks phase completion, validates prerequisites, and ensures context
    integrity across the product → specify → plan → tasks workflow sequence.
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize the workflow state manager.
        
        Args:
            workspace_path: Path to the workspace root. If None, uses current directory.
        """
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.spec_kit_dir = self.workspace_path / ".spec-kit"
        self.state_file = self.spec_kit_dir / "workflow-state.json"
        self.phase_markers_dir = self.spec_kit_dir / "phase-markers"
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.spec_kit_dir.mkdir(exist_ok=True)
        self.phase_markers_dir.mkdir(exist_ok=True)
    
    def _get_current_state(self) -> Dict[str, Any]:
        """
        Load current workflow state from file.
        
        Returns:
            Current workflow state as dictionary.
        """
        if not self.state_file.exists():
            return self._create_initial_state()
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise StateValidationError(f"Failed to load workflow state: {e}")
    
    def _create_initial_state(self) -> Dict[str, Any]:
        """
        Create initial workflow state.
        
        Returns:
            Initial state dictionary.
        """
        return {
            "currentPhase": None,
            "completedPhases": [],
            "featureName": self._get_feature_name(),
            "lastUpdated": datetime.now().isoformat(),
            "contextHash": None,
            "phaseData": {}
        }
    
    def _get_feature_name(self) -> Optional[str]:
        """
        Extract feature name from current git branch or directory context.
        
        Returns:
            Feature name if determinable, None otherwise.
        """
        try:
            import subprocess
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.workspace_path
            )
            if result.returncode == 0:
                branch_name = result.stdout.strip()
                # Extract feature name from branch naming convention (e.g., "001-feature-name")
                if "-" in branch_name:
                    return branch_name.split("-", 1)[1]
                return branch_name
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return None
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """
        Save workflow state to file.
        
        Args:
            state: State dictionary to save.
        """
        state["lastUpdated"] = datetime.now().isoformat()
        
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            raise StateValidationError(f"Failed to save workflow state: {e}")
    
    def _create_phase_marker(self, phase: WorkflowPhase) -> None:
        """
        Create a phase completion marker file.
        
        Args:
            phase: The completed phase.
        """
        marker_file = self.phase_markers_dir / f"{phase.value}.complete"
        marker_file.touch()
    
    def _remove_phase_marker(self, phase: WorkflowPhase) -> None:
        """
        Remove a phase completion marker file.
        
        Args:
            phase: The phase to mark as incomplete.
        """
        marker_file = self.phase_markers_dir / f"{phase.value}.complete"
        if marker_file.exists():
            marker_file.unlink()
    
    def _phase_is_complete(self, phase: WorkflowPhase) -> bool:
        """
        Check if a phase is marked as complete.
        
        Args:
            phase: The phase to check.
            
        Returns:
            True if phase is complete, False otherwise.
        """
        marker_file = self.phase_markers_dir / f"{phase.value}.complete"
        return marker_file.exists()
    
    def _calculate_context_hash(self, content: str) -> str:
        """
        Calculate SHA256 hash of content for integrity checking.
        
        Args:
            content: Content to hash.
            
        Returns:
            SHA256 hash as hexadecimal string.
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_current_phase(self) -> Optional[WorkflowPhase]:
        """
        Get the current active workflow phase.
        
        Returns:
            Current phase or None if no phase is active.
        """
        state = self._get_current_state()
        current_phase = state.get("currentPhase")
        if current_phase:
            return WorkflowPhase(current_phase)
        return None
    
    def get_completed_phases(self) -> List[WorkflowPhase]:
        """
        Get list of completed workflow phases.
        
        Returns:
            List of completed phases.
        """
        state = self._get_current_state()
        completed = state.get("completedPhases", [])
        return [WorkflowPhase(phase) for phase in completed]
    
    def validate_phase_prerequisites(self, target_phase: WorkflowPhase) -> None:
        """
        Validate that prerequisites for target phase are met.
        
        Args:
            target_phase: The phase to validate prerequisites for.
            
        Raises:
            PhasePrerequisiteError: If prerequisites are not met.
        """
        completed_phases = self.get_completed_phases()
        
        # Define phase sequence and prerequisites
        phase_sequence = [
            WorkflowPhase.PRODUCT,
            WorkflowPhase.SPECIFY,
            WorkflowPhase.PLAN,
            WorkflowPhase.TASKS
        ]
        
        target_index = phase_sequence.index(target_phase)
        
        # Check that all previous phases are completed
        for i in range(target_index):
            required_phase = phase_sequence[i]
            if required_phase not in completed_phases:
                raise PhasePrerequisiteError(
                    f"Cannot proceed to {target_phase.value} phase. "
                    f"Required prerequisite phase '{required_phase.value}' is not completed. "
                    f"Please complete the {required_phase.value} phase first."
                )
    
    def start_phase(self, phase: WorkflowPhase) -> None:
        """
        Start a new workflow phase after validating prerequisites.
        
        Args:
            phase: The phase to start.
            
        Raises:
            PhasePrerequisiteError: If prerequisites are not met.
        """
        # Validate prerequisites (except for product phase which is the starting point)
        if phase != WorkflowPhase.PRODUCT:
            self.validate_phase_prerequisites(phase)
        
        state = self._get_current_state()
        state["currentPhase"] = phase.value
        self._save_state(state)
    
    def complete_phase(self, phase: WorkflowPhase, context_content: Optional[str] = None) -> None:
        """
        Mark a phase as completed and update state.
        
        Args:
            phase: The phase to mark as completed.
            context_content: Content for context integrity checking.
        """
        state = self._get_current_state()
        
        # Add to completed phases if not already there
        if phase.value not in state.get("completedPhases", []):
            state.setdefault("completedPhases", []).append(phase.value)
        
        # Store context hash if content provided
        if context_content:
            state["contextHash"] = self._calculate_context_hash(context_content)
        
        # Create phase marker
        self._create_phase_marker(phase)
        
        # Clear current phase if it matches the completed phase
        if state.get("currentPhase") == phase.value:
            state["currentPhase"] = None
        
        self._save_state(state)
    
    def reset_phase(self, phase: WorkflowPhase) -> None:
        """
        Reset a phase to incomplete state.
        
        Args:
            phase: The phase to reset.
        """
        state = self._get_current_state()
        
        # Remove from completed phases
        completed = state.get("completedPhases", [])
        if phase.value in completed:
            completed.remove(phase.value)
            state["completedPhases"] = completed
        
        # Remove phase marker
        self._remove_phase_marker(phase)
        
        # Also reset any subsequent phases
        phase_sequence = [
            WorkflowPhase.PRODUCT,
            WorkflowPhase.SPECIFY,
            WorkflowPhase.PLAN,
            WorkflowPhase.TASKS
        ]
        
        reset_index = phase_sequence.index(phase)
        for subsequent_phase in phase_sequence[reset_index + 1:]:
            if subsequent_phase.value in completed:
                completed.remove(subsequent_phase.value)
                self._remove_phase_marker(subsequent_phase)
        
        state["completedPhases"] = completed
        self._save_state(state)
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get comprehensive workflow status information.
        
        Returns:
            Dictionary containing workflow status details.
        """
        state = self._get_current_state()
        completed_phases = self.get_completed_phases()
        current_phase = self.get_current_phase()
        
        return {
            "currentPhase": current_phase.value if current_phase else None,
            "completedPhases": [phase.value for phase in completed_phases],
            "featureName": state.get("featureName"),
            "lastUpdated": state.get("lastUpdated"),
            "nextPhase": self._get_next_phase(),
            "canProceedTo": self._get_available_phases()
        }
    
    def _get_next_phase(self) -> Optional[str]:
        """
        Determine the next available phase based on current progress.
        
        Returns:
            Next phase name or None if workflow is complete.
        """
        completed_phases = self.get_completed_phases()
        
        phase_sequence = [
            WorkflowPhase.PRODUCT,
            WorkflowPhase.SPECIFY,
            WorkflowPhase.PLAN,
            WorkflowPhase.TASKS
        ]
        
        for phase in phase_sequence:
            if phase not in completed_phases:
                return phase.value
        
        return None  # All phases completed
    
    def _get_available_phases(self) -> List[str]:
        """
        Get list of phases that can currently be executed.
        
        Returns:
            List of available phase names.
        """
        completed_phases = self.get_completed_phases()
        available = []
        
        phase_sequence = [
            WorkflowPhase.PRODUCT,
            WorkflowPhase.SPECIFY,
            WorkflowPhase.PLAN,
            WorkflowPhase.TASKS
        ]
        
        for i, phase in enumerate(phase_sequence):
            # Can execute if all previous phases are completed
            prerequisites_met = all(
                prev_phase in completed_phases 
                for prev_phase in phase_sequence[:i]
            )
            
            if prerequisites_met:
                available.append(phase.value)
            else:
                break  # Can't proceed further without prerequisites
        
        return available
    
    def validate_context_integrity(self, current_content: str) -> bool:
        """
        Validate context integrity against stored hash.
        
        Args:
            current_content: Current content to validate.
            
        Returns:
            True if content matches stored hash, False otherwise.
        """
        state = self._get_current_state()
        stored_hash = state.get("contextHash")
        
        if not stored_hash:
            return True  # No stored hash to validate against
        
        current_hash = self._calculate_context_hash(current_content)
        return current_hash == stored_hash
    
    def store_phase_data(self, phase: WorkflowPhase, data: Dict[str, Any]) -> None:
        """
        Store phase-specific data for context transfer.
        
        Args:
            phase: The phase to store data for.
            data: Data to store.
        """
        state = self._get_current_state()
        state.setdefault("phaseData", {})[phase.value] = data
        self._save_state(state)
    
    def get_phase_data(self, phase: WorkflowPhase) -> Optional[Dict[str, Any]]:
        """
        Retrieve phase-specific data.
        
        Args:
            phase: The phase to retrieve data for.
            
        Returns:
            Phase data or None if not found.
        """
        state = self._get_current_state()
        return state.get("phaseData", {}).get(phase.value)
    
    def clear_workflow_state(self) -> None:
        """Clear all workflow state and markers."""
        # Remove state file
        if self.state_file.exists():
            self.state_file.unlink()
        
        # Remove all phase markers
        for phase in WorkflowPhase:
            self._remove_phase_marker(phase)