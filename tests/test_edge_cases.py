"""
Edge case tests for Enhanced Workflow Enforcement.

This module tests edge cases, error conditions, and recovery scenarios
including corrupted state files, invalid transitions, and system failures.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import test modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from specify_cli.workflow_state import (
    WorkflowStateManager, 
    WorkflowPhase, 
    PhasePrerequisiteError,
    StateValidationError,
    WorkflowStateError
)
from specify_cli.context_transfer import ContextTransferManager
from specify_cli.command_integration import WorkflowCommandIntegrator
from specify_cli.validation_framework import ValidationLevel, ValidationIssue, ValidationResult


class TestCorruptedStateFiles:
    """Test handling of corrupted and invalid state files."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def state_manager(self, temp_workspace):
        """Create a WorkflowStateManager instance for testing."""
        return WorkflowStateManager(temp_workspace)
    
    def test_corrupted_json_state_file(self, state_manager):
        """Test handling of corrupted JSON in state file."""
        # Create a valid state first
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        
        # Corrupt the JSON
        with open(state_manager.state_file, 'w') as f:
            f.write('{"invalid": "json", "missing_bracket":')
        
        # Should handle corruption gracefully
        with pytest.raises(StateValidationError):
            state_manager._get_current_state()
    
    def test_missing_state_file_fields(self, state_manager):
        """Test handling of state files missing required fields."""
        # Create an incomplete state file
        incomplete_state = {"someField": "value"}
        
        with open(state_manager.state_file, 'w') as f:
            json.dump(incomplete_state, f)
        
        # Should create initial state when fields are missing
        state = state_manager._get_current_state()
        assert "completedPhases" in state
        assert "currentPhase" in state
    
    def test_invalid_phase_values_in_state(self, state_manager):
        """Test handling of invalid phase values in state file."""
        # Create state with invalid phase values
        invalid_state = {
            "currentPhase": "invalid_phase",
            "completedPhases": ["product", "invalid_phase", "specify"],
            "lastUpdated": "2024-01-01T00:00:00.000Z",
            "phaseData": {}
        }
        
        with open(state_manager.state_file, 'w') as f:
            json.dump(invalid_state, f)
        
        # Should handle invalid phases gracefully
        completed = state_manager.get_completed_phases()
        # Should only return valid phases
        assert WorkflowPhase.PRODUCT in completed
        assert WorkflowPhase.SPECIFY in completed
        assert len(completed) == 2  # Invalid phase should be filtered out
    
    def test_state_file_permission_errors(self, state_manager, temp_workspace):
        """Test handling of file permission errors."""
        # Create initial state
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        
        # Mock file permission error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(StateValidationError):
                state_manager._save_state({"test": "data"})
    
    def test_corrupted_phase_markers(self, state_manager):
        """Test handling of corrupted or missing phase markers."""
        # Complete a phase normally
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        state_manager.complete_phase(WorkflowPhase.PRODUCT)
        
        # Remove the phase marker file
        marker_file = state_manager.phase_markers_dir / "product.complete"
        if marker_file.exists():
            marker_file.unlink()
        
        # State should still show phase as completed (relies on state file)
        completed = state_manager.get_completed_phases()
        assert WorkflowPhase.PRODUCT in completed
        
        # But marker check should return False
        assert not state_manager._phase_is_complete(WorkflowPhase.PRODUCT)
    
    def test_directory_permission_errors(self, temp_workspace):
        """Test handling of directory creation permission errors."""
        # Mock permission error on directory creation
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            # Should raise appropriate error
            with pytest.raises(Exception):  # Could be various exceptions depending on implementation
                WorkflowStateManager(temp_workspace)
    
    def test_large_state_file_handling(self, state_manager):
        """Test handling of unusually large state files."""
        # Create a very large state file (simulate corruption or attack)
        large_data = {"huge_field": "x" * 1000000}  # 1MB of data
        
        with open(state_manager.state_file, 'w') as f:
            json.dump(large_data, f)
        
        # Should handle large files (though may be slow)
        try:
            state = state_manager._get_current_state()
            # Should create new initial state if current is invalid
            assert "completedPhases" in state
        except StateValidationError:
            # This is also acceptable - failing fast on invalid state
            pass
    
    def test_concurrent_state_file_access(self, temp_workspace):
        """Test handling of concurrent access to state files."""
        # Create multiple managers
        manager1 = WorkflowStateManager(temp_workspace)
        manager2 = WorkflowStateManager(temp_workspace)
        
        # Both try to start the same phase
        manager1.start_phase(WorkflowPhase.PRODUCT)
        
        # Second manager should see consistent state
        current_phase = manager2.get_current_phase()
        # Note: This test depends on how quickly state is persisted
        # In a real system, you might use file locking
        
        # Complete phase with first manager
        manager1.complete_phase(WorkflowPhase.PRODUCT)
        
        # Second manager should eventually see completion
        # (after creating new instance to reload state)
        manager3 = WorkflowStateManager(temp_workspace)
        completed = manager3.get_completed_phases()
        assert WorkflowPhase.PRODUCT in completed


class TestInvalidTransitions:
    """Test handling of invalid workflow transitions and edge cases."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def state_manager(self, temp_workspace):
        """Create a WorkflowStateManager instance for testing."""
        return WorkflowStateManager(temp_workspace)
    
    def test_invalid_phase_skipping_attempts(self, state_manager):
        """Test various invalid phase skipping attempts."""
        # Try to start with specify (should fail)
        with pytest.raises(PhasePrerequisiteError) as exc_info:
            state_manager.start_phase(WorkflowPhase.SPECIFY)
        assert "product" in str(exc_info.value).lower()
        
        # Try to start with plan (should fail)
        with pytest.raises(PhasePrerequisiteError):
            state_manager.start_phase(WorkflowPhase.PLAN)
        
        # Try to start with tasks (should fail)
        with pytest.raises(PhasePrerequisiteError):
            state_manager.start_phase(WorkflowPhase.TASKS)
    
    def test_completing_non_started_phase(self, state_manager):
        """Test completing a phase that was never started."""
        # Try to complete product phase without starting it
        # This should work (implementation choice - allows recovery)
        state_manager.complete_phase(WorkflowPhase.PRODUCT, "test content")
        
        # Verify it's marked as completed
        completed = state_manager.get_completed_phases()
        assert WorkflowPhase.PRODUCT in completed
    
    def test_multiple_phase_completions(self, state_manager):
        """Test completing the same phase multiple times."""
        # Complete product phase
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        state_manager.complete_phase(WorkflowPhase.PRODUCT, "first completion")
        
        # Complete it again
        state_manager.complete_phase(WorkflowPhase.PRODUCT, "second completion")
        
        # Should still only appear once in completed phases
        completed = state_manager.get_completed_phases()
        assert completed.count(WorkflowPhase.PRODUCT) == 1
    
    def test_resetting_non_completed_phase(self, state_manager):
        """Test resetting a phase that was never completed."""
        # Try to reset specify phase without completing it
        state_manager.reset_phase(WorkflowPhase.SPECIFY)
        
        # Should not cause errors
        completed = state_manager.get_completed_phases()
        assert WorkflowPhase.SPECIFY not in completed
    
    def test_invalid_phase_validation_calls(self, state_manager):
        """Test validation with invalid parameters."""
        # This tests the enum validation - should raise ValueError for invalid strings
        with pytest.raises(ValueError):
            WorkflowPhase("invalid_phase")
    
    def test_backward_phase_transitions(self, state_manager):
        """Test attempts to go backward in the workflow."""
        # Complete all phases
        for phase in WorkflowPhase:
            state_manager.start_phase(phase)
            state_manager.complete_phase(phase)
        
        # Try to start an earlier phase again
        # This should be allowed (for recovery/iteration)
        state_manager.start_phase(WorkflowPhase.SPECIFY)
        
        # Current phase should be updated
        current = state_manager.get_current_phase()
        assert current == WorkflowPhase.SPECIFY
    
    def test_context_integrity_with_invalid_content(self, state_manager):
        """Test context integrity checking with invalid content."""
        # Complete phase with content
        original_content = "original content"
        state_manager.complete_phase(WorkflowPhase.PRODUCT, original_content)
        
        # Check integrity with different content
        different_content = "different content"
        integrity_valid = state_manager.validate_context_integrity(different_content)
        assert integrity_valid is False
        
        # Check integrity with original content
        integrity_valid = state_manager.validate_context_integrity(original_content)
        assert integrity_valid is True


class TestSystemFailureScenarios:
    """Test handling of various system failure scenarios."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_disk_space_exhaustion(self, temp_workspace):
        """Test handling of disk space exhaustion."""
        state_manager = WorkflowStateManager(temp_workspace)
        
        # Mock disk space error
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            with pytest.raises(StateValidationError):
                state_manager.start_phase(WorkflowPhase.PRODUCT)
    
    def test_network_drive_disconnection(self, temp_workspace):
        """Test handling of network drive disconnection."""
        state_manager = WorkflowStateManager(temp_workspace)
        
        # Start normally
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        
        # Simulate network disconnection
        with patch('pathlib.Path.exists', return_value=False):
            # Should handle missing files gracefully
            try:
                state = state_manager._get_current_state()
                # Should create new initial state
                assert "completedPhases" in state
            except StateValidationError:
                # Also acceptable - failing fast when workspace is unavailable
                pass
    
    def test_python_environment_issues(self, temp_workspace):
        """Test handling of Python environment issues."""
        # Test JSON module failure
        with patch('json.load', side_effect=ImportError("No module named json")):
            with pytest.raises(StateValidationError):
                state_manager = WorkflowStateManager(temp_workspace)
                state_manager._get_current_state()
    
    def test_git_command_failures(self, temp_workspace):
        """Test handling of git command failures."""
        context_manager = ContextTransferManager(temp_workspace)
        
        # Mock git command failure
        with patch('subprocess.run', side_effect=FileNotFoundError("git command not found")):
            # Should handle git absence gracefully
            feature_name = context_manager.state_manager._get_feature_name()
            # Should return fallback value
            assert feature_name is not None
    
    def test_memory_constraints(self, temp_workspace):
        """Test handling of memory constraints."""
        state_manager = WorkflowStateManager(temp_workspace)
        
        # Mock memory error
        with patch('json.dump', side_effect=MemoryError("Out of memory")):
            with pytest.raises(StateValidationError):
                state_manager._save_state({"test": "data"})
    
    def test_unicode_handling_errors(self, temp_workspace):
        """Test handling of unicode and encoding errors."""
        state_manager = WorkflowStateManager(temp_workspace)
        
        # Complete phase with unicode content
        unicode_content = "Test with unicode: 你好世界 🌍 café"
        state_manager.complete_phase(WorkflowPhase.PRODUCT, unicode_content)
        
        # Should handle unicode content properly
        completed = state_manager.get_completed_phases()
        assert WorkflowPhase.PRODUCT in completed


class TestRecoveryScenarios:
    """Test recovery scenarios from various failure states."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_recovery_from_partial_state(self, temp_workspace):
        """Test recovery from partially corrupted state."""
        # Create a state manager and complete some phases
        manager1 = WorkflowStateManager(temp_workspace)
        manager1.start_phase(WorkflowPhase.PRODUCT)
        manager1.complete_phase(WorkflowPhase.PRODUCT)
        
        # Partially corrupt the state file
        state_file = manager1.state_file
        with open(state_file, 'r') as f:
            state_data = json.load(f)
        
        # Remove some fields but keep others
        del state_data["currentPhase"]
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f)
        
        # Create new manager - should recover gracefully
        manager2 = WorkflowStateManager(temp_workspace)
        completed = manager2.get_completed_phases()
        
        # Should still have completed phases
        assert WorkflowPhase.PRODUCT in completed
    
    def test_recovery_after_system_restart(self, temp_workspace):
        """Test recovery after simulated system restart."""
        # Simulate work session 1
        manager1 = WorkflowStateManager(temp_workspace)
        manager1.start_phase(WorkflowPhase.PRODUCT)
        manager1.complete_phase(WorkflowPhase.PRODUCT)
        manager1.start_phase(WorkflowPhase.SPECIFY)
        # Don't complete specify - simulate interruption
        
        # Simulate system restart (new manager instance)
        manager2 = WorkflowStateManager(temp_workspace)
        
        # Should recover to same state
        completed = manager2.get_completed_phases()
        current = manager2.get_current_phase()
        
        assert WorkflowPhase.PRODUCT in completed
        assert current == WorkflowPhase.SPECIFY
        
        # Should be able to continue from where left off
        manager2.complete_phase(WorkflowPhase.SPECIFY)
        assert WorkflowPhase.SPECIFY in manager2.get_completed_phases()
    
    def test_recovery_from_missing_directories(self, temp_workspace):
        """Test recovery from missing workspace directories."""
        # Create manager and complete a phase
        manager1 = WorkflowStateManager(temp_workspace)
        manager1.start_phase(WorkflowPhase.PRODUCT)
        manager1.complete_phase(WorkflowPhase.PRODUCT)
        
        # Remove the .spec-kit directory
        shutil.rmtree(manager1.spec_kit_dir)
        
        # Create new manager - should recreate directories
        manager2 = WorkflowStateManager(temp_workspace)
        
        # Directories should be recreated
        assert manager2.spec_kit_dir.exists()
        assert manager2.phase_markers_dir.exists()
        
        # Should start with clean state
        completed = manager2.get_completed_phases()
        assert len(completed) == 0
    
    def test_recovery_from_backup_state(self, temp_workspace):
        """Test recovery from backup state information."""
        # Create manager and complete phases
        manager1 = WorkflowStateManager(temp_workspace)
        
        for phase in [WorkflowPhase.PRODUCT, WorkflowPhase.SPECIFY]:
            manager1.start_phase(phase)
            manager1.complete_phase(phase)
        
        # Create backup of state file
        state_backup = manager1.state_file.read_text()
        
        # Corrupt the main state file
        manager1.state_file.write_text("corrupted data")
        
        # Simulate recovery process - restore from backup
        manager1.state_file.write_text(state_backup)
        
        # Create new manager - should recover successfully
        manager2 = WorkflowStateManager(temp_workspace)
        completed = manager2.get_completed_phases()
        
        assert WorkflowPhase.PRODUCT in completed
        assert WorkflowPhase.SPECIFY in completed
    
    def test_graceful_degradation_without_enforcement(self, temp_workspace):
        """Test graceful degradation when enforcement features fail."""
        # Test with mocked failures
        with patch.object(WorkflowStateManager, '_ensure_directories', side_effect=Exception("Directory creation failed")):
            # Should fail to create manager
            with pytest.raises(Exception):
                WorkflowStateManager(temp_workspace)
        
        # Test fallback behavior for command integration
        integrator = WorkflowCommandIntegrator(temp_workspace)
        
        # Mock state manager failure
        with patch.object(integrator.state_manager, 'validate_phase_prerequisites', side_effect=Exception("State validation failed")):
            # Should handle gracefully
            success, error = integrator.validate_command_prerequisites("test", WorkflowPhase.PRODUCT)
            assert success is False
            assert "validation failed" in error.lower()


class TestValidationEdgeCases:
    """Test edge cases in validation framework."""
    
    def test_validation_with_empty_content(self):
        """Test validation with empty or minimal content."""
        from specify_cli.validation_framework import SpecificationValidator, PlanValidator
        
        spec_validator = SpecificationValidator()
        plan_validator = PlanValidator()
        
        # Test with empty content
        empty_result = spec_validator.validate_specification("")
        assert empty_result.valid is False
        assert empty_result.score < 0.5
        
        empty_plan_result = plan_validator.validate_plan("")
        assert empty_plan_result.valid is False
        assert empty_plan_result.score < 0.5
    
    def test_validation_with_malformed_content(self):
        """Test validation with malformed or unusual content."""
        from specify_cli.validation_framework import SpecificationValidator
        
        validator = SpecificationValidator()
        
        # Test with very long lines
        long_content = "# Overview\n" + "A" * 10000 + "\n# Requirements\nTest requirement"
        result = validator.validate_specification(long_content)
        
        # Should handle long content (though may have clarity issues)
        assert result.score >= 0
        
        # Test with only special characters
        special_content = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        result = validator.validate_specification(special_content)
        assert result.valid is False
    
    def test_traceability_with_missing_phases(self, temp_workspace):
        """Test traceability validation with missing phase data."""
        from specify_cli.traceability_verification import TraceabilityValidator
        
        validator = TraceabilityValidator(temp_workspace)
        
        # Test with no completed phases
        result = validator.validate_full_traceability()
        assert result.valid is True  # Should handle gracefully
        assert "Insufficient phases" in result.summary
    
    def test_context_transfer_with_invalid_templates(self, temp_workspace):
        """Test context transfer with invalid or missing templates."""
        context_manager = ContextTransferManager(temp_workspace)
        
        # Test with non-existent template
        with pytest.raises(FileNotFoundError):
            context_manager.inject_product_context_into_spec(
                Mock(), 
                "non_existent_template.md"
            )


if __name__ == "__main__":
    # Run the edge case tests
    pytest.main([__file__, "-v"])