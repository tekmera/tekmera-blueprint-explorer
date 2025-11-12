"""
Entry point for running tekmera.interfaces.cli as a module.
This avoids the module import warning when using 'python -m tekmera.interfaces.cli'.
"""

if __name__ == "__main__":
    from .main import main

    main()
