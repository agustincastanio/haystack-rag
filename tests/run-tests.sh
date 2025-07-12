#!/bin/bash

# Test runner script for Haystack RAG Helm chart
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v helm &> /dev/null; then
        print_error "Helm is not installed"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed. Some tests may fail."
    fi
    
    # Check if helm-unittest plugin is installed
    if ! helm plugin list | grep -q "unittest"; then
        print_status "Installing helm-unittest plugin..."
        helm plugin install https://github.com/quintush/helm-unittest
    fi
    
    print_status "Prerequisites check completed"
}

# Run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    if helm unittest tests/unit/; then
        print_status "Unit tests passed"
    else
        print_error "Unit tests failed"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    if helm unittest tests/integration/; then
        print_status "Integration tests passed"
    else
        print_error "Integration tests failed"
        return 1
    fi
}

# Run chart linting
run_lint() {
    print_status "Running Helm lint..."
    if helm lint . --strict; then
        print_status "Helm lint passed"
    else
        print_error "Helm lint failed"
        return 1
    fi
}

# Run schema validation
run_schema_validation() {
    print_status "Running schema validation..."
    if command -v kubeconform &> /dev/null; then
        if helm template . | kubeconform -strict -summary -skip IngressRoute,Middleware,ServersTransport; then
            print_status "Schema validation passed"
        else
            print_error "Schema validation failed"
            return 1
        fi
    else
        print_warning "kubeconform not found, skipping schema validation"
    fi
}

# Test with custom values
test_custom_values() {
    print_status "Testing with custom values..."
    if helm template test-release . -f tests/test-values.yaml > /dev/null; then
        print_status "Custom values test passed"
    else
        print_error "Custom values test failed"
        return 1
    fi
}

# Generate test report
generate_report() {
    print_status "Generating test report..."
    helm unittest --output-type XUnit --output-file test-report.xml . || true
    if [ -f test-report.xml ]; then
        print_status "Test report generated: test-report.xml"
    fi
}

# Main execution
main() {
    print_status "Starting Helm chart tests..."
    
    # Change to chart directory
    cd "$(dirname "$0")/.."
    
    check_prerequisites
    
    # Run tests
    local exit_code=0
    
    run_lint || exit_code=1
    run_schema_validation || exit_code=1
    run_unit_tests || exit_code=1
    run_integration_tests || exit_code=1
    test_custom_values || exit_code=1
    generate_report
    
    if [ $exit_code -eq 0 ]; then
        print_status "All tests passed! 🎉"
    else
        print_error "Some tests failed! ❌"
    fi
    
    exit $exit_code
}

# Run main function
main "$@" 