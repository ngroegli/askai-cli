# Version Management System

This document describes the centralized version management system for AskAI CLI.

## Overview

The version management system implements a single source of truth approach with automated version bumping and release capabilities.

## Architecture

### Core Files

- **`src/askai/_version.py`**: Single source of truth for all version information
- **`src/askai/__init__.py`**: Imports version from `_version.py`
- **`src/askai/presentation/cli/cli_parser.py`**: CLI with `--version` flag
- **`src/scripts/bump_version.py`**: Automated version bumping utility
- **`src/scripts/release.py`**: Release management with git tagging
- **`src/scripts/validate_version.py`**: Version consistency validation

### Version Format

The system uses semantic versioning (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Usage

### Check Current Version

```bash
# CLI version display
python -m askai.main --version

# Or check from source
python src/scripts/validate_version.py
```

### Bump Version

```bash
# Patch bump (0.1.0 -> 0.1.1)
python src/scripts/bump_version.py patch

# Minor bump (0.1.0 -> 0.2.0)
python src/scripts/bump_version.py minor

# Major bump (0.1.0 -> 1.0.0)
python src/scripts/bump_version.py major

# Set specific version
python src/scripts/bump_version.py --set 2.1.0

# Dry run (preview changes)
python src/scripts/bump_version.py patch --dry-run
```### Create Release

```bash
# Create git tag for current version
python src/scripts/release.py

# Create release with auto-generated changelog
python src/scripts/release.py --auto-changelog

# Create release with custom notes file
python src/scripts/release.py --notes RELEASE_NOTES.md

# Dry run (preview release)
python src/scripts/release.py --dry-run --auto-changelog
```

### Validate Version Consistency

```bash
# Check all version references are consistent (includes Docker files)
python src/scripts/validate_version.py
```

### Docker Management

```bash
# Build Docker image with current version
python src/scripts/docker_manager.py build

# Build with specific version
python src/scripts/docker_manager.py build --version 1.2.3

# Start services
python src/scripts/docker_manager.py start

# Start with production profile
python src/scripts/docker_manager.py start --profile production

# Push to registry
python src/scripts/docker_manager.py push --registry your-registry/askai

# Show Docker status
python src/scripts/docker_manager.py status

# Clean old images
python src/scripts/docker_manager.py clean
```

## Files Updated by Version Bumping

The version bumping script automatically updates:

1. **`src/askai/_version.py`**: Primary version definition
2. **`pyproject.toml`**: Package configuration version
3. **`askai.sh`**: Wrapper script version (if exists)
4. **`Dockerfile`**: Docker image version label
5. **`docker-compose.yml`**: Container environment version variable

## Features

### Automated Updates
- Synchronizes version across all project files
- Validates semantic versioning format
- Prevents duplicate version bumps
- Supports dry-run mode for testing

### Release Management
- Git tag creation with release notes
- Automatic changelog generation from commits
- Release validation and error checking
- Changelog file maintenance

### Version Validation
- Consistency checking across files
- Import validation
- Format verification
- Error reporting for mismatches

## Integration

### CLI Integration
The `--version` flag is integrated into the main CLI parser:
```bash
python -m askai.main --version
# Output: AskAI CLI 0.1.0
```

### Package Integration
Version is centrally imported throughout the codebase:
```python
from askai._version import __version__
```

## Error Handling

The system includes comprehensive error handling for:
- Invalid version formats
- File update failures
- Git operation errors
- Import/dependency issues
- Version consistency mismatches

## Best Practices

1. **Always use the scripts** for version changes (don't edit manually)
2. **Run validation** after any version-related changes
3. **Use dry-run mode** to preview changes before applying
4. **Create releases** through the release script for consistency
5. **Keep changelog updated** for better release tracking

## Troubleshooting

### Common Issues

1. **Version mismatch errors**: Run `python src/scripts/validate_version.py` to identify inconsistencies
2. **Import errors**: Ensure all version imports use `from askai._version import __version__`
3. **Git tag conflicts**: Check existing tags with `git tag -l`
4. **Permission issues**: Ensure scripts are executable with `chmod +x src/scripts/*.py`

### Recovery

If version files become inconsistent:
1. Check current source version: `python -c "from askai._version import __version__; print(__version__)"`
2. Update all files: `python src/scripts/bump_version.py --set X.Y.Z`
3. Validate consistency: `python src/scripts/validate_version.py`

## Future Enhancements

Potential improvements to consider:
- CI/CD integration for automated releases
- Version branch management
- Release note templates
- Dependency version tracking
- Multi-package version coordination