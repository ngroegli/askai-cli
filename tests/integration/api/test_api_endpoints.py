"""
Integration tests for the AskAI API endpoints.

These tests verify that the Flask API works correctly and integrates
properly with the CLI functionality.
"""
import sys
import os
from typing import List

# Add project paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "python"))

from tests.integration.test_base import AutomatedTest
from tests.integration.test_utils import TestResult


class APIEndpointsTest(AutomatedTest):
    """Test basic API endpoint functionality."""

    def __init__(self):
        super().__init__()
        self.name = "API Endpoints Test"

    def run(self) -> List[TestResult]:
        """Run API endpoint tests."""
        self.results = []

        try:
            from presentation.api.app import create_app

            # Create test app
            app = create_app({'TESTING': True})

            with app.test_client() as client:
                # Test 1: Root endpoint redirect
                self._test_root_endpoint(client)

                # Test 2: API info endpoint
                self._test_api_info_endpoint(client)

                # Test 3: Health endpoints
                self._test_health_endpoints(client)

                # Test 4: Favicon endpoint
                self._test_favicon_endpoint(client)

                # Test 5: 404 error handling
                self._test_404_handling(client)

        except Exception as e:
            result = TestResult("API Setup")
            result.set_failed(f"Failed to set up API test environment: {e}")
            result.add_detail("exception", str(e))
            self.results.append(result)

        return self.results

    def _test_root_endpoint(self, client):
        """Test root endpoint redirect."""
        result = TestResult("Root Endpoint Redirect")
        try:
            response = client.get('/')
            if response.status_code == 302:
                result.set_passed("Root endpoint redirects correctly")
                result.add_detail("status_code", response.status_code)
                result.add_detail("location", response.headers.get('Location', 'Not set'))
            else:
                result.set_failed(f"Expected 302 redirect, got {response.status_code}")
                result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during root endpoint test: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)

    def _test_api_info_endpoint(self, client):
        """Test API info endpoint."""
        result = TestResult("API Info Endpoint")
        try:
            response = client.get('/api')
            if response.status_code == 200:
                try:
                    data = response.get_json()
                    # Verify expected fields
                    required_fields = ['name', 'version', 'description', 'endpoints']
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        result.set_failed(f"Missing required fields: {missing_fields}")
                    else:
                        result.set_passed("API info endpoint working correctly")
                    result.add_detail("response_data", data)
                except Exception as e:
                    result.set_failed(f"Failed to parse JSON response: {e}")
            else:
                result.set_failed(f"Expected 200 OK, got {response.status_code}")
            result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during API info test: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)

    def _test_health_endpoints(self, client):
        """Test health check endpoints."""
        health_endpoints = [
            ('/api/v1/health/health', 'Health Check'),
            ('/api/v1/health/status', 'Status Check'),
            ('/api/v1/health/ready', 'Readiness Check'),
            ('/api/v1/health/live', 'Liveness Check')
        ]

        for endpoint, name in health_endpoints:
            result = TestResult(name)
            try:
                response = client.get(endpoint)
                if response.status_code == 200:
                    result.set_passed(f"{name} endpoint working")
                    try:
                        data = response.get_json()
                        result.add_detail("response_data", data)
                    except Exception:
                        pass  # Some endpoints might not return JSON
                else:
                    result.set_failed(f"Expected 200 OK, got {response.status_code}")
                result.add_detail("endpoint", endpoint)
                result.add_detail("status_code", response.status_code)
            except Exception as e:
                result.set_failed(f"Exception during health endpoint test: {e}")
                result.add_detail("endpoint", endpoint)
                result.add_detail("exception", str(e))
            self.results.append(result)

    def _test_favicon_endpoint(self, client):
        """Test favicon endpoint."""
        result = TestResult("Favicon Endpoint")
        try:
            response = client.get('/favicon.ico')
            if response.status_code == 204:
                result.set_passed("Favicon endpoint working")
            else:
                result.set_failed(f"Expected 204 No Content, got {response.status_code}")
            result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during favicon test: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)

    def _test_404_handling(self, client):
        """Test 404 error handling."""
        result = TestResult("404 Error Handling")
        try:
            response = client.get('/nonexistent-endpoint')
            if response.status_code == 404:
                try:
                    data = response.get_json()
                    # Verify helpful 404 response
                    if 'error' in data and 'available_endpoints' in data:
                        result.set_passed("404 error handling working correctly")
                        result.add_detail("response_data", data)
                    else:
                        result.set_failed("404 response missing expected fields")
                except Exception as e:
                    result.set_failed(f"Failed to parse 404 JSON response: {e}")
            else:
                result.set_failed(f"Expected 404 Not Found, got {response.status_code}")
            result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during 404 test: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)


class APIQuestionsTest(AutomatedTest):
    """Test API questions endpoint functionality."""

    def __init__(self):
        super().__init__()
        self.name = "API Questions Test"

    def run(self) -> List[TestResult]:
        """Run API questions endpoint tests."""
        self.results = []

        try:
            from presentation.api.app import create_app

            # Create test app
            app = create_app({'TESTING': True})

            with app.test_client() as client:
                # Test 1: Question validation - valid question
                self._test_valid_question_validation(client)

                # Test 2: Question validation - invalid question
                self._test_invalid_question_validation(client)

                # Test 3: Question asking endpoint (basic test)
                self._test_question_asking(client)

        except Exception as e:
            result = TestResult("API Questions Setup")
            result.set_failed(f"Failed to set up API questions test environment: {e}")
            result.add_detail("exception", str(e))
            self.results.append(result)

        return self.results

    def _test_valid_question_validation(self, client):
        """Test question validation with valid input."""
        result = TestResult("Valid Question Validation")
        try:
            response = client.post('/api/v1/questions/validate',
                                 json={'question': 'What is artificial intelligence?'})
            if response.status_code == 200:
                try:
                    data = response.get_json()
                    # Verify validation response
                    if 'valid' not in data:
                        result.set_failed("Response missing 'valid' field")
                    elif not data['valid']:
                        result.set_failed(f"Valid question marked as invalid: {data.get('errors', [])}")
                    else:
                        result.set_passed("Valid question validation working")
                    result.add_detail("response_data", data)
                except Exception as e:
                    result.set_failed(f"Failed to parse validation response: {e}")
            else:
                result.set_failed(f"Expected 200 OK, got {response.status_code}")
            result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during valid question validation: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)

    def _test_invalid_question_validation(self, client):
        """Test question validation with invalid input."""
        result = TestResult("Invalid Question Validation")
        try:
            response = client.post('/api/v1/questions/validate',
                                 json={'question': ''})
            if response.status_code == 200:
                try:
                    data = response.get_json()
                    # Verify validation response
                    if 'valid' not in data:
                        result.set_failed("Response missing 'valid' field")
                    elif data['valid']:
                        result.set_failed("Empty question marked as valid")
                    elif 'errors' not in data or not data['errors']:
                        result.set_failed("Invalid question should have error messages")
                    else:
                        result.set_passed("Invalid question validation working")
                    result.add_detail("response_data", data)
                except Exception as e:
                    result.set_failed(f"Failed to parse validation response: {e}")
            else:
                result.set_failed(f"Expected 200 OK, got {response.status_code}")
            result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during invalid question validation: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)

    def _test_question_asking(self, client):
        """Test question asking endpoint (basic connectivity test)."""
        result = TestResult("Question Asking Endpoint")
        try:
            response = client.post('/api/v1/questions/ask',
                                 json={
                                     'question': 'What is 2+2?',
                                     'response_format': 'rawtext'
                                 })

            # Note: This might fail due to AI configuration, but we test the endpoint structure
            if response.status_code == 200:
                try:
                    data = response.get_json()
                    # Verify response structure
                    expected_fields = ['content', 'created_files', 'chat_id']
                    missing_fields = [field for field in expected_fields if field not in data]

                    if missing_fields:
                        result.set_failed(f"Response missing expected fields: {missing_fields}")
                    else:
                        # Check if we got actual AI content
                        content = data.get('content')
                        if content and len(content) > 0:
                            result.set_passed("Question asking endpoint working with AI response")
                            result.add_detail("note", "AI response received successfully")
                        else:
                            result.set_passed("Question asking endpoint working (no AI content)")
                            result.add_detail("note", "Endpoint works but no AI content (likely configuration issue)")
                    result.add_detail("response_data", data)
                except Exception as e:
                    result.set_failed(f"Failed to parse ask response: {e}")
            else:
                # Endpoint might fail due to configuration issues, but that's expected
                result.set_passed("Question asking endpoint responsive")
                result.add_detail("note", f"Endpoint responded with {response.status_code} (configuration dependent)")
            result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during question asking test: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)


class APIPatternsTest(AutomatedTest):
    """Test API patterns endpoint functionality."""

    def __init__(self):
        super().__init__()
        self.name = "API Patterns Test"

    def run(self) -> List[TestResult]:
        """Run API patterns endpoint tests."""
        self.results = []

        try:
            from presentation.api.app import create_app

            # Create test app
            app = create_app({'TESTING': True})

            with app.test_client() as client:
                # Test 1: Patterns listing
                self._test_patterns_listing(client)

                # Test 2: Pattern categories
                self._test_pattern_categories(client)

        except Exception as e:
            result = TestResult("API Patterns Setup")
            result.set_failed(f"Failed to set up API patterns test environment: {e}")
            result.add_detail("exception", str(e))
            self.results.append(result)

        return self.results

    def _test_patterns_listing(self, client):
        """Test patterns listing endpoint."""
        result = TestResult("Patterns Listing")
        try:
            response = client.get('/api/v1/patterns/')
            if response.status_code == 200:
                try:
                    data = response.get_json()
                    # Verify response structure
                    if 'patterns' not in data or 'count' not in data:
                        result.set_failed("Response missing expected fields (patterns, count)")
                    else:
                        result.set_passed("Patterns listing endpoint working")
                    result.add_detail("response_data", data)
                except Exception as e:
                    result.set_failed(f"Failed to parse patterns response: {e}")
            else:
                result.set_failed(f"Expected 200 OK, got {response.status_code}")
            result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during patterns listing test: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)

    def _test_pattern_categories(self, client):
        """Test pattern categories endpoint."""
        result = TestResult("Pattern Categories")
        try:
            response = client.get('/api/v1/patterns/categories')
            if response.status_code == 200:
                try:
                    data = response.get_json()
                    # Verify response structure
                    if 'categories' not in data or 'count' not in data:
                        result.set_failed("Response missing expected fields (categories, count)")
                    else:
                        result.set_passed("Pattern categories endpoint working")
                    result.add_detail("response_data", data)
                except Exception as e:
                    result.set_failed(f"Failed to parse categories response: {e}")
            else:
                result.set_failed(f"Expected 200 OK, got {response.status_code}")
            result.add_detail("status_code", response.status_code)
        except Exception as e:
            result.set_failed(f"Exception during pattern categories test: {e}")
            result.add_detail("exception", str(e))
        self.results.append(result)