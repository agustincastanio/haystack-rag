# Helm Chart Tests

This directory contains comprehensive tests for the Haystack RAG Helm chart.

## Test Structure

### Unit Tests (`tests/unit/`)
- **test-deployments.yaml**: Tests for deployment templates
- **test-opensearch.yaml**: Tests for OpenSearch StatefulSet and PVC
- **test-services.yaml**: Tests for service templates
- **test-ingress.yaml**: Tests for ingress and middleware
- **test-secrets-configmap.yaml**: Tests for secrets and configmap

### Integration Tests (`tests/integration/`)
- **test-chart-integration.yaml**: Tests the entire chart as a whole

### End-to-End Tests (`templates/tests/`)
- **test-connection.yaml**: Tests connectivity between components
- **test-opensearch.yaml**: Tests OpenSearch functionality

## Running Tests

### Prerequisites
```bash
# Install helm-unittest plugin
helm plugin install https://github.com/quintush/helm-unittest

# Install jq for JSON parsing in tests
# On Ubuntu/Debian: sudo apt-get install jq
# On macOS: brew install jq
# On Windows: choco install jq
```

### Unit and Integration Tests
```bash
# Run all unit tests
helm unittest tests/unit/

# Run all integration tests
helm unittest tests/integration/

# Run all tests with coverage report
helm unittest --output-type XUnit --output-file test-report.xml .
```

### End-to-End Tests
```bash
# Install the chart
helm install test-release . --namespace test-namespace --create-namespace

# Run the tests
helm test test-release

# Clean up
helm uninstall test-release
```

### Manual Testing
```bash
# Test chart rendering
helm template test-release . > rendered.yaml

# Validate with kubeconform
helm template test-release . | kubeconform -strict

# Test with different values
helm template test-release . -f values.yaml -f test-values.yaml
```

## Test Values

Create `test-values.yaml` for testing with different configurations:

```yaml
namespace: test-namespace
hostname: test.example.com
image:
  registry: test.registry.com
  tag: test-tag
opensearch:
  replicaCount: 2
  storageSize: 20Gi
secret:
  opensearchPassword: TestPassword123!
  openaiApiKey: sk-test-key
```

## Continuous Integration

The tests are integrated into the CI pipeline in `.github/workflows/chart-ci.yml`:

1. **Lint**: Helm strict linting
2. **Schema Validation**: kubeconform validation
3. **Unit Tests**: helm-unittest execution
4. **Integration Tests**: Full chart rendering tests

## Test Coverage

The test suite covers:

- ✅ Template rendering with default values
- ✅ Template rendering with custom values
- ✅ Resource naming and namespacing
- ✅ Service selectors and port configurations
- ✅ Deployment configurations
- ✅ OpenSearch StatefulSet and PVC
- ✅ Ingress and middleware configurations
- ✅ Secrets and ConfigMap structure
- ✅ Component connectivity
- ✅ OpenSearch functionality

## Adding New Tests

1. Create test file in appropriate directory (`tests/unit/` or `tests/integration/`)
2. Follow the helm-unittest format
3. Add test to CI pipeline if needed
4. Update this README with new test information 