#!/usr/bin/env python3
"""
Test runner for Simics integration tests.

This script runs all Simics-related tests and provides comprehensive reporting.
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json


class SimicsTestRunner:
    """Runner for Simics integration tests."""
    
    def __init__(self, spec_kit_root: Path):
        self.spec_kit_root = Path(spec_kit_root)
        self.test_dir = self.spec_kit_root / "tests"
        self.results = {}
        
    def discover_test_files(self) -> List[Path]:
        """Discover all Simics-related test files."""
        test_patterns = [
            "test_simics_*.py",
            "*_simics_test.py",
            "test_*simics*.py"
        ]
        
        test_files = []
        for pattern in test_patterns:
            test_files.extend(list(self.test_dir.glob(pattern)))
        
        return sorted(test_files)
    
    def run_pytest(self, test_files: List[Path], verbose: bool = True, coverage: bool = True) -> Dict[str, Any]:
        """Run pytest on the specified test files."""
        cmd = ["python", "-m", "pytest"]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend([
                "--cov=specify_cli",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov"
            ])
        
        # Add test files
        cmd.extend([str(f) for f in test_files])
        
        print(f"Running command: {' '.join(cmd)}")
        print(f"Working directory: {self.spec_kit_root}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.spec_kit_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Test execution timed out after 5 minutes",
                "success": False
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Test execution failed: {str(e)}",
                "success": False
            }
    
    def run_individual_tests(self, test_files: List[Path]) -> Dict[str, Dict[str, Any]]:
        """Run each test file individually for detailed reporting."""
        individual_results = {}
        
        for test_file in test_files:
            print(f"\nRunning individual test: {test_file.name}")
            
            result = self.run_pytest([test_file], verbose=True, coverage=False)
            individual_results[test_file.name] = result
            
            if result["success"]:
                print(f"✓ {test_file.name} passed")
            else:
                print(f"✗ {test_file.name} failed")
                if result["stderr"]:
                    print(f"Error output: {result['stderr'][:500]}...")
        
        return individual_results
    
    def validate_test_environment(self) -> Dict[str, Any]:
        """Validate the test environment setup."""
        validation_results = {
            "spec_kit_root_exists": self.spec_kit_root.exists(),
            "test_dir_exists": self.test_dir.exists(),
            "specify_cli_importable": False,
            "pytest_available": False,
            "required_modules": {}
        }
        
        # Check if specify_cli is importable
        try:
            import specify_cli
            validation_results["specify_cli_importable"] = True
        except ImportError as e:
            validation_results["specify_cli_import_error"] = str(e)
        
        # Check if pytest is available
        try:
            import pytest
            validation_results["pytest_available"] = True
            validation_results["pytest_version"] = pytest.__version__
        except ImportError:
            validation_results["pytest_available"] = False
        
        # Check required test modules
        required_modules = ["typer", "pathlib", "tempfile", "unittest.mock"]
        for module in required_modules:
            try:
                __import__(module)
                validation_results["required_modules"][module] = True
            except ImportError:
                validation_results["required_modules"][module] = False
        
        return validation_results
    
    def generate_report(self, test_results: Dict[str, Any], individual_results: Dict[str, Dict[str, Any]]) -> str:
        """Generate a comprehensive test report."""
        report_lines = [
            "# Simics Integration Test Report",
            "",
            "## Summary",
            f"- Overall Success: {'✓' if test_results['success'] else '✗'}",
            f"- Return Code: {test_results['returncode']}",
            "",
            "## Individual Test Results"
        ]
        
        for test_name, result in individual_results.items():
            status = '✓' if result['success'] else '✗'
            report_lines.append(f"- {status} {test_name}")
        
        report_lines.extend([
            "",
            "## Test Output",
            "### Standard Output",
            "```",
            test_results["stdout"][:2000] + ("..." if len(test_results["stdout"]) > 2000 else ""),
            "```",
            "",
            "### Standard Error",
            "```",
            test_results["stderr"][:1000] + ("..." if len(test_results["stderr"]) > 1000 else ""),
            "```"
        ])
        
        return "\n".join(report_lines)
    
    def run_all_tests(self, individual: bool = False, save_report: bool = True) -> bool:
        """Run all Simics integration tests."""
        print("Starting Simics Integration Test Suite")
        print(f"Spec-Kit Root: {self.spec_kit_root}")
        
        # Validate environment
        print("\n=== Environment Validation ===")
        env_validation = self.validate_test_environment()
        
        for key, value in env_validation.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    status = '✓' if sub_value else '✗'
                    print(f"  {status} {sub_key}")
            else:
                status = '✓' if value else '✗'
                print(f"{status} {key}")
        
        if not env_validation["spec_kit_root_exists"]:
            print("ERROR: Spec-Kit root directory not found")
            return False
        
        if not env_validation["pytest_available"]:
            print("ERROR: pytest not available. Install with: pip install pytest pytest-cov")
            return False
        
        # Discover tests
        print("\n=== Test Discovery ===")
        test_files = self.discover_test_files()
        
        if not test_files:
            print("No Simics test files found")
            return False
        
        print(f"Found {len(test_files)} test files:")
        for test_file in test_files:
            print(f"  - {test_file.name}")
        
        # Run tests
        print("\n=== Running Tests ===")
        
        individual_results = {}
        if individual:
            individual_results = self.run_individual_tests(test_files)
        
        # Run all tests together
        print("\nRunning all tests together...")
        overall_results = self.run_pytest(test_files, verbose=True, coverage=True)
        
        # Generate and save report
        if save_report:
            report_content = self.generate_report(overall_results, individual_results)
            report_file = self.spec_kit_root / "simics_test_report.md"
            report_file.write_text(report_content)
            print(f"\nTest report saved to: {report_file}")
        
        # Print summary
        print("\n=== Test Summary ===")
        print(f"Overall Result: {'PASSED' if overall_results['success'] else 'FAILED'}")
        print(f"Return Code: {overall_results['returncode']}")
        
        if individual_results:
            passed = sum(1 for r in individual_results.values() if r['success'])
            total = len(individual_results)
            print(f"Individual Tests: {passed}/{total} passed")
        
        return overall_results['success']


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Run Simics integration tests")
    parser.add_argument(
        "--spec-kit-root",
        default=".",
        help="Path to spec-kit root directory (default: current directory)"
    )
    parser.add_argument(
        "--individual",
        action="store_true",
        help="Run each test file individually for detailed reporting"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Don't save test report to file"
    )
    
    args = parser.parse_args()
    
    runner = SimicsTestRunner(Path(args.spec_kit_root))
    success = runner.run_all_tests(
        individual=args.individual,
        save_report=not args.no_report
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()