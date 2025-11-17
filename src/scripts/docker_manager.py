#!/usr/bin/env python3
"""
Docker management script for AskAI CLI with version awareness.

Provides utilities for building, tagging, and managing Docker images
with proper version management integration.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add parent directory (src) to path to import from askai
sys.path.insert(0, str(Path(__file__).parent.parent))

# pylint: disable=wrong-import-position
from askai._version import __version__ as current_version

def run_command(cmd, check=True):
    """Run shell command safely."""
    import shlex
    print(f"Running: {cmd}")
    
    try:
        # Try to use safer execution
        if any(char in cmd for char in ['|', '&', ';', '$', '`']):
            # Complex shell command - use shell=True but note it's for docker commands only
            result = subprocess.run(cmd, shell=True, check=False)  # nosec B602
        else:
            # Simple command - use safer approach  
            args = shlex.split(cmd)
            result = subprocess.run(args, check=False)
    except (ValueError, OSError):
        # Fallback for complex docker commands that need shell=True
        result = subprocess.run(cmd, shell=True, check=False)  # nosec B602
    
    if check and result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result.returncode

def build_image(version=None, tag_latest=True):
    """Build Docker image with version tag."""
    version = version or current_version
    image_name = "askai-cli"

    # Build with version tag
    cmd = f"docker build -t {image_name}:{version} ."
    run_command(cmd)

    # Also tag as latest if requested
    if tag_latest:
        cmd = f"docker tag {image_name}:{version} {image_name}:latest"
        run_command(cmd)

    print(f"✅ Built image: {image_name}:{version}")
    if tag_latest:
        print(f"✅ Tagged as: {image_name}:latest")

def push_image(version=None, registry=None, push_latest=True):
    """Push Docker image to registry."""
    version = version or current_version
    image_name = "askai-cli"

    if registry:
        image_name = f"{registry}/{image_name}"

    # Push version tag
    cmd = f"docker push {image_name}:{version}"
    run_command(cmd)

    # Push latest tag if requested
    if push_latest:
        cmd = f"docker push {image_name}:latest"
        run_command(cmd)

    print(f"✅ Pushed: {image_name}:{version}")
    if push_latest:
        print(f"✅ Pushed: {image_name}:latest")

def start_compose(profile=None):
    """Start docker-compose services."""
    cmd = "docker-compose up -d"
    if profile:
        cmd += f" --profile {profile}"

    run_command(cmd)
    print("✅ Services started")

def stop_compose():
    """Stop docker-compose services."""
    run_command("docker-compose down")
    print("✅ Services stopped")

def clean_images(keep_latest=True):
    """Clean up old Docker images."""
    image_name = "askai-cli"

    if keep_latest:
        # Remove all tags except latest and current version
        cmd = (f'docker images {image_name} --format "table {{{{.Tag}}}}" | '
               f'grep -v "TAG\\|latest\\|{current_version}" | '
               f'xargs -r docker rmi {image_name}:')
    else:
        # Remove all images
        cmd = f"docker rmi $(docker images {image_name} -q) 2>/dev/null || true"

    run_command(cmd, check=False)  # Don't fail if no images to remove
    print("✅ Cleaned up old images")

def show_status():
    """Show Docker status and running containers."""
    print("=== Docker Images ===")
    run_command("docker images askai-cli", check=False)

    print("\n=== Running Containers ===")
    run_command("docker ps --filter ancestor=askai-cli", check=False)

    print("\n=== Compose Services ===")
    run_command("docker-compose ps", check=False)

def main():
    """Main function for Docker management."""
    parser = argparse.ArgumentParser(description="Docker management for AskAI CLI")
    subparsers = parser.add_subparsers(dest='action', help='Available actions')

    # Build command
    build_parser = subparsers.add_parser('build', help='Build Docker image')
    build_parser.add_argument('--version', help='Version tag (default: current version)')
    build_parser.add_argument('--no-latest', action='store_true', help="Don't tag as latest")

    # Push command
    push_parser = subparsers.add_parser('push', help='Push Docker image')
    push_parser.add_argument('--version', help='Version tag (default: current version)')
    push_parser.add_argument('--registry', help='Docker registry (e.g., docker.io/username)')
    push_parser.add_argument('--no-latest', action='store_true', help="Don't push latest tag")

    # Compose commands
    start_parser = subparsers.add_parser('start', help='Start docker-compose services')
    start_parser.add_argument('--profile', help='Docker compose profile to use')

    subparsers.add_parser('stop', help='Stop docker-compose services')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean up old images')
    clean_parser.add_argument('--all', action='store_true', help='Remove all images including latest')

    # Status command
    subparsers.add_parser('status', help='Show Docker status')

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        return

    print(f"Current version: {current_version}")
    print()

    if args.action == 'build':
        build_image(args.version, not args.no_latest)
    elif args.action == 'push':
        push_image(args.version, args.registry, not args.no_latest)
    elif args.action == 'start':
        start_compose(getattr(args, 'profile', None))
    elif args.action == 'stop':
        stop_compose()
    elif args.action == 'clean':
        clean_images(not args.all)
    elif args.action == 'status':
        show_status()

if __name__ == "__main__":
    main()
