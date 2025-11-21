#!/usr/bin/env python3
"""
Release management script for AskAI CLI.

Handles creating releases with automated changelog generation,
git tagging, and semantic versioning.
"""

import argparse
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory (src) to path to import from askai
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position
from askai._version import __version__ as current_version

def run_command(cmd, check=True, capture=False):
    """Run shell command safely."""

    try:
        # Try safer execution for simple commands
        if any(char in cmd for char in ['|', '&', ';', '$', '`', '>']):
            # Complex shell command - use shell=True (needed for git operations)
            if capture:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)  # nosec B602
            else:
                result = subprocess.run(cmd, shell=True, check=False)  # nosec B602
        else:
            # Simple command - use safer approach
            args = shlex.split(cmd)
            if capture:
                result = subprocess.run(args, capture_output=True, text=True, check=False)
            else:
                result = subprocess.run(args, check=False)
    except (ValueError, OSError):
        # Fallback for complex git commands
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)  # nosec B602
        else:
            result = subprocess.run(cmd, shell=True, check=False)  # nosec B602

    if check and result.returncode:
        print(f"Command failed: {cmd}")
        if capture:
            print(f"Error: {result.stderr}")
        sys.exit(1)

    if capture:
        return result.stdout.strip()
    return result.returncode

def get_git_commits_since_tag(tag):
    """Get commits since last tag."""
    try:
        cmd = f"git log {tag}..HEAD --oneline"
        commits = run_command(cmd, check=False, capture=True)
        if isinstance(commits, str):
            return commits.split('\n') if commits else []
        return []
    except subprocess.CalledProcessError:
        # If tag doesn't exist, get all commits
        cmd = "git log --oneline"
        commits = run_command(cmd, check=False, capture=True)
        if isinstance(commits, str):
            return commits.split('\n')[:10]  # Limit to last 10
        return []

def get_last_tag():
    """Get the last git tag."""
    try:
        result = run_command("git describe --tags --abbrev=0", check=False, capture=True)
        return result if isinstance(result, str) else None
    except subprocess.CalledProcessError:
        return None

def generate_changelog_from_commits(commits):
    """Generate changelog from commit messages."""
    features = []
    fixes = []
    other = []

    for commit in commits:
        if not commit.strip():
            continue

        commit_lower = commit.lower()
        if any(word in commit_lower for word in ['feat:', 'feature:', 'add:']):
            features.append(commit)
        elif any(word in commit_lower for word in ['fix:', 'bug:', 'patch:']):
            fixes.append(commit)
        else:
            other.append(commit)

    changelog = []

    if features:
        changelog.append("### Added")
        for feat in features:
            changelog.append(f"- {feat}")
        changelog.append("")

    if fixes:
        changelog.append("### Fixed")
        for fix in fixes:
            changelog.append(f"- {fix}")
        changelog.append("")

    if other:
        changelog.append("### Changed")
        for change in other:
            changelog.append(f"- {change}")
        changelog.append("")

    return '\n'.join(changelog)

def create_release(version, release_notes=None):
    """Create a git release."""
    # Check if working directory is clean
    status = run_command("git status --porcelain", check=False, capture=True)
    if isinstance(status, str) and status.strip():
        print("Working directory is not clean. Please commit or stash changes.")
        print("Uncommitted changes:")
        print(status)
        return False

    # Check if version tag already exists
    try:
        existing = run_command(f"git tag -l v{version}", check=False, capture=True)
        if isinstance(existing, str) and existing.strip():
            print(f"Tag v{version} already exists!")
            return False
    except subprocess.CalledProcessError:
        pass

    # Create tag
    tag_msg = f"Release v{version}"
    if release_notes:
        tag_msg += f"\n\n{release_notes}"

    print(f"Creating tag v{version}...")
    run_command(f"git tag -a v{version} -m '{tag_msg}'")

    print("Release created successfully!")
    print(f"Tag: v{version}")
    print("To push the release:")
    print(f"  git push origin v{version}")
    print("  git push origin --tags")

    return True

def main():
    """Main function for creating releases."""
    parser = argparse.ArgumentParser(description="Create release for AskAI CLI")
    parser.add_argument('--version', help='Version to release (default: current version)')
    parser.add_argument('--notes', help='Release notes file')
    parser.add_argument('--auto-changelog', action='store_true',
                       help='Automatically generate changelog from git commits')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without creating release')

    args = parser.parse_args()

    version = args.version or current_version

    print(f"Preparing release for version {version}")

    # Get release notes
    release_notes = ""

    if args.notes and Path(args.notes).exists():
        release_notes = Path(args.notes).read_text(encoding='utf-8').strip()
    elif args.auto_changelog:
        last_tag = get_last_tag()
        print(f"Generating changelog since {last_tag or 'beginning'}")

        commits = get_git_commits_since_tag(last_tag) if last_tag else []
        if commits:
            release_notes = generate_changelog_from_commits(commits)
        else:
            release_notes = "- Initial release"

    if release_notes:
        print("Release notes:")
        print(release_notes)
        print()

    if args.dry_run:
        print("DRY RUN - no release created")
        return

    # Create the release
    success = create_release(version, release_notes)

    if success:
        print(f"\nRelease v{version} created successfully!")

        # Update changelog file
        if release_notes:
            changelog_file = Path(__file__).parent.parent.parent / "CHANGELOG.md"
            today = datetime.now().strftime("%Y-%m-%d")

            new_entry = f"\n## [{version}] - {today}\n\n{release_notes}\n"

            if changelog_file.exists():
                content = changelog_file.read_text(encoding='utf-8')
                # Find first ## and insert before it
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('## [') and version not in line:
                        insert_pos = i
                        break

                new_content = '\n'.join(lines[:insert_pos]) + new_entry + '\n'.join(lines[insert_pos:])
                changelog_file.write_text(new_content, encoding='utf-8')
            else:
                header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n"
                changelog_file.write_text(header + new_entry, encoding='utf-8')

            print(f"Updated {changelog_file}")

if __name__ == "__main__":
    main()
