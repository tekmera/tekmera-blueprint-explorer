# Development Scripts

This directory contains development and build scripts for the Tekmera project.

## Directory Structure

### `legacy/`
Contains all original development scripts preserved during the projection system migration:
- Development workflow scripts (`run-dev.sh`, `check-dev.sh`, `setup-dev.sh`)
- Release management scripts (`release-*.sh`)
- License generation scripts (`generate-*-license.py`)
- Environment-specific runners (`run-dev-*.sh`)

These scripts continue to work with the current legacy system and should be used for development until migration is complete.

## Usage

For current development, use scripts from the legacy folder:

```bash
# Setup development environment
./scripts/legacy/setup-dev.sh

# Run development environment
./scripts/legacy/run-dev.sh

# Check code quality  
./scripts/legacy/check-dev.sh

# Build releases
./scripts/legacy/release-patch.sh
```

## Migration Notes

As the projection system migration progresses, new scripts will be added to support the new architecture. Legacy scripts will be maintained until the migration is complete and all functionality has been validated.