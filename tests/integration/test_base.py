"""
Base classes for automated and semi-automated integration tests.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from tests.integration.test_utils import TestResult


class BaseIntegrationTest(ABC):
    """Base class for all integration tests."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.results = []
        
    @abstractmethod
    def run(self) -> List[TestResult]:
        """Run the test and return results."""
    
    def report(self):
        """Report the results of the test."""
        print(f"\n{'=' * 70}")
        print(f"Test: {self.name}")
        print(f"{'=' * 70}")
        
        for result in self.results:
            print(result)
            print("-" * 70)
        
        # Summary
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        print(f"\nSummary: {passed} passed, {failed} failed")
        
        return passed, failed


class AutomatedTest(BaseIntegrationTest):
    """Base class for fully automated tests that require no user interaction."""
            
    def add_result(self, test_name: str, passed: bool, message: str, details: Optional[Dict[str, Any]] = None):
        """Add a test result."""
        result = TestResult(test_name)
        if passed:
            result.set_passed(message)
        else:
            result.set_failed(message)
            
        if details:
            for k, v in details.items():
                result.add_detail(k, v)
                
        self.results.append(result)
        return result


class SemiAutomatedTest(BaseIntegrationTest):
    """Base class for tests requiring some user interaction or manual validation."""
    
        
    def prompt_user(self, message: str, options: Optional[List[str]] = None) -> str:
        """Prompt the user for input."""
        print(f"\n{message}")
        
        if options:
            option_str = "/".join(options)
            prompt = f"[{option_str}]: "
        else:
            prompt = ": "
            
        while True:
            response = input(prompt).strip()
            if not options or response in options:
                return response
            print(f"Invalid response. Please choose from: {', '.join(options)}")
            
    def add_manual_result(self, test_name: str) -> TestResult:
        """Add a result based on user validation."""
        response = self.prompt_user(
            f"Did the test '{test_name}' pass?", 
            ["y", "n"]
        )
        
        result = TestResult(test_name)
        if response.lower() == "y":
            result.set_passed("User confirmed test passed")
        else:
            failure_reason = input("Please provide a reason for the failure: ")
            result.set_failed(f"User reported failure: {failure_reason}")
            
        self.results.append(result)
        return result
