#!/usr/bin/env python3
"""
Main runner for askai-cli unit tests.
"""
import os
import sys
import argparse
import importlib
import inspect
from typing import Dict, Type

# Set the testing environment variables
os.environ['ASKAI_TESTING'] = 'true'
os.environ['ASKAI_NO_TUI'] = 'true'  # Disable TUI during tests

# Add the project root directory to sys.path FIRST
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Add the python directory so modules can be imported directly
python_dir = os.path.join(project_root, "python")
sys.path.insert(0, python_dir)

# Import project modules after path setup
# pylint: disable=wrong-import-position,import-error
from unit.test_base import BaseUnitTest

# Ensure 'unit' is a package and in sys.path before importing
unit_dir = os.path.join(os.path.dirname(__file__), "unit")
if unit_dir not in sys.path:
    sys.path.insert(0, unit_dir)


def discover_tests() -> Dict[str, Type[BaseUnitTest]]:
    """Dynamically discover all test classes in the unit test directories.

    Returns:
        Dict[str, Type[BaseUnitTest]]: Dictionary of test name to test class
    """
    tests = {}

    # Define the test modules to scan based on our layered architecture
    test_categories = [
        'shared',      # shared layer tests
        'modules',     # modules layer tests
        'presentation', # presentation layer tests
        'infrastructure' # infrastructure layer tests
    ]

    # Scan each category directory for test modules
    for category in test_categories:
        module_prefix = f"unit.{category}"
        category_dir = os.path.join(os.path.dirname(__file__), "unit", category)

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
                        if inspect.isclass(obj):
                            # Check if it's a test class by checking if it has the run method
                            # and is not the base class itself
                            if (hasattr(obj, 'run') and
                                hasattr(obj, 'add_result') and
                                hasattr(obj, 'report') and
                                name not in ['BaseUnitTest', 'MockMixin']):
                                # Create a test ID based on category and class name
                                test_id = f"{category}_{name.lower()}"
                                tests[test_id] = obj
                except (ImportError, AttributeError) as e:
                    print(f"Error importing tests from {full_module_name}: {e}")

    return tests


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run unit tests for askai-cli")
    parser.add_argument(
        "--layer",
        choices=["shared", "modules", "presentation", "infrastructure"],
        help="Run tests from a specific architectural layer"
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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output including test details"
    )

    return parser.parse_args()


def main():
    """Main entry point for unit test runner."""
    args = parse_args()

    # Discover available tests
    all_tests = discover_tests()

    if args.list:
        # Just list the available tests
        print("\nAvailable unit tests:")
        print("=" * 60)

        # Group by layer
        tests_by_layer = {}
        for test_id, test_class in all_tests.items():
            layer = test_id.split('_')[0]
            if layer not in tests_by_layer:
                tests_by_layer[layer] = []
            tests_by_layer[layer].append((test_id, test_class))

        # Print by layer
        for layer, tests in sorted(tests_by_layer.items()):
            print(f"\n{layer.upper()} LAYER TESTS:")
            for test_id, test_class in sorted(tests):
                print(f"  {test_id:<35} [{test_class.__module__}]")

        return 0

    # Filter by layer if specified
    if args.layer:
        layer_tests = {name: cls for name, cls in all_tests.items()
                      if name.startswith(args.layer)}
        all_tests = layer_tests

    # Filter tests based on command line arguments
    if args.test:
        if args.test not in all_tests:
            print(f"Error: Test '{args.test}' not found.")
            print(f"Available tests: {', '.join(all_tests.keys())}")
            print("Use --list to see all available tests")
            return 1
        selected_tests = {args.test: all_tests[args.test]}
    else:
        selected_tests = all_tests

    if not selected_tests:
        print("No tests selected to run.")
        print("Use --list to see all available tests")
        return 0

    # Show what we're running
    print(f"\nRunning {len(selected_tests)} unit test(s)...")
    if args.layer:
        print(f"Layer filter: {args.layer}")

    # Count total passed and failed tests and collect detailed results
    total_passed = 0
    total_failed = 0
    detailed_results = []

    # Run the selected tests
    for name, test_class in sorted(selected_tests.items()):
        print(f"\n{'='*50}")
        print(f"Running unit test: {name}")
        print(f"{'='*50}")

        test = test_class()
        test.run()
        passed, failed = test.report()
        total_passed += passed
        total_failed += failed

        # Collect detailed results for the summary table
        for result in test.results:
            detailed_results.append({
                'test_file': name,
                'test_action': result.name,
                'status': 'PASS' if result.passed else 'FAIL',
                'message': result.message
            })

    # Print overall summary with color formatting
    print("\n" + "=" * 70)

    # ANSI color codes
    GREEN = "\033[92m"  # Bright green  # pylint: disable=invalid-name
    RED = "\033[91m"    # Bright red    # pylint: disable=invalid-name
    BLUE = "\033[94m"   # Bright blue   # pylint: disable=invalid-name
    RESET = "\033[0m"   # Reset color   # pylint: disable=invalid-name

    print(f"{BLUE}UNIT TEST SUMMARY{RESET}")
    print("=" * 70)

    # Determine the color formatting based on test results
    if total_passed > 0 and total_failed == 0:
        # All tests passed - everything in green
        print(f"OVERALL RESULT: {GREEN}{total_passed} passed{RESET}, {GREEN}{total_failed} failed{RESET}")
    elif total_passed == 0 and total_failed > 0:
        # All tests failed - both numbers in red
        print(f"OVERALL RESULT: {RED}{total_passed} passed{RESET}, {RED}{total_failed} failed{RESET}")
    else:
        # Mixed results - passed in green, failed in red
        print(f"OVERALL RESULT: {GREEN}{total_passed} passed{RESET}, {RED}{total_failed} failed{RESET}")

    # Print detailed results table if verbose or if there are failures
    if args.verbose or total_failed > 0:
        print("\nDETAILED TEST RESULTS:")

        # Calculate column widths
        max_file_width = max(len(r['test_file']) for r in detailed_results) if detailed_results else 20
        max_action_width = max(len(r['test_action']) for r in detailed_results) if detailed_results else 25
        max_message_width = max(len(r['message']) for r in detailed_results) if detailed_results else 35

        # Ensure minimum and maximum widths
        file_width = max(20, min(max_file_width, 35))
        action_width = max(25, min(max_action_width, 40))
        message_width = max(35, min(max_message_width, 50))
        status_width = 8

        # Calculate total table width
        total_width = file_width + action_width + status_width + message_width + 3  # +3 for spaces

        print("=" * total_width)
        print(f"{'TEST FILE':<{file_width}} {'TEST METHOD':<{action_width}} "
              f"{'STATUS':<{status_width}} {'MESSAGE':<{message_width}}")
        print("-" * total_width)

        # Print each test result
        for result in detailed_results:
            # Truncate long strings if necessary
            test_file = (result['test_file'][:file_width-3] + "..."
                        if len(result['test_file']) > file_width
                        else result['test_file'])
            test_action = (result['test_action'][:action_width-3] + "..."
                          if len(result['test_action']) > action_width
                          else result['test_action'])
            message = (result['message'][:message_width-3] + "..."
                      if len(result['message']) > message_width
                      else result['message'])

            # Color the status
            status = result['status']
            if status == 'PASS':
                colored_status = f"{GREEN}{status}{RESET}"
            else:
                colored_status = f"{RED}{status}{RESET}"

            print(f"{test_file:<{file_width}} {test_action:<{action_width}} "
                  f"{colored_status:<15} {message:<{message_width}}")

        print("=" * total_width)

    # Return appropriate exit code
    return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
