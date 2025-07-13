# Helm Chart Testing Framework

This directory contains a comprehensive testing framework for the Haystack RAG Helm chart.

## Overview

The testing framework uses Python to provide reliable, comprehensive testing of Helm chart functionality without relying on external plugins that may have compatibility issues.

## Test Structure

### Core Testing Files
- **`run-tests.py`**: Main testing framework that validates chart rendering and functionality
- **`generate-report.py`**: Generates XUnit format test reports for CI integration
- **`test-values.yaml`**: Test values for validating custom configurations

### Test Coverage

The framework tests:

#### ✅ Chart Rendering
- Basic chart rendering with default values
- Chart rendering with custom values
- Template syntax validation

#### ✅ Resource Validation
- All required Kubernetes resources (Namespace, Deployments, Services, StatefulSet, PVC, Secret, ConfigMap)
- Specific named resources (rag-frontend, rag-query, rag-indexing, opensearch, etc.)
- Resource naming consistency

#### ✅ Configuration Validation
- Namespace consistency across all resources
- Custom namespace application
- Service selectors and port configurations
- Image references and versions
- Environment variable configuration

#### ✅ Integration Testing
- End-to-end chart functionality
- Custom values processing
- Template variable substitution

## Running Tests

### Prerequisites
```bash
# Install Python dependencies
pip install pyyaml kubernetes

# Ensure Helm is installed
helm version
```

### Local Testing
```bash
# Run all tests
python tests/run-tests.py

# Generate test report
python tests/generate-report.py
```

### CI Integration
The tests are automatically run in the GitHub Actions workflow:
1. **Helm lint** - Validates chart syntax
2. **Schema validation** - Validates Kubernetes resources with kubeconform
3. **Comprehensive testing** - Runs all validation tests
4. **Report generation** - Creates XUnit format reports
5. **Artifact upload** - Saves test results

## Test Results

### Output Files
- **`test-results.json`**: Detailed test results in JSON format
- **`test-report.xml`**: XUnit format report for CI integration

### Sample Output
```
🚀 Starting Helm Chart Testing...
==================================================
🧪 Testing chart rendering...
✅ PASS Chart Rendering: Chart renders successfully
🧪 Testing custom values rendering...
✅ PASS Custom Values Rendering: Custom values render successfully
🧪 Testing required resources...
✅ PASS Required Resources: All required resources found
...

📋 TEST SUMMARY
==================================================
Total tests: 10
Passed: 10
Failed: 0
🎉 All tests passed!
```

## Adding New Tests

To add new tests to the framework:

1. **Add test method** to `HelmChartTester` class in `run-tests.py`:
```python
def test_new_functionality(self) -> TestResult:
    """Test new functionality"""
    print("🧪 Testing new functionality...")
    # Your test logic here
    if condition:
        return TestResult("New Functionality", True, "Test passed")
    else:
        return TestResult("New Functionality", False, "Test failed")
```

2. **Register the test** in the `run_all_tests()` method:
```python
tests = [
    # ... existing tests ...
    self.test_new_functionality
]
```

## Benefits

### ✅ Reliability
- No external plugin dependencies
- Consistent behavior across environments
- Clear error messages and debugging

### ✅ Comprehensiveness
- Tests all critical chart functionality
- Validates both default and custom configurations
- Checks resource relationships and dependencies

### ✅ Maintainability
- Simple Python codebase
- Easy to extend and modify
- Clear test structure and organization

### ✅ CI Integration
- Generates standard XUnit reports
- Provides detailed test results
- Integrates seamlessly with GitHub Actions

## Troubleshooting

### Common Issues

**Test fails with "Chart rendering failed"**
- Check that Helm is installed and working
- Verify Chart.yaml and values.yaml are valid
- Ensure all template files are properly formatted

**Missing resources in tests**
- Update the `required_resources` list in `test_required_resources()`
- Add new resource patterns to match your chart structure

**Custom values not working**
- Verify `tests/test-values.yaml` contains valid YAML
- Check that custom values are being applied correctly in templates

### Debugging
- Tests provide detailed output for each step
- Check `test-results.json` for detailed failure information
- Review rendered YAML output for template issues 