#!/usr/bin/env python3
"""
Simple test script for the AskAI API.

This script tests basic API functionality to ensure everything is working correctly.
"""
import requests
import json
import time
import sys


def test_health_endpoint(base_url):
    """Test health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data.get('status')}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_patterns_endpoint(base_url):
    """Test patterns listing endpoint."""
    print("Testing patterns endpoint...")
    try:
        response = requests.get(f"{base_url}/patterns/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            pattern_count = data.get('count', 0)
            print(f"✓ Patterns listed: {pattern_count} patterns found")
            return True
        else:
            print(f"✗ Patterns listing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Patterns listing error: {e}")
        return False


def test_question_validation(base_url):
    """Test question validation endpoint."""
    print("Testing question validation...")
    try:
        payload = {
            "question": "What is artificial intelligence?",
            "response_format": "rawtext"
        }
        response = requests.post(
            f"{base_url}/questions/validate",
            json=payload,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                print("✓ Question validation passed")
                return True
            else:
                print(f"✗ Question validation failed: {data.get('errors')}")
                return False
        else:
            print(f"✗ Question validation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Question validation error: {e}")
        return False


def test_swagger_docs(base_url):
    """Test Swagger documentation endpoint."""
    print("Testing Swagger documentation...")
    try:
        # Test if docs endpoint is accessible
        docs_url = base_url.replace('/api/v1', '/docs/')
        response = requests.get(docs_url, timeout=10)
        if response.status_code == 200:
            print("✓ Swagger documentation accessible")
            return True
        else:
            print(f"✗ Swagger docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Swagger docs error: {e}")
        return False


def main():
    """Main test runner."""
    # Default API base URL
    base_url = "http://localhost:8080/api/v1"

    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"Testing AskAI API at: {base_url}")
    print("=" * 50)

    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)

    # Run tests
    tests = [
        test_health_endpoint,
        test_swagger_docs,
        test_patterns_endpoint,
        test_question_validation,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test(base_url):
            passed += 1
        print()

    # Summary
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()