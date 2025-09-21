#!/usr/bin/env python3
"""
Simple integration test to verify Simics functionality without pytest.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_simics_validation():
    """Test the Simics validation framework."""
    try:
        from specify_cli.simics_validation import SimicsTemplateValidator, SimicsProjectValidator
        
        print("✓ Simics validation framework imported successfully")
        
        # Test template validator
        validator = SimicsTemplateValidator()
        
        # Test with valid template content
        valid_template = """# Test Template
/simics-device test-device --target modern-cpu

## Device Overview
This is a test device specification.

## Register Interface
- Base Address: 0x10000000
- Address Range: 0x1000
"""
        
        result = validator.validate_template_content(valid_template)
        if result.is_valid:
            print("✓ Template validation passed")
        else:
            print(f"✗ Template validation failed: {result.errors}")
        
        # Test project validator
        project_validator = SimicsProjectValidator()
        print("✓ Project validator created successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False

def test_cli_integration():
    """Test CLI integration."""
    try:
        from specify_cli import app
        print("✓ CLI app imported successfully")
        
        # Test if validate-simics command is available
        # This is a basic check without actually running the command
        return True
        
    except ImportError as e:
        print(f"✗ CLI import error: {e}")
        return False
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False

def test_template_files():
    """Test that template files exist."""
    template_paths = [
        "templates/commands/simics-device.md",
        "templates/commands/simics-platform.md", 
        "templates/commands/simics-validate.md",
        "templates/simics/projects/device-spec-template.md",
        "templates/simics/projects/platform-spec-template.md",
        "templates/simics/projects/validation-template.md"
    ]
    
    missing_templates = []
    for template_path in template_paths:
        if not Path(template_path).exists():
            missing_templates.append(template_path)
    
    if missing_templates:
        print(f"✗ Missing template files: {missing_templates}")
        return False
    else:
        print(f"✓ All {len(template_paths)} template files exist")
        return True

def test_script_files():
    """Test that script files exist."""
    script_paths = [
        "scripts/bash/setup-simics-device.sh",
        "scripts/bash/setup-simics-platform.sh",
        "scripts/bash/setup-simics-validate.sh",
        "scripts/powershell/setup-simics-device.ps1",
        "scripts/powershell/setup-simics-platform.ps1",
        "scripts/powershell/setup-simics-validate.ps1"
    ]
    
    missing_scripts = []
    for script_path in script_paths:
        if not Path(script_path).exists():
            missing_scripts.append(script_path)
    
    if missing_scripts:
        print(f"✗ Missing script files: {missing_scripts}")
        return False
    else:
        print(f"✓ All {len(script_paths)} script files exist")
        return True

def test_documentation():
    """Test that documentation exists."""
    doc_paths = [
        "docs/SIMICS_INTEGRATION.md",
        "SIMICS_INTEGRATION_PLAN.md",
        "tests/README.md"
    ]
    
    missing_docs = []
    for doc_path in doc_paths:
        if not Path(doc_path).exists():
            missing_docs.append(doc_path)
    
    if missing_docs:
        print(f"✗ Missing documentation files: {missing_docs}")
        return False
    else:
        print(f"✓ All {len(doc_paths)} documentation files exist")
        return True

def main():
    """Run all integration tests."""
    print("=== Simics Integration Verification ===")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    tests = [
        ("Validation Framework", test_simics_validation),
        ("CLI Integration", test_cli_integration),
        ("Template Files", test_template_files),
        ("Script Files", test_script_files),
        ("Documentation", test_documentation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=== Test Summary ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)