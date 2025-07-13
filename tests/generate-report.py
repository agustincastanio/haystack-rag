#!/usr/bin/env python3
"""
Generate XUnit test report from test results
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List

def load_test_results(filename: str = "test-results.json") -> Dict:
    """Load test results from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found, creating empty report")
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "results": []
        }

def create_xunit_report(results: Dict) -> str:
    """Create XUnit XML report from test results"""
    # Create root element
    testsuites = ET.Element("testsuites")
    testsuites.set("name", "Helm Chart Tests")
    testsuites.set("tests", str(results.get("total_tests", 0)))
    testsuites.set("failures", str(results.get("failed_tests", 0)))
    testsuites.set("time", "0.0")
    
    # Create testsuite element
    testsuite = ET.SubElement(testsuites, "testsuite")
    testsuite.set("name", "Helm Chart Validation")
    testsuite.set("tests", str(results.get("total_tests", 0)))
    testsuite.set("failures", str(results.get("failed_tests", 0)))
    testsuite.set("time", "0.0")
    testsuite.set("timestamp", results.get("timestamp", datetime.now().isoformat()))
    
    # Add test cases
    for test_result in results.get("results", []):
        testcase = ET.SubElement(testsuite, "testcase")
        testcase.set("name", test_result["name"])
        testcase.set("classname", "HelmChartTester")
        testcase.set("time", "0.0")
        
        if not test_result["passed"]:
            failure = ET.SubElement(testcase, "failure")
            failure.set("message", test_result["message"])
            failure.text = test_result["message"]
    
    # Convert to string
    return ET.tostring(testsuites, encoding='unicode')

def main():
    """Generate XUnit report from test results"""
    print("📊 Generating test report...")
    
    # Load test results
    results = load_test_results()
    
    # Create XUnit report
    xunit_xml = create_xunit_report(results)
    
    # Write to file
    with open("test-report.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xunit_xml)
    
    print("✅ XUnit report generated: test-report.xml")
    
    # Print summary
    total = results.get("total_tests", 0)
    passed = results.get("passed_tests", 0)
    failed = results.get("failed_tests", 0)
    
    print(f"\n📋 Report Summary:")
    print(f"   Total tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"   Success rate: {success_rate:.1f}%")

if __name__ == "__main__":
    main() 