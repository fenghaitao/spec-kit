"""
Comprehensive test suite for Enhanced Workflow Enforcement.

This module tests the workflow enforcement system including positive flows,
negative flows, and edge cases for the product → specify → plan → tasks sequence.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the modules we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from specify_cli.workflow_state import (
    WorkflowStateManager, 
    WorkflowPhase, 
    PhasePrerequisiteError,
    StateValidationError
)
from specify_cli.context_transfer import (
    ContextTransferManager,
    ProductContext,
    SpecificationContext,
    PlanContext
)
from specify_cli.command_integration import WorkflowCommandIntegrator
from specify_cli.validation_framework import SpecificationValidator, PlanValidator
from specify_cli.traceability_verification import TraceabilityValidator


class TestWorkflowStateManager:
    """Test the core workflow state management functionality."""
    
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
    
    def test_initialization(self, state_manager, temp_workspace):
        """Test that the state manager initializes correctly."""
        assert state_manager.workspace_path == Path(temp_workspace)
        assert state_manager.spec_kit_dir.exists()
        assert state_manager.phase_markers_dir.exists()
    
    def test_initial_state_creation(self, state_manager):
        """Test creation of initial workflow state."""
        state = state_manager._get_current_state()
        
        assert state["currentPhase"] is None
        assert state["completedPhases"] == []
        assert "lastUpdated" in state
        assert "featureName" in state
    
    def test_phase_progression_valid(self, state_manager):
        """Test valid phase progression through the workflow."""
        # Start with product phase
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        assert state_manager.get_current_phase() == WorkflowPhase.PRODUCT
        
        # Complete product phase
        state_manager.complete_phase(WorkflowPhase.PRODUCT, "test content")
        assert WorkflowPhase.PRODUCT in state_manager.get_completed_phases()
        
        # Start specify phase
        state_manager.start_phase(WorkflowPhase.SPECIFY)
        assert state_manager.get_current_phase() == WorkflowPhase.SPECIFY
        
        # Complete specify phase
        state_manager.complete_phase(WorkflowPhase.SPECIFY, "test spec content")
        assert WorkflowPhase.SPECIFY in state_manager.get_completed_phases()
        
        # Continue with plan phase
        state_manager.start_phase(WorkflowPhase.PLAN)
        state_manager.complete_phase(WorkflowPhase.PLAN, "test plan content")
        assert WorkflowPhase.PLAN in state_manager.get_completed_phases()
        
        # Complete with tasks phase
        state_manager.start_phase(WorkflowPhase.TASKS)
        state_manager.complete_phase(WorkflowPhase.TASKS, "test tasks content")
        assert WorkflowPhase.TASKS in state_manager.get_completed_phases()
    
    def test_phase_prerequisite_validation(self, state_manager):
        """Test that phase prerequisites are properly validated."""
        # Should not be able to start specify without product
        with pytest.raises(PhasePrerequisiteError):
            state_manager.validate_phase_prerequisites(WorkflowPhase.SPECIFY)
        
        # Should not be able to start plan without specify
        with pytest.raises(PhasePrerequisiteError):
            state_manager.validate_phase_prerequisites(WorkflowPhase.PLAN)
        
        # Should not be able to start tasks without plan
        with pytest.raises(PhasePrerequisiteError):
            state_manager.validate_phase_prerequisites(WorkflowPhase.TASKS)
        
        # Product phase should always be valid
        state_manager.validate_phase_prerequisites(WorkflowPhase.PRODUCT)  # Should not raise
    
    def test_phase_skipping_prevention(self, state_manager):
        """Test that phase skipping is prevented."""
        # Complete product phase
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        state_manager.complete_phase(WorkflowPhase.PRODUCT)
        
        # Try to skip to plan phase (should fail)
        with pytest.raises(PhasePrerequisiteError):
            state_manager.start_phase(WorkflowPhase.PLAN)
        
        # Try to skip to tasks phase (should fail)
        with pytest.raises(PhasePrerequisiteError):
            state_manager.start_phase(WorkflowPhase.TASKS)
    
    def test_phase_reset_functionality(self, state_manager):
        """Test that phases can be reset properly."""
        # Complete all phases
        for phase in [WorkflowPhase.PRODUCT, WorkflowPhase.SPECIFY, WorkflowPhase.PLAN, WorkflowPhase.TASKS]:
            state_manager.start_phase(phase)
            state_manager.complete_phase(phase)
        
        # Reset specify phase
        state_manager.reset_phase(WorkflowPhase.SPECIFY)
        
        completed = state_manager.get_completed_phases()
        assert WorkflowPhase.PRODUCT in completed
        assert WorkflowPhase.SPECIFY not in completed
        assert WorkflowPhase.PLAN not in completed  # Should also be reset
        assert WorkflowPhase.TASKS not in completed  # Should also be reset
    
    def test_workflow_status(self, state_manager):
        """Test workflow status reporting."""
        status = state_manager.get_workflow_status()
        
        assert "currentPhase" in status
        assert "completedPhases" in status
        assert "nextPhase" in status
        assert "canProceedTo" in status
        
        # Initially should be able to proceed to product phase only
        assert "product" in status["canProceedTo"]
        
        # Complete product phase and check updated status
        state_manager.start_phase(WorkflowPhase.PRODUCT)
        state_manager.complete_phase(WorkflowPhase.PRODUCT)
        
        status = state_manager.get_workflow_status()
        assert "specify" in status["canProceedTo"]


class TestContextTransfer:
    """Test context transfer functionality between phases."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def context_manager(self, temp_workspace):
        """Create a ContextTransferManager instance for testing."""
        return ContextTransferManager(temp_workspace)
    
    @pytest.fixture
    def sample_product_context(self):
        """Create sample product context data."""
        return ProductContext(
            vision="Test platform for embedded systems",
            success_criteria=["Boots successfully", "All components functional"],
            constraints=["Must be Simics compatible", "ARM Cortex-A architecture"],
            stakeholders=[
                {"name": "Developer", "role": "Implementation"},
                {"name": "Architect", "role": "Design validation"}
            ],
            requirements=[
                {"id": "REQ-001", "description": "Support ARM instruction set"},
                {"id": "REQ-002", "description": "Include essential peripherals"}
            ],
            metadata={"platform_type": "embedded", "target_system": "ARM Cortex-A"}
        )
    
    def test_product_context_storage_retrieval(self, context_manager, sample_product_context):
        """Test storing and retrieving product context."""
        # Store context
        context_manager.store_context_for_phase(WorkflowPhase.PRODUCT, sample_product_context)
        
        # Retrieve context
        retrieved = context_manager.retrieve_context_for_phase(WorkflowPhase.PRODUCT)
        
        assert retrieved is not None
        assert retrieved["vision"] == sample_product_context.vision
        assert len(retrieved["requirements"]) == len(sample_product_context.requirements)
    
    def test_context_extraction_from_documents(self, context_manager, temp_workspace):
        """Test extracting context from document files."""
        # Create a sample product specification
        spec_content = """
        # Product Vision
        
        Test platform for embedded systems targeting ARM Cortex-A architecture.
        
        # Success Criteria
        
        - Platform boots successfully in Simics
        - All identified components are functional
        
        # Technical Constraints
        
        - Must be compatible with Simics simulation environment
        - Platform type: embedded
        """
        
        spec_file = Path(temp_workspace) / "product_spec.md"
        spec_file.write_text(spec_content)
        
        # Extract product context
        context = context_manager.extract_product_context(spec_file)
        
        assert "embedded systems" in context.vision.lower()
        assert len(context.success_criteria) >= 1
        assert len(context.constraints) >= 1
    
    def test_template_injection(self, context_manager, sample_product_context, temp_workspace):
        """Test injecting context into templates."""
        # Create a simple template
        template_content = """
        # Specification
        
        ## Overview
        {{PRODUCT_VISION}}
        
        ## Requirements
        {{REQUIREMENTS}}
        
        ## Constraints
        {{TECHNICAL_CONSTRAINTS}}
        """
        
        template_file = Path(temp_workspace) / "spec_template.md"
        template_file.write_text(template_content)
        
        # Inject product context
        injected = context_manager.inject_product_context_into_spec(
            sample_product_context, template_file
        )
        
        assert sample_product_context.vision in injected
        assert "REQ-001" in injected
        assert "ARM Cortex-A" in injected
    
    def test_context_flow_validation(self, context_manager, sample_product_context):
        """Test validation of context flow across phases."""
        # Store product context
        context_manager.store_context_for_phase(WorkflowPhase.PRODUCT, sample_product_context)
        
        # Validate context flow (should pass with product context)
        validation = context_manager.validate_context_flow()
        assert validation["valid"] is True
        assert len(validation["issues"]) == 0


class TestCommandIntegration:
    """Test command integration with workflow enforcement."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def integrator(self, temp_workspace):
        """Create a WorkflowCommandIntegrator instance for testing."""
        return WorkflowCommandIntegrator(temp_workspace)
    
    def test_prerequisite_validation_success(self, integrator):
        """Test successful prerequisite validation."""
        # Product phase should always pass
        success, error = integrator.validate_command_prerequisites("simics-platform", WorkflowPhase.PRODUCT)
        assert success is True
        assert error is None
    
    def test_prerequisite_validation_failure(self, integrator):
        """Test prerequisite validation failure."""
        # Specify phase should fail without product completion
        success, error = integrator.validate_command_prerequisites("specify", WorkflowPhase.SPECIFY)
        assert success is False
        assert error is not None
        assert "product" in error.lower()
        assert "/simics-platform" in error
    
    def test_command_context_preparation(self, integrator):
        """Test preparation of command execution context."""
        # Test with product phase (should work)
        context = integrator.prepare_command_context(
            "simics-platform", 
            WorkflowPhase.PRODUCT, 
            {"description": "test platform"}
        )
        
        assert context.command_name == "simics-platform"
        assert context.target_phase == WorkflowPhase.PRODUCT
        assert context.prerequisites_met is True
    
    def test_workflow_guidance_generation(self, integrator):
        """Test generation of workflow guidance."""
        # Test guidance for product phase
        guidance = integrator.generate_command_guidance(WorkflowPhase.PRODUCT)
        assert guidance["status"] == "ready"
        assert "entry point" in guidance["description"].lower()
        
        # Test guidance for specify phase (should be blocked initially)
        guidance = integrator.generate_command_guidance(WorkflowPhase.SPECIFY)
        assert guidance["status"] == "blocked"
        assert guidance["next_command"] == "/simics-platform"
    
    def test_phase_execution_lifecycle(self, integrator):
        """Test complete phase execution lifecycle."""
        # Start product phase
        integrator.start_phase_execution(WorkflowPhase.PRODUCT)
        
        # Complete product phase
        integrator.complete_phase_execution(
            WorkflowPhase.PRODUCT, 
            "test content",
            {"test": "data"}
        )
        
        # Verify completion
        status = integrator.get_workflow_status()
        assert "product" in status["completedPhases"]


class TestValidationFramework:
    """Test the validation framework components."""
    
    def test_specification_validation_success(self):
        """Test successful specification validation."""
        validator = SpecificationValidator()
        
        good_spec = """
        # Overview
        This is a comprehensive specification for our system.
        
        # Requirements
        - REQ-001: System must support user authentication
        - REQ-002: System must handle 1000 concurrent users
        
        # Architecture
        The system follows a microservices architecture with:
        - API Gateway for routing
        - Authentication service
        - Business logic services
        
        # Technical Details
        - REST API interfaces
        - PostgreSQL database
        - Redis for caching
        
        # Interfaces
        - HTTP REST API
        - WebSocket connections
        
        # Validation
        - Unit tests for all components
        - Integration tests for API endpoints
        
        # Constraints
        - Must be cloud-native
        - Must support horizontal scaling
        """
        
        result = validator.validate_specification(good_spec)
        assert result.valid is True
        assert result.score > 0.7
    
    def test_specification_validation_failure(self):
        """Test specification validation with issues."""
        validator = SpecificationValidator()
        
        poor_spec = """
        # Overview
        Basic overview.
        
        [NEEDS CLARIFICATION: What should this do?]
        """
        
        result = validator.validate_specification(poor_spec)
        assert result.valid is False
        assert len(result.issues) > 0
        assert any("Missing required section" in issue.message for issue in result.issues)
    
    def test_plan_validation_success(self):
        """Test successful plan validation."""
        validator = PlanValidator()
        
        good_plan = """
        # Implementation Strategy
        We will implement this system using agile methodology with 2-week sprints.
        The development will follow test-driven development practices.
        
        # Technology Stack
        - Frontend: React with TypeScript
        - Backend: Node.js with Express
        - Database: PostgreSQL
        - Cache: Redis
        - Deployment: Docker with Kubernetes
        
        # Architecture
        Microservices architecture with API Gateway pattern.
        
        # Milestones
        - Week 1-2: Project setup and infrastructure
        - Week 3-4: Core API development
        - Week 5-6: Frontend implementation
        - Week 7-8: Testing and deployment
        
        # Dependencies
        - External API for payment processing
        - Third-party authentication service
        
        # Resources
        - 3 developers
        - 1 DevOps engineer
        - 1 QA engineer
        
        # Risk Analysis
        - Dependency on external APIs
        - Potential scaling challenges
        
        # Testing Strategy
        Comprehensive testing including unit, integration, and e2e tests.
        """
        
        result = validator.validate_plan(good_plan)
        assert result.valid is True
        assert result.score > 0.7
    
    def test_plan_validation_failure(self):
        """Test plan validation with missing elements."""
        validator = PlanValidator()
        
        poor_plan = """
        # Overview
        This is a basic plan.
        """
        
        result = validator.validate_plan(poor_plan)
        assert result.valid is False
        assert len(result.issues) > 0
        assert any("Missing required element" in issue.message for issue in result.issues)


class TestWorkflowEnforcementIntegration:
    """Test end-to-end workflow enforcement scenarios."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def setup_components(self, temp_workspace):
        """Set up all workflow enforcement components."""
        state_manager = WorkflowStateManager(temp_workspace)
        context_manager = ContextTransferManager(temp_workspace)
        integrator = WorkflowCommandIntegrator(temp_workspace)
        traceability_validator = TraceabilityValidator(temp_workspace)
        
        return {
            "state": state_manager,
            "context": context_manager,
            "integrator": integrator,
            "traceability": traceability_validator,
            "workspace": temp_workspace
        }
    
    def test_complete_workflow_success(self, setup_components):
        """Test successful execution of complete workflow sequence."""
        components = setup_components
        state = components["state"]
        context = components["context"]
        
        # Step 1: Product phase
        state.start_phase(WorkflowPhase.PRODUCT)
        product_context = ProductContext(
            vision="Test embedded platform",
            success_criteria=["Functional", "Reliable"],
            constraints=["ARM architecture"],
            stakeholders=[{"name": "Dev", "role": "Implementation"}],
            requirements=[{"id": "REQ-001", "description": "ARM support"}],
            metadata={"type": "embedded"}
        )
        context.store_context_for_phase(WorkflowPhase.PRODUCT, product_context)
        state.complete_phase(WorkflowPhase.PRODUCT, "product content")
        
        # Step 2: Specify phase
        state.start_phase(WorkflowPhase.SPECIFY)
        spec_context = SpecificationContext(
            technical_requirements=[{"id": "TECH-001", "description": "ARM ISA support"}],
            architecture_decisions=[{"decision": "Use ARM Cortex-A"}],
            design_constraints=["Performance constraints"],
            interfaces=[{"name": "UART", "description": "Serial interface"}],
            validation_criteria=["Boot test", "Functional test"],
            clarifications_resolved=["Architecture choice clarified"],
            metadata={"completion_date": "2024-01-01"}
        )
        context.store_context_for_phase(WorkflowPhase.SPECIFY, spec_context)
        state.complete_phase(WorkflowPhase.SPECIFY, "spec content")
        
        # Step 3: Plan phase
        state.start_phase(WorkflowPhase.PLAN)
        plan_context = PlanContext(
            implementation_strategy="Agile development with TDD",
            technology_stack=["C", "Simics", "ARM GCC"],
            resource_allocation={"developers": 2, "timeline": "4 weeks"},
            milestones=[{"name": "MVP", "date": "2024-02-01"}],
            dependencies=["Simics license", "ARM toolchain"],
            risk_analysis=[{"risk": "Hardware compatibility", "mitigation": "Early testing"}],
            design_artifacts=["architecture.md", "interfaces.md"],
            metadata={"planning_date": "2024-01-15"}
        )
        context.store_context_for_phase(WorkflowPhase.PLAN, plan_context)
        state.complete_phase(WorkflowPhase.PLAN, "plan content")
        
        # Step 4: Tasks phase
        state.start_phase(WorkflowPhase.TASKS)
        state.complete_phase(WorkflowPhase.TASKS, "tasks content")
        
        # Verify complete workflow
        completed_phases = state.get_completed_phases()
        assert len(completed_phases) == 4
        assert all(phase in completed_phases for phase in WorkflowPhase)
        
        # Verify traceability
        traceability_result = components["traceability"].validate_full_traceability()
        assert traceability_result.valid is True
    
    def test_workflow_enforcement_blocking(self, setup_components):
        """Test that workflow enforcement properly blocks invalid sequences."""
        components = setup_components
        integrator = components["integrator"]
        
        # Try to start with specify phase (should be blocked)
        success, error = integrator.validate_command_prerequisites("specify", WorkflowPhase.SPECIFY)
        assert success is False
        assert "product" in error.lower()
        
        # Try to start with plan phase (should be blocked)
        success, error = integrator.validate_command_prerequisites("plan", WorkflowPhase.PLAN)
        assert success is False
        assert "product" in error.lower() or "specify" in error.lower()
        
        # Try to start with tasks phase (should be blocked)
        success, error = integrator.validate_command_prerequisites("tasks", WorkflowPhase.TASKS)
        assert success is False
    
    def test_partial_workflow_validation(self, setup_components):
        """Test validation with partially completed workflow."""
        components = setup_components
        state = components["state"]
        traceability = components["traceability"]
        
        # Complete only product and specify phases
        state.start_phase(WorkflowPhase.PRODUCT)
        state.complete_phase(WorkflowPhase.PRODUCT)
        
        state.start_phase(WorkflowPhase.SPECIFY)
        state.complete_phase(WorkflowPhase.SPECIFY)
        
        # Validate traceability (should handle partial completion)
        result = traceability.validate_full_traceability()
        assert result.score > 0  # Should have some score even with partial completion
    
    def test_workflow_reset_scenarios(self, setup_components):
        """Test workflow reset and recovery scenarios."""
        components = setup_components
        state = components["state"]
        
        # Complete all phases
        for phase in WorkflowPhase:
            state.start_phase(phase)
            state.complete_phase(phase)
        
        # Reset specify phase (should reset subsequent phases too)
        state.reset_phase(WorkflowPhase.SPECIFY)
        
        completed = state.get_completed_phases()
        assert WorkflowPhase.PRODUCT in completed
        assert WorkflowPhase.SPECIFY not in completed
        assert WorkflowPhase.PLAN not in completed
        assert WorkflowPhase.TASKS not in completed
        
        # Should now be able to restart from specify
        state.start_phase(WorkflowPhase.SPECIFY)  # Should not raise exception


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])