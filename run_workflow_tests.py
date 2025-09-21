#!/usr/bin/env python3
"""
Test runner for Enhanced Workflow Enforcement.

This script runs comprehensive tests for the workflow enforcement system
and provides detailed reporting on test results and system functionality.
"""

import sys
import subprocess
import json
import time
from pathlib import Path


def run_command(cmd, capture_output=True):
    """Run a command and return result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def check_python_dependencies():
    """Check if required Python dependencies are available."""
    print("🔍 Checking Python dependencies...")
    
    required_modules = ['pytest', 'json', 'pathlib', 'tempfile', 'unittest.mock']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"  ❌ {module}")
    
    if missing_modules:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_modules)}")
        print("Install with: pip install pytest")
        return False
    
    print("✅ All dependencies available\n")
    return True


def run_unit_tests():
    """Run unit tests for workflow enforcement."""
    print("🧪 Running unit tests...")
    
    test_files = [
        "tests/test_workflow_enforcement.py",
        "tests/test_integration.py", 
        "tests/test_edge_cases.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"  ⚠️  Test file not found: {test_file}")
            results[test_file] = {"status": "missing", "output": ""}
            continue
        
        print(f"  Running {test_file}...")
        success, stdout, stderr = run_command(f"python -m pytest {test_file} -v")
        
        results[test_file] = {
            "status": "passed" if success else "failed",
            "output": stdout,
            "error": stderr
        }
        
        if success:
            print(f"    ✅ {test_file}")
        else:
            print(f"    ❌ {test_file}")
            if stderr:
                print(f"    Error: {stderr[:200]}...")
    
    return results


def test_workflow_state_functionality():
    """Test core workflow state functionality."""
    print("🔄 Testing workflow state functionality...")
    
    try:
        # Add src to path for imports
        sys.path.insert(0, str(Path("src")))
        
        from specify_cli.workflow_state import WorkflowStateManager, WorkflowPhase
        import tempfile
        import shutil
        
        # Create temporary workspace
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Test basic functionality
            manager = WorkflowStateManager(temp_dir)
            
            # Test phase progression
            manager.start_phase(WorkflowPhase.PRODUCT)
            manager.complete_phase(WorkflowPhase.PRODUCT, "test content")
            
            assert WorkflowPhase.PRODUCT in manager.get_completed_phases()
            print("  ✅ Phase completion tracking")
            
            # Test prerequisites validation
            try:
                manager.validate_phase_prerequisites(WorkflowPhase.SPECIFY)
                print("  ✅ Prerequisites validation")
            except Exception as e:
                print(f"  ❌ Prerequisites validation failed: {e}")
                return False
            
            # Test state persistence
            manager2 = WorkflowStateManager(temp_dir)
            completed = manager2.get_completed_phases()
            assert WorkflowPhase.PRODUCT in completed
            print("  ✅ State persistence")
            
            print("✅ Workflow state functionality working\n")
            return True
            
        finally:
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"  ❌ Workflow state test failed: {e}")
        return False


def test_context_transfer_functionality():
    """Test context transfer functionality."""
    print("📋 Testing context transfer functionality...")
    
    try:
        from specify_cli.context_transfer import ContextTransferManager, ProductContext
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            manager = ContextTransferManager(temp_dir)
            
            # Test context storage and retrieval
            test_context = ProductContext(
                vision="Test platform",
                success_criteria=["Criterion 1"],
                constraints=["Constraint 1"],
                stakeholders=[{"name": "Dev", "role": "Developer"}],
                requirements=[{"id": "REQ-1", "description": "Test requirement"}],
                metadata={"test": "data"}
            )
            
            manager.store_context_for_phase(WorkflowPhase.PRODUCT, test_context)
            retrieved = manager.retrieve_context_for_phase(WorkflowPhase.PRODUCT)
            
            assert retrieved is not None
            assert retrieved["vision"] == "Test platform"
            print("  ✅ Context storage and retrieval")
            
            print("✅ Context transfer functionality working\n")
            return True
            
        finally:
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"  ❌ Context transfer test failed: {e}")
        return False


def test_command_integration():
    """Test command integration functionality."""
    print("⚙️  Testing command integration...")
    
    try:
        from specify_cli.command_integration import WorkflowCommandIntegrator
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            integrator = WorkflowCommandIntegrator(temp_dir)
            
            # Test prerequisite validation
            success, error = integrator.validate_command_prerequisites("simics-platform", WorkflowPhase.PRODUCT)
            assert success is True
            print("  ✅ Product phase validation (should pass)")
            
            success, error = integrator.validate_command_prerequisites("specify", WorkflowPhase.SPECIFY)
            assert success is False
            assert "product" in error.lower()
            print("  ✅ Specify phase blocking (should fail without product)")
            
            print("✅ Command integration working\n")
            return True
            
        finally:
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"  ❌ Command integration test failed: {e}")
        return False


def test_validation_framework():
    """Test validation framework functionality."""
    print("🔍 Testing validation framework...")
    
    try:
        from specify_cli.validation_framework import SpecificationValidator, PlanValidator
        
        # Test specification validation
        spec_validator = SpecificationValidator()
        
        good_spec = """
        # Overview
        This is a test specification.
        
        # Requirements  
        - REQ-001: Test requirement
        
        # Architecture
        Test architecture description.
        
        # Technical Details
        Technical implementation details.
        
        # Interfaces
        System interfaces description.
        
        # Validation
        Validation approach.
        
        # Constraints
        System constraints.
        """
        
        result = spec_validator.validate_specification(good_spec)
        assert result.valid is True
        assert result.score > 0.7
        print("  ✅ Specification validation")
        
        # Test plan validation
        plan_validator = PlanValidator()
        
        good_plan = """
        # Implementation Strategy
        Agile development approach with test-driven development.
        
        # Technology Stack
        - Python
        - pytest
        - Git
        
        # Architecture
        Modular architecture with clear separation of concerns.
        
        # Milestones
        - Week 1: Initial setup
        - Week 2: Core development
        
        # Dependencies
        - Development tools
        - Testing framework
        
        # Resources
        - 2 developers
        - 4 weeks timeline
        """
        
        result = plan_validator.validate_plan(good_plan)
        assert result.valid is True
        print("  ✅ Plan validation")
        
        print("✅ Validation framework working\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Validation framework test failed: {e}")
        return False


def test_traceability_verification():
    """Test traceability verification functionality."""
    print("🔗 Testing traceability verification...")
    
    try:
        from specify_cli.traceability_verification import TraceabilityValidator
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            validator = TraceabilityValidator(temp_dir)
            
            # Test with no phases (should handle gracefully)
            result = validator.validate_full_traceability()
            assert result.valid is True  # Should handle empty state gracefully
            print("  ✅ Empty state handling")
            
            print("✅ Traceability verification working\n")
            return True
            
        finally:
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"  ❌ Traceability verification test failed: {e}")
        return False


def test_script_integration():
    """Test integration with bash/PowerShell scripts."""
    print("📜 Testing script integration...")
    
    # Check if scripts exist
    bash_scripts = [
        "scripts/bash/setup-simics-platform.sh",
        "scripts/bash/create-new-feature.sh", 
        "scripts/bash/setup-plan.sh",
        "scripts/bash/check-task-prerequisites.sh"
    ]
    
    powershell_scripts = [
        "scripts/powershell/setup-simics-platform.ps1",
        "scripts/powershell/create-new-feature.ps1",
        "scripts/powershell/setup-plan.ps1", 
        "scripts/powershell/check-task-prerequisites.ps1"
    ]
    
    scripts_found = 0
    total_scripts = len(bash_scripts) + len(powershell_scripts)
    
    for script in bash_scripts:
        if Path(script).exists():
            scripts_found += 1
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} (missing)")
    
    for script in powershell_scripts:
        if Path(script).exists():
            scripts_found += 1
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} (missing)")
    
    if scripts_found == total_scripts:
        print("✅ All scripts present\n")
        return True
    else:
        print(f"⚠️  {scripts_found}/{total_scripts} scripts found\n")
        return False


def generate_test_report(test_results):
    """Generate comprehensive test report."""
    print("📊 Generating test report...")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_tests": len(test_results),
            "passed": sum(1 for r in test_results.values() if r.get("status") == "passed"),
            "failed": sum(1 for r in test_results.values() if r.get("status") == "failed"),
            "missing": sum(1 for r in test_results.values() if r.get("status") == "missing")
        },
        "details": test_results
    }
    
    # Write report to file
    report_file = Path("workflow_enforcement_test_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Test report written to: {report_file}")
    
    # Print summary
    summary = report["summary"]
    print(f"""
📈 Test Summary:
   Total Tests: {summary['total_tests']}
   ✅ Passed: {summary['passed']}
   ❌ Failed: {summary['failed']}
   ⚠️  Missing: {summary['missing']}
""")
    
    return report


def main():
    """Run all tests and generate report."""
    print("🚀 Enhanced Workflow Enforcement Test Runner")
    print("=" * 50)
    
    # Check dependencies first
    if not check_python_dependencies():
        print("❌ Cannot proceed without required dependencies")
        return 1
    
    # Run all tests
    test_results = {}
    
    # Unit tests
    unit_test_results = run_unit_tests()
    test_results.update(unit_test_results)
    
    # Functional tests
    functional_tests = [
        ("workflow_state", test_workflow_state_functionality),
        ("context_transfer", test_context_transfer_functionality),
        ("command_integration", test_command_integration),
        ("validation_framework", test_validation_framework),
        ("traceability_verification", test_traceability_verification),
        ("script_integration", test_script_integration)
    ]
    
    for test_name, test_func in functional_tests:
        try:
            success = test_func()
            test_results[test_name] = {
                "status": "passed" if success else "failed",
                "type": "functional"
            }
        except Exception as e:
            test_results[test_name] = {
                "status": "failed",
                "type": "functional", 
                "error": str(e)
            }
    
    # Generate report
    report = generate_test_report(test_results)
    
    # Determine exit code
    failed_tests = [name for name, result in test_results.items() 
                   if result.get("status") == "failed"]
    
    if failed_tests:
        print(f"❌ {len(failed_tests)} test(s) failed:")
        for test in failed_tests:
            print(f"   - {test}")
        return 1
    else:
        print("🎉 All tests passed!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)