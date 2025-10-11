"""
Entry point for PyInstaller binary builds.
This allows PyInstaller to properly handle the package structure.
"""

if __name__ == "__main__":
    from tekmera.interfaces.cli.main import main
    main()