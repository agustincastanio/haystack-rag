#!/usr/bin/env python3
"""
Comprehensive Helm Chart Testing Framework
Tests chart rendering, validation, and functionality
"""

import yaml
import subprocess
import json
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    details: Optional[Dict] = None

class HelmChartTester:
    def __init__(self, chart_dir: str = "."):
        self.chart_dir = chart_dir
        self.results: List[TestResult] = []
        self.rendered_yaml = ""
        self.rendered_custom_yaml = ""
        
    def run_command(self, cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and return the result"""
        try:
            result = subprocess.run(cmd, capture_output=capture_output, text=True, cwd=self.chart_dir)
            return result
        except Exception as e:
            return subprocess.CompletedProcess(cmd, -1, "", str(e))

    def test_chart_rendering(self) -> TestResult:
        """Test basic chart rendering"""
        print("🧪 Testing chart rendering...")
        result = self.run_command(["helm", "template", "test-release", ".", "-f", "values.yaml"])
        
        if result.returncode == 0:
            self.rendered_yaml = result.stdout
            return TestResult("Chart Rendering", True, "Chart renders successfully")
        else:
            return TestResult("Chart Rendering", False, f"Chart rendering failed: {result.stderr}")

    def test_custom_values_rendering(self) -> TestResult:
        """Test chart rendering with custom values"""
        print("🧪 Testing custom values rendering...")
        result = self.run_command(["helm", "template", "test-release", ".", "-f", "tests/test-values.yaml"])
        
        if result.returncode == 0:
            self.rendered_custom_yaml = result.stdout
            return TestResult("Custom Values Rendering", True, "Custom values render successfully")
        else:
            return TestResult("Custom Values Rendering", False, f"Custom values rendering failed: {result.stderr}")

    def test_required_resources(self) -> TestResult:
        """Test that all required resources are present"""
        print("🧪 Testing required resources...")
        required_resources = [
            ("Namespace", "kind: Namespace"),
            ("Deployment", "kind: Deployment"),
            ("Service", "kind: Service"),
            ("StatefulSet", "kind: StatefulSet"),
            ("PersistentVolumeClaim", "kind: PersistentVolumeClaim"),
            ("Secret", "kind: Secret"),
            ("ConfigMap", "kind: ConfigMap")
        ]
        
        missing_resources = []
        for resource_name, resource_pattern in required_resources:
            if resource_pattern not in self.rendered_yaml:
                missing_resources.append(resource_name)
        
        if not missing_resources:
            return TestResult("Required Resources", True, "All required resources found")
        else:
            return TestResult("Required Resources", False, f"Missing resources: {', '.join(missing_resources)}")

    def test_specific_resources(self) -> TestResult:
        """Test that specific named resources are present"""
        print("🧪 Testing specific resources...")
        required_names = [
            "rag-frontend",
            "rag-query", 
            "rag-indexing",
            "opensearch",
            "rag-secrets",
            "rag-config"
        ]
        
        missing_names = []
        for name in required_names:
            if f"name: {name}" not in self.rendered_yaml:
                missing_names.append(name)
        
        if not missing_names:
            return TestResult("Specific Resources", True, "All specific resources found")
        else:
            return TestResult("Specific Resources", False, f"Missing resources: {', '.join(missing_names)}")

    def test_namespace_consistency(self) -> TestResult:
        """Test that all resources use the correct namespace"""
        print("🧪 Testing namespace consistency...")
        namespace_count = self.rendered_yaml.count("namespace: haystack-rag")
        
        if namespace_count > 0:
            return TestResult("Namespace Consistency", True, f"Found {namespace_count} resources with correct namespace")
        else:
            return TestResult("Namespace Consistency", False, "No resources found with correct namespace")

    def test_custom_namespace(self) -> TestResult:
        """Test that custom namespace is applied correctly"""
        print("🧪 Testing custom namespace...")
        if "namespace: test-namespace" in self.rendered_custom_yaml:
            return TestResult("Custom Namespace", True, "Custom namespace applied correctly")
        else:
            return TestResult("Custom Namespace", False, "Custom namespace not applied")

    def test_service_selectors(self) -> TestResult:
        """Test that services have correct selectors"""
        print("🧪 Testing service selectors...")
        services = [
            ("rag-frontend", "app: rag-frontend"),
            ("rag-query", "app: rag-query"),
            ("rag-indexing", "app: rag-indexing"),
            ("opensearch", "app: opensearch")
        ]
        
        missing_selectors = []
        for service_name, selector in services:
            if selector not in self.rendered_yaml:
                missing_selectors.append(f"{service_name} ({selector})")
        
        if not missing_selectors:
            return TestResult("Service Selectors", True, "All service selectors correct")
        else:
            return TestResult("Service Selectors", False, f"Missing selectors: {', '.join(missing_selectors)}")

    def test_image_references(self) -> TestResult:
        """Test that image references are correct"""
        print("🧪 Testing image references...")
        expected_images = [
            "public.ecr.aws/e8b9x6t1/haystack-frontend:0.1.0",
            "opensearchproject/opensearch:2.18.0"
        ]
        
        missing_images = []
        for image in expected_images:
            if image not in self.rendered_yaml:
                missing_images.append(image)
        
        if not missing_images:
            return TestResult("Image References", True, "All image references correct")
        else:
            return TestResult("Image References", False, f"Missing images: {', '.join(missing_images)}")

    def test_port_configurations(self) -> TestResult:
        """Test that port configurations are correct"""
        print("🧪 Testing port configurations...")
        port_configs = [
            ("opensearch", "9200"),
            ("rag-frontend", "80"),
            ("rag-query", "8000"),
            ("rag-indexing", "8000")
        ]
        
        missing_ports = []
        for service_name, port in port_configs:
            if f"port: {port}" not in self.rendered_yaml:
                missing_ports.append(f"{service_name}:{port}")
        
        if not missing_ports:
            return TestResult("Port Configurations", True, "All port configurations correct")
        else:
            return TestResult("Port Configurations", False, f"Missing ports: {', '.join(missing_ports)}")

    def test_environment_variables(self) -> TestResult:
        """Test that environment variables are set correctly"""
        print("🧪 Testing environment variables...")
        env_vars = [
            "REACT_APP_HAYSTACK_API_URL",
            "OPENSEARCH_HOST",
            "OPENSEARCH_PORT"
        ]
        
        missing_env_vars = []
        for env_var in env_vars:
            if env_var not in self.rendered_yaml:
                missing_env_vars.append(env_var)
        
        if not missing_env_vars:
            return TestResult("Environment Variables", True, "All environment variables set")
        else:
            return TestResult("Environment Variables", False, f"Missing env vars: {', '.join(missing_env_vars)}")

    def run_all_tests(self) -> List[TestResult]:
        """Run all tests and return results"""
        print("🚀 Starting Helm Chart Testing...")
        print("=" * 50)
        
        # Run all tests
        tests = [
            self.test_chart_rendering,
            self.test_custom_values_rendering,
            self.test_required_resources,
            self.test_specific_resources,
            self.test_namespace_consistency,
            self.test_custom_namespace,
            self.test_service_selectors,
            self.test_image_references,
            self.test_port_configurations,
            self.test_environment_variables
        ]
        
        for test in tests:
            result = test()
            self.results.append(result)
            
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} {result.name}: {result.message}")
        
        return self.results

    def save_results(self, filename: str = "test-results.json"):
        """Save test results to JSON file"""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "chart_dir": self.chart_dir,
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.passed),
            "failed_tests": sum(1 for r in self.results if not r.passed),
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n📊 Test results saved to {filename}")

def main():
    """Main test runner"""
    tester = HelmChartTester()
    results = tester.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("🎉 All tests passed!")
        tester.save_results()
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        tester.save_results()
        sys.exit(1)

if __name__ == "__main__":
    main() 