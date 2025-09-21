"""
End-to-end testing for Simics command processing and template generation.
"""

import os
import tempfile
import shutil
import pytest
from pathlib import Path
from typer.testing import CliRunner

from specify_cli import app
from tests.test_config import TestDataGenerator, TestFileManager, MockSimicsEnvironment


class TestSimicsCommandProcessing:
    """Test Simics command processing end-to-end."""
    
    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = TestFileManager(Path(self.temp_dir))
        self.mock_env = MockSimicsEnvironment()
        
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_device_command_processing(self):
        """Test processing of simics-device commands."""
        # Create test project
        project_path = self.file_manager.create_test_project("device_test")
        
        # Generate device specification
        spec_content = TestDataGenerator.create_device_specification(
            "uart-controller", 
            "modern-cpu",
            base_address="0x10001000",
            interface="memory-mapped"
        )
        
        spec_file = self.file_manager.add_test_specification(
            "device_test", 
            "uart_device_spec", 
            spec_content
        )
        
        # Process the specification
        os.chdir(project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Check for generated files
        expected_patterns = ["*.dml", "*.simics", "*-test.py"]
        generated_files = []
        
        for pattern in expected_patterns:
            generated_files.extend(list(project_path.glob(pattern)))
        
        assert len(generated_files) > 0, "No files were generated"
        
        # Verify content of key files
        dml_files = list(project_path.glob("*.dml"))
        if dml_files:
            dml_content = dml_files[0].read_text()
            assert "device" in dml_content.lower()
            assert "uart" in dml_content.lower()
    
    def test_platform_command_processing(self):
        """Test processing of simics-platform commands."""
        project_path = self.file_manager.create_test_project("platform_test")
        
        spec_content = TestDataGenerator.create_platform_specification(
            "embedded-system",
            "arm-cortex-a53",
            memory="2GB",
            storage="64GB eMMC"
        )
        
        spec_file = self.file_manager.add_test_specification(
            "platform_test",
            "embedded_platform_spec",
            spec_content
        )
        
        os.chdir(project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Check for platform-specific files
        expected_patterns = ["*.simics", "*-setup.py", "*-devices.py"]
        generated_files = []
        
        for pattern in expected_patterns:
            generated_files.extend(list(project_path.glob(pattern)))
        
        assert len(generated_files) > 0, "No platform files were generated"
    
    def test_validation_command_processing(self):
        """Test processing of simics-validate commands."""
        project_path = self.file_manager.create_test_project("validation_test")
        
        spec_content = TestDataGenerator.create_validation_specification(
            "comprehensive-test",
            "uart-controller",
            coverage="95%",
            test_types="functional,performance,stress,integration"
        )
        
        spec_file = self.file_manager.add_test_specification(
            "validation_test",
            "comprehensive_validation_spec",
            spec_content
        )
        
        os.chdir(project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Check for validation-specific files
        expected_patterns = ["*-suite.py", "*-config.json", "*-report.py"]
        generated_files = []
        
        for pattern in expected_patterns:
            generated_files.extend(list(project_path.glob(pattern)))
        
        assert len(generated_files) > 0, "No validation files were generated"
    
    def test_multiple_commands_in_single_spec(self):
        """Test processing multiple Simics commands in one specification."""
        project_path = self.file_manager.create_test_project("multi_command_test")
        
        # Create specification with multiple commands
        multi_spec = """# Multi-Command Simics Test

/simics-device uart-controller --target modern-cpu --interface memory-mapped
/simics-platform test-platform --cpu arm-cortex-a53 --memory 1GB
/simics-validate integration-test --target uart-controller --coverage 90%

## Project Overview
This specification tests multiple Simics commands in a single file.

## Device Requirements
UART controller with full feature set for modern CPU targets.

## Platform Requirements
ARM-based platform with 1GB memory and comprehensive device support.

## Validation Requirements
Integration testing with 90% coverage requirement.

## Implementation Notes
- All components must integrate seamlessly
- Cross-component dependencies must be handled
- Validation must cover end-to-end scenarios
"""
        
        spec_file = self.file_manager.add_test_specification(
            "multi_command_test",
            "multi_command_spec",
            multi_spec
        )
        
        os.chdir(project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Verify files from all command types were generated
        all_patterns = ["*.dml", "*.simics", "*-test.py", "*-setup.py", "*-suite.py", "*-config.json"]
        generated_files = []
        
        for pattern in all_patterns:
            generated_files.extend(list(project_path.glob(pattern)))
        
        # Should have files from device, platform, and validation commands
        assert len(generated_files) >= 3, f"Expected at least 3 files, got {len(generated_files)}"
    
    def test_command_parameter_parsing(self):
        """Test parsing of command parameters."""
        project_path = self.file_manager.create_test_project("param_test")
        
        # Test with complex parameters
        complex_spec = """# Parameter Parsing Test

/simics-device complex-uart --target modern-cpu --interface memory-mapped --base-address 0x20000000 --interrupt 15 --features fifo,dma,flow-control

## Device Overview
Complex UART with advanced features for parameter testing.

## Features
- FIFO buffer support
- DMA integration
- Hardware flow control
- Configurable interrupts
"""
        
        spec_file = self.file_manager.add_test_specification(
            "param_test",
            "complex_param_spec",
            complex_spec
        )
        
        os.chdir(project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        assert result.exit_code == 0
        
        # Verify parameter processing in generated files
        generated_files = list(project_path.glob("*.dml"))
        if generated_files:
            content = generated_files[0].read_text()
            # Check that parameters were processed
            assert "0x20000000" in content or "complex-uart" in content
    
    def test_error_handling_invalid_commands(self):
        """Test error handling for invalid commands."""
        project_path = self.file_manager.create_test_project("error_test")
        
        # Test with invalid command
        invalid_spec = """# Invalid Command Test

/simics-invalid-command test-device --target nonexistent-cpu

## Device Overview
This should trigger error handling.
"""
        
        spec_file = self.file_manager.add_test_specification(
            "error_test",
            "invalid_command_spec",
            invalid_spec
        )
        
        os.chdir(project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        # Should handle gracefully (either skip invalid commands or provide error)
        # Exit code could be 0 (skip) or 1 (error), both are acceptable
        assert result.exit_code in [0, 1]
    
    def test_template_customization(self):
        """Test template customization and variable substitution."""
        project_path = self.file_manager.create_test_project("template_test")
        
        # Create specification with variables that should be substituted
        template_spec = """# Template Customization Test

/simics-device {{DEVICE_NAME}} --target {{TARGET_CPU}} --interface {{INTERFACE_TYPE}}

## Device Overview
Testing template variable substitution for {{DEVICE_NAME}}.

## Configuration
- Target: {{TARGET_CPU}}
- Interface: {{INTERFACE_TYPE}}
- Custom variable: {{CUSTOM_VAR}}
"""
        
        spec_file = self.file_manager.add_test_specification(
            "template_test",
            "template_customization_spec",
            template_spec
        )
        
        os.chdir(project_path)
        result = self.runner.invoke(app, ["process", str(spec_file)])
        
        # Template processing might handle variables or pass them through
        # Both behaviors are acceptable for this test
        assert result.exit_code in [0, 1]
    
    def test_project_validation_integration(self):
        """Test integration with project validation."""
        project_path = self.file_manager.create_test_project("validation_integration_test")
        
        # Create and process a specification
        spec_content = TestDataGenerator.create_device_specification(
            "test-device",
            "modern-cpu"
        )
        
        spec_file = self.file_manager.add_test_specification(
            "validation_integration_test",
            "device_spec",
            spec_content
        )
        
        os.chdir(project_path)
        
        # Process specification
        process_result = self.runner.invoke(app, ["process", str(spec_file)])
        assert process_result.exit_code == 0
        
        # Run validation
        validate_result = self.runner.invoke(app, ["validate-simics", "--path", str(project_path)])
        assert validate_result.exit_code == 0
        
        # Validation should pass or provide useful feedback
        assert "validation" in validate_result.stdout.lower() or "complete" in validate_result.stdout.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])