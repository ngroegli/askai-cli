#!/usr/bin/env python3
"""
Main runner for askai-cli integration tests.
"""
import os
import sys
import argparse
import importlib
import inspect
from typing import Dict, Type

# Set the testing environment variable to suppress spinner animations
os.environ['ASKAI_TESTING'] = 'true'

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import base test class
from tests.integration.test_base import BaseIntegrationTest, AutomatedTest, SemiAutomatedTest


def discover_tests() -> Dict[str, Type[BaseIntegrationTest]]:
    """Dynamically discover all test classes in the integration test directories.
    
    Returns:
        Dict[str, Type[BaseIntegrationTest]]: Dictionary of test name to test class
    """
    tests = {}
    
    # Define the test modules to scan
    test_categories = [
        'general',
        'question',
        'pattern'
    ]
    
    # Scan each category directory for test modules
    for category in test_categories:
        module_prefix = f"tests.integration.{category}"
        category_dir = os.path.join(os.path.dirname(__file__), "integration", category)
        
        if not os.path.isdir(category_dir):
            continue
            
        # Find all Python files in the category directory
        for filename in os.listdir(category_dir):
            if filename.startswith("test_") and filename.endswith(".py"):
                module_name = filename[:-3]  # Remove .py extension
                full_module_name = f"{module_prefix}.{module_name}"
                
                try:
                    # Import the module
                    module = importlib.import_module(full_module_name)
                    
                    # Find all test classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and issubclass(obj, BaseIntegrationTest) 
                                and obj != BaseIntegrationTest
                                and obj != AutomatedTest
                                and obj != SemiAutomatedTest):
                            # Create a test ID based on category and class name
                            test_id = f"{category}_{name.lower()}"
                            tests[test_id] = obj
                except (ImportError, AttributeError) as e:
                    print(f"Error importing tests from {full_module_name}: {e}")
    
    return tests


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run integration tests for askai-cli")
    parser.add_argument(
        "--automated-only",
        action="store_true",
        help="Run only fully automated tests (no user interaction)"
    )
    parser.add_argument(
        "--semi-automated-only",
        action="store_true", 
        help="Run only semi-automated tests (requiring user interaction)"
    )
    parser.add_argument(
        "--category",
        choices=["general", "question", "pattern"],
        help="Run tests from a specific category"
    )
    parser.add_argument(
        "--test",
        type=str,
        help="Run a specific test by name"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tests without running them"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for test runner."""
    args = parse_args()
    
    # Discover available tests
    all_tests = discover_tests()
    
    if args.list:
        # Just list the available tests
        print("\nAvailable integration tests:")
        print("=" * 50)
        
        # Group by category
        tests_by_category = {}
        for test_id, test_class in all_tests.items():
            category = test_id.split('_')[0]
            if category not in tests_by_category:
                tests_by_category[category] = []
            tests_by_category[category].append((test_id, test_class))
        
        # Print by category
        for category, tests in sorted(tests_by_category.items()):
            print(f"\n{category.upper()} TESTS:")
            for test_id, test_class in sorted(tests):
                test_type = "Automated" if issubclass(test_class, AutomatedTest) else "Semi-automated"
                print(f"  {test_id:<30} [{test_type}]")
        
        return 0
    
    # Categorize tests
    automated_tests = {name: cls for name, cls in all_tests.items() 
                      if issubclass(cls, AutomatedTest)}
    semi_automated_tests = {name: cls for name, cls in all_tests.items() 
                           if issubclass(cls, SemiAutomatedTest)}
    
    # Filter by category if specified
    if args.category:
        category_tests = {name: cls for name, cls in all_tests.items() 
                         if name.startswith(args.category)}
        all_tests = category_tests
        automated_tests = {name: cls for name, cls in automated_tests.items() 
                          if name.startswith(args.category)}
        semi_automated_tests = {name: cls for name, cls in semi_automated_tests.items() 
                               if name.startswith(args.category)}
    
    # Filter tests based on command line arguments
    if args.test:
        if args.test not in all_tests:
            print(f"Error: Test '{args.test}' not found.")
            print(f"Available tests: {', '.join(all_tests.keys())}")
            print("Use --list to see all available tests")
            return 1
        selected_tests = {args.test: all_tests[args.test]}
    elif args.automated_only:
        selected_tests = automated_tests
        print(f"Running only automated tests: {', '.join(selected_tests.keys())}")
    elif args.semi_automated_only:
        selected_tests = semi_automated_tests
        print(f"Running only semi-automated tests: {', '.join(selected_tests.keys())}")
    else:
        selected_tests = all_tests
    
    if not selected_tests:
        print("No tests selected to run.")
        print("Use --list to see all available tests")
        return 0
    
    # Count total passed and failed tests
    total_passed = 0
    total_failed = 0
    
    # Run the selected tests
    for name, test_class in sorted(selected_tests.items()):
        print(f"\nRunning test: {name}")
        test = test_class()
        test.run()
        passed, failed = test.report()
        total_passed += passed
        total_failed += failed
    
    # Print overall summary with color formatting
    print("\n" + "=" * 70)
    
    # ANSI color codes
    GREEN = "\033[92m"  # Bright green
    RED = "\033[91m"    # Bright red
    RESET = "\033[0m"   # Reset color
    
    # Determine the color formatting based on test results
    if total_passed > 0 and total_failed == 0:
        # All tests passed - everything in green
        print(f"OVERALL SUMMARY: {GREEN}{total_passed} passed{RESET}, {GREEN}{total_failed} failed{RESET}")
    elif total_passed == 0 and total_failed > 0:
        # All tests failed - both numbers in red
        print(f"OVERALL SUMMARY: {RED}{total_passed} passed{RESET}, {RED}{total_failed} failed{RESET}")
    else:
        # Mixed results - passed in green, failed in red
        print(f"OVERALL SUMMARY: {GREEN}{total_passed} passed{RESET}, {RED}{total_failed} failed{RESET}")
    
    print("=" * 70)
    
    # Return appropriate exit code
    return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
