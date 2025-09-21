"""
Test configuration and utilities for Simics integration tests.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# Test configuration constants
TEST_CONFIG = {
    "simics_commands": {
        "device": {
            "required_params": ["device_name", "target"],
            "optional_params": ["interface", "base_address", "interrupt"],
            "expected_outputs": [".dml", ".simics", "-test.py"]
        },
        "platform": {
            "required_params": ["platform_name", "cpu"],
            "optional_params": ["memory", "storage", "devices"],
            "expected_outputs": [".simics", "-devices.py", "-setup.py"]
        },
        "validate": {
            "required_params": ["validation_name", "target"],
            "optional_params": ["coverage", "test_types", "performance"],
            "expected_outputs": ["-suite.py", "-config.json", "-report.py"]
        }
    },
    "validation_rules": {
        "template_requirements": [
            "Must contain at least one Simics command",
            "Must have proper YAML frontmatter",
            "Must include device/platform overview",
            "Must specify implementation requirements"
        ],
        "project_structure": [
            "Generated files must have proper extensions",
            "Script files must be executable",
            "Configuration files must be valid JSON/YAML"
        ]
    },
    "test_scenarios": {
        "basic_device": {
            "command": "/simics-device uart-controller --target modern-cpu",
            "expected_files": ["uart-controller.dml", "uart-controller.simics"],
            "validation_checks": ["syntax", "completeness", "executable"]
        },
        "basic_platform": {
            "command": "/simics-platform embedded-system --cpu arm-cortex-a53",
            "expected_files": ["embedded-system.simics", "embedded-system-setup.py"],
            "validation_checks": ["syntax", "completeness", "dependencies"]
        },
        "basic_validation": {
            "command": "/simics-validate device-test --target uart-controller",
            "expected_files": ["device-test-suite.py", "device-test-config.json"],
            "validation_checks": ["syntax", "test_coverage", "automation"]
        }
    }
}

class TestDataGenerator:
    """Generate test data for Simics integration tests."""
    
    @staticmethod
    def create_device_specification(device_name: str, target: str, **kwargs) -> str:
        """Create a test device specification."""
        base_address = kwargs.get("base_address", "0x10000000")
        interface = kwargs.get("interface", "memory-mapped")
        
        return f"""# {device_name.title()} Device Specification

/simics-device {device_name} --target {target} --interface {interface} --base-address {base_address}

## Device Overview
Test {device_name} device for {target} target platform.

## Register Interface
- Base Address: {base_address}
- Address Range: 0x1000
- Interface Type: {interface}

## Implementation Requirements
- DML-based device model
- Interrupt support capability
- Register access validation
- Performance optimization

## Behavioral Model
The device implements standard {device_name} functionality with:
1. Data transmission/reception
2. Status monitoring
3. Interrupt generation
4. Error handling

## Integration Points
- Memory mapping at {base_address}
- Interrupt lines as configured
- Clock domain integration
- Reset signal handling
"""
    
    @staticmethod
    def create_platform_specification(platform_name: str, cpu: str, **kwargs) -> str:
        """Create a test platform specification."""
        memory = kwargs.get("memory", "1GB")
        storage = kwargs.get("storage", "32GB eMMC")
        
        return f"""# {platform_name.title()} Platform Specification

/simics-platform {platform_name} --cpu {cpu} --memory {memory}

## Platform Overview
Test {platform_name} platform based on {cpu} processor.

## System Architecture
- CPU: {cpu}
- Memory: {memory} DDR4
- Storage: {storage}
- Boot Method: U-Boot + Linux

## Device Integration
- UART controllers: 2x for console/debug
- GPIO controllers: 4x for general purpose
- SPI controllers: 2x for peripheral communication
- I2C controllers: 2x for sensor integration

## Memory Map
- System RAM: 0x40000000 - 0x7FFFFFFF
- Device MMIO: 0x10000000 - 0x1FFFFFFF
- Boot ROM: 0x00000000 - 0x0000FFFF

## Platform Configuration
- Clock frequencies optimized for simulation
- Interrupt routing configured
- Power management support
- Debug interface enabled
"""
    
    @staticmethod
    def create_validation_specification(validation_name: str, target: str, **kwargs) -> str:
        """Create a test validation specification."""
        coverage = kwargs.get("coverage", "90%")
        test_types = kwargs.get("test_types", "functional,performance,stress")
        
        return f"""# {validation_name.title()} Validation Specification

/simics-validate {validation_name} --target {target} --coverage {coverage}

## Validation Overview
Comprehensive validation suite for {target} component.

## Test Coverage Requirements
- Functional Coverage: {coverage}
- Code Coverage: 85%
- Performance Testing: Required
- Stress Testing: Required

## Test Scenarios
1. Basic functionality verification
2. Edge case handling
3. Performance benchmarking
4. Stress testing under load
5. Error condition testing
6. Integration testing

## Test Types
{test_types.replace(',', ', ')}

## Automation Requirements
- Continuous integration support
- Automated report generation
- Performance trend analysis
- Regression testing capability

## Success Criteria
- All functional tests pass
- Coverage targets met
- Performance within specifications
- No critical issues identified
"""

class TestFileManager:
    """Manage test files and directories."""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.test_projects = {}
    
    def create_test_project(self, project_name: str, project_type: str = "mixed") -> Path:
        """Create a test project directory structure."""
        project_path = self.base_path / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create standard directories
        directories = ["templates", "scripts", "docs", "tests", "generated"]
        for directory in directories:
            (project_path / directory).mkdir(exist_ok=True)
        
        # Create Simics-specific directories
        simics_dirs = [
            "templates/simics/commands",
            "templates/simics/projects",
            "scripts/bash",
            "scripts/powershell"
        ]
        for simics_dir in simics_dirs:
            (project_path / simics_dir).mkdir(parents=True, exist_ok=True)
        
        self.test_projects[project_name] = {
            "path": project_path,
            "type": project_type,
            "created_files": []
        }
        
        return project_path
    
    def add_test_specification(self, project_name: str, spec_name: str, spec_content: str) -> Path:
        """Add a test specification to a project."""
        if project_name not in self.test_projects:
            raise ValueError(f"Project {project_name} not found")
        
        project_path = self.test_projects[project_name]["path"]
        spec_file = project_path / f"{spec_name}.md"
        spec_file.write_text(spec_content)
        
        self.test_projects[project_name]["created_files"].append(spec_file)
        return spec_file
    
    def cleanup_project(self, project_name: str):
        """Clean up a test project."""
        if project_name in self.test_projects:
            import shutil
            project_path = self.test_projects[project_name]["path"]
            if project_path.exists():
                shutil.rmtree(project_path)
            del self.test_projects[project_name]

class MockSimicsEnvironment:
    """Mock Simics environment for testing."""
    
    def __init__(self):
        self.simics_version = "6.0.185"
        self.available_targets = [
            "modern-cpu",
            "arm-cortex-a53",
            "x86-64",
            "risc-v-rv64",
            "power-pc"
        ]
        self.device_models = [
            "uart-controller",
            "gpio-controller",
            "spi-controller",
            "i2c-controller",
            "ethernet-controller"
        ]
    
    def validate_target(self, target: str) -> bool:
        """Validate if target is supported."""
        return target in self.available_targets
    
    def validate_device(self, device: str) -> bool:
        """Validate if device model is supported."""
        return any(device in model for model in self.device_models)
    
    def get_target_info(self, target: str) -> Dict[str, Any]:
        """Get information about a target."""
        target_info = {
            "modern-cpu": {
                "architecture": "x64",
                "features": ["virtualization", "advanced-debug"],
                "memory_limit": "64GB"
            },
            "arm-cortex-a53": {
                "architecture": "aarch64",
                "features": ["neon", "crypto", "virtualization"],
                "memory_limit": "4GB"
            }
        }
        return target_info.get(target, {})

def save_test_config(config_path: Path):
    """Save test configuration to file."""
    with open(config_path, 'w') as f:
        json.dump(TEST_CONFIG, f, indent=2)

def load_test_config(config_path: Path) -> Dict[str, Any]:
    """Load test configuration from file."""
    with open(config_path, 'r') as f:
        return json.load(f)