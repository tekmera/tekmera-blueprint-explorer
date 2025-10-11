"""
Version information for Tekmera CLI.
This file is automatically updated during the build process.
"""

__version__ = "0.1.0"
__build_date__ = "dev"
__commit__ = "dev"
__platform__ = "dev"

def get_version_info():
    """Get comprehensive version information."""
    return {
        "version": __version__,
        "build_date": __build_date__,
        "commit": __commit__,
        "platform": __platform__,
    }

def get_version_string():
    """Get a formatted version string for display."""
    if __build_date__ == "dev":
        return f"{__version__} (development)"
    return f"{__version__} (built {__build_date__})"