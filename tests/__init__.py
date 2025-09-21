"""
Test package for spec-kit Simics integration.

This package contains comprehensive tests for the Simics integration functionality,
including unit tests, integration tests, and end-to-end tests.
"""

# Version information
__version__ = "1.0.0"
__author__ = "Spec-Kit Development Team"

# Test configuration
TEST_CONFIG = {
    "simics_integration": {
        "version": "1.0.0",
        "supported_targets": ["modern-cpu", "arm-cortex-a53", "x86-64", "risc-v-rv64"],
        "supported_commands": ["simics-device", "simics-platform", "simics-validate"],
        "test_timeout": 300,  # 5 minutes
        "temp_dir_prefix": "spec_kit_simics_test_"
    }
}

# Export test utilities
from .test_config import (
    TestDataGenerator,
    TestFileManager,
    MockSimicsEnvironment,
    TEST_CONFIG as CONFIG
)

__all__ = [
    "TestDataGenerator",
    "TestFileManager", 
    "MockSimicsEnvironment",
    "CONFIG",
    "TEST_CONFIG"
]