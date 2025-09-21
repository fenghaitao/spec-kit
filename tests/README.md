# Simics Integration Tests

This directory contains comprehensive tests for the Spec-Kit Simics integration functionality.

## Test Structure

### Test Files

1. **test_simics_integration.py** - Main integration test suite
   - Tests for all three Simics commands (device, platform, validate)
   - Template validation testing
   - Project validation testing
   - Command-line integration testing
   - Error handling testing

2. **test_simics_e2e.py** - End-to-end testing
   - Complete workflow testing
   - Multi-command specification processing
   - Parameter parsing and validation
   - Template customization testing

3. **test_config.py** - Test configuration and utilities
   - Test data generators
   - Mock environment setup
   - File management utilities
   - Configuration constants

### Support Files

- **__init__.py** - Test package initialization
- **pytest.ini** - Pytest configuration
- **run_simics_tests.py** - Comprehensive test runner script

## Running Tests

### Quick Start

```bash
# Run all Simics tests
python run_simics_tests.py

# Run with individual test reporting
python run_simics_tests.py --individual

# Run using pytest directly
pytest tests/test_simics_*.py -v
```

### Prerequisites

Install required testing dependencies:

```bash
pip install pytest pytest-cov typer
```

### Test Categories

The tests are organized into several categories:

#### Unit Tests
- Template validation
- Command parsing
- Parameter processing
- Error handling

#### Integration Tests
- Command processing workflows
- File generation validation
- CLI integration
- Validation framework testing

#### End-to-End Tests
- Complete specification processing
- Multi-command workflows
- Project validation
- Cross-component integration

## Test Coverage

The test suite aims for comprehensive coverage of:

- **Command Processing**: All three Simics commands (device, platform, validate)
- **Template Generation**: Device, platform, and validation templates
- **Script Integration**: Bash and PowerShell script generation
- **Validation Framework**: Template and project validation
- **Error Handling**: Invalid commands, malformed specifications, missing parameters
- **CLI Integration**: Command-line interface functionality

## Test Data

Test data is generated dynamically using the `TestDataGenerator` class, which creates:

- Device specifications with various parameters
- Platform specifications for different architectures
- Validation specifications with different coverage requirements
- Multi-command specifications for integration testing

## Mock Environment

The `MockSimicsEnvironment` class provides:

- Simulated Simics environment
- Target validation
- Device model validation
- Configuration information

## Running Specific Tests

### Run only integration tests
```bash
pytest tests/test_simics_integration.py -v
```

### Run only end-to-end tests
```bash
pytest tests/test_simics_e2e.py -v
```

### Run with coverage reporting
```bash
pytest tests/test_simics_*.py --cov=specify_cli --cov-report=html
```

### Run specific test methods
```bash
pytest tests/test_simics_integration.py::TestSimicsIntegration::test_simics_device_command_basic -v
```

## Test Output

Tests generate temporary projects and files in system temp directories. These are automatically cleaned up after each test.

Key verification points:
- File generation (DML files, Simics scripts, Python test files)
- Content validation (proper syntax, required elements)
- Integration validation (CLI processing, validation framework)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure specify_cli package is in Python path
2. **Missing Dependencies**: Install pytest and other test dependencies
3. **Permission Errors**: Ensure write access to temp directories
4. **Timeout Issues**: Increase timeout in test configuration if needed

### Debug Mode

Run tests with verbose output:
```bash
pytest tests/test_simics_*.py -v -s
```

### Test Isolation

Each test method uses isolated temporary directories to prevent interference between tests.

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use the provided test utilities and data generators
3. Ensure proper cleanup in teardown methods
4. Add appropriate test markers (@pytest.mark.simics, etc.)
5. Update this documentation for significant additions

## Test Results

Test results are saved to `simics_test_report.md` in the spec-kit root directory when using the test runner script.