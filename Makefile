.PHONY: test test-integration test-integration-automated test-integration-semi test-integration-general test-integration-question test-integration-pattern list-tests lint clean

# Default Python interpreter
PYTHON := python3

# Run all tests
test: test-integration

# Run integration tests
test-integration:
	bash tests/run_integration_tests.sh

# Run automated integration tests only
test-integration-automated:
	bash tests/run_integration_tests.sh --automated-only

# Run semi-automated integration tests only
test-integration-semi:
	bash tests/run_integration_tests.sh --semi-automated-only

# Run tests by category
test-integration-general:
	bash tests/run_integration_tests.sh --category general

test-integration-question:
	bash tests/run_integration_tests.sh --category question

test-integration-pattern:
	bash tests/run_integration_tests.sh --category pattern

# Run a specific integration test
test-integration-%:
	bash tests/run_integration_tests.sh --test $*

# List available tests
list-tests:
	bash tests/run_integration_tests.sh --list

# Run linting
lint:
	./run_pylint.sh

# Clean build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

# Help command
help:
	@echo "Available targets:"
	@echo "  test               Run all tests"
	@echo "  test-integration   Run all integration tests"
	@echo "  test-integration-X Run specific integration test (e.g., test-integration-cli_help)"
	@echo "  lint               Run linting"
	@echo "  clean              Remove build artifacts"
	@echo "  help               Show this help message"
