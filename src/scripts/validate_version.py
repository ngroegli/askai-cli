#!/usr/bin/env python3
"""
Validation script for version management system.

Checks version consistency across all project files.
"""

import sys
from pathlib import Path
import re

# Add parent directory (src) to path to import from askai
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position
from askai._version import __version__, get_version_info

def get_pyproject_version():
    """Get version from pyproject.toml."""
    pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
    if not pyproject.exists():
        return None

    content = pyproject.read_text(encoding='utf-8')
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else None

def get_init_version():
    """Get version from __init__.py."""
    try:
        return __version__
    except ImportError:
        return None

def get_wrapper_version():
    """Get version from wrapper script."""
    wrapper = Path(__file__).parent.parent.parent / "askai.sh"
    if not wrapper.exists():
        return None

    content = wrapper.read_text(encoding='utf-8')
    match = re.search(r'VERSION="([^"]+)"', content)
    return match.group(1) if match else None

def get_dockerfile_version():
    """Get version from Dockerfile label."""
    dockerfile = Path(__file__).parent.parent.parent / "Dockerfile"
    if not dockerfile.exists():
        return None

    content = dockerfile.read_text(encoding='utf-8')
    match = re.search(r'LABEL version="([^"]+)"', content)
    return match.group(1) if match else None

def get_docker_compose_version():
    """Get version from docker-compose.yml environment."""
    compose_file = Path(__file__).parent.parent.parent / "docker-compose.yml"
    if not compose_file.exists():
        return None

    content = compose_file.read_text(encoding='utf-8')
    match = re.search(r'ASKAI_VERSION[=:]([^\n\s]+)', content)
    return match.group(1) if match else None

def main():
    """Validate version consistency."""
    print("Checking version consistency across project files...")
    print(f"Source version: {__version__}")
    print(f"Version tuple: {get_version_info()}")
    print()

    errors = []

    # Check pyproject.toml
    pyproject_version = get_pyproject_version()
    if pyproject_version:
        if pyproject_version != __version__:
            errors.append(f"pyproject.toml version mismatch: {pyproject_version} != {__version__}")
        else:
            print(f"✅ pyproject.toml: {pyproject_version}")
    else:
        print("⚠️  pyproject.toml: version not found")

    # Check wrapper script
    wrapper_version = get_wrapper_version()
    if wrapper_version:
        if wrapper_version != __version__:
            errors.append(f"askai.sh version mismatch: {wrapper_version} != {__version__}")
        else:
            print(f"✅ askai.sh: {wrapper_version}")
    else:
        print("⚠️  askai.sh: version not found")

    # Check __init__.py import
    init_version = get_init_version()
    if init_version:
        if init_version != __version__:
            errors.append(f"__init__.py version mismatch: {init_version} != {__version__}")
        else:
            print(f"✅ __init__.py: {init_version}")
    else:
        errors.append("__init__.py: failed to import version")

    # Check Dockerfile
    dockerfile_version = get_dockerfile_version()
    if dockerfile_version:
        if dockerfile_version != __version__:
            errors.append(f"Dockerfile version mismatch: {dockerfile_version} != {__version__}")
        else:
            print(f"✅ Dockerfile: {dockerfile_version}")
    else:
        print("⚠️  Dockerfile: version label not found")

    # Check docker-compose.yml
    compose_version = get_docker_compose_version()
    if compose_version:
        if compose_version != __version__:
            errors.append(f"docker-compose.yml version mismatch: {compose_version} != {__version__}")
        else:
            print(f"✅ docker-compose.yml: {compose_version}")
    else:
        print("⚠️  docker-compose.yml: ASKAI_VERSION not found")

    print()

    if errors:
        print("❌ Version consistency check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("✅ All versions are consistent!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
