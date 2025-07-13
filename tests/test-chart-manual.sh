#!/bin/bash

# Manual chart testing script
set -e

echo "Testing chart rendering manually..."

# Test 1: Basic chart rendering
echo "Test 1: Basic chart rendering"
helm template test-release . > /tmp/rendered.yaml
echo "✅ Chart renders successfully"

# Test 2: Check for required resources
echo "Test 2: Check for required resources"
if grep -q "kind: Namespace" /tmp/rendered.yaml; then
    echo "✅ Namespace found"
else
    echo "❌ Namespace missing"
    exit 1
fi

if grep -q "kind: Deployment" /tmp/rendered.yaml; then
    echo "✅ Deployment found"
else
    echo "❌ Deployment missing"
    exit 1
fi

if grep -q "kind: Service" /tmp/rendered.yaml; then
    echo "✅ Service found"
else
    echo "❌ Service missing"
    exit 1
fi

if grep -q "kind: StatefulSet" /tmp/rendered.yaml; then
    echo "✅ StatefulSet found"
else
    echo "❌ StatefulSet missing"
    exit 1
fi

# Test 3: Check namespace consistency
echo "Test 3: Check namespace consistency"
NAMESPACE_COUNT=$(grep -c "namespace: haystack-rag" /tmp/rendered.yaml || echo "0")
echo "Found $NAMESPACE_COUNT resources with namespace 'haystack-rag'"

# Test 4: Test with custom values
echo "Test 4: Test with custom values"
helm template test-release . -f tests/test-values.yaml > /tmp/rendered-custom.yaml
echo "✅ Custom values render successfully"

# Test 5: Check custom namespace
echo "Test 5: Check custom namespace"
if grep -q "namespace: test-namespace" /tmp/rendered-custom.yaml; then
    echo "✅ Custom namespace applied"
else
    echo "❌ Custom namespace not applied"
    exit 1
fi

echo "All manual tests passed! 🎉" 