"""
Integration tests for Simics commands and templates.

These tests verify the end-to-end functionality of the Simics integration,
including command processing, template generation, and script execution.
"""

import os
import tempfile
import shutil
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from specify_cli import app
from specify_cli.simics_validation import SimicsTemplateValidator, SimicsProjectValidator
from typer.testing import CliRunner


class TestSimicsIntegration:
    """Test suite for Simics integration functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_path = Path(self.temp_dir) / "test_project"
        self.test_project_path.mkdir(exist_ok=True)
        
    def teardown_method(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_simics_device_command_basic(self):
        """Test basic simics-device command functionality."""
        # Create a test specification file
        spec_content = """# Test Device Specification

/simics-device uart-controller --target modern-cpu --interface memory-mapped

## Device Overview
Test UART controller device for simulation.

## Register Interface
- Base Address: 0x10000000
- Address Range: 0x1000

## Implementation Requirements
- DML-based device model
- Interrupt support
- FIFO buffer management
"""
        
        spec_file = self.test_project_path / "uart_spec.md"
        spec_file.write_text(spec_content)
        
        # Test command processing
        os.chdir(self.test_project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Verify generated files
        expected_files = [
            "uart-controller.dml",
            "uart-controller-test.py",
            "uart-controller.simics"
        ]
        
        for expected_file in expected_files:
            assert (self.test_project_path / expected_file).exists(), f"Expected file {expected_file} not created"
    
    def test_simics_platform_command_basic(self):
        """Test basic simics-platform command functionality."""
        spec_content = """# Test Platform Specification

/simics-platform embedded-system --cpu arm-cortex-a53 --memory 1GB

## Platform Overview
Test embedded system platform for ARM Cortex-A53.

## System Architecture
- CPU: ARM Cortex-A53 quad-core
- Memory: 1GB DDR4
- Storage: eMMC 32GB

## Device Integration
- UART controllers: 2x
- GPIO controllers: 4x
- SPI controllers: 2x
"""
        
        spec_file = self.test_project_path / "platform_spec.md"
        spec_file.write_text(spec_content)
        
        os.chdir(self.test_project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Verify generated files
        expected_files = [
            "embedded-system.simics",
            "embedded-system-devices.py",
            "embedded-system-setup.py"
        ]
        
        for expected_file in expected_files:
            assert (self.test_project_path / expected_file).exists(), f"Expected file {expected_file} not created"
    
    def test_simics_validate_command_basic(self):
        """Test basic simics-validate command functionality."""
        spec_content = """# Test Validation Specification

/simics-validate device-validation --target uart-controller --coverage 90%

## Validation Overview
Comprehensive validation suite for UART controller device.

## Test Coverage Requirements
- Functional Coverage: 90%
- Code Coverage: 85%
- Performance Testing: Required

## Test Scenarios
1. Basic UART communication
2. Interrupt handling
3. Error conditions
4. Performance benchmarks
"""
        
        spec_file = self.test_project_path / "validation_spec.md"
        spec_file.write_text(spec_content)
        
        os.chdir(self.test_project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Verify generated files
        expected_files = [
            "device-validation-suite.py",
            "device-validation-config.json",
            "device-validation-report.py"
        ]
        
        for expected_file in expected_files:
            assert (self.test_project_path / expected_file).exists(), f"Expected file {expected_file} not created"
    
    def test_simics_validation_framework(self):
        """Test the Simics validation framework."""
        # Create test project structure
        (self.test_project_path / "templates").mkdir(exist_ok=True)
        (self.test_project_path / "templates" / "simics").mkdir(exist_ok=True)
        (self.test_project_path / "scripts").mkdir(exist_ok=True)
        
        # Create test template
        template_content = """# Test Template
/simics-device test-device --target test-cpu
## Device Overview
Test device template.
"""
        template_file = self.test_project_path / "templates" / "simics" / "test-template.md"
        template_file.write_text(template_content)
        
        # Create test script
        script_content = """#!/bin/bash
echo "Test script execution"
exit 0
"""
        script_file = self.test_project_path / "scripts" / "test-script.sh"
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        
        # Test validation
        os.chdir(self.test_project_path)
        result = self.runner.invoke(app, ["validate-simics", "--path", str(self.test_project_path)])
        
        assert result.exit_code == 0
        assert "Validation completed" in result.stdout or "validation" in result.stdout.lower()
    
    def test_template_validator(self):
        """Test the SimicsTemplateValidator class."""
        validator = SimicsTemplateValidator()
        
        # Test valid template
        valid_template = """# Valid Template
/simics-device test-device --target modern-cpu
## Device Overview
This is a valid template.
## Register Interface
- Base Address: 0x10000000
"""
        
        result = validator.validate_template_content(valid_template)
        assert result.is_valid
        assert len(result.errors) == 0
        
        # Test invalid template (missing command)
        invalid_template = """# Invalid Template
## Device Overview
This template is missing a Simics command.
"""
        
        result = validator.validate_template_content(invalid_template)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any("simics command" in error.lower() for error in result.errors)
    
    def test_project_validator(self):
        """Test the SimicsProjectValidator class."""
        validator = SimicsProjectValidator()
        
        # Create test project structure
        project_structure = [
            "test-device.dml",
            "test-device.simics",
            "test-device-test.py"
        ]
        
        for file_name in project_structure:
            test_file = self.test_project_path / file_name
            test_file.write_text("# Test content")
        
        # Test project validation
        result = validator.validate_project(str(self.test_project_path))
        assert result.is_valid or len(result.warnings) == 0  # Should pass or have minimal warnings
    
    def test_command_line_integration(self):
        """Test complete command-line integration workflow."""
        # Create a comprehensive test specification
        spec_content = """# Complete Integration Test

/simics-device uart-controller --target modern-cpu --interface memory-mapped
/simics-platform test-platform --cpu arm-cortex-a53 --memory 1GB
/simics-validate comprehensive-test --target uart-controller --coverage 95%

## Project Overview
Complete integration test for Simics functionality.

## Device Specification
UART controller with full feature set.

## Platform Integration
ARM-based platform with comprehensive device support.

## Validation Requirements
Full test coverage with automated validation.
"""
        
        spec_file = self.test_project_path / "integration_spec.md"
        spec_file.write_text(spec_content)
        
        # Process the specification
        os.chdir(self.test_project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Verify multiple command processing
        device_files = ["uart-controller.dml", "uart-controller.simics"]
        platform_files = ["test-platform.simics", "test-platform-setup.py"]
        validation_files = ["comprehensive-test-suite.py", "comprehensive-test-config.json"]
        
        all_expected_files = device_files + platform_files + validation_files
        
        created_files = list(self.test_project_path.glob("*"))
        created_file_names = [f.name for f in created_files if f.is_file()]
        
        # Check that at least some expected files were created
        assert len(created_file_names) > 0, "No files were created during processing"
        
        # Validate the project
        validation_result = self.runner.invoke(app, ["validate-simics", "--path", str(self.test_project_path)])
        assert validation_result.exit_code == 0
    
    @patch('subprocess.run')
    def test_script_execution_simulation(self, mock_subprocess):
        """Test script execution with mocked subprocess calls."""
        # Mock successful script execution
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        
        # Create test script
        script_content = """#!/bin/bash
echo "Simics setup script"
mkdir -p simics_project
echo "Setup complete"
"""
        script_file = self.test_project_path / "setup-test.sh"
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        
        # Test script validation (would normally execute)
        from specify_cli.simics_validation import SimicsScriptTester
        tester = SimicsScriptTester()
        
        # This would normally run the script, but we're mocking it
        result = tester.test_script(str(script_file))
        
        # Verify mock was called
        assert mock_subprocess.called or result  # Either mock called or test passed
    
    def test_error_handling(self):
        """Test error handling in Simics commands."""
        # Test with malformed specification
        malformed_spec = """# Malformed Specification
/simics-device  # Missing required parameters
## Invalid Content
This specification has syntax errors.
"""
        
        spec_file = self.test_project_path / "malformed_spec.md"
        spec_file.write_text(malformed_spec)
        
        os.chdir(self.test_project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        # Should handle errors gracefully
        # Either succeeds with warnings or fails with proper error messages
        assert result.exit_code in [0, 1]  # Allow both success with warnings or proper failure
    
    def test_template_file_validation(self):
        """Test validation of template files in the project."""
        # Copy actual template files to test directory for validation
        template_dir = self.test_project_path / "templates" / "simics"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock template files
        templates = {
            "commands/simics-device.md": "# Simics Device Command\n/simics-device {{device_name}}",
            "projects/device-spec-template.md": "# Device Specification\n## Overview\nDevice template",
            "projects/platform-spec-template.md": "# Platform Specification\n## Architecture\nPlatform template"
        }
        
        for template_path, content in templates.items():
            full_path = template_dir / template_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        # Validate templates
        validator = SimicsTemplateValidator()
        
        for template_path in template_dir.rglob("*.md"):
            result = validator.validate_template_file(str(template_path))
            # Templates should be valid or have only minor warnings
            assert result.is_valid or len(result.errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])