"""Simics Integration Validation Framework"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SimicsValidationError(Exception):
    """Exception raised when Simics validation fails"""
    pass


class SimicsTemplateValidator:
    """Validator for Simics integration templates and projects"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_simics_integration(self) -> Tuple[bool, List[str], List[str]]:
        """Validate complete Simics integration setup"""
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        # Validate template structure
        self._validate_template_structure()
        
        # Validate command templates
        self._validate_command_templates()
        
        # Validate script templates
        self._validate_script_templates()
        
        # Validate project structure templates
        self._validate_project_templates()
        
        return len(self.validation_errors) == 0, self.validation_errors, self.validation_warnings
    
    def _validate_template_structure(self):
        """Validate Simics template directory structure"""
        required_dirs = [
            "templates/simics",
            "templates/simics/projects", 
            "templates/simics/commands",
            "templates/simics/examples"
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                self.validation_errors.append(f"Missing required directory: {dir_path}")
            elif not full_path.is_dir():
                self.validation_errors.append(f"Path exists but is not a directory: {dir_path}")
    
    def _validate_command_templates(self):
        """Validate Simics command templates"""
        commands_dir = self.project_root / "templates" / "commands"
        required_commands = [
            "simics-device.md",
            "simics-platform.md", 
            "simics-validate.md"
        ]
        
        for cmd_file in required_commands:
            cmd_path = commands_dir / cmd_file
            if not cmd_path.exists():
                self.validation_errors.append(f"Missing command template: {cmd_file}")
                continue
            
            # Validate command template content
            try:
                content = cmd_path.read_text(encoding='utf-8')
                self._validate_command_template_content(cmd_file, content)
            except Exception as e:
                self.validation_errors.append(f"Error reading command template {cmd_file}: {e}")
    
    def _validate_command_template_content(self, filename: str, content: str):
        """Validate individual command template content"""
        # Check for YAML frontmatter
        if not content.startswith('---'):
            self.validation_errors.append(f"Command template {filename} missing YAML frontmatter")
            return
        
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break
        
        if frontmatter_end == -1:
            self.validation_errors.append(f"Command template {filename} has malformed YAML frontmatter")
            return
        
        frontmatter = '\n'.join(lines[1:frontmatter_end])
        
        # Check for required YAML fields
        required_fields = ['description', 'scripts']
        for field in required_fields:
            if f'{field}:' not in frontmatter:
                self.validation_errors.append(f"Command template {filename} missing required field: {field}")
        
        # Check for script variants
        if 'sh:' not in frontmatter:
            self.validation_errors.append(f"Command template {filename} missing bash script variant")
        if 'ps:' not in frontmatter:
            self.validation_errors.append(f"Command template {filename} missing PowerShell script variant")
        
        # Check for template placeholders
        template_body = '\n'.join(lines[frontmatter_end+1:])
        required_placeholders = ['{SCRIPT}', '{ARGS}']
        for placeholder in required_placeholders:
            if placeholder not in template_body:
                self.validation_warnings.append(f"Command template {filename} missing placeholder: {placeholder}")
    
    def _validate_script_templates(self):
        """Validate Simics script templates"""
        script_variants = [
            ("scripts/bash", [
                "setup-simics-device.sh",
                "setup-simics-platform.sh", 
                "setup-simics-validate.sh"
            ]),
            ("scripts/powershell", [
                "setup-simics-device.ps1",
                "setup-simics-platform.ps1",
                "setup-simics-validate.ps1"
            ])
        ]
        
        for script_dir, script_files in script_variants:
            dir_path = self.project_root / script_dir
            if not dir_path.exists():
                self.validation_errors.append(f"Missing script directory: {script_dir}")
                continue
            
            for script_file in script_files:
                script_path = dir_path / script_file
                if not script_path.exists():
                    self.validation_errors.append(f"Missing script file: {script_dir}/{script_file}")
                    continue
                
                # Validate script content
                try:
                    content = script_path.read_text(encoding='utf-8')
                    self._validate_script_content(script_file, content)
                except Exception as e:
                    self.validation_errors.append(f"Error reading script {script_file}: {e}")
    
    def _validate_script_content(self, filename: str, content: str):
        """Validate individual script content"""
        # Check for shebang
        if filename.endswith('.sh') and not content.startswith('#!/bin/bash'):
            self.validation_warnings.append(f"Script {filename} missing bash shebang")
        
        # Check for main function
        if 'main()' not in content:
            self.validation_errors.append(f"Script {filename} missing main() function")
        
        # Check for JSON output support
        if '--json' not in content:
            self.validation_errors.append(f"Script {filename} missing JSON output support")
        
        # Check for error handling
        if filename.endswith('.sh') and 'set -euo pipefail' not in content:
            self.validation_warnings.append(f"Script {filename} missing error handling (set -euo pipefail)")
    
    def _validate_project_templates(self):
        """Validate Simics project templates"""
        projects_dir = self.project_root / "templates" / "simics" / "projects"
        required_templates = [
            "device-spec-template.md",
            "platform-spec-template.md",
            "validation-template.md"
        ]
        
        for template_file in required_templates:
            template_path = projects_dir / template_file
            if not template_path.exists():
                self.validation_errors.append(f"Missing project template: {template_file}")
                continue
            
            # Validate template content
            try:
                content = template_path.read_text(encoding='utf-8')
                self._validate_project_template_content(template_file, content)
            except Exception as e:
                self.validation_errors.append(f"Error reading project template {template_file}: {e}")
    
    def _validate_project_template_content(self, filename: str, content: str):
        """Validate individual project template content"""
        # Check for execution flow
        if 'Execution Flow' not in content:
            self.validation_warnings.append(f"Project template {filename} missing execution flow section")
        
        # Check for mandatory sections marker
        if '*(mandatory)*' not in content:
            self.validation_warnings.append(f"Project template {filename} missing mandatory sections marker")
        
        # Check for review checklist
        if 'Review & Acceptance Checklist' not in content:
            self.validation_errors.append(f"Project template {filename} missing review checklist")
        
        # Check for execution status
        if 'Execution Status' not in content:
            self.validation_errors.append(f"Project template {filename} missing execution status section")


class SimicsProjectValidator:
    """Validator for Simics projects created with spec-kit"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_project_setup(self) -> Tuple[bool, List[str], List[str]]:
        """Validate Simics project setup"""
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        # Check project structure
        self._validate_project_directories()
        
        # Check template availability
        self._validate_template_availability()
        
        # Check script availability
        self._validate_script_availability()
        
        return len(self.validation_errors) == 0, self.validation_errors, self.validation_warnings
    
    def _validate_project_directories(self):
        """Validate project directory structure"""
        required_dirs = [
            ".specify",
            ".specify/templates", 
            ".specify/templates/simics",
            ".specify/scripts"
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_path / dir_path
            if not full_path.exists():
                self.validation_errors.append(f"Missing project directory: {dir_path}")
    
    def _validate_template_availability(self):
        """Validate template availability in project"""
        template_path = self.project_path / ".specify" / "templates" / "simics"
        if not template_path.exists():
            self.validation_errors.append("Simics templates not available in project")
            return
        
        # Check for key template files
        key_templates = [
            "projects/device-spec-template.md",
            "projects/platform-spec-template.md",
            "projects/validation-template.md"
        ]
        
        for template in key_templates:
            template_file = template_path / template
            if not template_file.exists():
                self.validation_warnings.append(f"Template not found: {template}")
    
    def _validate_script_availability(self):
        """Validate script availability in project"""
        scripts_path = self.project_path / ".specify" / "scripts"
        if not scripts_path.exists():
            self.validation_errors.append("Scripts directory not available in project")
            return
        
        # Check for either bash or PowerShell scripts
        bash_scripts = scripts_path / "bash"
        ps_scripts = scripts_path / "powershell"
        
        has_bash = bash_scripts.exists() and any(
            script.name.startswith("setup-simics-") 
            for script in bash_scripts.glob("*.sh")
        )
        
        has_powershell = ps_scripts.exists() and any(
            script.name.startswith("setup-simics-")
            for script in ps_scripts.glob("*.ps1")
        )
        
        if not (has_bash or has_powershell):
            self.validation_errors.append("No Simics setup scripts found")


class SimicsScriptTester:
    """Test runner for Simics scripts"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.test_results = []
    
    def test_scripts(self) -> Tuple[bool, List[Dict]]:
        """Test Simics scripts functionality"""
        self.test_results.clear()
        
        # Test bash scripts if available
        bash_scripts_path = self.project_path / ".specify" / "scripts" / "bash"
        if bash_scripts_path.exists():
            self._test_bash_scripts(bash_scripts_path)
        
        # Test PowerShell scripts if available
        ps_scripts_path = self.project_path / ".specify" / "scripts" / "powershell"
        if ps_scripts_path.exists():
            self._test_powershell_scripts(ps_scripts_path)
        
        # Check if all tests passed
        all_passed = all(result['passed'] for result in self.test_results)
        return all_passed, self.test_results
    
    def _test_bash_scripts(self, scripts_path: Path):
        """Test bash scripts"""
        if os.name == "nt":
            # Skip bash tests on Windows
            return
        
        simics_scripts = [
            "setup-simics-device.sh",
            "setup-simics-platform.sh",
            "setup-simics-validate.sh"
        ]
        
        for script_name in simics_scripts:
            script_path = scripts_path / script_name
            if script_path.exists():
                self._test_script_execution(script_path, "bash")
    
    def _test_powershell_scripts(self, scripts_path: Path):
        """Test PowerShell scripts"""
        simics_scripts = [
            "setup-simics-device.ps1",
            "setup-simics-platform.ps1", 
            "setup-simics-validate.ps1"
        ]
        
        for script_name in simics_scripts:
            script_path = scripts_path / script_name
            if script_path.exists():
                self._test_script_execution(script_path, "powershell")
    
    def _test_script_execution(self, script_path: Path, script_type: str):
        """Test individual script execution"""
        test_result = {
            'script': script_path.name,
            'type': script_type,
            'passed': False,
            'error': None,
            'output': None
        }
        
        try:
            # Test script with minimal input
            if script_type == "bash":
                cmd = ["bash", str(script_path), "--json", "test device"]
            else:  # powershell
                cmd = ["powershell", "-File", str(script_path), "-Json", "test device"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_path
            )
            
            test_result['output'] = result.stdout
            
            if result.returncode == 0:
                # Try to parse JSON output
                try:
                    json_output = json.loads(result.stdout)
                    if json_output.get('success'):
                        test_result['passed'] = True
                    else:
                        test_result['error'] = json_output.get('error', 'Script reported failure')
                except json.JSONDecodeError:
                    test_result['error'] = 'Invalid JSON output'
            else:
                test_result['error'] = f"Script failed with exit code {result.returncode}: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            test_result['error'] = 'Script execution timed out'
        except Exception as e:
            test_result['error'] = f'Test execution failed: {e}'
        
        self.test_results.append(test_result)


def validate_simics_integration(project_root: Path) -> Dict:
    """Main validation function for Simics integration"""
    validator = SimicsTemplateValidator(project_root)
    success, errors, warnings = validator.validate_simics_integration()
    
    return {
        'success': success,
        'errors': errors,
        'warnings': warnings,
        'summary': f"Validation {'passed' if success else 'failed'} with {len(errors)} errors and {len(warnings)} warnings"
    }


def validate_simics_project(project_path: Path) -> Dict:
    """Main validation function for Simics projects"""
    validator = SimicsProjectValidator(project_path)
    success, errors, warnings = validator.validate_project_setup()
    
    return {
        'success': success,
        'errors': errors,
        'warnings': warnings,
        'summary': f"Project validation {'passed' if success else 'failed'} with {len(errors)} errors and {len(warnings)} warnings"
    }


def test_simics_scripts(project_path: Path) -> Dict:
    """Main testing function for Simics scripts"""
    tester = SimicsScriptTester(project_path)
    success, results = tester.test_scripts()
    
    return {
        'success': success,
        'results': results,
        'summary': f"Script testing {'passed' if success else 'failed'} - {len([r for r in results if r['passed']])}/{len(results)} scripts passed"
    }