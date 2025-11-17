"""
Version information for AskAI CLI.

This is the single source of truth for version information.
All other files should import from here.
"""

__version__ = "1.2.1-dev"

# Parse version info, handling suffixes like -dev, -alpha, etc.
def _parse_version(version_str):
    """Parse version string into tuple of integers, ignoring suffixes."""
    import re
    # Extract just the numeric version part (before any suffix)
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return tuple(map(int, match.groups()))
    else:
        raise ValueError(f"Invalid version format: {version_str}")

__version_info__ = _parse_version(__version__)

# Build and release information
__build__ = None
__commit__ = None
__release_date__ = None

# Version components
MAJOR = __version_info__[0]
MINOR = __version_info__[1]
PATCH = __version_info__[2]

def get_version():
    """Get the current version string."""
    return __version__

def get_version_info():
    """Get version info as a tuple of integers (major, minor, patch)."""
    return __version_info__

def get_full_version():
    """Get full version string with build info if available."""
    version = __version__
    if __build__:
        version += f"+{__build__}"
    return version

def get_version_dict():
    """Get version information as a dictionary."""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "major": MAJOR,
        "minor": MINOR,
        "patch": PATCH,
        "build": __build__,
        "commit": __commit__,
        "release_date": __release_date__,
        "full_version": get_full_version()
    }
