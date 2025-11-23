# Development Scripts

This directory will contain development and build scripts for the Tekmera project.

## Status

Development scripts are being redesigned to support the new pure functional architecture. 

For current development, use standard Python development practices:

```bash
# Setup development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Run tests
pytest tests/ -v

# Check code quality
flake8 src/ tests/
black src/ tests/
mypy src/
```