# Unit Test Structure

This document describes the mapping between production code and unit tests.

## Test Directory Structure

The test directory structure mirrors the production code structure:

```
tests/unit/
├── core/
│   ├── ai/
│   │   ├── test_service.py          → src/askai/core/ai/service.py
│   │   ├── test_service_minimal.py  → src/askai/core/ai/service.py (minimal tests)
│   │   ├── test_openrouter.py       → src/askai/core/ai/openrouter.py
│   │   └── test_messaging.py        → src/askai/core/ai/* (integration tests)
│   ├── chat/
│   │   └── test_manager.py          → src/askai/core/chat/manager.py
│   ├── messaging/
│   │   └── test_builder.py          → src/askai/core/messaging/builder.py
│   ├── patterns/
│   │   ├── test_manager.py          → src/askai/core/patterns/manager.py
│   │   ├── test_configuration.py    → src/askai/core/patterns/configuration.py
│   │   ├── test_inputs.py           → src/askai/core/patterns/inputs.py (TODO)
│   │   └── test_outputs.py          → src/askai/core/patterns/outputs.py (TODO)
│   └── questions/
│       ├── test_processor.py        → src/askai/core/questions/processor.py
│       └── test_models.py           → src/askai/core/questions/models.py (TODO)
├── output/
│   ├── test_coordinator.py          → src/askai/output/coordinator.py
│   ├── formatters/
│   │   ├── test_base.py             → src/askai/output/formatters/base.py (TODO)
│   │   ├── test_markdown.py         → src/askai/output/formatters/markdown.py (TODO)
│   │   └── test_terminal.py         → src/askai/output/formatters/terminal.py (TODO)
│   ├── processors/
│   │   ├── test_directory.py        → src/askai/output/processors/directory.py
│   │   ├── test_extractor.py        → src/askai/output/processors/extractor.py (TODO)
│   │   ├── test_normalizer.py       → src/askai/output/processors/normalizer.py (TODO)
│   │   └── test_pattern.py          → src/askai/output/processors/pattern.py (TODO)
│   └── writers/
│       ├── test_base.py             → src/askai/output/writers/base.py
│       ├── test_chain.py            → src/askai/output/writers/chain.py (TODO)
│       ├── test_css.py              → src/askai/output/writers/css.py (TODO)
│       ├── test_html.py             → src/askai/output/writers/html.py (TODO)
│       ├── test_json.py             → src/askai/output/writers/json.py (TODO)
│       ├── test_js.py               → src/askai/output/writers/js.py (TODO)
│       ├── test_markdown.py         → src/askai/output/writers/markdown.py (TODO)
│       └── test_text.py             → src/askai/output/writers/text.py (TODO)
├── presentation/
│   ├── cli/
│   │   ├── test_handler.py          → src/askai/presentation/cli/handler.py
│   │   └── test_parser.py           → src/askai/presentation/cli/parser.py
│   └── tui/
│       └── test_fallback.py         → src/askai/presentation/tui/fallback.py
└── utils/
    ├── test_config.py               → src/askai/utils/config.py
    ├── test_config_safe.py          → src/askai/utils/config.py (safe mode tests)
    ├── test_helpers.py              → src/askai/utils/helpers.py
    └── test_logging.py              → src/askai/utils/logging.py
```

## Test Coverage Status

### Fully Covered
- ✅ core/ai/service.py
- ✅ core/ai/openrouter.py (newly added)
- ✅ core/chat/manager.py
- ✅ core/messaging/builder.py
- ✅ core/patterns/manager.py
- ✅ core/patterns/configuration.py (newly added)
- ✅ core/questions/processor.py
- ✅ output/coordinator.py
- ✅ output/processors/directory.py
- ✅ output/writers/base.py
- ✅ presentation/cli/handler.py
- ✅ presentation/cli/parser.py
- ✅ presentation/tui/fallback.py
- ✅ utils/config.py
- ✅ utils/helpers.py
- ✅ utils/logging.py (newly added)

### Needs Test Coverage (TODO)
- ⚠️ core/patterns/inputs.py
- ⚠️ core/patterns/outputs.py
- ⚠️ core/questions/models.py
- ⚠️ output/formatters/base.py
- ⚠️ output/formatters/markdown.py
- ⚠️ output/formatters/terminal.py
- ⚠️ output/processors/extractor.py
- ⚠️ output/processors/normalizer.py
- ⚠️ output/processors/pattern.py
- ⚠️ output/writers/chain.py
- ⚠️ output/writers/css.py
- ⚠️ output/writers/html.py
- ⚠️ output/writers/json.py
- ⚠️ output/writers/js.py
- ⚠️ output/writers/markdown.py
- ⚠️ output/writers/text.py

## Running Tests

### Run All Unit Tests
```bash
python tests/run_unit_tests.py
```

### Run Specific Test File
```bash
cd tests/unit
python core/ai/test_service.py
```

### Run Tests for Specific Module
```bash
# Test all core tests
python -m pytest tests/unit/core/ -v

# Test all output tests
python -m pytest tests/unit/output/ -v
```

## Test Naming Convention

- Test files should be named `test_<module>.py` matching the production module name
- Test classes should be named `Test<ClassName>` matching the production class
- Test methods should be named `test_<functionality>` describing what is being tested

## Recent Changes

### Structure Refactoring (November 2025)
- Reorganized test directory structure to mirror production code
- Moved tests from flat structure to nested directories matching production
- Created subdirectories for ai/, chat/, messaging/, patterns/, questions/, formatters/, processors/, writers/
- Added new test files for previously untested modules:
  - test_openrouter.py for OpenRouter client
  - test_logging.py for logging functionality
  - test_configuration.py for pattern configuration classes

### Legacy Code Cleanup
- Removed all legacy import paths (shared.*, modules.*, infrastructure.*)
- Updated sys.modules references to use new paths
- Eliminated duplicate test directory structures
