#!/usr/bin/env python3
"""
Version bumping utility for AskAI CLI.

This script handles version bumping across all project files:
- src/askai/_version.py (main version definition)
- pyproject.toml (Python packaging)
- Any other files that reference version

Usage:
    python src/scripts/bump_version.py patch   # 1.2.3 -> 1.2.4
    python src/scripts/bump_version.py minor   # 1.2.3 -> 1.3.0
    python src/scripts/bump_version.py major   # 1.2.3 -> 2.0.0
    python src/scripts/bump_version.py --set 2.1.0  # Set specific version
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory (src) to path to import from askai
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position
from askai._version import __version__ as current_version

def parse_version(version_str):
    """Parse version string into major, minor, patch components."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:[.\-+].*)?$', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")

    return tuple(map(int, match.groups()))

def bump_version(version_str, bump_type):
    """Bump version according to type (patch, minor, major)."""
    major, minor, patch = parse_version(version_str)

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return f"{major}.{minor}.{patch}"

def validate_version(version_str):
    """Validate version format."""
    try:
        parse_version(version_str)
        return True
    except ValueError:
        return False

def update_version_file(new_version):
    """Update the main version file."""
    version_file = Path(__file__).parent.parent / "askai" / "_version.py"

    if not version_file.exists():
        raise FileNotFoundError(f"Version file not found: {version_file}")

    content = version_file.read_text(encoding='utf-8')

    # Update __version__
    content = re.sub(
        r'__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{new_version}"',
        content
    )

    # Update __version_info__ - it will automatically recalculate from __version__
    content = re.sub(
        r'__version_info__\s*=\s*tuple\(map\(int,\s*__version__\.split\(["\']\.["\']?\)\)\)',
        '__version_info__ = tuple(map(int, __version__.split(".")))',
        content
    )

    # Update individual components - they reference __version_info__
    content = re.sub(r'MAJOR\s*=\s*__version_info__\[0\]', 'MAJOR = __version_info__[0]', content)
    content = re.sub(r'MINOR\s*=\s*__version_info__\[1\]', 'MINOR = __version_info__[1]', content)
    content = re.sub(r'PATCH\s*=\s*__version_info__\[2\]', 'PATCH = __version_info__[2]', content)

    version_file.write_text(content, encoding='utf-8')
    return version_file

def update_pyproject_toml(new_version):
    """Update version in pyproject.toml."""
    pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"

    if not pyproject_file.exists():
        print(f"Warning: pyproject.toml not found at {pyproject_file}")
        return None

    content = pyproject_file.read_text(encoding='utf-8')

    # Update version in [project] section
    content = re.sub(
        r'version\s*=\s*["\'][^"\']+["\']',
        f'version = "{new_version}"',
        content
    )

    pyproject_file.write_text(content, encoding='utf-8')
    return pyproject_file

def update_wrapper_script(new_version):
    """Update version in wrapper script if it exists."""
    wrapper_file = Path(__file__).parent.parent.parent / "askai.sh"

    if not wrapper_file.exists():
        return None

    content = wrapper_file.read_text(encoding='utf-8')

    # Update VERSION variable
    if 'VERSION=' in content:
        content = re.sub(
            r'VERSION=["\'][^"\']+["\']',
            f'VERSION="{new_version}"',
            content
        )
        wrapper_file.write_text(content, encoding='utf-8')
        return wrapper_file

    return None

def update_dockerfile(new_version):
    """Update version labels in Dockerfile."""
    dockerfile = Path(__file__).parent.parent.parent / "Dockerfile"

    if not dockerfile.exists():
        return None

    content = dockerfile.read_text(encoding='utf-8')

    # Add or update version label
    if 'LABEL version=' in content:
        content = re.sub(
            r'LABEL version=["\'][^"\']+["\']',
            f'LABEL version="{new_version}"',
            content
        )
    elif 'LABEL' in content:
        # Add version label after existing labels
        content = re.sub(
            r'(LABEL [^\n]+\n)',
            f'\\1LABEL version="{new_version}"\n',
            content,
            count=1
        )
    else:
        # Add version label after FROM statement
        content = re.sub(
            r'(FROM [^\n]+\n)',
            f'\\1\nLABEL version="{new_version}"\n',
            content,
            count=1
        )

    dockerfile.write_text(content, encoding='utf-8')
    return dockerfile

def update_docker_compose(new_version):
    """Update version-related configurations in docker-compose.yml."""
    compose_file = Path(__file__).parent.parent.parent / "docker-compose.yml"

    if not compose_file.exists():
        return None

    content = compose_file.read_text(encoding='utf-8')

    # Add image tag if using external image (future enhancement)
    # For now, we're building from Dockerfile, so no changes needed
    # But we could add a version label as environment variable

    if 'ASKAI_VERSION:' not in content:
        # Add version as environment variable
        env_pattern = r'(environment:\s*\n(?:\s+-[^\n]+\n)*)'
        if re.search(env_pattern, content):
            content = re.sub(
                env_pattern,
                f'\\1      - ASKAI_VERSION={new_version}\n',
                content
            )
    else:
        # Update existing version environment variable
        content = re.sub(
            r'ASKAI_VERSION=[^\n]+',
            f'ASKAI_VERSION={new_version}',
            content
        )

    compose_file.write_text(content, encoding='utf-8')
    return compose_file

def generate_changelog_entry(new_version, bump_type):
    """Generate a changelog entry."""
    today = datetime.now().strftime("%Y-%m-%d")

    entry = f"\n## [{new_version}] - {today}\n\n"

    if bump_type == "major":
        entry += "### Added\n- Major version update with breaking changes\n\n"
    elif bump_type == "minor":
        entry += "### Added\n- New features and enhancements\n\n"
    elif bump_type == "patch":
        entry += "### Fixed\n- Bug fixes and improvements\n\n"

    return entry

def main():
    """Main function for version bumping."""
    parser = argparse.ArgumentParser(description="Bump version for AskAI CLI")
    parser.add_argument('bump_type', nargs='?', choices=['patch', 'minor', 'major'],
                       help='Type of version bump')
    parser.add_argument('--set', dest='specific_version',
                       help='Set specific version (e.g., 2.1.0)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without making changes')
    parser.add_argument('--changelog', action='store_true',
                       help='Generate changelog entry')

    args = parser.parse_args()

    if not args.bump_type and not args.specific_version:
        parser.error("Must specify either bump type or --set with specific version")

    old_version = current_version

    if args.specific_version:
        new_version = args.specific_version
        if not validate_version(new_version):
            print(f"Error: Invalid version format: {new_version}")
            return 1
        bump_type = "custom"
    else:
        new_version = bump_version(old_version, args.bump_type)
        bump_type = args.bump_type

    print(f"Version bump: {old_version} -> {new_version} (type: {bump_type})")

    if args.dry_run:
        print("DRY RUN - no changes made")
        return 0

    # Validate that this is actually a version change
    if old_version == new_version:
        print("No version change needed")
        return 0

    try:
        # Update all version files
        updated_files = []

        # Main version file
        version_file = update_version_file(new_version)
        updated_files.append(str(version_file))

        # pyproject.toml
        pyproject_file = update_pyproject_toml(new_version)
        if pyproject_file:
            updated_files.append(str(pyproject_file))

        # Wrapper script
        wrapper_file = update_wrapper_script(new_version)
        if wrapper_file:
            updated_files.append(str(wrapper_file))

        # Docker files
        dockerfile = update_dockerfile(new_version)
        if dockerfile:
            updated_files.append(str(dockerfile))

        compose_file = update_docker_compose(new_version)
        if compose_file:
            updated_files.append(str(compose_file))

        print("✅ Version bumped successfully!")
        print("Updated files:")
        for file in updated_files:
            print(f"  - {file}")

        # Generate changelog if requested
        if args.changelog:
            entry = generate_changelog_entry(new_version, bump_type)
            print("\nChangelog entry:")
            print(entry)

        print(f"\nNew version: {new_version}")

    except Exception as e:
        print(f"❌ Error updating version: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
