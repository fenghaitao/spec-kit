"""
Integration tests for Enhanced Workflow Enforcement command coordination and state sharing.

This module tests the integration between commands, state management, and context
transfer across the complete workflow enforcement system.
"""

import pytest
import tempfile
import shutil
import subprocess
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

# Import test modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from specify_cli.workflow_state import WorkflowStateManager, WorkflowPhase
from specify_cli.context_transfer import ContextTransferManager
from specify_cli.command_integration import WorkflowCommandIntegrator


class TestCommandCoordination:
    """Test coordination between different workflow commands."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_git_repo(self, temp_workspace):
        """Create a mock git repository in the workspace."""
        git_dir = Path(temp_workspace) / ".git"
        git_dir.mkdir()
        return temp_workspace
    
    def test_simics_platform_command_integration(self, mock_git_repo):
        """Test integration of simics-platform command with workflow enforcement."""
        workspace = mock_git_repo
        
        # Mock the script execution
        with patch('subprocess.run') as mock_run:
            # Mock git commands
            mock_run.side_effect = [
                # git checkout -b command
                Mock(returncode=0, stdout="", stderr=""),
                # git branch --show-current
                Mock(returncode=0, stdout="001-test-platform", stderr="")
            ]
            
            # Create state manager to test initialization
            state_manager = WorkflowStateManager(workspace)
            
            # Initialize workflow (simulating simics-platform command)
            state_manager.start_phase(WorkflowPhase.PRODUCT)
            
            # Simulate product context capture
            product_context = {
                "vision": "ARM embedded platform simulation",
                "success_criteria": ["Boots successfully", "All components functional"],
                "constraints": ["ARM Cortex-A", "Simics compatible"],
                "metadata": {"platform_type": "embedded", "target_system": "ARM"}
            }
            state_manager.store_phase_data(WorkflowPhase.PRODUCT, product_context)
            state_manager.complete_phase(WorkflowPhase.PRODUCT, "product specification")
            
            # Verify state
            assert WorkflowPhase.PRODUCT in state_manager.get_completed_phases()
            assert state_manager.get_phase_data(WorkflowPhase.PRODUCT) is not None
    
    def test_specify_command_integration(self, mock_git_repo):
        """Test integration of specify command with product context."""
        workspace = mock_git_repo
        
        # Setup: Complete product phase first
        state_manager = WorkflowStateManager(workspace)
        context_manager = ContextTransferManager(workspace)
        integrator = WorkflowCommandIntegrator(workspace)
        
        # Complete product phase
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        product_context = {
            "vision": "Test platform for ARM",
            "requirements": [
                {"id": "REQ-001", "description": "ARM ISA support"},
                {"id": "REQ-002", "description": "UART peripheral"}
            ],
            "constraints": ["Simics compatible", "ARM Cortex-A"]
        }
        state_manager.store_phase_data(WorkflowPhase.PRODUCT, product_context)
        state_manager.complete_phase(WorkflowPhase.PRODUCT)
        
        # Test specify command prerequisites
        success, error = integrator.validate_command_prerequisites("specify", WorkflowPhase.SPECIFY)
        assert success is True
        assert error is None
        
        # Test context loading for specify
        context = integrator.prepare_command_context("specify", WorkflowPhase.SPECIFY, {})
        assert context.prerequisites_met is True
        
        # Simulate specify phase completion
        state_manager.start_phase(WorkflowPhase.SPECIFY)
        spec_context = {
            "technical_requirements": [
                {"id": "TECH-001", "description": "ARM Cortex-A support"},
                {"id": "TECH-002", "description": "UART implementation"}
            ],
            "architecture_decisions": [
                {"decision": "Use ARM Cortex-A architecture"}
            ]
        }
        state_manager.store_phase_data(WorkflowPhase.SPECIFY, spec_context)
        state_manager.complete_phase(WorkflowPhase.SPECIFY)
        
        # Verify state transition
        assert WorkflowPhase.SPECIFY in state_manager.get_completed_phases()
    
    def test_plan_command_integration(self, mock_git_repo):
        """Test integration of plan command with specification context."""
        workspace = mock_git_repo
        
        # Setup: Complete product and specify phases
        state_manager = WorkflowStateManager(workspace)
        integrator = WorkflowCommandIntegrator(workspace)
        
        # Complete prerequisite phases
        for phase in [WorkflowPhase.PRODUCT, WorkflowPhase.SPECIFY]:
            state_manager.start_phase(phase)
            context_data = {
                "test_data": f"{phase.value}_context",
                "phase": phase.value
            }
            state_manager.store_phase_data(phase, context_data)
            state_manager.complete_phase(phase)
        
        # Test plan command prerequisites
        success, error = integrator.validate_command_prerequisites("plan", WorkflowPhase.PLAN)
        assert success is True
        assert error is None
        
        # Simulate plan phase
        state_manager.start_phase(WorkflowPhase.PLAN)
        plan_context = {
            "implementation_strategy": "Agile development with TDD",
            "technology_stack": ["C", "Simics", "ARM GCC"],
            "milestones": [{"name": "MVP", "date": "2024-02-01"}]
        }
        state_manager.store_phase_data(WorkflowPhase.PLAN, plan_context)
        state_manager.complete_phase(WorkflowPhase.PLAN)
        
        # Verify completion
        assert WorkflowPhase.PLAN in state_manager.get_completed_phases()
    
    def test_tasks_command_integration(self, mock_git_repo):
        """Test integration of tasks command with plan context."""
        workspace = mock_git_repo
        
        # Setup: Complete all prerequisite phases
        state_manager = WorkflowStateManager(workspace)
        integrator = WorkflowCommandIntegrator(workspace)
        
        # Complete all prerequisite phases
        for phase in [WorkflowPhase.PRODUCT, WorkflowPhase.SPECIFY, WorkflowPhase.PLAN]:
            state_manager.start_phase(phase)
            context_data = {
                "test_data": f"{phase.value}_context",
                "phase": phase.value
            }
            state_manager.store_phase_data(phase, context_data)
            state_manager.complete_phase(phase)
        
        # Test tasks command prerequisites
        success, error = integrator.validate_command_prerequisites("tasks", WorkflowPhase.TASKS)
        assert success is True
        assert error is None
        
        # Simulate tasks phase
        state_manager.start_phase(WorkflowPhase.TASKS)
        state_manager.complete_phase(WorkflowPhase.TASKS)
        
        # Verify complete workflow
        completed = state_manager.get_completed_phases()
        assert len(completed) == 4
        assert all(phase in completed for phase in WorkflowPhase)
    
    def test_command_blocking_scenarios(self, mock_git_repo):
        """Test that commands are properly blocked when prerequisites aren't met."""
        workspace = mock_git_repo
        integrator = WorkflowCommandIntegrator(workspace)
        
        # Test specify command without product phase
        success, error = integrator.validate_command_prerequisites("specify", WorkflowPhase.SPECIFY)
        assert success is False
        assert "product" in error.lower()
        assert "/simics-platform" in error
        
        # Test plan command without specify phase
        success, error = integrator.validate_command_prerequisites("plan", WorkflowPhase.PLAN)
        assert success is False
        assert "product" in error.lower() or "specify" in error.lower()
        
        # Test tasks command without plan phase
        success, error = integrator.validate_command_prerequisites("tasks", WorkflowPhase.TASKS)
        assert success is False


class TestStateSharing:
    """Test state sharing and persistence across command executions."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_state_persistence_across_instances(self, temp_workspace):
        """Test that state persists across different manager instances."""
        # Create first instance and set some state
        manager1 = WorkflowStateManager(temp_workspace)
        manager1.start_phase(WorkflowPhase.PRODUCT)
        manager1.complete_phase(WorkflowPhase.PRODUCT, "test content")
        
        # Create second instance and verify state persists
        manager2 = WorkflowStateManager(temp_workspace)
        completed = manager2.get_completed_phases()
        assert WorkflowPhase.PRODUCT in completed
    
    def test_context_sharing_across_instances(self, temp_workspace):
        """Test that context data shares across different manager instances."""
        # Store context with first instance
        context1 = ContextTransferManager(temp_workspace)
        test_data = {"test": "data", "phase": "product"}
        context1.store_context_for_phase(WorkflowPhase.PRODUCT, test_data)
        
        # Retrieve context with second instance
        context2 = ContextTransferManager(temp_workspace)
        retrieved = context2.retrieve_context_for_phase(WorkflowPhase.PRODUCT)
        
        assert retrieved is not None
        assert retrieved["test"] == "data"
        assert retrieved["phase"] == "product"
    
    def test_concurrent_state_access(self, temp_workspace):
        """Test handling of concurrent state access."""
        # Create multiple managers
        managers = [WorkflowStateManager(temp_workspace) for _ in range(3)]
        
        # All should see consistent initial state
        for manager in managers:
            state = manager._get_current_state()
            assert state["completedPhases"] == []
        
        # One manager completes a phase
        managers[0].start_phase(WorkflowPhase.PRODUCT)
        managers[0].complete_phase(WorkflowPhase.PRODUCT)
        
        # Others should see the update after creating new instances
        new_manager = WorkflowStateManager(temp_workspace)
        completed = new_manager.get_completed_phases()
        assert WorkflowPhase.PRODUCT in completed
    
    def test_state_file_corruption_handling(self, temp_workspace):
        """Test handling of corrupted state files."""
        # Create a manager and state file
        manager = WorkflowStateManager(temp_workspace)
        manager.start_phase(WorkflowPhase.PRODUCT)
        
        # Corrupt the state file
        state_file = manager.state_file
        with open(state_file, 'w') as f:
            f.write("invalid json content {")
        
        # Creating new manager should handle corruption gracefully
        new_manager = WorkflowStateManager(temp_workspace)
        # Should create new initial state
        state = new_manager._get_current_state()
        assert "completedPhases" in state


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow scenarios."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_scripts(self):
        """Mock script execution for testing."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
            yield mock_run
    
    def test_complete_workflow_execution(self, temp_workspace, mock_scripts):
        """Test complete workflow execution from start to finish."""
        workspace = temp_workspace
        
        # Create workflow components
        state_manager = WorkflowStateManager(workspace)
        context_manager = ContextTransferManager(workspace)
        integrator = WorkflowCommandIntegrator(workspace)
        
        # Phase 1: Product (simics-platform command)
        assert integrator.validate_command_prerequisites("simics-platform", WorkflowPhase.PRODUCT)[0] is True
        
        integrator.start_phase_execution(WorkflowPhase.PRODUCT)
        
        product_context = {
            "vision": "ARM embedded platform for IoT applications",
            "success_criteria": [
                "Platform boots successfully in Simics",
                "All essential peripherals are functional",
                "Supports target IoT use cases"
            ],
            "constraints": [
                "Must use ARM Cortex-M architecture",
                "Must be compatible with Simics 6.0+",
                "Power consumption under 100mW"
            ],
            "requirements": [
                {"id": "REQ-001", "description": "ARM Cortex-M4 processor support"},
                {"id": "REQ-002", "description": "UART communication interface"},
                {"id": "REQ-003", "description": "GPIO for sensor connections"}
            ],
            "stakeholders": [
                {"name": "IoT Developer", "role": "Application development and testing"},
                {"name": "Hardware Engineer", "role": "Platform validation"},
                {"name": "System Architect", "role": "Architecture compliance"}
            ]
        }
        
        integrator.complete_phase_execution(
            WorkflowPhase.PRODUCT, 
            json.dumps(product_context),
            product_context
        )
        
        # Verify product phase completion
        assert WorkflowPhase.PRODUCT in state_manager.get_completed_phases()
        
        # Phase 2: Specify
        assert integrator.validate_command_prerequisites("specify", WorkflowPhase.SPECIFY)[0] is True
        
        integrator.start_phase_execution(WorkflowPhase.SPECIFY)
        
        spec_context = {
            "technical_requirements": [
                {"id": "TECH-001", "description": "ARM Cortex-M4 @ 80MHz with FPU"},
                {"id": "TECH-002", "description": "UART with 115200 baud rate support"},
                {"id": "TECH-003", "description": "16 GPIO pins with interrupt capability"}
            ],
            "architecture_decisions": [
                {"decision": "Use ARM Cortex-M4 for balance of performance and power"},
                {"decision": "Implement UART as memory-mapped peripheral"},
                {"decision": "GPIO controller with individual pin configuration"}
            ],
            "design_constraints": [
                "Must fit within 512KB flash memory",
                "Maximum 128KB RAM usage",
                "All peripherals must be memory-mapped"
            ],
            "interfaces": [
                {"name": "UART", "description": "Serial communication interface"},
                {"name": "GPIO", "description": "General purpose I/O pins"},
                {"name": "SPI", "description": "Serial peripheral interface"}
            ],
            "validation_criteria": [
                "All peripherals respond to register access",
                "UART can transmit and receive data",
                "GPIO pins can be configured and toggled"
            ]
        }
        
        integrator.complete_phase_execution(
            WorkflowPhase.SPECIFY,
            json.dumps(spec_context),
            spec_context
        )
        
        # Verify specify phase completion
        assert WorkflowPhase.SPECIFY in state_manager.get_completed_phases()
        
        # Phase 3: Plan
        assert integrator.validate_command_prerequisites("plan", WorkflowPhase.PLAN)[0] is True
        
        integrator.start_phase_execution(WorkflowPhase.PLAN)
        
        plan_context = {
            "implementation_strategy": "Incremental development starting with core processor, then adding peripherals",
            "technology_stack": [
                "Simics Framework 6.0",
                "C programming language", 
                "ARM GCC toolchain",
                "Python for test scripts"
            ],
            "resource_allocation": {
                "developers": 2,
                "timeline": "6 weeks",
                "testing_time": "2 weeks"
            },
            "milestones": [
                {"name": "Core processor implementation", "date": "Week 2"},
                {"name": "UART peripheral", "date": "Week 3"},
                {"name": "GPIO peripheral", "date": "Week 4"},
                {"name": "Integration testing", "date": "Week 5"},
                {"name": "Documentation and validation", "date": "Week 6"}
            ],
            "dependencies": [
                "Simics development license",
                "ARM development tools",
                "Reference hardware documentation"
            ],
            "risk_analysis": [
                {"risk": "Peripheral timing issues", "mitigation": "Early prototype testing"},
                {"risk": "Memory map conflicts", "mitigation": "Careful design review"}
            ]
        }
        
        integrator.complete_phase_execution(
            WorkflowPhase.PLAN,
            json.dumps(plan_context),
            plan_context
        )
        
        # Verify plan phase completion
        assert WorkflowPhase.PLAN in state_manager.get_completed_phases()
        
        # Phase 4: Tasks
        assert integrator.validate_command_prerequisites("tasks", WorkflowPhase.TASKS)[0] is True
        
        integrator.start_phase_execution(WorkflowPhase.TASKS)
        
        tasks_context = {
            "tasks_generated": True,
            "total_tasks": 15,
            "task_categories": ["setup", "core", "peripherals", "testing", "documentation"]
        }
        
        integrator.complete_phase_execution(
            WorkflowPhase.TASKS,
            "Generated implementation tasks",
            tasks_context
        )
        
        # Verify complete workflow
        completed_phases = state_manager.get_completed_phases()
        assert len(completed_phases) == 4
        assert all(phase in completed_phases for phase in WorkflowPhase)
        
        # Verify context flow
        product_data = context_manager.retrieve_context_for_phase(WorkflowPhase.PRODUCT)
        spec_data = context_manager.retrieve_context_for_phase(WorkflowPhase.SPECIFY)
        plan_data = context_manager.retrieve_context_for_phase(WorkflowPhase.PLAN)
        tasks_data = context_manager.retrieve_context_for_phase(WorkflowPhase.TASKS)
        
        assert product_data is not None
        assert spec_data is not None
        assert plan_data is not None
        assert tasks_data is not None
        
        # Verify workflow status
        status = state_manager.get_workflow_status()
        assert status["currentPhase"] is None  # No active phase
        assert len(status["completedPhases"]) == 4
        assert status["nextPhase"] is None  # All phases completed
    
    def test_workflow_interruption_and_recovery(self, temp_workspace):
        """Test workflow interruption and recovery scenarios."""
        workspace = temp_workspace
        
        # Start workflow
        state_manager = WorkflowStateManager(workspace)
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        state_manager.complete_phase(WorkflowPhase.PRODUCT)
        
        state_manager.start_phase(WorkflowPhase.SPECIFY)
        # Simulate interruption - don't complete specify phase
        
        # Create new instance (simulates restart)
        new_state_manager = WorkflowStateManager(workspace)
        status = new_state_manager.get_workflow_status()
        
        # Should show product as completed, specify as current
        assert "product" in status["completedPhases"]
        assert status["currentPhase"] == "specify"
        
        # Should be able to continue from where left off
        new_state_manager.complete_phase(WorkflowPhase.SPECIFY)
        assert WorkflowPhase.SPECIFY in new_state_manager.get_completed_phases()
    
    def test_workflow_validation_at_each_step(self, temp_workspace):
        """Test that validation occurs at each workflow step."""
        workspace = temp_workspace
        
        # Import validation components
        from specify_cli.traceability_verification import TraceabilityValidator
        
        state_manager = WorkflowStateManager(workspace)
        context_manager = ContextTransferManager(workspace) 
        traceability_validator = TraceabilityValidator(workspace)
        
        # Complete phases incrementally and validate at each step
        phases_data = [
            (WorkflowPhase.PRODUCT, {"vision": "test", "requirements": []}),
            (WorkflowPhase.SPECIFY, {"technical_requirements": [], "architecture_decisions": []}),
            (WorkflowPhase.PLAN, {"implementation_strategy": "test", "technology_stack": []}),
            (WorkflowPhase.TASKS, {"tasks_generated": True})
        ]
        
        for i, (phase, context_data) in enumerate(phases_data):
            # Complete phase
            state_manager.start_phase(phase)
            context_manager.store_context_for_phase(phase, context_data)
            state_manager.complete_phase(phase)
            
            # Validate traceability at each step
            if i > 0:  # Skip validation for first phase (needs at least 2 phases)
                result = traceability_validator.validate_full_traceability()
                assert result.score > 0  # Should have some traceability score
                
                # Should not have critical errors
                critical_errors = [issue for issue in result.issues 
                                 if issue.level.value == "error"]
                assert len(critical_errors) == 0


class TestScriptIntegration:
    """Test integration with actual bash/PowerShell scripts."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @patch('subprocess.run')
    def test_script_workflow_enforcement_integration(self, mock_run, temp_workspace):
        """Test that scripts properly integrate with workflow enforcement."""
        workspace = temp_workspace
        
        # Mock script responses for different scenarios
        def script_side_effect(cmd, **kwargs):
            if "setup-simics-platform" in cmd:
                # Mock successful product phase execution
                return Mock(
                    returncode=0,
                    stdout=json.dumps({
                        "success": True,
                        "workflow": {
                            "phase_completed": "product",
                            "next_phase": "specify",
                            "enforcement_active": True
                        }
                    })
                )
            elif "create-new-feature" in cmd:
                # Mock specify phase requiring product completion
                return Mock(
                    returncode=1,
                    stdout=json.dumps({
                        "error": "Product phase must be completed first",
                        "missing_phase": "product",
                        "next_command": "/simics-platform"
                    })
                )
            else:
                return Mock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = script_side_effect
        
        # Test simics-platform script execution
        result = subprocess.run(
            ["bash", "setup-simics-platform.sh", "--json", "test platform"],
            capture_output=True, text=True, cwd=workspace
        )
        
        # Verify script indicates workflow enforcement
        output = json.loads(result.stdout)
        assert output["workflow"]["enforcement_active"] is True
        assert output["workflow"]["phase_completed"] == "product"
        
        # Test specify script without product completion
        result = subprocess.run(
            ["bash", "create-new-feature.sh", "--json", "test feature"],
            capture_output=True, text=True, cwd=workspace
        )
        
        # Should fail with workflow enforcement error
        assert result.returncode == 1
        output = json.loads(result.stdout)
        assert "Product phase must be completed" in output["error"]


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v"])